from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    book_author: Mapped[str] = mapped_column(String(128), nullable=False)
    binding: Mapped[str] = mapped_column(String(32), nullable=False)
    publisher: Mapped[str] = mapped_column(String(128), nullable=False)
    price: Mapped[str] = mapped_column(String(32), nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    pubdate: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    isbn: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    image: Mapped[str] = mapped_column(String(128), nullable=False)
