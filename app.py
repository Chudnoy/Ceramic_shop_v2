from flask import Flask, session 
from db import init_db
from routes.admin import admin_bp
from routes.main import main_bp
from datetime import timedelta
import os
from dotenv import load_dotenv
from services.cart_service import get_cart_count

load_dotenv()

init_db()


app = Flask(__name__)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)
app.permanent_session_lifetime = timedelta(minutes=30)
app.secret_key = os.environ.get('SECRET_KEY', 'def-secret-key')

@app.context_processor
def inject_cart_count():
    return {"cart_count": get_cart_count(session)}
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)