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