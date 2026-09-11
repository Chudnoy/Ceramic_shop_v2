# Известные ограничения

Это не backlog всех возможных улучшений, а список разрывов, важных для понимания текущей системы.

## 1. Два runtime одновременно

Target schema существует, но:

```text
legacy cart/checkout/admin
```

по-прежнему опираются на Product.

Это временно увеличивает когнитивную нагрузку и число допустимых путей к данным.

## 2. Product всё ещё является write-side truth

Новый Work/ShopItem read-side уже работает, но legacy checkout меняет:

```text
Product.status
```

а не target stock.

До cutover нельзя считать ShopItem inventory полноценным единственным источником коммерческой истины.

## 3. `OrderItem.shop_item_id` — bridge, а не завершённый commerce runtime

v012/v013 подготовили связь, но новые order creation/cancel/complete операции ещё не переведены на ShopItem inventory.

## 4. Public Shop service без route

`public_shop_service.py` и tests существуют, но `/v2/shop` ещё не подключён.

## 5. Нет Works/Projects index routes

Новый public base navigation пока в основном ведёт к homepage anchors.

Отдельные index pages ещё не реализованы.

## 6. Project page WIP

Текущий Project service уже отдаёт больше данных, чем template использует.

Template сейчас использует только первый paragraph и первую Work в first movement.

Дополнительные `break_image`, `process_image`, `field_images` уже доступны read-model, но ещё не все отражены в markup.

`project.css` на snapshot-дате является развивающейся desktop-композицией; окончательный responsive слой ещё впереди.

## 7. Семантика Project image position неявна

Сейчас:

```text
position 1..4
```

имеют особые роли только в service.

Database хранит лишь integer position.

Для будущей admin может понадобиться явная image role либо другой editor model.

## 8. Series почти не развита

Schema уже содержит Series, но public/admin runtime почти не использует её.

## 9. N+1-like read patterns допустимы пока из-за малого масштаба

Public services часто:

```text
load list
↓
для каждого item load cover
```

При текущем маленьком каталоге это приемлемо и понятно.

При росте данных можно перейти к более богатым JOIN/read queries, если появится реальная проблема.

## 10. Legacy cart quantity и unique model

Legacy cart умеет quantity как общий механизм Product.

Target Shop уже различает `unique` и `stock`, но target cart ещё не реализован.

## 11. Нет production server/deployment

Сейчас:

```text
Flask dev server
debug=True
```

Нет production process model, reverse proxy/platform config, health endpoint и production logging.

## 12. Нет online payment/delivery/email

Эти функции не являются текущей частью проекта.

## 13. Нет полноценного user system

Admin — одна credential pair из environment + session flag.

## 14. Media storage local

Изображения — файловые paths внутри static/uploads/public assets.

Object storage/CDN pipeline не реализован.

## 15. Placeholder content

Новая public base содержит временные footer/contact links и example email.

Seed содержит demo content и изображения.

## 16. Backup DB tracked в Git

`shop_before_runtime_rewrite.db` присутствует в root на snapshot commit.

Нужно принять осознанное решение о его дальнейшем хранении.

## 17. Старые docs/scenarios устарели

Existing `docs/scenarios/` в старой документации описывает Product-era архитектуру до v008–v013.

Если сохранять их, лучше перенести под явный `docs/legacy/`, а не оставлять рядом с текущими документами без маркировки.

## 18. Нет browser tests нового JS

Work carousel/story и mobile nav пока не имеют отдельного browser/e2e слоя.

Это не блокирует текущую разработку, но перед production smoke tests полезны.
