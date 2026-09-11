# Текущее состояние проекта

## 1. Что представляет собой Ceramic Shop v2

Ceramic Shop v2 — Flask-приложение для художественного сайта Полины Яланской с будущим магазином.

Проект прошёл важную архитектурную развилку. Изначально почти весь мир приложения был сжат в `Product`. Сейчас новая схема уже разделяет:

```text
Project
Work
ShopItem
Order / OrderItem
```

Но runtime переводится постепенно. Поэтому в репозитории одновременно существуют:

```text
legacy world
Product + legacy catalog/cart/admin

и

target world
Project + Work + ShopItem + /v2 public
```

Это текущее сознательное состояние миграции, а не окончательная архитектура.

## 2. Что завершено на уровне схемы

Migration registry содержит `v001–v013`.

Новая художественная часть уже создана:

- `projects`;
- `series`;
- `materials`;
- `works`;
- `project_images`;
- `work_images`;
- `work_categories`;
- `work_tags`;
- `work_materials`.

Новая коммерческая часть уже создана:

- `shop_items`;
- `shop_item_images`;
- `shop_item_categories`;
- `shop_item_tags`;
- `shop_item_materials`.

В `order_items` добавлен `shop_item_id`.

Старые `products`, `product_tags`, `orders`, `order_items` не удалены, потому что старый runtime всё ещё использует их.

## 3. Новый public runtime

Blueprint:

```text
public_bp
url_prefix = /v2
```

Реализованные маршруты:

```text
GET /v2/
GET /v2/works/<slug>
GET /v2/projects/<slug>
```

### `/v2/`

Использует `public_home_service.py`.

Берёт:

- опубликованные Works;
- их cover images;
- опубликованные ShopItems;
- вычисленную availability;
- отбирает доступные Shop preview items.

### Work detail

`public_work_service.py` собирает read-model:

- Work;
- все изображения;
- cover;
- detail images;
- categories;
- tags;
- materials;
- опубликованный связанный ShopItem;
- availability;
- Project preview, если Work входит в опубликованный Project;
- другие опубликованные Works.

Страница имеет отдельные `work.css` и `work.js`. Responsive-карусель и раскрытие длинного описания уже являются частью текущей реализации.

### Project detail

`public_project_service.py` собирает:

- Project;
- текст, разделённый на параграфы;
- project images;
- семантическое распределение первых изображений по position;
- опубликованные Works проекта в `project_position`;
- cover каждой Work.

Текущая `project.html` использует threshold, premise и first movement. Верстка продолжает развиваться.

## 4. Что уже подготовлено для Shop

`public_shop_service.py` уже существует и тестируется.

Он:

- получает опубликованные ShopItems;
- исключает `is_orderable=0`;
- исключает `is_retired=1`;
- для linked item требует опубликованную Work;
- вычисляет availability;
- исключает unique item с `out_of_stock`;
- получает правильную cover image для linked или standalone ShopItem.

Однако отдельный public route `/v2/shop` пока не зарегистрирован в `routes/public`.

## 5. Что остаётся legacy

### Старый публичный runtime

`main_bp` продолжает обслуживать:

- `/`;
- `/catalog`;
- `/product/<product_id>`;
- `/cart`;
- `/checkout`;
- order success.

Он основан на `products` и legacy `Product.status`.

### Корзина

Session хранит:

```text
{product_id: quantity}
```

`cart_service.py` повторно загружает Products из БД и решает, что доступно для заказа через legacy Product rules.

### Checkout

`order_service.create_order_with_items()`:

1. создаёт Order;
2. создаёт OrderItems;
3. переводит каждый Product `available → reserved`;
4. коммитит всё одной транзакцией;
5. делает rollback, если хотя бы одна работа уже недоступна.

Target `shop_item_id` уже присутствует в OrderItem, но новый checkout ещё не переведён на него.

### Админка

Текущая admin работает с:

```text
Products
Orders
Categories
Tags
```

Новой полноценной admin для Projects / Works / ShopItems пока нет.

## 6. Текущее frontend-состояние

Новый public frontend отделён:

```text
templates/public/
static/public/
```

Сейчас там:

```text
base.html
home.html
work.html
project.html

css/site.css
css/work.css
css/project.css

js/site.js
js/work.js
```

`site.css` содержит общую design system и главную.

`work.css` — большой самостоятельный responsive stylesheet.

`project.css` — отдельная арт-директированная сетка страницы Project и пока развивается.

## 7. Что не следует считать завершённым

- Works archive/index;
- Projects index;
- отдельный Shop route/page;
- Shop detail для standalone items;
- новая cart/checkout ветка на ShopItem;
- новая admin target-модели;
- окончательный runtime cutover;
- production server;
- deployment;
- production logging/health checks;
- доставка/онлайн-оплата/email;
- окончательная content model Project page.

## 8. Главная оценка состояния

Самое точное описание:

```text
schema evolution            — далеко продвинута
migration v008–v013         — реализована
target read-side            — активно строится
new Work page               — реализована
new Project page            — WIP
new Shop read-side          — частично готов
legacy commerce write-side  — всё ещё основной
new admin                   — ещё не начата
production                  — впереди
```

Главная техническая задача сейчас — не очередная новая схема, а постепенный перенос runtime на уже созданную target-модель.
