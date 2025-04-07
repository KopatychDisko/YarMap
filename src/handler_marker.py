'''fad'''
import os
import asyncio
import requests
import base64

import pandas as pd      

from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ContentType
from collections import defaultdict

from filter import ChatTypeFilter
from state import Markers

router_marker = Router()

router_marker.message.filter(
    ChatTypeFilter(chat_type="private")
)

# Буфер для альбомов (media groups)
album_buffer = defaultdict(list)


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
    await msg.answer('Введи координаты объекта: (скопируй с яндекс карт)')
    
    await state.set_state(Markers.point)

    
@router_marker.message(Markers.point)
async def name_markers(msg: Message, state: FSMContext):
    '''fad'''
    temp = msg.text.split(', ')
    point = tuple(map(float, temp))
    
    df = pd.read_json('../data/markers.json')
    
    if len(point) != 2:
        await msg.answer('Неправильный формат координат. Должен быть : 53.234, 23.67')
        
        return
    
    if point in df.index:
        await msg.answer('К сожалению, объект с такими координатми уже существует =(')
        
        await state.clear()
        
        return
    await state.set_data({'point': point})
    
    await msg.answer('Напишите название объекта:')
    
    await state.set_state(Markers.name) 
    
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
    
    await msg.answer('Оцени обеъект по доступноти от 1 до 10. Просто введи целое число')
    
    await state.set_state(Markers.stars)

    
@router_marker.message(Markers.stars)
async def stars(msg: Message, state: FSMContext):
    '''fad'''
    await state.update_data({'stars': int(msg.text)})
    
    await msg.answer('Остался последний этап. Пришли несколько фотографий с места событий')
    
    await state.set_state(Markers.photo)
    

@router_marker.message(Markers.photo, F.media_group_id, F.content_type == ContentType.PHOTO)
async def handle_album(message: Message, bot: Bot, state: FSMContext):
    album_buffer[message.media_group_id].append(message)
    await asyncio.sleep(2)  # немного ждём, чтобы все фото пришли
    
    data = await state.get_data()
    folder_name = data['name'].replace(' ', '_')

    messages = album_buffer.pop(message.media_group_id, [])
    if messages:
        count = await save_album_photos(messages, folder_name, bot)
        await message.answer(f"Фото загружены, подождите немного я добавлю все Ваши данные на карту")
    
    
    links = await upload_all_images_from_folder(f'../image/{folder_name}', repo_name='for_image', folder_in_repo=f'image/{folder_name}')
    
    await state.clear()