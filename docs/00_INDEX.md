# Документация Ceramic Shop v2

## Назначение

Эта папка является каноническим описанием текущего проекта. Документы разделяют:

- **реализованное сейчас**;
- **архитектурные правила, которые уже действуют**;
- **известные ограничения**;
- **будущие решения, которые ещё нельзя считать частью кода**.

Такое разделение особенно важно перед переходом от универсальной сущности `products` к более точной модели художественных проектов, работ и магазинных предложений.

## Рекомендуемый порядок чтения

1. [01_CURRENT_STATE.md](01_CURRENT_STATE.md) — что проект представляет собой сейчас.
2. [02_ARCHITECTURE.md](02_ARCHITECTURE.md) — как разделены ответственности.
3. [03_DOMAIN_MODEL.md](03_DOMAIN_MODEL.md) — таблицы, статусы и инварианты.
4. [04_DATABASE_AND_MIGRATIONS.md](04_DATABASE_AND_MIGRATIONS.md) — история схемы и правила новых миграций.
5. [05_PUBLIC_SCENARIOS.md](05_PUBLIC_SCENARIOS.md) — публичные пользовательские потоки.
6. [06_ADMIN_SCENARIOS.md](06_ADMIN_SCENARIOS.md) — административные потоки.
7. [07_TESTING_AND_CI.md](07_TESTING_AND_CI.md) — тесты и GitHub Actions.
8. [08_SECURITY_AND_CONFIGURATION.md](08_SECURITY_AND_CONFIGURATION.md) — текущая защита и production-разрывы.
9. [09_DEVELOPMENT_RULES.md](09_DEVELOPMENT_RULES.md) — правила дальнейшей разработки.
10. [10_KNOWN_LIMITATIONS.md](10_KNOWN_LIMITATIONS.md) — честная карта технического долга.
11. [11_ROADMAP_TO_PRODUCTION.md](11_ROADMAP_TO_PRODUCTION.md) — дальнейший маршрут.
12. [12_DECISION_LOG.md](12_DECISION_LOG.md) — принятые и открытые решения.
13. [13_GLOSSARY.md](13_GLOSSARY.md) — термины.
14. [14_RELEASE_CHECKLIST.md](14_RELEASE_CHECKLIST.md) — контрольные списки.
15. [15_SOURCE_SNAPSHOT.md](15_SOURCE_SNAPSHOT.md) — источники и граница актуальности.

## Быстрый выбор по задаче

| Задача | Документ |
|---|---|
| Понять проект целиком | `README.md`, `PROJECT_MAP.md`, `01_CURRENT_STATE.md` |
| Добавить функцию | `02_ARCHITECTURE.md`, `09_DEVELOPMENT_RULES.md` |
| Изменить таблицы | `04_DATABASE_AND_MIGRATIONS.md` |
| Разобраться с заказом | `03_DOMAIN_MODEL.md`, `05_PUBLIC_SCENARIOS.md`, `06_ADMIN_SCENARIOS.md` |
| Написать тест | `07_TESTING_AND_CI.md` |
| Готовиться к размещению | `08_SECURITY_AND_CONFIGURATION.md`, `14_RELEASE_CHECKLIST.md` |
| Обсуждать модель с Полиной | `03_DOMAIN_MODEL.md`, `10_KNOWN_LIMITATIONS.md`, `11_ROADMAP_TO_PRODUCTION.md` |

## Правило актуальности

При изменении поведения проекта обновляются одновременно:

```text
код
+ тесты
+ соответствующий документ
```

Документация не должна описывать желаемое как уже реализованное. Будущие идеи маркируются словами **план**, **открытый вопрос** или **кандидат на решение**.
