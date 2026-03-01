# Skill Blog

Учебный Django-проект уровня junior, но с production-like подходом: кастомный пользователь, блог, категории, комментарии с модерацией, админка и тесты.

## Стек
- Python 3.13+
- Django 5.x
- SQLite
- Pillow (для `ImageField`)

## Запуск локально
1. Создать виртуальное окружение:
   ```powershell
   python -m venv .venv
   ```
2. Активировать окружение:
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

Открыть: `http://127.0.0.1:8000/`

## Основные URL
- `/` — список опубликованных постов
- `/categories/` — список категорий
- `/category/create/` — создание категории (для авторизованного пользователя)
- `/category/<slug:slug>/` — посты категории
- `/post/create/` — создание поста
- `/post/<slug:slug>/` — детальная страница
- `/register/`, `/login/`, `/logout/`, `/profile/<str:username>/`
- `/admin/` — админка

## Важные технические решения
- Логин по `username`, `email` уникальный и дополнительно валидируется в форме регистрации.
- `logout` выполняется только через `POST` + CSRF.
- `Post.slug` генерируется автоматически через `slugify`; при коллизии добавляются суффиксы `-2`, `-3`.
- `slug` ограничен `max_length=200`, при суффиксе база режется, чтобы длина не превышала лимит.
- На странице поста показываются только одобренные комментарии.
- Права: неавторизованный пользователь получает redirect на login; авторизованный не-автор — 403.
- Поиск активируется только если `q.strip()` непустой.

## Кастомные ошибки 403/404
Шаблоны ошибок подключены в `skill_blog/urls.py` через `handler403/handler404`.

Для проверки поведения максимально близкого к продакшену установите:
- `DEBUG=False`
- корректный `ALLOWED_HOSTS`

## Тесты
Запуск:
```powershell
python manage.py test
```

Тесты покрывают:
- регистрацию и профиль,
- права доступа,
- фильтрацию опубликованных постов,
- поиск,
- пагинацию,
- модерацию комментариев,
- admin bulk action для approve comments.

## API (DRF + JWT)
Базовый префикс: `/api/`

Поиск в API работает через `?search=...` (не `q`).
Списки в API возвращают стандартный формат пагинации DRF:
- `count`
- `next`
- `previous`
- `results`

REST-статусы:
- `POST` create -> `201`
- `DELETE` -> `204`

### Получение JWT токена
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"your_password\"}"
```

### Обновление access токена
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ ^
  -H "Content-Type: application/json" ^
  -d "{\"refresh\":\"<your_refresh_token>\"}"
```

### Создание поста через API
```bash
curl -X POST http://127.0.0.1:8000/api/posts/ ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"API post\",\"content\":\"Body\",\"category\":1,\"is_published\":true}"
```

### Создание комментария через API
```bash
curl -X POST http://127.0.0.1:8000/api/posts/<post_slug>/comments/ ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Отличный пост\"}"
```

### Список эндпоинтов API
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

---

## Карта проекта
- `skill_blog/settings.py` — настройки проекта: apps, auth model, templates, static/media.
- `skill_blog/urls.py` — корневые маршруты + обработчики 403/404.
- `skill_blog/views.py` — функции рендера страниц ошибок.
- `accounts/models.py` — кастомный `User` и `Profile`.
- `accounts/forms.py` — регистрация и валидация email.
- `accounts/views.py` — register/login/logout/profile.
- `accounts/signals.py` — автосоздание профиля после регистрации.
- `accounts/urls.py` — маршруты аккаунта.
- `accounts/admin.py` — настройки админки пользователей и профилей.
- `blog/models.py` — `Category`, `Post`, `Comment`, логика автослага.
- `blog/forms.py` — формы поста и комментария.
- `blog/views.py` — список/деталь/CRUD постов, категории, комментарии, permission checks.
- `blog/urls.py` — маршруты блога.
- `blog/admin.py` — админка постов/категорий/комментариев + action `Approve comments`.
- `templates/` — HTML-шаблоны страниц, включая 403/404.
- `static/css/styles.css` — минимальные стили интерфейса.
- `requirements.txt` — зависимости проекта.

## Чеклист ручной проверки
1. Регистрация и вход:
   - создать нового пользователя на `/register`;
   - проверить вход на `/login`.
2. Профиль:
   - открыть `/profile/<username>`;
   - проверить отображение `bio` и аватара (если загружен).
3. Создание поста:
   - авторизоваться и создать пост через `/post/create`;
   - проверить автогенерацию slug.
4. Права доступа:
   - открыть редактирование/удаление чужого поста авторизованным не-автором — должен быть 403;
   - неавторизованному — redirect на login.
5. Публикация:
   - убедиться, что в списке `/` видны только `is_published=True`.
6. Комментарии и модерация:
   - оставить комментарий под постом;
   - в админке одобрить комментарий action `Approve comments`;
   - проверить, что до одобрения комментарий не виден, после — виден.
7. Пагинация:
   - создать >10 опубликованных постов и проверить переход на вторую страницу.
8. Поиск:
   - проверить поиск по `title/content` через `?q=`;
   - проверить, что пустой/пробельный `q` ведет себя как обычный список.

## Что исправлено (Repo-fix)
- Нормализованы URL-маршруты `accounts` и `blog`: добавлены корректные path converters и хвостовые `/`.
- `logout` закреплен как POST-only endpoint (`CustomLogoutView.http_method_names`), в `base.html` остается form + CSRF.
- `requirements.txt` приведен к валидному виду для `pip install -r` (по одной зависимости на строку).
- Подтверждена корректность настроек `MEDIA/STATIC` и безопасного показа аватара в шаблоне профиля.
- Выполнены проверки: `compileall`, `check`, `makemigrations`, `migrate`, `test`, smoke `runserver`.
