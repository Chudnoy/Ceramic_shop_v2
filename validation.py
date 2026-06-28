def validate_review(name, rating_str, comment):
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