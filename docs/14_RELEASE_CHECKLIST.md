# Release checklist

Это не утверждение, что release уже близко. Документ нужен, чтобы production не превратился в неструктурированную стену терминов.

## 1. Product scope

- [ ] определён первый release scope;
- [ ] закончены обязательные public pages;
- [ ] определён Shop MVP;
- [ ] post-launch features вынесены из release-critical списка;
- [ ] нет незавершённых placeholder sections, ведущих в никуда.

## 2. Runtime cutover

- [ ] новый public runtime больше не требует legacy Product для художественных страниц;
- [ ] target cart/checkout использует ShopItem;
- [ ] target order lifecycle согласован с inventory;
- [ ] legacy routes отключены или явно перенаправлены;
- [ ] legacy admin заменена в нужном объёме.

## 3. Data

- [ ] все migrations воспроизводятся на чистой базе;
- [ ] migration procedure проверена на копии реальных данных;
- [ ] production seed не создаёт demo content;
- [ ] backup policy определена;
- [ ] restore реально проверен;
- [ ] tracked DB backups в repository проверены/удалены при необходимости.

## 4. Configuration

- [ ] реальные secrets не в Git;
- [ ] `.env.example` актуален;
- [ ] debug выключен;
- [ ] production DATABASE path определён;
- [ ] environment settings отделены от source.

## 5. Security

- [ ] CSRF работает на всех state-changing forms;
- [ ] admin credentials безопасны;
- [ ] secure session cookie settings включены для HTTPS;
- [ ] upload/file validation проверена;
- [ ] ошибки не показывают stack trace посетителю;
- [ ] privacy policy/contact data реальные.

## 6. Server

- [ ] выбран production app server;
- [ ] приложение запускается без debug server;
- [ ] HTTPS работает;
- [ ] domain/DNS настроены;
- [ ] reverse proxy/PaaS routing проверен;
- [ ] static/media serving определено;
- [ ] health endpoint существует, если его требует platform.

## 7. Observability

- [ ] есть понятный application log;
- [ ] ошибки startup видны;
- [ ] ошибки order flow видны;
- [ ] лог не содержит секреты/лишние customer data;
- [ ] понятно, как проверить, что приложение живо.

## 8. Quality

```bash
python -m ruff check .
python -m ruff format --check
python -m pytest -q
```

- [ ] CI green на release commit;
- [ ] manual desktop pass;
- [ ] manual tablet pass;
- [ ] manual mobile pass;
- [ ] keyboard navigation pass;
- [ ] basic screen-reader semantics pass;
- [ ] cart/order smoke test;
- [ ] broken links checked;
- [ ] footer placeholders removed.

## 9. Content

- [ ] настоящие Project/Work texts;
- [ ] alt texts достаточно осмысленны;
- [ ] цены проверены;
- [ ] availability соответствует данным;
- [ ] контакты реальные;
- [ ] social links реальные или скрыты;
- [ ] demo Lorem Ipsum удалён.

## 10. Release

- [ ] production migration/backup выполнены;
- [ ] deploy;
- [ ] smoke test на production URL;
- [ ] проверить admin;
- [ ] проверить один тестовый order flow;
- [ ] проверить логи;
- [ ] зафиксировать release commit/tag.

## 11. После release

Только после стабильного первого запуска возвращать из backlog:

- drag-and-drop sections;
- page builder;
- расширенную CMS;
- richer analytics;
- дополнительные editorial experiments.
