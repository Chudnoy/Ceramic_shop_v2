import re


def validate_review(name, rating_str, comment):
    """
Валидирует данные формы отзыва.

Проверяет, что имя заполнено, оценка является числом от 1 до 5, а комментарий
не превышает допустимую длину. Возвращает флаг успеха, сообщение об ошибке и
очищенные данные отзыва.
"""
    name = name.strip()
    comment = comment.strip() if comment else ""
    
    if not name:
        return False, "Имя обязательно для заполнения", {}
        
    try:
        rating = int(rating_str)
        if rating < 1 or rating > 5:
            raise ValueError
    except (ValueError, TypeError):
        return False, "Оценка должна быть числом от 1 до 5", {}
    
    if len(comment) > 1000:
        return False, "Длина комментария не должна превышать 1000 символов", {}
        
    return True, "", {"name": name, "rating": rating, "comment": comment}
    
    
def validate_product(name, price, description, category_id):
    """
Валидирует основные данные товара.

Проверяет наличие названия и описания, преобразует цену в целое положительное
число и проверяет корректность category_id. Возвращает флаг успеха, сообщение
об ошибке и очищенные данные товара без статуса.
"""
    name = name.strip()
    if not name:
        return False, "Имя обязательно для заполнения", {}
        
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
        category_id = int(category_id)
    except (TypeError, ValueError):
        return False, "Некорректный ID категории", {}
        
    return True, "", {"name": name, "price": price, "description": description, "category_id": category_id}


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