# Правила дальнейшей разработки

## 1. Не переписывать всё одним движением

Текущая стратегия:

```text
expand schema
↓
backfill
↓
new read-side beside legacy
↓
vertical runtime slices
↓
cutover
↓
cleanup
```

Рабочий legacy runtime удаляется только после появления заменяющего target slice.

## 2. Данные и поведение мигрируются по-разному

```text
данные
→ migrations/backfill

поведение
→ tests + new services/routes
```

Не пытаться «мигрировать код» SQL-migration.

## 3. Route должен оставаться тонким

Хорошо:

```text
parse request
↓
call service
↓
404/redirect/render
```

Плохо:

```text
route
├── 5 SQL queries
├── stock math
├── transaction
├── file operations
└── render
```

## 4. Service — владелец сценария

Если операция затрагивает несколько записей и должна быть atomic, connection/transaction должна контролироваться на уровне сценария.

## 5. Database module — raw SQL, узкая ответственность

Database function должна отвечать на конкретный вопрос.

Не смешивать в одной функции:

```text
SQL
HTTP
flash
template decisions
filesystem cleanup
```

## 6. Derived state не хранить без необходимости

Target Shop:

```text
stock_quantity — stored
reserved_quantity — derived
available_quantity — derived
stock_state — derived
can_order — derived
```

Если новое состояние можно надёжно вывести из первичных фактов, сначала предпочитать вычисление.

## 7. Public read-model разрешён

Не надо заставлять template самому собирать:

```text
Project + images + Works
```

или:

```text
Work + ShopItem + availability
```

Service может вернуть специальный page data object/dict.

## 8. Frontend

Принцип:

```text
HTML = смысл и базовый контент
CSS  = пространственная/визуальная система
JS   = изменение состояния и progressive enhancement
```

JS не должен быть нужен только для того, чтобы посетитель вообще увидел основной текст страницы.

## 9. CSS

Текущая новая public design system уже активно использует:

- custom properties;
- logical properties;
- Grid;
- Flex;
- `clamp`;
- `aspect-ratio`;
- `object-fit`;
- responsive breakpoints;
- capability query `@media (hover: hover)`.

При новых компонентах сначала искать существующие design tokens и patterns, а не создавать новый локальный мир без причины.

## 10. BEM-like naming

Новый public frontend использует:

```text
.block
.block__element
.block--modifier
```

Это naming convention, не framework.

JS-hooks лучше держать через `data-*`, если hook описывает поведение, а не визуальный стиль.

## 11. Новая модульность страниц — позже

Идея page sections / reorderable admin логична, но текущий принцип:

```text
сначала несколько реальных независимых sections
↓
потом наблюдаем повторяющийся контракт
↓
только потом абстрагируем Page/Section
```

Не строить собственный универсальный page builder до production.

## 12. Backend runway

Допустимо держать backend примерно на один экран/страницу впереди frontend.

Ближайшие хорошие кандидаты:

```text
Works index read-model
Projects index read-model
Shop page route/read-model refinement
```

Не стоит на опережение полностью переписывать cart/checkout, пока Shop public UX ещё не определён.

## 13. Исторические migrations immutable

`v001–v013` — история.

Новый schema change:

```text
v014+
```

а не редактирование старой migration, если она уже является частью истории проекта.

## 14. Документация

После существенного архитектурного изменения обновить:

```text
01_CURRENT_STATE
PROJECT_MAP
и профильный документ
```

Не обязательно менять все Markdown-файлы после каждой CSS-правки, если архитектурный контракт не изменился.
