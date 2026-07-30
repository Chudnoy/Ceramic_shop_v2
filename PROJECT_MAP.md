# PROJECT MAP — Ceramic Shop v2

## 1. Точки входа

```text
app.py
├── Flask app
├── main_bp
├── admin_bp
├── CSRF before_request
├── cart_count context_processor
└── csrf_token context_processor
```

## 2. Публичные сценарии

### Каталог

```text
GET catalog
→ routes/main.py
→ database/products.py
→ filters/search/sort
→ template
```

### Страница работы

```text
GET product
→ product by id
→ category
→ tags
→ reviews
→ template
```

### Корзина

```text
GET cart
→ build_cart_summary(session)
→ get_products_by_ids
→ unavailable reason
→ available_products
→ total
→ template
```

### Checkout

```text
POST /checkout
→ build_cart_summary
→ process_checkout_form
→ confirm_partial_order
→ build_order_item_list
→ create_order_with_items
    ├── INSERT orders
    ├── INSERT order_items
    ├── available → reserved
    └── COMMIT / ROLLBACK
→ удалить из session только заказанные ID
→ order_success
```

## 3. Административные сценарии

### Работа

```text
POST create
→ process_product_form
→ process_product_tag_ids
→ create_product_with_tags
    ├── save image
    ├── INSERT product
    ├── replace tags
    ├── COMMIT
    └── rollback + delete new image
```

```text
POST edit
→ active order check
→ save optional image
→ UPDATE product
→ replace tags
→ COMMIT
→ delete old image
```

```text
POST delete
→ archived check
→ active order check
→ delete product data
→ COMMIT
→ delete image
```

### Заказ

```text
new
├── edit
├── confirm
└── cancel

confirmed
├── complete
└── cancel

completed
└── read only

canceled
└── delete
```

## 4. Сервисы

### `cart_service.py`

- получение и изменение session-корзины;
- сводка;
- удаление недоступных;
- счётчик;
- удаление оформленных позиций.

### `product_service.py`

- обработка форм;
- причина недоступности;
- создание с тегами;
- редактирование с тегами и изображением;
- удаление;
- защита активным заказом.

### `order_service.py`

- checkout data;
- позиции;
- создание и резерв;
- редактирование нового заказа;
- confirm;
- complete и sell;
- cancel и release;
- удаление canceled.

### `image_service.py`

- валидация;
- случайное имя;
- сохранение;
- удаление.

### `csrf_service.py`

- генерация и проверка токена.

## 5. Database-модули

```text
connection.py  → соединение и PRAGMA
schema.py      → таблицы и стартовые данные
products.py    → products
categories.py  → categories
tags.py        → tags + product_tags
reviews.py     → reviews
orders.py      → orders + active-order query
order_items.py → позиции
stats.py       → dashboard
```

## 6. Транзакционные границы

```text
create_product_with_tags
update_product_with_tags
delete_product_with_image
update_product_state_with_order_check
create_order_with_items
update_order_with_items
confirm_order
complete_order
cancel_order
delete_canceled_order
```

## 7. Главные инварианты

```text
недоступная работа не входит в заказ
заказ и все позиции создаются целиком
активный заказ резервирует работу
отмена снимает резерв
выполнение продаёт работу
активный заказ нельзя удалить
работу активного заказа нельзя вывести из reserved
историческая позиция переживает удаление работы
частичный заказ требует явного согласия
ошибка создания заказа не очищает корзину
```

## 8. Текущие риски

См. `scenarios/14_KNOWN_ISSUES.md`.
