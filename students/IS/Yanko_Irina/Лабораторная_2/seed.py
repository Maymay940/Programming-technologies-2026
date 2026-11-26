from sqlalchemy import select
from database import Base, SessionLocal, engine
from models import Book

BOOKS = [
    ("BK-118", "Лето в пионерском галстуке"),
    ("BK-205", "Всё закончится на нас"),
    ("BK-310", "Шестёрка воронов"),
    ("BK-407", "Четвёртое крыло"),
    ("BK-512", "Гипотеза любви"),
]

def main():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        for code, title in BOOKS:
            existing = db.scalar(
                select(Book).where(Book.code == code)
            )
            if existing is None:
                db.add(Book(code=code, title=title))
        db.commit()

    print("справочник заполнен")


if __name__ == "__main__":
    main()
