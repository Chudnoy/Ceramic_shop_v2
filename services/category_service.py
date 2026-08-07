import sqlite3

from database.categories import (
    create_category,
    delete_category,
    find_category_by_name,
    find_category_by_slug,
    get_product_count_by_category_id,
    update_category,
)
from database.connection import get_db_connection
from validation import validate_category


def process_category_form(form):
    """
    Обрабатывает данные формы категории.

    Достаёт из формы название, slug и описание, передаёт их в validate_category
    и возвращает результат в формате service-слоя: успешность обработки,
    сообщение об ошибке и очищенные данные.
    """
    name = form.get("name", "")
    slug = form.get("slug", "")
    description = form.get("description", "")

    is_valid, message, data = validate_category(name, slug, description)

    if not is_valid:
        return False, message, None

    return True, "", data


def create_category_from_form(form):
    is_valid, error_message, data = process_category_form(form)

    if not is_valid:
        return False, error_message

    conn = None

    try:
        conn = get_db_connection()

        if find_category_by_name(conn, data["name"]):
            return False, "Категория с таким названием уже существует"

        if find_category_by_slug(conn, data["slug"]):
            return False, "Категория с таким slug уже существует"

        create_category(
            conn=conn,
            name=data["name"],
            slug=data["slug"],
            description=data["description"],
        )

        conn.commit()

        return True, ""

    except sqlite3.IntegrityError:
        if conn is not None:
            conn.rollback()

        return False, "Категория с таким названием или slug уже существует"

    except Exception:
        if conn is not None:
            conn.rollback()

        raise

    finally:
        if conn is not None:
            conn.close()


def update_category_from_form(form, current_category):
    is_valid, error_message, data = process_category_form(form)

    if not is_valid:
        return False, error_message

    conn = None

    try:
        conn = get_db_connection()

        existing_by_name = find_category_by_name(
            conn,
            data["name"],
        )

        if existing_by_name and existing_by_name["id"] != current_category["id"]:
            return False, "Категория с таким названием уже существует"

        existing_by_slug = find_category_by_slug(
            conn,
            data["slug"],
        )

        if existing_by_slug and existing_by_slug["id"] != current_category["id"]:
            return False, "Категория с таким slug уже существует"

        is_updated = update_category(
            conn=conn,
            name=data["name"],
            slug=data["slug"],
            description=data["description"],
            category_id=current_category["id"],
        )

        if not is_updated:
            conn.rollback()
            return False, "Категория не найдена"

        conn.commit()

        return True, ""

    except sqlite3.IntegrityError:
        if conn is not None:
            conn.rollback()

        return False, "Категория с таким названием или slug уже существует"

    except Exception:
        if conn is not None:
            conn.rollback()

        raise

    finally:
        if conn is not None:
            conn.close()


def delete_category_by_id(category_id):
    conn = None

    try:
        conn = get_db_connection()

        products_count = get_product_count_by_category_id(
            conn=conn,
            category_id=category_id,
        )

        if products_count > 0:
            return False, "Категорию нельзя удалить пока к ней привязаны работы"

        is_deleted = delete_category(
            conn=conn,
            category_id=category_id,
        )

        if not is_deleted:
            conn.rollback()
            return False, "Категория не найдена"

        conn.commit()

        return True, ""

    except sqlite3.IntegrityError:
        if conn is not None:
            conn.rollback()

        return False, "Категорию нельзя удалить пока к ней привязаны работы"

    except Exception:
        if conn is not None:
            conn.rollback()

        raise

    finally:
        if conn is not None:
            conn.close()
