# Roadmap до production

Этот документ описывает не календарные сроки, а зависимость этапов.

## Этап A — закончить новый публичный художественный read-side

Сейчас:

```text
new home          exists
new Work detail   exists
new Project       WIP
```

Далее:

```text
закончить Project detail
↓
Works index/archive
↓
Projects index
↓
общая навигация между ними
```

Backend этих index pages можно готовить на один шаг раньше верстки.

## Этап B — Shop public

Нужно определить:

- Shop index composition;
- linked Work item vs standalone item;
- состояния available / reserved / out of stock;
- карточку standalone ShopItem;
- что происходит при click linked item;
- нужен ли отдельный ShopItem detail для linked Work или Work detail достаточно.

После этого уже существующий `public_shop_service` можно довести до реального route/template contract.

## Этап C — target admin

Не начинать как полный rewrite.

Вертикальные slices:

```text
Project management
↓
Work management
↓
ShopItem management
↓
media/taxonomy ordering
```

Сначала минимальные необходимые операции, затем удобство редактора.

Page-section drag-and-drop — post-launch feature, если реальная потребность сохранится.

## Этап D — commerce cutover

Самая рискованная часть.

Новый cart:

```text
session stores ShopItem IDs
```

Новый availability:

```text
stock - active reservations
```

Order creation должна атомарно гарантировать:

```text
requested quantity <= available quantity
```

Order lifecycle должен корректно влиять на inventory/reservations.

Нужно отдельно решить completed semantics для `stock_quantity`.

## Этап E — legacy cleanup

Только после подтверждённого cutover:

- убрать legacy public catalog;
- убрать Product-based cart/checkout;
- убрать Product admin;
- решить судьбу `products` и старых columns;
- при необходимости отдельными migrations почистить schema.

Cleanup не должен предшествовать replacement.

## Этап F — production readiness

### Runtime

- production WSGI/app server;
- debug off;
- environment configuration;
- error handling;
- logging;
- health endpoint;
- graceful startup.

### HTTP/platform

- HTTPS;
- domain/DNS;
- reverse proxy или PaaS routing;
- static/media strategy.

### Data

- production DB path/storage;
- backups;
- restore test;
- migration procedure;
- seed strategy отделена от production data.

### Security

- secure cookies;
- secrets;
- admin exposure;
- upload validation;
- CSRF audit.

### Quality

- full pytest/Ruff;
- browser smoke path;
- responsive pass;
- accessibility pass;
- broken links/placeholders cleanup.

## Этап G — первый release

Feature freeze перед release.

Критерий:

```text
основной сайт можно смотреть
контент можно поддерживать
магазин выполняет выбранный MVP-сценарий
заказ не нарушает inventory invariants
production runtime воспроизводим
```

Не требуется до первого release:

- page builder;
- drag-and-drop всех sections;
- универсальный CMS;
- сложные animations;
- бесконечный список «классных будущих фич».

## После release

Уже в работающем продукте можно добавлять:

- reorderable sections;
- richer Project editor;
- event/exhibition sections;
- charity sections;
- advanced inventory;
- notifications;
- analytics;
- более сложные editorial compositions.

Главная защита проекта от вечного pre-release: разделять **release-critical** и **post-launch-interesting**.
