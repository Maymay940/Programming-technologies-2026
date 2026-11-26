from datetime import datetime, timezone
from sqlalchemy import (DateTime, ForeignKey, Integer, String, Text)
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

class LibraryRequest(Base):
    __tablename__ = "library_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(30))
    summary: Mapped[str] = mapped_column(Text)
    book_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reader_card: Mapped[str | None] = mapped_column(String(100), nullable=True)
    requested_period: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    book_id: Mapped[int | None] = mapped_column(ForeignKey("books.id"), nullable=True)
    match_status: Mapped[str] = mapped_column(String(20), nullable=False)