# Runtime cutover: legacy → target

## 1. Почему этот документ нужен

Сейчас схема уже содержит target entities, но часть runtime всё ещё живёт в legacy Product.

Самая опасная ошибка на этом этапе — спутать:

```text
«таблица уже есть»
```

с:

```text
«приложение уже использует её как единственную истину»
```

## 2. Current truth map

### Художественное чтение

Уже target:

```text
/v2 homepage
/v2 Work detail
/v2 Project detail
```

### Public Shop read-side

Target service существует, route ещё нет.

### Корзина

Legacy:

```text
session product_id
↓
Product
```

### Checkout

Legacy:

```text
Product availability/status
↓
Order
↓
OrderItem
↓
Product available → reserved
```

### OrderItem bridge

Hybrid:

```text
product_id
+
shop_item_id
```

### Admin

Legacy Product-oriented.

## 3. Почему bridge полезен

v012/v013 позволяют active historical orders связать с target ShopItems до полного checkout rewrite.

Это снижает риск «обрубить» существующие обязательства при переходе.

Но bridge сам по себе не меняет write logic.

## 4. Вертикальные slices cutover

Хороший порядок:

```text
Slice 1: Home read
Slice 2: Work detail read
Slice 3: Project detail read
Slice 4: Works index read
Slice 5: Projects index read
Slice 6: Shop read
Slice 7: target admin writes
Slice 8: cart
Slice 9: checkout/order writes
Slice 10: legacy cleanup
```

Первые три уже существуют в разной степени готовности.

## 5. Почему cart/checkout позже

Commerce write-side содержит больше инвариантов:

- quantity;
- unique/stock;
- concurrent reservation;
- partial checkout;
- cancellation;
- completion;
- historical snapshots.

До стабильного Shop UX преждевременный rewrite создаст правила, которые интерфейс ещё не подтвердил.

## 6. Cutover cart contract

Target cart должен хранить ShopItem identifiers.

При каждом показе/checkout:

```text
session IDs
↓
reload ShopItems
↓
derive availability from DB
```

Session не должна быть источником цены/stock.

## 7. Atomic order creation target

Conceptual target:

```text
BEGIN
↓
re-check availability
↓
create Order
↓
create OrderItems with ShopItem snapshot/reference
↓
reservation becomes visible via active OrderItems
↓
COMMIT
```

Если quantity уже нельзя зарезервировать:

```text
ROLLBACK
```

Точная реализация completion/decrement ещё является открытым вопросом.

## 8. Legacy compatibility rule

Пока legacy order code работает, target changes не должны молча ломать его assumptions.

Особенно:

```text
Product.status
active order relationships
order_items.product_id
```

Migration preflight v009/v013 именно поэтому проверяет active obligations.

## 9. Cleanup conditions

Можно удалять legacy scenario только когда:

```text
есть target replacement
AND tests фиксируют нужное поведение
AND реальные routes переключены
AND old code больше не вызывается
```

Не раньше.

## 10. Конечное состояние

После cutover желательно прийти к:

```text
Public
Project / Work / ShopItem

Admin
Project / Work / ShopItem / Orders

Cart
ShopItem

Orders
ShopItem references + historical snapshot

Product
не участвует в runtime
```

Дальнейшая физическая чистка Product schema — отдельная задача после стабилизации.
