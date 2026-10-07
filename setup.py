import os
import shutil

os.system("pip install -r requirements.txt")

shutil.rmtree("user_data/log", ignore_errors=True)

# Удаляем папки
shutil.rmtree(".ori", ignore_errors=True)
shutil.rmtree(".vs", ignore_errors=True)
shutil.rmtree(".history", ignore_errors=True)
shutil.rmtree(".session-notes", ignore_errors=True)

# Удаляем лог файлы
shutil.rmtree("user_data/log", ignore_errors=True)

# Python
shutil.rmtree(".venv", ignore_errors=True)
shutil.rmtree("__pycache__", ignore_errors=True)
shutil.rmtree(".pytest_cache", ignore_errors=True)
shutil.rmtree(".mypy_cache", ignore_errors=True)
shutil.rmtree(".ruff_cache", ignore_errors=True)
shutil.rmtree(".hypothesis", ignore_errors=True)
shutil.rmtree(".tox", ignore_errors=True)
shutil.rmtree(".nox", ignore_errors=True)

# IDE
shutil.rmtree(".gigaide", ignore_errors=True)
shutil.rmtree(".vscode", ignore_errors=True)
shutil.rmtree(".idea", ignore_errors=True)
shutil.rmtree(".fleet", ignore_errors=True)
shutil.rmtree(".cursor", ignore_errors=True)
shutil.rmtree(".windsurf", ignore_errors=True)
shutil.rmtree(".zed", ignore_errors=True)

# AI / coding assistants
shutil.rmtree(".copilot", ignore_errors=True)
shutil.rmtree(".continue", ignore_errors=True)
shutil.rmtree(".aider", ignore_errors=True)
shutil.rmtree(".claude", ignore_errors=True)
shutil.rmtree(".gigacode", ignore_errors=True)
shutil.rmtree(".antigravitycli", ignore_errors=True)

# Разные инструменты
shutil.rmtree(".cache", ignore_errors=True)
shutil.rmtree(".coverage", ignore_errors=True)
shutil.rmtree("htmlcov", ignore_errors=True)

# Jupyter
shutil.rmtree(".ipynb_checkpoints", ignore_errors=True)

# Build / packaging
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)
