import os
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'uploads')

def save_uploaded_image(file):
	if not file or not file.filename:
		return ''
	
	filename = f'{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}'

	disk_path = os.path.join(UPLOAD_FOLDER, filename)
	db_path = f'/static/uploads/{filename}'

	file.save(disk_path)

	return db_path