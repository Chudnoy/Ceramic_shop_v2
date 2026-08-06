from validation import validate_tag


def process_tag_form(form):
    tag_name = form.get("tag_name", "")
    tag_slug = form.get("tag_slug", "")

    is_valid_tag, error_message, tag_data = validate_tag(tag_name, tag_slug)

    if not is_valid_tag:
        return False, error_message, None

    return True, "", tag_data
