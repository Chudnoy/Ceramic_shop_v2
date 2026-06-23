from flask import get_flashed_messages

def render_flash():
    messages = get_flashed_messages(with_categories=True)
    if not messages:
        return ""
    
    html = ""
    for category, message in messages:
        color = "green" if category == "success" else "red"
        html += f"<div style='color: {color}; border: 1px solid {color}; padding: 10px; margin: 10px 0;'>{message}</div>"
    return html