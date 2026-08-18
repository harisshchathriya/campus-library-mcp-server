import sqlite3

connection = sqlite3.connect("data/library.db")
connection.row_factory = sqlite3.Row

books = connection.execute(
    """
    SELECT
        id,
        title,
        author,
        category,
        total_copies,
        available_copies
    FROM books
    ORDER BY id
    """
).fetchall()

for book in books:
    print(
        f"{book['id']}. {book['title']} | "
        f"{book['author']} | "
        f"{book['category']} | "
        f"Available: {book['available_copies']}/{book['total_copies']}"
    )

connection.close()