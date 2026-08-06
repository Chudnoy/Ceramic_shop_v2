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
