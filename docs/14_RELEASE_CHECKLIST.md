# Контрольные списки

## 1. Перед обычным commit

```text
[ ] git status понятен
[ ] нет .env, shop.db, cache и случайных uploads
[ ] diff прочитан
[ ] тесты затронутого модуля зелёные
[ ] весь python -m pytest зелёный
[ ] docs обновлены при изменении поведения
[ ] commit не смешивает массовое форматирование и бизнес-логику
```

Команды:

```bash
git status
git diff
python -m pytest
git ls-files shop.db
```

## 2. Перед новой миграцией

```text
[ ] предметное решение зафиксировано
[ ] определено состояние до и после
[ ] выбран следующий свободный номер
[ ] старые migration files не изменяются
[ ] apply использует переданный conn
[ ] внутри apply нет commit/rollback
[ ] написан integration test на старых данных
[ ] проверены FK/CHECK/default/nullability
[ ] протестирован rollback
[ ] обновлены domain и migration docs
```

## 3. После изменения заказов

```text
[ ] happy path
[ ] неверный expected status
[ ] отсутствующий заказ
[ ] отсутствующая позиция
[ ] rollback заказа
[ ] rollback статусов работ
[ ] snapshot не потерян
[ ] cancel освобождает резерв
[ ] complete продаёт работы
[ ] повторное действие не проходит
```

## 4. После изменения работ

```text
[ ] публичная видимость
[ ] архив
[ ] продажа
[ ] featured требует visible
[ ] active order сохраняет reserved
[ ] tags обновляются атомарно
[ ] новое изображение удаляется после rollback
[ ] старое изображение удаляется только после commit
```

## 5. Локальный smoke test

```text
[ ] запуск на существующей базе
[ ] повторный запуск
[ ] главная
[ ] каталог
[ ] карточка
[ ] корзина
[ ] checkout
[ ] order success
[ ] admin login/logout
[ ] создание/редактирование/архив работы
[ ] confirm/cancel/complete заказа
```

## 6. Проверка чистой базы

Только когда данные disposable или есть backup:

```text
[ ] остановить приложение
[ ] переименовать shop.db в backup
[ ] запустить приложение
[ ] проверить schema_migrations 1–7
[ ] проверить seed
[ ] повторно запустить
[ ] убедиться в отсутствии дублей
```

## 7. Перед staging

```text
[ ] production-like config
[ ] debug off
[ ] отдельные secrets
[ ] migration command
[ ] persistent uploads
[ ] database backup
[ ] restore test
[ ] HTTPS
[ ] secure cookies
[ ] logging
[ ] error pages
[ ] health check
[ ] max upload size
[ ] privacy drafts
[ ] full checkout lifecycle
```

## 8. Перед production

```text
[ ] финальные решения Project/Work/Shop item
[ ] уникальные/складские инварианты
[ ] контент утверждён Полиной
[ ] домен и HTTPS
[ ] production admin password
[ ] debug=False
[ ] WSGI deployment
[ ] миграции rehearsed на копии
[ ] backup создан и восстановлен в тесте
[ ] uploads сохраняются между deployments
[ ] персональные данные защищены
[ ] order success закрыт от чужого доступа
[ ] rate limiting login
[ ] мониторинг и error tracking
[ ] понятный аварийный способ отключить checkout
[ ] первый post-release smoke test запланирован
```

## 9. После deployment

```text
[ ] приложение отвечает
[ ] главная и статика загружаются
[ ] база на ожидаемой migration version
[ ] admin login работает
[ ] тестовый заказ проходит
[ ] cancel освобождает резерв
[ ] logs не содержат новых ошибок
[ ] backup job работает
[ ] мобильная версия проверена
```
