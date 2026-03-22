# Запуск через Docker Compose

- Шаг 1: Клонируй репозиторий и перейди в проект.
```
git clone https://github.com/your-repo/text-analyzer.git
cd text-analyzer
```
- Шаг 2: Убедись, что Docker и Docker Compose установлены.
```
docker --version
docker-compose --version
```
- Шаг 3: Запусти Docker на своём устройстве.
- Шаг 4: выполни команду `docker-compose up --build` из корня проекта

После запуска сервис будет доступен по адресу: http://localhost:8000

# Возможности

- Загрузка файлов любого размера
- Морфологическая нормализация слов (pymorphy3)
- Фоновые задачи через Celery + Redis
- Отслеживание статуса задачи
- Результат в формате Excel (.xlsx)
- Автоматическая очистка старых файлов (24 часа)

# Технологии

- FastAPI - веб-фреймворк
- Celery - очередь задач
- Redis - брокер сообщений
- SQLite - временное хранилище статистики
- pymorphy3 - морфологический анализ
- openpyxl - генерация Excel
- Docker - контейнеризация
