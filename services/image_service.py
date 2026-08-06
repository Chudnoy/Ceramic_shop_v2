import os
import uuid

from werkzeug.utils import secure_filename

IMAGE_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(IMAGE_SERVICE_DIR)

UPLOAD_FOLDER = os.path.join(PROJECT_DIR, "static", "uploads")
UPLOAD_URL = "/static/uploads/"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}


def is_allowed_image(filename):
    """
    Проверяет, что имя файла имеет разрешённое расширение изображения.

    Возвращает True для файлов с расширениями jpg, jpeg, png, webp и gif.
    Если у файла нет расширения или расширение не входит в список разрешённых, возвращает False.
    """
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def save_image(file):
    """
    Сохраняет загруженное изображение товара в папку static/uploads.

    Если файл не передан или имя файла пустое, возвращает пустую строку.
    Проверяет расширение файла, создаёт папку uploads при необходимости,
    генерирует безопасное уникальное имя файла, сохраняет изображение на диск
    и возвращает путь для сохранения в базе данных
    """
    if not file or not file.filename:
        return True, "", ""

    if not is_allowed_image(file.filename):
        return False, "Недопустимый формат изображения", None

    safe_filename = secure_filename(file.filename)

    if not safe_filename:
        return False, "Некорректное имя файла", None

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    filename = f"{uuid.uuid4().hex[:8]}_{safe_filename}"

    disk_path = os.path.join(UPLOAD_FOLDER, filename)
    db_path = f"{UPLOAD_URL}{filename}"

    file.save(disk_path)

    return True, "", db_path


def delete_image(img_path):
    """
    Удаляет изображение товара из папки static/uploads.

    Удаляет только файлы, путь которых начинается с UPLOAD_URL, чтобы не трогать
    статические изображения из основной папки static/img. Если файла на диске нет
    или путь пустой, функция ничего не делает.
    """
    if not img_path or not img_path.startswith(UPLOAD_URL):
        return

    filename = os.path.basename(img_path)

    if not filename:
        return

    disk_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(disk_path):
        os.remove(disk_path)
