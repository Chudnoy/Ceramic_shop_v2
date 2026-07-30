# Ceramic Shop v2

Сайт-портфолио и небольшая коммерческая витрина керамических работ художницы Полины Яланской.

Проект построен на Flask и SQLite. Публичная часть ориентирована на презентацию художественной практики: каталог, отдельные страницы работ, материалы, годы, категории и смысловые теги. Коммерческая часть включает session-корзину, оформление заказа и административное управление жизненным циклом заказов и работ.

## Реализовано

- публичный каталог и страницы работ;
- фильтры, поиск и сортировка;
- категории и теги many-to-many;
- отзывы;
- флаги публикации, продажи, архива и избранного;
- статусы работ `available`, `reserved`, `sold`;
- session-корзина с повторной проверкой базы;
- полный и подтверждаемый частичный checkout;
- таблицы `orders` и `order_items`;
- резервирование работ при создании заказа;
- подтверждение, выполнение и отмена;
- снятие резерва при отмене;
- перевод работ в `sold` при выполнении;
- удаление только отменённых заказов;
- административная панель;
- загрузка и замена изображений;
- CSRF-защита;
- хешированный пароль администратора;
- database-, service- и route-тесты;
- транзакционные rollback-сценарии.

## Технологии

- Python
- Flask
- SQLite
- Jinja2
- HTML и CSS
- pytest
- python-dotenv
- Werkzeug

## Структура

```text
Ceramic_shop_v2/
├── app.py
├── validation.py
├── database/
│   ├── connection.py
│   ├── schema.py
│   ├── products.py
│   ├── categories.py
│   ├── tags.py
│   ├── reviews.py
│   ├── orders.py
│   ├── order_items.py
│   └── stats.py
├── routes/
│   ├── main.py
│   └── admin/
│       ├── __init__.py
│       ├── auth.py
│       ├── dashboard.py
│       ├── products.py
│       ├── orders.py
│       ├── categories.py
│       └── tags.py
├── services/
│   ├── cart_service.py
│   ├── category_service.py
│   ├── csrf_service.py
│   ├── image_service.py
│   ├── order_service.py
│   ├── product_service.py
│   └── tag_service.py
├── templates/
├── static/
├── tests/
├── scenarios/
├── requirements.txt
└── PROJECT_MAP.md
```

## Модель данных

Основные таблицы:

- `categories`;
- `products`;
- `tags`;
- `product_tags`;
- `reviews`;
- `orders`;
- `order_items`.

`order_items` хранит исторические название, цену и количество. При удалении заказа позиции удаляются каскадно. При удалении работы историческая позиция сохраняется, а `product_id` становится `NULL`.

## Доступность работы

Для оформления работа должна:

```text
существовать
не быть архивной
быть видимой
быть предназначенной для продажи
иметь status = available
```

Создание заказа:

```text
available → reserved
```

Отмена:

```text
reserved → available
```

Выполнение:

```text
reserved → sold
```

## Статусы заказов

```text
new
confirmed
completed
canceled
```

Переходы:

```text
new → confirmed
new → canceled
confirmed → completed
confirmed → canceled
canceled → delete
```

## Установка

```bash
git clone <URL-РЕПОЗИТОРИЯ>
cd Ceramic_shop_v2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## `.env`

```env
SECRET_KEY=...
ADMIN_LOGIN=admin
ADMIN_PASSWORD_HASH=...
```

```bash
python -c "import secrets; print(secrets.token_hex(32))"
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('ПАРОЛЬ'))"
```

## Запуск

```bash
python app.py
```

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/admin/login
```

## Тесты

```bash
python -m pytest
```

`pytest` рекомендуется вынести в `requirements-dev.txt`.

## Документация

Подробные главы находятся в `scenarios/`. Начинать с `scenarios/00_INDEX.md`.

## Известные задачи

- исправить условие подтверждения partial checkout;
- удалить неиспользуемый SQL с лишней запятой;
- подключить GitHub Actions;
- ввести миграции;
- перейти к `create_app()`;
- определить модель уникальных и складских товаров;
- закрыть session-доступом страницу успешного заказа;
- отключить debug при размещении.

Подробности: `scenarios/14_KNOWN_ISSUES.md`.
