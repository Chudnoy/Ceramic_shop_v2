# Ceramic Shop v2

Персональный сайт художницы Полины Яланской, художественный архив и будущий магазин керамических работ.

Проект находится в переходном состоянии: в одном Flask-приложении одновременно живут **старый рабочий runtime на `Product`** и **новая предметная модель `Project → Work → ShopItem`**, на которую постепенно переводится публичный сайт. Это не случайный дубль и не два независимых приложения: новая система строится рядом со старой, пока отдельные вертикальные срезы не будут готовы к cutover.

## Текущее состояние

По состоянию на `main` / commit `7d996da41b25bd033d2c52f431b4b6a84bfdcdce` от 11 сентября 2026 года:

- миграционная цепочка доведена до `v013`;
- художественное ядро `Project / Work / Series / Material` уже существует в схеме;
- коммерческое ядро `ShopItem` уже существует в схеме;
- `order_items` содержит и legacy-связь `product_id`, и новый bridge `shop_item_id`;
- новый публичный blueprint работает под `/v2`;
- новая главная `/v2/` реализована;
- новая страница Work `/v2/works/<slug>` реализована и имеет отдельный responsive CSS/JS;
- страница Project `/v2/projects/<slug>` находится в активной верстке;
- backend read-model для будущего публичного магазина уже существует, но отдельный `/v2/shop` route пока не зарегистрирован;
- старый каталог, корзина, checkout и текущая админка всё ещё работают через `Product`.

## Главная идея предметной модели

```text
Project
  └── 0..N Work

Work
  ├── 0..N images
  ├── categories / tags / materials
  └── 0..1 ShopItem

ShopItem
  ├── может быть связан с Work
  └── может существовать самостоятельно

Order
  └── 1..N OrderItem
            ├── legacy product_id
            └── target shop_item_id
```

Разделение смыслов принципиально:

- `Project` — авторский художественный контекст;
- `Work` — художественная работа;
- `ShopItem` — коммерческое предложение;
- `OrderItem` — историческая позиция заказа.

Work не становится «товаром» только потому, что его можно купить. ShopItem не обязан быть художественной Work, потому что в будущем магазин может содержать самостоятельные тиражные или утилитарные позиции.

## Архитектура

Приложение остаётся модульным монолитом:

```text
Browser
  ↓
Flask route / blueprint
  ↓
Service
  ↓
Database module / raw SQL
  ↓
SQLite
```

Для новых публичных страниц применяется отдельный read-side:

```text
/v2 route
  ↓
public_*_service
  ↓
projects.py / works.py / shop_items.py
  ↓
target tables
```

Legacy commerce пока идёт по старой ветке:

```text
/, /catalog, /cart, /checkout, /admin
  ↓
legacy routes/services
  ↓
products / product status
```

Подробно: [`PROJECT_MAP.md`](PROJECT_MAP.md), [`docs/02_ARCHITECTURE.md`](docs/02_ARCHITECTURE.md).

## Технологии

- Python;
- Flask 3;
- SQLite;
- raw SQL;
- Jinja2;
- HTML / CSS / browser JavaScript;
- pytest;
- Ruff;
- GitHub Actions;
- python-dotenv.

Production-зависимостей вроде Gunicorn, reverse proxy или внешнего object storage в текущем репозитории пока нет.

## Локальный запуск

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Зависимости разработки:

```bash
python -m pip install -r requirements-dev.txt
```

Создать `.env` по файлу `.env.example`:

```env
SECRET_KEY=...
ADMIN_LOGIN=admin
ADMIN_PASSWORD_HASH=...
```

Секрет:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Хеш пароля:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('ВАШ_ПАРОЛЬ'))"
```

Запуск:

```bash
python app.py
```

`create_app()` при `AUTO_INIT_DB=True` вызывает `init_db()`, migration runner применяет все pending migrations, затем `seed_initial_data()` заполняет пустую target-базу демонстрационными данными.

Development server запускается на порту `8000` с `debug=True`. Это локальный режим, не production.

## Тесты и качество кода

```bash
python -m ruff check .
python -m ruff format --check
python -m pytest -q
```

GitHub Actions выполняет те же три шага на Python 3.14 при `push` и `pull_request`.

Документация не утверждает, что конкретный commit «зелёный», если статус CI отдельно не проверен. Здесь описана конфигурация репозитория.

## Где читать дальше

Начать с [`docs/00_INDEX.md`](docs/00_INDEX.md).

Самые полезные документы для быстрого восстановления контекста:

- [`docs/01_CURRENT_STATE.md`](docs/01_CURRENT_STATE.md) — что уже сделано и что ещё legacy;
- [`docs/03_DOMAIN_MODEL.md`](docs/03_DOMAIN_MODEL.md) — сущности, связи, инварианты;
- [`docs/04_DATABASE_AND_MIGRATIONS.md`](docs/04_DATABASE_AND_MIGRATIONS.md) — v001–v013;
- [`docs/16_FRONTEND_ARCHITECTURE.md`](docs/16_FRONTEND_ARCHITECTURE.md) — новый публичный frontend;
- [`docs/17_RUNTIME_CUTOVER.md`](docs/17_RUNTIME_CUTOVER.md) — как старый и новый мир сосуществуют;
- [`docs/11_ROADMAP_TO_PRODUCTION.md`](docs/11_ROADMAP_TO_PRODUCTION.md) — следующий маршрут.

## Статус проекта

Это учебный проект, но его текущая сложность уже включает реальную эволюцию схемы, миграцию предметной модели, параллельный runtime, транзакционные бизнес-сценарии, responsive frontend и тестовую инфраструктуру.

При этом production ещё не достигнут. Главная задача ближайшего периода — не добавлять максимум возможностей, а постепенно закончить новый public runtime, затем новую admin/runtime-ветку и только после этого провести коммерческий cutover и production hardening.
