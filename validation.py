import re

    
def validate_product(name, price, description, category_id, year, materials, is_visible, is_for_sale, is_featured):
    """
Валидирует основные данные товара.

Проверяет наличие названия и описания, преобразует цену в целое положительное
число и проверяет корректность category_id. Возвращает флаг успеха, сообщение
об ошибке и очищенные данные товара без статуса.
"""
    materials = materials.strip()
    if not materials:
        return False, "Материалы обязательны для заполнения", {}
    
    materials = ", ".join([material.strip() for material in materials.split(",") if material.strip()])

    name = name.strip()
    if not name:
        return False, "Название обязательно для заполнения", {}
        
    description = description.strip()
    if not description:
        return False, "Описание обязательно для заполнения", {}
    
    try:
        price = int(price)
        if price < 1:
            raise ValueError
    except (TypeError, ValueError):
        return False, "Цена должна быть положительным числом", {}
        
    try:
        year = int(year)
        if year < 1990 or year > 2100:
            raise ValueError
    except (TypeError, ValueError):
        return False, "Введите корректный год", {}
    
    try:
        is_visible = int(is_visible)
        if is_visible < 0 or is_visible > 1:
            raise ValueError
    except (TypeError, ValueError):
        return False, 'Некорректные данные доступности на сайте', {}
    
    try:
        is_for_sale = int(is_for_sale)
        if is_for_sale < 0 or is_for_sale > 1:
            raise ValueError
    except (TypeError, ValueError):
        return False, 'Некорректные данные о возможности продажи', {}
        
    try:
        is_featured = int(is_featured)
        if is_featured < 0 or is_featured > 1:
            raise ValueError
    except (TypeError, ValueError):
        return False, "Получены некорректные данные об избранном товаре", {}
    
    try:
        category_id = int(category_id)
    except (TypeError, ValueError):
        return False, "Некорректный ID категории", {}
        
    return True, "", {"name": name, 
                      "price": price, 
                      "description": description, 
                      "category_id": category_id, 
                      "year": year, 
                      "materials": materials, 
                      'is_visible': is_visible,
                      'is_for_sale': is_for_sale,
                      "is_featured": is_featured}


def is_valid_slug(s):
    """
    Проверяет, что slug состоит только из разрешённых символов.

    Разрешены латинские буквы, цифры и дефис.
    Возвращает True, если slug соответствует правилу, иначе False.
    """
    return re.fullmatch(r'^[A-Za-z0-9-]+$', s) is not None


def validate_category(name, slug, description):
    """
    Валидирует данные формы категории.

    Очищает название, slug и описание от лишних пробелов.
    Проверяет, что название заполнено, а slug заполнен и состоит только
    из латинских букв, цифр и дефисов. Описание может быть пустым.

    Возвращает кортеж:
    - True, "", cleaned_data — если данные корректны;
    - False, error_message, None — если данные не прошли проверку.
    """
    name = name.strip()
    if not name:
        return False, 'Имя обязательно для заполнения', None
    
    slug = slug.strip().lower()
    if not slug or not is_valid_slug(slug):
        return False, 'Slug обязателен и может содержать только латинские буквы, цифры и дефис', None
    
    description = description.strip()
    
    return True, '', {'name': name, 'slug': slug, 'description': description}


def validate_tag(tag_name, tag_slug):
    tag_name = tag_name.strip()
    if not tag_name:
        return False, 'Название тега должно быть заполнено', None
    
    tag_slug = tag_slug.strip().lower()
    if not tag_slug or not is_valid_slug(tag_slug):
        return False, 'Slug обязателен и может содержать только латинские буквы, цифры и дефис', None
    
    return True, '', {'tag_name': tag_name, 'tag_slug': tag_slug}