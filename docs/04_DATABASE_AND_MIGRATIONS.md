# База данных и миграции

## 1. Единственный путь построения схемы

`init_db()`:

```text
get_db_connection()
↓
run_migrations(MIGRATIONS)
↓
close
↓
seed_initial_data()
```

Схема строится через migration runner.

`seed_initial_data()` выполняется после миграций и заполняет пустой target-мир демонстрационным контентом.

## 2. Registry

Migration:

```python
@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    apply: Callable
```

Registry валидирует:

- version — положительный `int`;
- версии уникальны;
- name — непустая строка;
- names уникальны.

## 3. Транзакция migration runner

Для каждой pending migration:

```text
BEGIN
↓
migration.apply(conn)
↓
INSERT schema_migrations
↓
COMMIT
```

При исключении:

```text
ROLLBACK
raise
```

Запись о применении migration находится в той же транзакции, что и её изменение схемы/данных.

## 4. v001–v007 — legacy foundation

```text
v001 create_products
v002 add_categories
v003 create_orders_with_json_items
v004 add_order_status
v005 expand_products
v006 add_tags
v007 normalize_order_items
```

`v007` переносит Order.items JSON в таблицу `order_items` и оставляет snapshots `product_name`, `unit_price`, `quantity`.

## 5. v008 — artistic core

Создаёт:

```text
projects
series
materials
works
project_images
work_images
work_categories
work_tags
work_materials
```

Ключевые ограничения:

- `Work.project_id` и `series_id` взаимоисключающие;
- `project_position > 0`;
- `project_position` возможен только при Project;
- `(project_id, project_position)` unique;
- image positions positive and unique per owner.

## 6. v009 — artistic backfill

Перед записью выполняются preflight checks.

### Materials

Legacy `products.materials` должен:

- быть непустым;
- корректно делиться по запятым;
- содержать только известные aliases;
- не содержать повторов после normalize.

Поддерживаемые aliases migration:

```text
каменная масса → stoneware
фарфор         → porcelain
глазурь        → glaze
```

### Active orders

Активные `new/confirmed` OrderItems не могут иметь `product_id = NULL`.

Проверяется согласованность Product status с активным количеством:

```text
available → active_quantity = 0
reserved  → active_quantity = 1
sold      → active_quantity = 0
```

### Target emptiness

Перед backfill должны быть пусты:

```text
works
materials
work_images
work_categories
work_tags
work_materials
```

### Backfill

Product → Work сохраняет тот же `id`.

Visibility mapping:

```text
Product is_visible=1 AND is_archived=0
→ Work.is_published=1
```

Image Product становится Work image position 1.

Category/tags/materials переносятся в target join tables.

## 7. v010 — Shop core

Создаёт ShopItem и standalone auxiliary tables.

Ключевой принцип:

```text
linked ShopItem
→ контент наследуется от Work

standalone ShopItem
→ собственный контент обязателен/разрешён
```

Для linked item собственные `name/description/dimensions` запрещены CHECK-ами.

## 8. v011 — Shop backfill

Backfill создаёт `unique` ShopItems только для legacy Products, которые должны участвовать в коммерческом runtime.

Кандидаты:

```text
available
AND is_for_sale=1
AND is_archived=0

OR

reserved
AND is_archived=0
AND существует active new/confirmed order
```

Не создаются ShopItems для sold/archived и для available non-sale Products.

Mapping:

```text
work_id        = product.id
price          = product.price
inventory_type = unique
stock_quantity = 1
is_published   = is_visible * is_for_sale
is_orderable   = is_for_sale
is_retired     = 0
```

Перед backfill:

- target Shop tables должны быть пусты;
- каждый candidate Product должен иметь соответствующую Work.

## 9. v012 — bridge schema

Добавляет:

```sql
order_items.shop_item_id
REFERENCES shop_items(id)
ON DELETE SET NULL
```

## 10. v013 — bridge backfill

Preflight:

- `order_items.shop_item_id` ещё нигде не заполнен;
- каждый active OrderItem должен иметь matching ShopItem через `ShopItem.work_id = product_id`.

Backfill заполняет `shop_item_id` только для Orders:

```text
new
confirmed
```

Исторические completed/canceled позиции не обязаны получать bridge этой migration.

## 11. Почему preflight — часть migration

Preflight — защита смысла, а не просто синтаксиса.

Backfill, который выполнился технически успешно, но неправильно интерпретировал старые данные, опаснее migration, которая остановилась до изменения.

Поэтому pattern:

```text
inspect old truth
↓
reject ambiguous/inconsistent state
↓
backfill
```

предпочтительнее «попробовать перенести всё».

## 12. Правила новых миграций

Новые migration files:

- не переписывают историю v001–v013;
- делают одну понятную эволюцию;
- используют preflight, если требуется интерпретация старых данных;
- не полагаются на seed;
- тестируются отдельно;
- должны корректно работать через общий `run_migrations`;
- не смешивают runtime cutover и schema migration без необходимости.

## 13. Seed и migration — разные вещи

Migration:

```text
история схемы и переноса существующих данных
```

Seed:

```text
демонстрационные данные для пустой базы после migrations
```

Нельзя считать demo seed источником production-data migration.
