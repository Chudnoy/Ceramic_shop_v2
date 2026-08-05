# Граница актуальности и источники

## Снимок

Документация подготовлена **5 августа 2026 года**.

Изученная опубликованная ветка GitHub `main` находилась на commit:

```text
e3d3e90321f241beef5606df2cf5b81660a12c2a
«Окончание миграций»
```

Пользователь сообщил о локально выполненном:

```bash
git rm --cached shop.db
```

но изменение на момент подготовки архива ещё не было отправлено в GitHub. Поэтому документация описывает целевое и уже локально подготовленное состояние: `shop.db` не отслеживается.

## Изученные области

### Точка входа и конфигурация

- `app.py`;
- `.env` contract;
- `requirements.txt`;
- `requirements-dev.txt`;
- `.github/workflows/tests.yml`;
- `.gitignore`.

### Database

- connection;
- schema/seed;
- migration runner;
- `v001–v007`;
- products;
- categories;
- tags;
- orders;
- order_items;
- admin stats.

### Services

- cart;
- products;
- orders;
- images;
- CSRF;
- category/tag form processing;
- validation.

### Routes

- весь публичный blueprint;
- admin auth;
- dashboard;
- products;
- orders;
- categories;
- tags.

### Tests

- общие fixtures;
- migration engine tests;
- version integration tests;
- double-run `init_db` test;
- ранее сформированная database/service/route тестовая архитектура.

## Что намеренно не объявлено фактом

- точная будущая схема `Project / Work / Shop item`;
- конкретный production-хостинг;
- обязательность PostgreSQL;
- платёжный провайдер;
- служба доставки;
- окончательный дизайн;
- точное число production-пользователей;
- необходимость микросервисов.

## Как поддерживать актуальность

После значимого изменения добавляйте в этот файл:

```text
дата
commit
затронутые документы
важные новые решения
```

Документация является снимком состояния, а не заменой Git-истории и тестов.
