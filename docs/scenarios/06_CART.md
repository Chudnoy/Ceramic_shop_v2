# 6. Корзина

## Хранение

Корзина хранится в Flask session как словарь:

```python
{"product-uuid-1": 1, "product-uuid-2": 2}
```

Ключ — ID работы, значение — количество.

Flask подписывает cookie, поэтому незаметно изменить содержимое нельзя без нарушения подписи. Данные не шифруются, поэтому секреты в session хранить нельзя.

## Основные операции

```python
cart = session.get("cart", {})
cart[product_id] = cart.get(product_id, 0) + quantity
del cart[product_id]
session["cart"] = cart
session.modified = True
```

## `build_cart_summary()`

Сводка строится по актуальной базе и возвращает:

```text
cart
products
available_products
total
cart_count
has_unavailable_items
```

Каждой найденной работе добавляются:

```text
cart_quantity
cart_item_total
is_available_for_order
unavailable_reason
```

## Почему session не является источником товарных данных

В session хранится только ID и количество. Название, цена и статус всегда загружаются заново из базы.

## Удалённые работы

В session может остаться ID удалённой строки. Поэтому сравниваются ID корзины и найденные ID. Если часть не найдена, `has_unavailable_items = True`.

## Сумма

В `total` входят только доступные позиции. Недоступные остаются видимыми, но не входят в заказ.

## После заказа

Полностью очищать корзину нельзя при частичном заказе. Удаляются только ID, реально попавшие в `order_items`. Ошибка создания заказа не должна менять session.

## Инварианты

```text
цена не хранится в session
недоступная работа не входит в total
неоформленная позиция не исчезает
ошибка заказа не меняет корзину
session.modified меняется только при реальном изменении
```
