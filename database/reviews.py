from database.connection import get_db_connection

def get_reviews_by_product(product_id):
    """
Возвращает все отзывы для указанного товара.

Принимает product_id, ищет связанные с ним записи в таблице reviews и возвращает
их в порядке от новых к старым. Используется на странице товара для вывода блока
отзывов.
"""
    conn = get_db_connection()
    reviews = conn.execute("SELECT * FROM reviews WHERE product_id = ? ORDER BY created_at DESC", (product_id,)).fetchall()
    conn.close()
    return reviews
    
    
def add_review_db(product_id, name, rating, comment):
    """
Добавляет новый отзыв к товару в таблицу reviews.

Принимает id товара, имя автора, оценку и текст комментария. Функция предполагает,
что данные уже прошли валидацию до вызова, и только сохраняет их в базу данных.
"""
    conn = get_db_connection()
    conn.execute("INSERT INTO reviews (product_id, name, rating, comment) VALUES (?, ?, ?, ?)", (product_id, name, rating, comment))
    conn.commit()
    conn.close()