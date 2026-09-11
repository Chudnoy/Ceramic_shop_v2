# Frontend architecture нового public runtime

## 1. Отдельная public-зона

Новый frontend находится отдельно от legacy templates/assets:

```text
templates/public/
static/public/
```

Это позволяет строить новый визуальный язык без механического редизайна старого Product catalog.

## 2. Base template

`templates/public/base.html` задаёт:

- `lang="ru"`;
- viewport meta;
- shared stylesheet;
- sticky header;
- semantic `<nav>`;
- mobile menu button с `aria-expanded`;
- footer;
- shared `site.js`;
- `{% block styles %}`;
- `{% block scripts %}`.

Page-specific CSS/JS подключаются только там, где нужны.

## 3. CSS layers

### `site.css`

Содержит:

- design tokens;
- reset/base;
- accessibility helpers;
- header/footer;
- homepage sections;
- responsive rules.

Root tokens:

```text
--color-background
--color-text
--color-muted
--color-accent
--color-dark

--page-start
--page-end
--site-header-height

--font-serif
--font-sans
```

### `work.css`

Страница Work имеет отдельную большую систему layout.

Она использует:

- responsive Grid/Flex;
- logical properties;
- custom dimensions;
- `object-fit` и cutout media;
- story expansion states;
- Work carousel;
- desktop/tablet/mobile composition changes.

### `project.css`

Project detail построен как art-directed 12-column editorial grid.

Текущие sections:

```text
project-threshold
project-premise
project-first-movement
```

Page ещё развивается.

## 4. JavaScript philosophy

### `site.js`

Mobile navigation:

```text
find header/toggle/nav
↓
click toggles .is-open
↓
sync aria-expanded
↓
click nav link closes
↓
.is-enhanced marks successful enhancement
```

### `work.js`

Два независимых компонента.

Story:

```text
JS enables is-collapsible
↓
measure real overflow
↓
show toggle only if needed
↓
is-expanded is single CSS state
```

Carousel:

```text
currentIndex = persistent state

viewport + CSS geometry
↓
visibleItems / maxIndex / gap / width / step
↓
transform + controls state
```

На resize всё пересчитывается.

## 5. Progressive enhancement

Пример Story:

Без JS текст не должен исчезнуть навсегда.

JS сначала подтверждает существование нужного DOM и только потом включает collapsed state.

То же мышление применимо к mobile nav.

## 6. HTML vs CSS vs JS

Полезная граница:

```text
HTML / Jinja
что существует и что означает

CSS
где это находится и как выглядит

JS
как компонент меняет состояние во времени
```

Например carousel:

```text
Jinja creates cards
CSS decides card geometry
JS moves track
```

JS не должен дублировать CSS formulas: он читает итоговую geometry через `getComputedStyle` и `getBoundingClientRect`.

## 7. Grid как editorial coordinate system

В Project page Grid используется не как таблица.

Несколько elements могут занимать одну row и пересекающиеся columns.

`z-index`, `align-self`, `isolation` и margins создают композицию поверх общей 12-column coordinate plane.

Это осознанный art-direction pattern.

## 8. Responsive strategy

Work page уже использует cumulative media rules:

```text
base
+ <=900px
+ <=640px
```

Mobile overrides не создают страницу «с нуля» — они переопределяют выбранные свойства.

Некоторые desktop systems на mobile намеренно уничтожаются, например Grid → block или fixed height → auto.

## 9. Accessibility patterns, которые уже есть

- semantic `<main>`, `<nav>`, `<figure>`;
- `lang="ru"`;
- `aria-label`;
- `aria-expanded`;
- `aria-controls`;
- focus-visible outline;
- `.sr-only`;
- decorative elements с `aria-hidden`.

Это база, а не завершённый accessibility audit.

## 10. Что дальше

При создании Works/Projects/Shop pages желательно переиспользовать:

- shared tokens;
- header/footer;
- text-link patterns;
- existing card/media decisions;
- `data-*` JS hooks;
- progressive enhancement.

Но не превращать стили в универсальную component library раньше реальной повторяемости.
