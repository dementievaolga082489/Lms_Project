# LMS Project

API для онлайн-платформы обучения.


## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cp .env.example .env
```

## Запуск

```bash
docker compose up --build
```

После старта:

- Приложение: http://localhost:8000
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- Админка: http://localhost:8000/admin

Миграции применяются автоматически при старте сервиса `web`.

## Полезные команды

```bash
# Создать суперпользователя
docker compose exec web python manage.py createsuperuser

# Применить миграции вручную
docker compose exec web python manage.py migrate

# Логи Celery worker
docker compose logs -f celery

# Логи Celery beat
docker compose logs -f celery-beat

# Остановить контейнеры
docker compose down

# Остановить и удалить данные (БД, Redis, media)
docker compose down -v
```

## Сервисы

| Сервис | Образ / сборка | Назначение | Порт |
|---|---|---|---|
| `db` | `postgres:16-alpine` | база данных | только внутри сети (`expose`) |
| `redis` | `redis:7-alpine` | брокер и backend для Celery | только внутри сети (`expose`) |
| `web` | `build: .` | Django-приложение | `8000` (наружу) |
| `celery` | `build: .` | Celery worker | — |
| `celery-beat` | `build: .` | периодические задачи | — |

## Разработка без Docker

```bash
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

