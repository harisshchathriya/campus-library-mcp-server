import sqlite3

DATABASE_PATH = "data/library.db"


BOOKS = [
    (
        "Python Crash Course",
        "Eric Matthes",
        "Programming",
        "9781593279288",
        5,
        3,
    ),
    (
        "Clean Code",
        "Robert C. Martin",
        "Programming",
        "9780132350884",
        4,
        2,
    ),
    (
        "Database System Concepts",
        "Abraham Silberschatz",
        "Database",
        "9780078022159",
        6,
        4,
    ),
    (
        "Computer Networks",
        "Andrew S. Tanenbaum",
        "Networking",
        "9780132126953",
        5,
        1,
    ),
    (
        "Operating System Concepts",
        "Abraham Silberschatz",
        "Operating Systems",
        "9781119456339",
        5,
        0,
    ),
    (
        "Artificial Intelligence: A Modern Approach",
        "Stuart Russell",
        "Artificial Intelligence",
        "9780134610993",
        4,
        2,
    ),
    (
        "Design Patterns",
        "Erich Gamma",
        "Software Engineering",
        "9780201633610",
        3,
        1,
    ),
    (
        "Hands-On Machine Learning",
        "Aurélien Géron",
        "Machine Learning",
        "9781098125974",
        5,
        4,
    ),
    (
        "Data Structures and Algorithms in Python",
        "Michael T. Goodrich",
        "Data Structures",
        "9781118290279",
        4,
        3,
    ),
    (
        "Computer Organization and Design",
        "David A. Patterson",
        "Computer Architecture",
        "9780128201091",
        3,
        2,
    ),
]


def seed_database() -> None:
    connection = sqlite3.connect(DATABASE_PATH)

    connection.executemany(
        """
        INSERT OR IGNORE INTO books (
            title,
            author,
            category,
            isbn,
            total_copies,
            available_copies
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        BOOKS,
    )

    connection.commit()
    connection.close()

    print(f"Seeded {len(BOOKS)} library books.")


if __name__ == "__main__":
    seed_database()