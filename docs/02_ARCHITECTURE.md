# Архитектура

## 1. Тип приложения

Ceramic Shop v2 — модульный монолит на Flask и SQLite.

Намеренно не используется ORM. SQL находится в `database/`, бизнес-оркестрация — в `services/`, HTTP — в `routes/`.

Базовое направление зависимостей:

```text
route
  ↓
service
  ↓
database
  ↓
SQLite
```

Jinja templates получают уже собранные данные и не должны становиться местом бизнес-логики.

## 2. App factory

`create_app(test_config=None)`:

- создаёт Flask app;
- читает config;
- позволяет тестам переопределить config;
- при `AUTO_INIT_DB=True` вызывает `init_db()`;
- регистрирует три blueprints;
- ставит глобальную CSRF-проверку для POST;
- добавляет `cart_count` и `csrf_token` через context processors.

Это позволяет тестам использовать отдельный database path без изменения local config.

## 3. Blueprints

```text
admin_bp
main_bp
public_bp
```

### `main_bp`

Legacy public runtime без URL prefix.

### `admin_bp`

Legacy admin без общего blueprint prefix; сами routes объявлены как `/admin/...`.

### `public_bp`

Новая публичная ветка:

```python
Blueprint("public", __name__, url_prefix="/v2")
```

Это временная безопасная зона для развития target runtime рядом со старым сайтом.

## 4. Database modules

Database-модуль должен отвечать на узкие вопросы и получать `conn`, если операция участвует в более крупной транзакции.

Примеры target read-side:

```text
database/projects.py
database/works.py
database/shop_items.py
```

Примеры legacy:

```text
database/products.py
database/orders.py
database/order_items.py
```

`database/connection.py`:

- берёт путь из `current_app.config["DATABASE"]`;
- включает `PRAGMA foreign_keys = ON`;
- задаёт `sqlite3.Row`.

## 5. Service layer

Service связывает несколько database-вызовов в один прикладной сценарий.

Новая публичная ветка:

```text
public_home_service
public_work_service
public_project_service
public_shop_service
shop_availability_service
```

Legacy transactional/write-side:

```text
product_service
cart_service
order_service
image_service
```

Пример Work read-model:

```text
route /v2/works/<slug>
↓
get_public_work_page_data(slug)
↓
Work
+ media
+ taxonomy
+ ShopItem
+ availability
+ Project preview
+ other Works
↓
public/work.html
```

Route остаётся тонким.

## 6. Transaction ownership

В write-сценариях транзакцией должен владеть слой, который видит бизнес-операцию целиком.

Пример legacy order creation:

```text
service opens conn
↓
INSERT order
↓
INSERT order_items
↓
reserve every Product
↓
commit
```

Если один reserve не проходит:

```text
rollback whole operation
```

Migration runner тоже имеет явную транзакционную границу, но на уровне одной migration.

## 7. Read-model как отдельное понятие

Новые `public_*_service.py` не обязаны возвращать строки таблиц «как есть».

Они формируют данные именно для страницы.

Например `public_project_service.py`:

```text
Project.text
↓ split by blank lines
project_paragraphs

project_images
↓ position mapping
cover / premise / break / process / field

Works
↓ cover lookup
project_works_data
```

Это нормально: public read-model — представление предметной модели для конкретного интерфейса.

## 8. Две архитектурные эпохи в одном репозитории

Сейчас проект нельзя описать одной схемой request flow.

### Legacy

```text
browser
↓
main/admin route
↓
Product-oriented service/database
↓
products
```

### Target public

```text
browser
↓
public /v2 route
↓
public service
↓
Project / Work / ShopItem database modules
```

Эти ветки должны сосуществовать только пока идёт cutover.

## 9. Что не следует делать

Не стоит:

- заставлять новый public runtime снова зависеть от Product;
- переносить бизнес-правила availability в Jinja;
- хранить derived availability отдельной колонкой;
- переписывать весь runtime одним большим commit;
- смешивать новую admin с legacy Product-формами без явной границы;
- создавать универсальный page-builder до реального требования.

## 10. Целевая архитектурная траектория

```text
Target schema ready
↓
Target public read-side
↓
Target admin/write-side
↓
Target cart/checkout/orders
↓
Cut legacy runtime
↓
Production hardening
```

Развитие идёт вертикальными срезами, а не массовой заменой всех файлов одного слоя целиком.
