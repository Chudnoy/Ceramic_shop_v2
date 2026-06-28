from validation import validate_product

def process_product_form(form):
    name = form.get("name", "").strip()
    description = form.get("description", "").strip()
    price = form.get("price", 0)
    category_id = form.get("category_id")
        
    is_valid, error_message, cleaned_data = validate_product(name, price, description, category_id)
    
    if not is_valid:
        return False, error_message, None
        
    return True, "", cleaned_data