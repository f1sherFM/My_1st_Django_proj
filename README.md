# Skill Blog (Django + DRF + JWT)

`skill_blog` — учебный, но production-like проект на Django 5.x: веб-интерфейс на шаблонах + REST API (DRF + JWT), с акцентом на читаемую архитектуру и корректные права доступа.

## Features
- Кастомный пользователь (`accounts.User`) и профиль (`avatar`, `bio`, `created_at`).
- Регистрация, логин, логаут, страница профиля.
- Блог с категориями, постами и комментариями.
- Публикация/черновики (`is_published`) и поиск по постам.
- Комментарии с премодерацией (`is_approved=False` до одобрения).
- Админка с удобной модерацией комментариев (bulk action).
- REST API в отдельном приложении `api`.
- JWT-аутентификация для API (`access/refresh`).
- Пагинация и поиск в API (`search`, формат `count/next/previous/results`).
- Endpoint `GET /api/me/` для получения профиля текущего пользователя в API-клиенте.

## Архитектурные решения
- Почему отдельное приложение `api`:
  API-слой изолирован от HTML-части (`blog`/`accounts`), чтобы не смешивать сериализаторы/permissions с шаблонными views.
- Почему для draft-постов в API используется 404:
  Для неавтора и не-staff черновик «не существует», это снижает утечку информации о приватном контенте.
- Почему премодерация комментариев:
  Новый комментарий сохраняется как `is_approved=False`, чтобы не публиковать спам/нежелательный контент сразу.

## Стек
- Python 3.12+ (проверено на 3.13)
- Django 5.x
- SQLite
- Django REST Framework
- SimpleJWT
- django-filter
- Pillow

## Быстрый старт
1. Создать виртуальное окружение:
   ```powershell
   python -m venv .venv
   ```
2. Активировать:
   ```powershell
   .\.venv\Scripts\activate
   ```
3. Установить зависимости:
   ```powershell
   pip install -r requirements.txt
   ```
4. Применить миграции:
   ```powershell
   python manage.py migrate
   ```
5. Создать суперпользователя:
   ```powershell
   python manage.py createsuperuser
   ```
6. Запустить сервер:
   ```powershell
   python manage.py runserver
   ```

Проект: `http://127.0.0.1:8000/`

## Конфигурация окружения
В репозитории есть файл `.env.example` с базовыми переменными.

Для локального запуска переменные не обязательны: настройки по умолчанию берутся из `settings.py`.
Для деплоя/CI файл служит шаблоном; подключение `dotenv` остаётся опциональным.

## API examples
Базовый префикс: `/api/`

Поиск в API: `?search=...`.
Throttling включен:
- `anon`: `200/day`
- `user`: `2000/day`

### Получить JWT-токен
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'
```

### Обновить access-токен
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

### Подготовить категорию для API-CRUD
Перед созданием поста убедитесь, что есть категория, и возьмите её `id`:
```bash
python manage.py shell -c "from blog.models import Category; c,_=Category.objects.get_or_create(name='General', defaults={'slug':'general'}); print(c.id)"
```

### Создать пост
```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Пост через API","content":"Текст","category":<id_категории>,"is_published":true}'
```

### Создать комментарий
```bash
curl -X POST http://127.0.0.1:8000/api/posts/<post_slug>/comments/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Комментарий через API"}'
```

### Получить профиль текущего пользователя
```bash
curl -X GET http://127.0.0.1:8000/api/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Основные API endpoint'ы
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `GET /api/posts/`
- `POST /api/posts/`
- `GET /api/posts/<slug>/`
- `PATCH /api/posts/<slug>/`
- `DELETE /api/posts/<slug>/`
- `GET /api/categories/`
- `GET /api/categories/<slug>/posts/`
- `GET /api/posts/<slug>/comments/`
- `POST /api/posts/<slug>/comments/`
- `PATCH /api/comments/<id>/approve/` (staff)
- `GET /api/me/`

## Code quality
Проверка кода:
```powershell
ruff check .
black --check .
isort --check-only .
```

Автоформатирование:
```powershell
black .
isort .
```

## How to run tests
Запустить все тесты:
```powershell
python manage.py test
```

Запустить только API-тесты:
```powershell
python manage.py test api.tests
```

Coverage: `97%` (`coverage run manage.py test; coverage report -m`).

## Команды (Makefile)
Если используешь `make`:
- `make install` — установить зависимости
- `make migrate` — применить миграции
- `make run` — запустить сервер
- `make test` — запустить тесты
- `make check` — Django checks

## Структура проекта
- `skill_blog/` — настройки проекта, root urls, handlers.
- `accounts/` — кастомный пользователь, профиль, auth views/forms.
- `blog/` — модели и HTML-логика постов/категорий/комментариев.
- `api/` — DRF serializers/views/permissions/tests.
- `templates/` — шаблоны UI.
- `static/` — стили.

## Примечания
- Для production-поведения кастомных 403/404 страниц используйте `DEBUG=False` и корректный `ALLOWED_HOSTS`.
- В API create возвращает `201`, delete — `204`.
