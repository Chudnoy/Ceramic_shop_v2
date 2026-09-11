# Документация Ceramic Shop v2

Эта папка описывает **реальное состояние репозитория**, а не только желаемую конечную архитектуру.

Срез актуальности: `main`, commit `7d996da41b25bd033d2c52f431b4b6a84bfdcdce`, 2026-09-11.

## Как читать

Если нужно быстро восстановить проект после паузы:

1. [`01_CURRENT_STATE.md`](01_CURRENT_STATE.md)
2. [`02_ARCHITECTURE.md`](02_ARCHITECTURE.md)
3. [`03_DOMAIN_MODEL.md`](03_DOMAIN_MODEL.md)
4. [`17_RUNTIME_CUTOVER.md`](17_RUNTIME_CUTOVER.md)
5. [`11_ROADMAP_TO_PRODUCTION.md`](11_ROADMAP_TO_PRODUCTION.md)

Если нужно глубже:

| Документ | О чём |
|---|---|
| `01_CURRENT_STATE.md` | Что уже реализовано, что WIP, что legacy |
| `02_ARCHITECTURE.md` | Route → service → database и границы модулей |
| `03_DOMAIN_MODEL.md` | Project / Work / ShopItem / OrderItem |
| `04_DATABASE_AND_MIGRATIONS.md` | v001–v013, preflight, backfill |
| `05_PUBLIC_SCENARIOS.md` | Legacy public и новый `/v2` read-side |
| `06_ADMIN_SCENARIOS.md` | Текущая Product-admin и граница будущей admin |
| `07_TESTING_AND_CI.md` | pytest, fixtures, Ruff, Actions |
| `08_SECURITY_AND_CONFIGURATION.md` | `.env`, session auth, CSRF, production gaps |
| `09_DEVELOPMENT_RULES.md` | Практические правила дальнейшего развития |
| `10_KNOWN_LIMITATIONS.md` | Известные технические и модельные ограничения |
| `11_ROADMAP_TO_PRODUCTION.md` | Дальнейшая последовательность |
| `12_DECISION_LOG.md` | Уже принятые решения и открытые вопросы |
| `13_GLOSSARY.md` | Термины проекта |
| `14_RELEASE_CHECKLIST.md` | Чеклисты до первой публикации |
| `15_SOURCE_SNAPSHOT.md` | На каких файлах основана документация |
| `16_FRONTEND_ARCHITECTURE.md` | Новый Jinja/CSS/JS public frontend |
| `17_RUNTIME_CUTOVER.md` | Сосуществование legacy и target runtime |

Корневой [`PROJECT_MAP.md`](../PROJECT_MAP.md) — самая короткая техническая карта.

## Правило документации

Документ считается текущим только пока совпадает с кодом.

При изменении бизнес-поведения:

```text
код
+ тесты
+ соответствующая документация
```

Будущие идеи должны явно маркироваться как:

- **план**;
- **кандидат**;
- **открытый вопрос**.

Нельзя описывать будущий Shop checkout или новую admin как уже работающие только потому, что таблицы для них существуют.
