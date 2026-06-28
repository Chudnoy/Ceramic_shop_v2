import os
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'uploads')
UPLOAD_URL = "/static/uploads/"

def save_image(file):
	if not file or not file.filename:
		return ''
	
	filename = f'{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}'

	disk_path = os.path.join(UPLOAD_FOLDER, filename)
	db_path = f'{UPLOAD_URL}{filename}'

	file.save(disk_path)

	return db_path


def delete_image(img_path):
    if not img_path or not img_path.startswith(UPLOAD_URL):
        return 
    
    filename = os.path.basename(img_path)
    disk_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(disk_path):
        os.remove(disk_path)