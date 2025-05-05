'''fad'''
from collections import defaultdict

import os
import asyncio
import requests
import base64
import shutil

import pandas as pd      

from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from aiogram import types

from git import Repo

from filter import ChatTypeFilter
from state import Markers

from map.map_creator import map_to_html

album_buffer = defaultdict(list)
album_processing_locks = {}

router_marker = Router()

router_marker.message.filter(
    ChatTypeFilter(chat_type="private")
)

# Буфер для альбомов (media groups)
album_buffer = defaultdict(list)


def push_to_github_with_token(
    repo_path: str = '../',
    github_username: str = 'KopatychDisko',
    repo_name: str = 'YarMap',
    commit_message: str = "Auto commit",
    branch: str = "master"
):
    # Токен из переменной окружения (безопасно)
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("❌ GITHUB_TOKEN не найден в переменных окружения")

    try:
        # Открываем репозиторий
        repo = Repo(repo_path)

        # Добавляем и коммитим изменения
        repo.git.add(A=True)
        if repo.is_dirty():
            repo.index.commit(commit_message)

        # Формируем HTTPS URL с токеном
        remote_url = f"https://{github_token}@github.com/{github_username}/{repo_name}.git"

        # Устанавливаем origin
        if "origin" not in [r.name for r in repo.remotes]:
            origin = repo.create_remote("origin", remote_url)
        else:
            origin = repo.remote("origin")
            origin.set_url(remote_url)

        # Пушим на GitHub
        origin.push(refspec=f"{branch}:{branch}")
        print("✅ Пуш успешно завершён.")

    except Exception as e:
        print(f"❌ Ошибка при пуше: {e}")


def delete_all_in_directory(directory_path):
    """
    Удаляет все файлы и папки внутри указанной папки (не удаляя саму папку).
    
    :param directory_path: Путь к папке, внутри которой нужно удалить все.
    """
    # Проверяем, существует ли папка
    if os.path.exists(directory_path):
        # Проходим по всем объектам в папке
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                # Если это папка, рекурсивно её удаляем
                shutil.rmtree(item_path)
            else:
                # Если это файл, просто удаляем
                os.remove(item_path)
        print(f"✅ Все содержимое папки '{directory_path}' удалено.")
    else:
        print(f"❌ Папка {directory_path} не существует.")


def upload_html_to_github(
    html_path,
    path_in_repo="index.html",  # Путь в репозитории (корень)
    repo_name="Map",
    repo_owner="KopatychDisko",
    commit_message="Добавил index.html",
    token='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'
):
    '''Загружает HTML-файл в GitHub-репозиторий (в корень репозитория)'''
    with open(html_path, "rb") as html_file:
        encoded_content = base64.b64encode(html_file.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path_in_repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Проверяем, существует ли файл (чтобы получить SHA)
    get_response = requests.get(url, headers=headers)
    
    # Выводим ответ для диагностики
    if get_response.status_code == 200:
        print("Ответ GET запроса:", get_response.json())  # Это покажет, что именно возвращает GitHub
        sha = get_response.json().get("sha") if isinstance(get_response.json(), dict) else None
    else:
        print(f"Ошибка при получении файла: {get_response.status_code}")
        sha = None

    data = {
        "message": commit_message,
        "content": encoded_content
    }
    if sha:
        data["sha"] = sha  # добавляем SHA для обновления файла

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        content_url = response.json()["content"]["download_url"]
        print("✅ HTML-файл успешно загружен.")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.json())

# 📁 Функция сохранения
async def save_album_photos(messages: list[Message], folder_name: str, bot: Bot) -> int:
    """
    Сохраняет фото из сообщений в папку ../image/<folder_name>/ как 1.jpg, 2.jpg, ...
    Возвращает количество сохранённых файлов.
    """
    # Создаём папку ../image/folder_name
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'image'))
    target_folder = os.path.join(base_path, folder_name)
    os.makedirs(target_folder, exist_ok=True)

    for i, msg in enumerate(messages, start=1):
        photo = msg.photo[-1]  # самое большое по размеру фото
        file = await bot.get_file(photo.file_id)
        dest_path = os.path.join(target_folder, f"{i}.jpg")
        await bot.download_file(file.file_path, destination=dest_path)

    return len(messages)


async def upload_image_to_github(image_path, path_in_repo, repo_name="for_image", repo_owner="KopatychDisko", commit_message="Добавил фото", token='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'):
    '''upload image to github'''
    with open(image_path, "rb") as image_file:
        encoded_content = base64.b64encode(image_file.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path_in_repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "message": commit_message,
        "content": encoded_content
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        content_url = response.json()["content"]["download_url"]
        return content_url
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.json())
        return None
    

# 🔄 Загружаем все фото из папки
async def upload_all_images_from_folder(folder_path, folder_in_repo="uploads", repo_name="for_image", repo_owner="KopatychDisko", token='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'):
    links = []

    if not os.path.exists(folder_path):
        print(f"❌ Папка {folder_path} не найдена.")
        return []

    files = sorted(os.listdir(folder_path))
    for filename in files:
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            local_path = os.path.join(folder_path, filename)
            path_in_repo = f"{folder_in_repo}/{filename}"

            url = await upload_image_to_github(
                image_path=local_path,
                path_in_repo=path_in_repo,
                repo_name=repo_name,
                repo_owner=repo_owner,
                token=token
            )
            if url:
                links.append(url)

    return links


@router_marker.message(F.text.lower() == 'метки')
async def start_markers(msg: Message, state: FSMContext):
    '''fad'''
    await msg.answer('Введи координаты объекта: (скопируй с яндекс карт)', reply_markup=types.ReplyKeyboardRemove())
    
    await state.set_state(Markers.point)

    
@router_marker.message(Markers.point)
async def name_markers(msg: Message, state: FSMContext):
    '''Получение координат объекта'''
    try:
        temp = msg.text.split(', ')
        point = tuple(map(float, temp))

        if len(point) != 2:
            await msg.answer('Неправильный формат координат. Должен быть: 53.234, 23.67')
            return

        df = pd.read_json('../data/markers.json')

        # Проверяем, что все элементы в 'point' имеют длину 2
        if any(len(p) != 2 for p in df['point']):
            await msg.answer('Некорректные данные в базе координат. Проверьте формат.')
            return

        # Проверяем, есть ли такие же координаты в DataFrame
        if any(tuple(p) == point for p in df['point']):
            await msg.answer('К сожалению, объект с такими координатами уже существует =(. Если у тебя больше нет объектов жми /cancel')
            return

        await state.set_data({'point': point})
        await msg.answer('Напишите название объекта:')
        await state.set_state(Markers.name)

    except ValueError:
        await msg.answer('Ошибка в формате координат. Убедитесь, что числа разделены запятой.')


@router_marker.message(Markers.name)
async def name(msg: Message, state: FSMContext):
    await state.update_data({'name': msg.text})
    
    await msg.answer('Введите адрес объекта:')
    
    await state.set_state(Markers.addres)

@router_marker.message(Markers.addres)
async def addres(msg: Message, state: FSMContext):
    await state.update_data({'addres': msg.text})
    
    await msg.answer('Супер! Дай краткое описание объекта. (Описать нужно его доступность)')
    
    await state.set_state(Markers.describe)
    

@router_marker.message(Markers.describe)
async def describe(msg: Message, state: FSMContext):
    '''fad'''
    await state.update_data({'describe': msg.text})
    
    await msg.answer('Оцени обеъект по доступноти от 0 до 10. Просто введи целое число')
    
    await state.set_state(Markers.stars)

    
@router_marker.message(Markers.stars)
async def stars(msg: Message, state: FSMContext):
    '''fad'''
    maybe_star = msg.text
    
    if not maybe_star.isdigit():
        await msg.answer('К сожалению Вы ввели не число. Попробуете еще!')
        return
    
    maybe_star = int(maybe_star)
    
    if not (0 <= maybe_star <= 10):
       await msg.answer('Решил проверить меня? Теперь повтори, но введи число от 0 до 10')
       return
    
    await state.update_data({'star': int(maybe_star)})
    
    await msg.answer('Остался последний этап. Пришли несколько фотографий с места событий. (Как только ты скинешь фото бот будет думать примерно 10 сек так что не пугайся, он живой)')
    
    await state.set_state(Markers.photo)
    

@router_marker.message(Markers.photo, F.media_group_id, F.content_type == ContentType.PHOTO)
async def handle_album(message: Message, bot: Bot, state: FSMContext):
    media_group_id = message.media_group_id
    album_buffer[media_group_id].append(message)

    # Если уже обрабатывается — выходим
    if album_processing_locks.get(media_group_id):
        return

    # Ставим флаг "обрабатывается"
    album_processing_locks[media_group_id] = True

    # Ждём немного, чтобы все фото успели прийти
    await asyncio.sleep(10)

    messages = album_buffer.pop(media_group_id, [])
    album_processing_locks.pop(media_group_id, None)  # снимаем флаг

    if not messages:
        return

    # Получаем данные из FSM
    data = await state.get_data()
    folder_name = data['name'].replace(' ', '_')

    count = await save_album_photos(messages, folder_name, bot)
    await message.answer("Фото загружены, подождите немного, я добавлю все Ваши данные на карту")

    await upload_all_images_from_folder(
        f'../image/{folder_name}',
        repo_name='for_image',
        folder_in_repo=f'image/{folder_name}'
    )

    await asyncio.sleep(5)

    data['photo'] = count

    # Загружаем и сохраняем markers.json
    df = pd.read_json('../data/markers.json')
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_json('../data/markers.json', orient='records', indent=4, force_ascii=False)

    await message.answer('Создаю карту с твоими данными....')

    map_to_html('../data/yar_districts.json', '../data/markers.json', '../data/index.html')

    await message.reply_sticker('CAACAgIAAxkBAAKVRmf0zOU0lat_UAIqZfAiK0g31glYAALJbQACxKNIS6T3gguKQd5tNgQ')
    
    upload_html_to_github('../data/index.html')
    
    await message.answer(f'Вот ваша карта:\n https://yar-available-environment.onrender.com/')

    delete_all_in_directory('../image')
    
    await state.clear()

