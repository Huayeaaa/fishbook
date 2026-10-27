from typing import List

from sqlalchemy import Boolean, ForeignKey, Integer, String, desc, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.handlers.book import YuShuBook
from app.models.base import Base


class Wish(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    isbn: Mapped[str] = mapped_column(String(32), nullable=False)
    launched: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User")

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def get_user_wishes(cls, uid):
        return (
            cls.query.filter_by(uid=uid, launched=False)
            .order_by(desc(cls.created_at))
            .all()
        )

    @classmethod
    def get_gifts_count(cls, isbn_list: List[str]):
        from app.models.gift import Gift

        gifts = (
            db.session.query(func.count(Gift.id), Gift.isbn)
            .filter(
                Gift.launched.is_(False),
                Gift.isbn.in_(isbn_list),
                Gift.is_deleted.is_(False),
            )
            .group_by(Gift.isbn)
            .all()
        )
        count_list = [{"count": gift[0], "isbn": gift[1]} for gift in gifts]
        return count_list
