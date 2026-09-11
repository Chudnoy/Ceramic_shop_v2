# Source snapshot

## Граница актуальности

Эта документация подготовлена по состоянию:

```text
repository: Chudnoy/Ceramic_shop_v2
branch: main
commit: 7d996da41b25bd033d2c52f431b4b6a84bfdcdce
commit message: WIP продолжение страницы project
date: 2026-09-11
```

Она описывает код, а не планы из старых документов.

## Основные просмотренные источники

### Root/config

```text
app.py
README.md
PROJECT_MAP.md
requirements.txt
requirements-dev.txt
pyproject.toml
.gitignore
.github/workflows/tests.yml
```

### Database

```text
database/connection.py
database/migrations.py
database/schema.py
database/projects.py
database/works.py
database/shop_items.py
database/orders.py
database/order_items.py
database/products.py
```

### Migrations

```text
v001–v013 registry
v007_normalize_order_items.py
v008_create_artistic_core.py
v009_backfill_artistic_core.py
v010_create_shop_core.py
v011_backfill_shop_core.py
v012_add_shop_item_to_order_items.py
v013_backfill_order_item_shop_bridge.py
```

### Services

```text
cart_service.py
order_service.py
csrf_service.py
public_home_service.py
public_work_service.py
public_project_service.py
public_shop_service.py
shop_availability_service.py
```

### Routes

```text
routes/main/*
routes/admin/*
routes/public/*
```

### New frontend

```text
templates/public/base.html
templates/public/home.html
templates/public/work.html
templates/public/project.html

static/public/css/site.css
static/public/css/work.css
static/public/css/project.css

static/public/js/site.js
static/public/js/work.js
```

### Tests / CI

Структура `tests/` и текущий GitHub Actions workflow.

## Что специально не утверждается

Документация не утверждает:

- что latest commit прошёл CI;
- точное текущее количество passing tests;
- что Project page закончена;
- что `/v2/shop` существует;
- что target cart/checkout уже работает;
- что production deployment настроен.

## Как обновлять snapshot

После крупного этапа:

1. записать новый commit SHA;
2. перечитать файлы, которые менялись архитектурно;
3. обновить `01_CURRENT_STATE.md`;
4. обновить `PROJECT_MAP.md`;
5. поправить профильный документ;
6. не переписывать docs ради чисто косметической CSS-правки, если архитектурный контракт не изменился.
