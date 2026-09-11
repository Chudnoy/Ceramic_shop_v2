# Предметная модель

## 1. Зачем модель была разделена

Legacy `Product` одновременно обозначает:

```text
художественную работу
публичную карточку
товар
состояние продажи
часть админского workflow
```

Target-модель разносит эти смыслы.

## 2. Project

`projects`:

```text
id
name
slug
intro
text
period
is_published
```

Project — художественный контекст, в котором может находиться несколько Works.

Project может существовать без Works.

Публичный Project выбирается только при `is_published = 1`.

## 3. Work

`works`:

```text
id
slug
name
description
year
dimensions

project_id
series_id
project_position

is_published

is_commissionable
commission_note
```

Work — художественная сущность.

Она не обязана:

- принадлежать Project;
- принадлежать Series;
- иметь ShopItem;
- быть доступной для продажи.

Schema ограничивает:

```text
project_id и series_id не могут быть заданы одновременно
```

Если есть `project_position`, должен существовать `project_id`.

Внутри одного Project `project_position` уникален.

## 4. Series

`series` пока минимальна:

```text
id
name
```

Это отдельный будущий способ группировки Work.

Runtime вокруг Series сейчас практически не развит.

## 5. Images

### Project images

```text
project_images
project_id
image_path
position
```

`(project_id, position)` уникальна.

Текущий public Project read-model **временно интерпретирует position семантически**:

```text
1 cover
2 premise
3 break
4 process
>=5 field images
```

Это действующий runtime-контракт, но не обязательно окончательная content model будущей admin.

### Work images

```text
work_images
work_id
image_path
position
```

Position 1 используется как cover.

## 6. Categories, tags, materials

Для Work:

```text
work_categories
work_tags
work_materials
```

Это many-to-many связи.

`materials` — отдельный target-справочник с `name` и `slug`.

## 7. ShopItem

`shop_items`:

```text
id
work_id UNIQUE NULLABLE

name
description
dimensions
sales_note

price
inventory_type
stock_quantity

is_published
is_orderable
is_retired
```

### Linked ShopItem

Если `work_id IS NOT NULL`:

- собственные `name`, `description`, `dimensions` должны быть `NULL`;
- display-данные наследуются от Work;
- media/categories/tags/materials читаются через Work-связи.

### Standalone ShopItem

Если `work_id IS NULL`:

- `name` обязателен и непуст;
- собственные media/taxonomy хранятся в `shop_item_*` таблицах.

Это позволяет магазину содержать утилитарные/тиражные вещи, не притворяясь, что каждая из них является художественной Work.

## 8. Inventory type

```text
unique
stock
```

Для `unique` schema требует:

```text
stock_quantity IN (0, 1)
```

Для `stock`:

```text
stock_quantity >= 0
```

`stock_quantity` — физическое количество, а не «сколько можно заказать прямо сейчас».

## 9. Reservation — derived truth

Активными для reservation считаются Orders:

```text
new
confirmed
```

`reserved_quantity`:

```sql
SUM(order_items.quantity)
WHERE order_items.shop_item_id = ?
  AND order.status IN ('new', 'confirmed')
```

`available_quantity`:

```text
stock_quantity - reserved_quantity
```

Если результат отрицательный, service считает это нарушением инварианта.

## 10. ShopItem policy axes

Хранятся отдельно:

```text
is_published
is_orderable
is_retired
```

Они не являются заменой друг другу.

Примеры:

```text
published=1, orderable=1, retired=0
→ обычная публичная продажа, если есть availability

published=0, orderable=1
→ модель допускает непубличное коммерческое предложение

retired=1
→ жизненный цикл закрыт
```

Текущий `can_order` public-service дополнительно требует `is_published=1`.

## 11. Orders

Order сохраняет:

```text
customer_name
customer_email
customer_phone
customer_address
total
created_at
status
```

Статусы:

```text
new
confirmed
completed
canceled
```

Legacy order state machine остаётся рабочей частью приложения.

## 12. OrderItem

После v013:

```text
id
order_id
product_id NULLABLE
shop_item_id NULLABLE
product_name
unit_price
quantity
```

`product_name` и `unit_price` — исторический snapshot.

`product_id` — legacy reference.

`shop_item_id` — target bridge.

У active legacy order items v013 заполняет `shop_item_id`, если соответствующий ShopItem существует.

## 13. Product

`Product` всё ещё существует и нельзя считать его «удалённой старой моделью».

Он по-прежнему является runtime truth для:

- legacy catalog;
- legacy cart;
- legacy checkout;
- legacy admin;
- части order lifecycle.

До cutover он остаётся действующей сущностью.

## 14. Главные target-инварианты

```text
Work ≠ ShopItem.

ShopItem может быть linked или standalone.

Одна Work имеет максимум один ShopItem.

Unique stock ∈ {0, 1}.

Reservation не должна храниться как отдельный ShopItem status.

reserved_quantity <= stock_quantity.

available_quantity вычисляется, а не хранится.

Publication policy и orderability policy независимы.

Историческая OrderItem не должна зависеть от существования исходной карточки.
```
