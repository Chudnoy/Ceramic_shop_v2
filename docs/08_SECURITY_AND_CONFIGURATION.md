# Security и configuration

## 1. Текущая конфигурация

`app.py` ожидает:

```text
SECRET_KEY
ADMIN_LOGIN
ADMIN_PASSWORD_HASH
```

Database path по умолчанию:

```text
<project dir>/shop.db
```

`test_config` может переопределить настройки.

## 2. `.env`

Реальный `.env` игнорируется Git.

В этом documentation pack добавлен `.env.example`, потому что старый README ссылался на такой файл, а в текущем root его нет.

В `.env.example` нельзя помещать реальные секреты.

## 3. Admin password

Пароль не хранится в plaintext.

`routes/admin/auth.py` использует:

```python
werkzeug.security.check_password_hash
```

В config хранится hash.

## 4. Session

После успешного login:

```text
session.permanent = True
session["is_admin"] = True
```

`app.permanent_session_lifetime = 1 day`.

Это простая одноадминистраторская модель, а не полноценная user/role system.

## 5. CSRF

`app.before_request` проверяет все POST requests.

Token:

- создаётся через `secrets.token_urlsafe(32)`;
- хранится в session;
- передаётся в формы;
- сравнивается с `request.form["csrf_token"]`.

Невалидный POST перенаправляется с flash error.

## 6. SQLite safety

Каждое новое connection включает:

```sql
PRAGMA foreign_keys = ON
```

Это необходимо для фактической работы FOREIGN KEY constraints в SQLite.

## 7. Local development risks

Текущий `app.py`:

```python
app.run(host="0.0.0.0", port=8000, debug=True)
```

`debug=True` недопустим для production.

Built-in Flask development server не является production deployment strategy.

## 8. Не реализовано как production security layer

До публичного запуска следует отдельно решить:

- production app server;
- HTTPS/TLS termination;
- secure cookie settings;
- reverse proxy / platform config;
- secret management;
- upload limits и media validation;
- logging без утечки чувствительных данных;
- backup/restore;
- error pages;
- rate limits для чувствительных endpoints при необходимости.

## 9. Admin hardening

Текущая одноадминистраторская session-модель может быть достаточной для маленького приватного admin MVP, но перед production нужно проверить:

```text
SESSION_COOKIE_SECURE
SESSION_COOKIE_HTTPONLY
SESSION_COOKIE_SAMESITE
SECRET_KEY quality
login exposure
logout semantics
CSRF on all state-changing forms
```

## 10. Database files в репозитории

`.gitignore` исключает:

```text
shop.db
shop.db-journal
shop.db-shm
shop.db-wal
```

Но в текущем root репозитория присутствует отслеживаемый файл:

```text
shop_before_runtime_rewrite.db
```

Это отдельный backup snapshot с другим именем и он не покрывается текущим правилом `shop.db`.

Перед production/public repository стоит решить явно:

- нужен ли этот backup в Git;
- содержит ли он данные, которые вообще допустимо публиковать;
- если это только локальный safety copy, перенести его вне repository и удалить из history при необходимости.

## 11. Privacy/content placeholders

В новом `templates/public/base.html` сейчас есть placeholder-like contact/footer links, например example email и `href="#"`.

До релиза их нужно заменить реальными публичными данными и страницами/ссылками либо удалить.
