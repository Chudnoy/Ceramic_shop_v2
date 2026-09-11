# Публичные сценарии

Сейчас существуют две публичные ветки: legacy и target `/v2`.

## 1. Legacy homepage

```text
GET /
↓
Product query
only_visible
not archived
featured
↓
index.html
```

Это старая Product-oriented страница.

## 2. Legacy catalog

```text
GET /catalog
```

Поддерживает:

- category;
- tag;
- `q`;
- sorting/order.

Route валидирует category/tag и получает Products из legacy database layer.

## 3. Legacy Product detail

```text
GET /product/<product_id>
```

Если Product отсутствует, скрыт или archived, пользователь возвращается в catalog.

## 4. Legacy cart

Session:

```text
cart = {
    product_id: quantity
}
```

`build_cart_summary()` каждый раз повторно читает Products из БД.

Это важно: session не считается источником цены/доступности.

Summary строит:

```text
products
available_products
total
has_unavailable_items
cart_count
```

Недоступная позиция может оставаться видимой в cart, но не входит в `available_products` и `total`.

## 5. Legacy checkout

GET:

```text
cart summary
↓
есть cart?
↓
есть available_products?
↓
показать checkout
```

POST:

```text
rebuild cart from DB
↓
validate customer form
↓
если есть unavailable items:
    требуется confirm_partial_order=1
↓
build OrderItems
↓
create_order_with_items
↓
remove only ordered Product IDs from session
↓
order success
```

## 6. Atomic legacy order creation

`create_order_with_items()`:

```text
INSERT order
↓
INSERT order_items
↓
для каждого item:
Product available → reserved
↓
COMMIT
```

Любой failed reserve:

```text
ROLLBACK
```

## 7. New public homepage

```text
GET /v2/
↓
get_home_page_data()
↓
published Works + covers
published ShopItems + availability
↓
templates/public/home.html
```

Shop preview выбирает только items с `availability["can_order"]`.

## 8. New Work detail

```text
GET /v2/works/<slug>
```

Service:

```text
published Work?
↓ no → 404

yes:
images
cover/detail images
categories
tags
materials
published ShopItem
availability
published Project preview
other published Works
```

Template показывает художественную Work независимо от того, существует ли ShopItem.

Это важное отличие от legacy Product page.

## 9. New Project detail

```text
GET /v2/projects/<slug>
```

Неопубликованный Project → 404.

Service:

```text
Project
↓
split text into paragraphs
↓
map project_images by position
↓
load published Works ordered by project_position
↓
add cover image per Work
```

Текущий template использует:

- threshold;
- premise;
- first movement.

Следующие параграфы, Works и дополнительные Project images уже приходят в read-model, но не все ещё выведены в текущем WIP template.

## 10. Future Shop read-side уже частично существует

`get_public_shop_page_data()` уже умеет собрать список ShopItems.

Но route/template ещё не созданы.

Это хороший пример backend runway: read-model может быть готов немного раньше визуального слоя.

## 11. Не смешивать public visibility rules

Для разных сущностей разные правила.

Work detail:

```text
Work.is_published
```

Project detail:

```text
Project.is_published
```

Shop:

```text
ShopItem publication/order/lifecycle
+ linked Work publication
+ inventory state
```

Нельзя заменять это одним универсальным `visible`.

## 12. Progressive enhancement

Новый public frontend рассчитан так, чтобы основной контент существовал в HTML/Jinja.

JS усиливает:

- mobile navigation;
- Work story disclosure;
- Work carousel.

Бизнес-контент и ссылки не должны зависеть от того, отработал ли JavaScript.
