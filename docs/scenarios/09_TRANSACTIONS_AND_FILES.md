# 9. Транзакции и файловая система

## Транзакционная граница

Пользователь нажимает одну кнопку, хотя внутри выполняется несколько SQL-команд. Результат должен быть единым:

```text
либо всё
либо ничего
```

Все шаги получают одно соединение, `commit()` вызывает сервис в конце.

## Типовой шаблон

```python
conn = None

try:
    conn = get_db_connection()
    first_step(conn)
    second_step(conn)
    conn.commit()
    return True, ""
except Exception:
    if conn is not None:
        conn.rollback()
    raise
finally:
    if conn is not None:
        conn.close()
```

## Зачем `conn = None`

Ошибка может произойти в `get_db_connection()`. Предварительное значение позволяет безопасно проверить, существует ли соединение.

## `return False` и `raise`

`return False` — ожидаемая ситуация: неверный файл, недопустимый переход, запись не найдена.

`raise` — неожиданная техническая ошибка. Перед повторным выбросом сервис делает уборку.

## Файлы не входят в SQLite-транзакцию

`file.save()` создаёт реальный файл, а `rollback()` не умеет его удалить. Поэтому используются компенсационные действия.

### Создание работы

```text
save new image
INSERT product
INSERT tags
COMMIT
```

При ошибке:

```text
ROLLBACK
удалить new image
raise
```

### Редактирование

```text
save new image
UPDATE product
replace tags
COMMIT
удалить old image
```

При ошибке до commit новый файл удаляется, старый остаётся.

Старый файл нельзя удалять до commit: после rollback база снова укажет на старый путь.

## Неизбежная граница

Если удаление старого файла упадёт после commit, останется лишний файл. Это безопаснее, чем база, указывающая на отсутствующее изображение.

## Транзакции заказов

```text
create: orders + order_items + reserve
complete: order completed + products sold
cancel: order canceled + products available
edit: contacts + total + all quantities
```
