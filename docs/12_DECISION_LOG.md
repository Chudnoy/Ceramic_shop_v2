# Decision log

Не полный журнал всех commits, а список решений, которые важно помнить.

## D001 — modular monolith

**Принято:** оставаться в одном Flask-приложении, пока реальная сложность не требует другого.

Причина: текущие границы routes/services/database достаточно выражают систему.

## D002 — raw SQL вместо ORM

**Принято:** SQL остаётся написан вручную.

Database layer является явной частью обучения и контроля модели.

## D003 — миграции являются историей

**Принято:** v001–v013 не переписывать задним числом после того, как они стали частью истории.

Новые schema changes → новые versions.

## D004 — Project / Work / ShopItem разделены

**Принято:** художественная сущность и коммерческое предложение — разные вещи.

Work может не продаваться.

ShopItem может быть standalone.

## D005 — одна linked Work → максимум один ShopItem

Обеспечивается `shop_items.work_id UNIQUE`.

## D006 — availability derived

**Принято:**

```text
reserved_quantity
available_quantity
stock_state
can_order
```

вычисляются, а не становятся набором stored statuses.

## D007 — active reservation = Order new/confirmed

Используется в target availability и migration preflights.

## D008 — новый runtime растёт рядом со старым

**Принято:** `/v2` служит отдельной веткой target public runtime.

Старый runtime не удаляется, пока replacement не готов.

## D009 — public route тонкий

Page assembly выполняется в `public_*_service.py`.

## D010 — public read-model может быть специальным

Service имеет право преобразовывать DB rows в структуру, удобную конкретной странице.

## D011 — progressive enhancement

Базовый public контент должен быть доступен из server-rendered HTML.

JS усиливает navigation/disclosure/carousel, а не создаёт смысл страницы.

## D012 — public design author-first

Новый public runtime строится вокруг Projects/Works и художественного повествования, а не как старый каталог Product, перекрашенный в новый CSS.

## D013 — новая admin после прояснения public content model

Public pages сначала выявляют, какие данные и редакционные операции реально нужны.

## D014 — backend может идти на один шаг впереди frontend

Read-side следующей страницы можно подготовить раньше её CSS.

Но не следует на месяцы вперёд проектировать write-side без проверенного UI/use-case.

## D015 — page-builder не является pre-release scope

Идея модульных reorderable sections сохранена как будущая возможность.

До первого release — только конкретные section components, необходимые страницам.

## Открытые вопросы

### Q001 — Project content model

Останется ли:

```text
Project.text + image positions
```

или появятся явные content blocks/image roles?

### Q002 — Series

Какую роль Series будет играть в public archive и admin?

### Q003 — Shop detail

Нужна ли linked ShopItem отдельная коммерческая страница или Work detail остаётся единственной точкой?

### Q004 — Stock completion

Когда Order становится `completed`, в какой момент и как именно уменьшается physical `stock_quantity` в target runtime?

### Q005 — First production platform

PaaS или свой reverse-proxy/server stack — решение ещё впереди.

### Q006 — Database production strategy

Останется ли SQLite на первом release или появится причина переходить на PostgreSQL?

Не менять только «потому что production».
