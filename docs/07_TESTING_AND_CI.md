# Тестирование и CI

## 1. Инструменты

Development dependencies:

```text
pytest
pytest-cov
ruff 0.16.1
```

Runtime:

```text
Flask >=3,<4
python-dotenv >=1,<2
```

## 2. Test database

App factory принимает `test_config`.

Тесты используют отдельные SQLite-файлы и настоящий migration runner вместо локальной `shop.db`.

Это позволяет проверять:

```text
пустая база
↓
migrations
↓
test scenario
```

без влияния на developer database.

## 3. Основные группы тестов в репозитории

В текущем `tests/` присутствуют тесты:

- app factory;
- DB connection;
- schema;
- migrations и migration versions;
- Products;
- Categories;
- Tags;
- Works;
- Projects;
- ShopItems;
- Orders;
- OrderItems;
- Product service;
- Order service;
- Cart service;
- Checkout integration;
- Public routes;
- Public Home service;
- Public Work service;
- Public Project service;
- Public Shop service;
- Shop availability service;
- validation.

Это важный сигнал текущей архитектуры: тестовая база уже покрывает и legacy, и target ветки.

## 4. Migration tests

Migration tests должны проверять не только happy path.

Особенно для v009/v011/v013 важны:

```text
preflight rejects inconsistent old data
target emptiness assumptions
backfill mappings
active order bridges
transaction rollback
deterministic result
```

Preflight — часть контракта migration.

## 5. Public service tests

Новые read-model services тестируются отдельно от HTML.

Например Project tests проверяют:

- unpublished Project → `None`;
- published Works only;
- `project_position` ordering;
- image roles by position;
- cover image per Work;
- paragraph split.

Shop tests проверяют visibility policy и linked/standalone media.

## 6. Availability tests

`shop_availability_service` должен покрывать как минимум:

```text
available
fully_reserved
out_of_stock
reserved > stock → error
publication/orderability/retired effects
```

Особенно важно не заменять эти tests будущими template tests: это предметная логика.

## 7. CI

`.github/workflows/tests.yml` запускается на:

```text
push
pull_request
```

Environment:

```text
ubuntu-latest
Python 3.14
```

Steps:

```bash
pip install -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check
python -m pytest -q
```

## 8. Ruff config

`pyproject.toml` содержит per-file ignores для blueprint `__init__.py`, потому что imports там регистрируют route modules побочным эффектом.

Tests имеют отдельное исключение `PLR0402`.

## 9. Что CI пока не проверяет

В текущем workflow нет:

- browser/e2e tests;
- JavaScript unit tests;
- CSS visual regression;
- deployment;
- security scanner;
- production health check.

Это не обязательно добавлять сейчас. Но перед production хотя бы небольшой browser smoke-test public/commerce flow будет полезен.

## 10. Практическое правило

Для новой бизнес-логики сначала формулируется контракт.

Хороший порядок:

```text
test
↓
узкая реализация
↓
refactor
```

Для чисто визуальной CSS-настройки TDD не является самоцелью.

## 11. Команды

```bash
python -m pytest
python -m pytest -q
python -m ruff check .
python -m ruff format .
python -m ruff format --check
```

Не документировать точное количество зелёных тестов как постоянный факт: оно быстро устаревает.
