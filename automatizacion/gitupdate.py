import git
import os

repo_dir = 'D:/LLLIT/Code-W11/PY/api_bot_bd'
file_path = os.path.join(repo_dir, 'temp_calendar/reservations_all.csv')

repo = git.Repo(repo_dir)
repo.git.add(file_path)
repo.index.commit('Actualizar archivo de reservas')
origin = repo.remote(name='origin')
origin.push()