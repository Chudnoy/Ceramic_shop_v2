# Глоссарий

## Backfill

Перенос/производное заполнение новой структуры из уже существующих данных.

Пример:

```text
Product → Work
Product → linked ShopItem
OrderItem.product_id → OrderItem.shop_item_id
```

## Preflight

Проверка предпосылок до изменения данных.

Если old state противоречив, migration должна остановиться до backfill.

## Runtime

Код и поведение, выполняющиеся при работе приложения:

```text
request → route → service → DB → response
```

Это не то же самое, что migration time.

## Cutover

Момент, когда конкретный сценарий перестаёт использовать legacy source и начинает использовать target implementation.

## Legacy

Текущая старая рабочая часть, основанная на Product.

Слово не означает «бесполезный код».

## Target

Новая модель/ветка, к которой идёт приложение:

```text
Project / Work / ShopItem
```

## Project

Авторский художественный контекст для Works.

## Work

Художественная работа.

Не равна товару.

## ShopItem

Коммерческое предложение.

Может ссылаться на Work или существовать standalone.

## Linked ShopItem

ShopItem с `work_id`.

Display/content данные в значительной степени наследуются от Work.

## Standalone ShopItem

ShopItem без `work_id`, со своим name/media/taxonomy.

## OrderItem snapshot

Сохранённые при заказе:

```text
product_name
unit_price
quantity
```

Нужны для истории.

## Inventory

Физическое количество, выраженное `stock_quantity`.

## Reservation

Количество, удерживаемое активными `new/confirmed` orders.

## Available quantity

```text
stock_quantity - reserved_quantity
```

## Read-side

Код, который собирает данные для чтения/показа, например `public_work_service.py`.

## Write-side

Код, который меняет состояние: order creation, admin edit, inventory changes.

## Read-model

Структура данных для конкретного интерфейса, а не обязательно одна DB row.

## Blueprint

Flask-группа routes.

Текущие:

```text
main
admin
public
```

## App factory

`create_app(test_config=None)` — функция создания Flask application.

## Migration registry

`MIGRATIONS` в `database/migrations.py`.

## Seed

Демо/начальные данные для пустой базы после migrations.

Не равен backfill.

## Progressive enhancement

HTML уже функционален как базовый документ; JS добавляет удобство там, где доступен.

## BEM-like naming

CSS naming:

```text
.block
.block__element
.block--modifier
```

## Logical properties

CSS:

```text
inline-size
block-size
margin-inline
padding-block
```

используемые вместо жёсткой привязки только к width/height/left/right.

## Stacking context

Локальная система слоёв CSS, часто создаваемая `isolation: isolate`.

## Vertical slice

Небольшой цельный кусок функциональности через несколько слоёв:

```text
DB → service → route → template → tests
```

вместо массового переписывания одного слоя целиком.

## Feature freeze

Период перед release, когда не добавляются новые необязательные возможности и работа сосредоточена на завершении/стабилизации.
