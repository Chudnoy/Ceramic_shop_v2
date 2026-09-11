# Административные сценарии

## 1. Важная оговорка

Текущая admin — **legacy Product-admin**.

Она остаётся рабочей и не должна в документации называться «новой админкой Projects/Works/ShopItems».

Модули:

```text
routes/admin/auth.py
routes/admin/dashboard.py
routes/admin/products.py
routes/admin/orders.py
routes/admin/categories.py
routes/admin/tags.py
```

## 2. Доступ

Перед каждым admin request:

```text
/admin/login
→ разрешён

остальные endpoints
→ требуют session["is_admin"]
```

Login:

- сравнивает login с `ADMIN_LOGIN`;
- проверяет Werkzeug password hash;
- ставит permanent session;
- сохраняет `session["is_admin"] = True`.

Logout — POST и удаляет session flag.

## 3. Product management

Legacy admin умеет:

- создавать Product;
- редактировать Product;
- управлять изображением;
- управлять тегами;
- менять publication/sale/status-related state;
- архивировать;
- восстанавливать;
- удалять при допустимых условиях.

Точные инварианты остаются в `product_service.py` и соответствующих tests.

## 4. Categories / Tags

Это отдельные admin modules и legacy/target shared справочники.

Важно: target Works тоже используют существующие `categories` и `tags` через новые join tables. Поэтому эти справочники не являются полностью «устаревшими».

## 5. Orders

Текущая Order-admin работает с legacy lifecycle:

```text
new
↓ confirm
confirmed
↓ complete
completed
```

Отмена:

```text
new → canceled
confirmed → canceled
```

Удаление применяется к canceled order в рамках legacy rules.

OrderItem хранит snapshots, поэтому история заказа не должна исчезать вместе с удалённой карточкой товара.

## 6. Почему новую admin пока не стоит строить поверх старых форм

Новая модель требует редактировать разные сущности:

```text
Project
Work
ShopItem
```

а не «новый Product с большим количеством полей».

Будущая admin должна явно разделять:

```text
художественное содержание
коммерческое предложение
заказы
```

## 7. Что public Project page уже выявляет для будущей admin

Текущий frontend использует Project images по `position`:

```text
1 cover
2 premise
3 break
4 process
>=5 field
```

Это уже реальное требование read-side, но ещё не доказано, что администратору удобно управлять такими ролями только числом position.

Перед новой Project admin следует решить:

- нужны ли image roles;
- как менять порядок;
- как редактировать текстовые «движения» Project;
- должен ли Project text оставаться одним TEXT с разделением пустыми строками;
- как выставлять `project_position` Works.

## 8. Что будущая Work admin должна уметь

Минимально:

- name/slug/description/year/dimensions;
- publication;
- Project/Series relation;
- project_position;
- images + ordering;
- categories/tags/materials;
- commissionability.

Коммерческая цена/stock не должны снова заселиться в Work.

## 9. Что будущая Shop admin должна уметь

Для linked ShopItem:

- выбрать Work;
- price;
- inventory type;
- stock;
- publication;
- orderability;
- retired;
- sales note.

Для standalone:

- собственное name/description/dimensions;
- own images/taxonomy;
- те же коммерческие поля.

## 10. Правило перехода

Не переписывать всю admin заранее.

Правильнее:

```text
public model стабилизирует требования
↓
target write service
↓
узкий admin slice
↓
tests
↓
следующий slice
```

Legacy admin удаляется только после того, как соответствующая target-функция действительно заменена.
