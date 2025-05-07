from git import Repo, GitCommandError
from dotenv import load_dotenv

import os

load_dotenv()

TOKEN = os.getenv('TOKEN')

def push_to_github_repo(
    repo_path: str,
    github_username: str = 'KopatychDisko',
    github_token: str = TOKEN,
    repo_name: str = 'YarMap',
    branch: str = "master",
    commit_message: str = "Добавили метки"
):
    """
    Выполняет git add, commit и push в приватный GitHub-репозиторий через токен.
    
    :param repo_path: Путь к локальному git-репозиторию
    :param github_username: Логин GitHub
    :param github_token: Personal Access Token
    :param repo_name: Название репозитория на GitHub
    :param branch: Ветка для push (по умолчанию 'main')
    :param commit_message: Сообщение коммита
    """
    try:
        # Формируем URL с токеном
        remote_url = f"https://{github_username}:{github_token}@github.com/{github_username}/{repo_name}.git"
        
        # Загружаем репозиторий
        repo = Repo(repo_path)
        origin = repo.remote(name="origin")
        origin.set_url(remote_url)

        # Добавляем изменения и коммитим
        repo.git.add('data/')
        if repo.is_dirty():
            repo.index.commit(commit_message)
            print("✅ Изменения закоммичены.")
        else:
            print("ℹ️ Нет изменений для коммита.")

        # Пушим на GitHub
        origin.push(refspec=f"{branch}:{branch}")
        print("✅ Успешный push в репозиторий.")
        
    except GitCommandError as e:
        print(f"❌ Ошибка Git: {e}")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")