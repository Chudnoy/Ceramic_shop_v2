# 13. Локальный запуск и конфигурация

## Установка

```bash
git clone <URL>
cd Ceramic_shop_v2
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Для тестов рекомендуется `requirements-dev.txt`:

```text
-r requirements.txt
pytest>=8,<9
```

## `.env`

```env
SECRET_KEY=длинная-случайная-строка
ADMIN_LOGIN=admin
ADMIN_PASSWORD_HASH=хеш
```

```bash
python -c "import secrets; print(secrets.token_hex(32))"
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('пароль'))"
```

## Запуск

```bash
python app.py
```

Текущая локальная конфигурация:

```text
host = 0.0.0.0
port = 8000
debug = True
```

## Инициализация базы

`init_db()` вызывается только при запуске `app.py` как программы. При production-запуске через WSGI понадобится отдельная команда миграции/инициализации.

## Будущая фабрика

```python
def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(...)

    if test_config:
        app.config.update(test_config)

    ...
    return app
```

Преимущества: тестовая конфигурация, временная база, отсутствие глобальных побочных эффектов и простой production-запуск.

## GitHub Actions

```yaml
name: tests

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: python -m pytest
        env:
          SECRET_KEY: test-secret
          ADMIN_LOGIN: admin
          ADMIN_PASSWORD_HASH: test-hash
```
