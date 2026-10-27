from typing import List

from flask import current_app
from sqlalchemy import Boolean, ForeignKey, Integer, String, desc, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.handlers.book import YuShuBook
from app.models.base import Base


class Gift(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    isbn: Mapped[str] = mapped_column(String(32), nullable=False)
    launched: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User")

    def is_yourself_gift(self, uid):
        return True if self.uid == uid else False

    @classmethod
    def recent(cls):
        recent_gift_list = (
            cls.query.filter_by(launched=False)
            .order_by(desc(cls.created_at))
            .group_by(cls.isbn)
            .limit(current_app.config["RECENT_BOOK_PER_PAGE"])
            .distinct()
            .all()
        )
        return recent_gift_list

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def get_user_gifts(cls, uid):
        return (
            cls.query.filter_by(uid=uid, launched=False)
            .order_by(desc(cls.created_at))
            .all()
        )

    @classmethod
    def get_wishes_count(cls, isbn_list: List[str]):
        from app.models.wish import Wish

        wishes = (
            db.session.query(func.count(Wish.id), Wish.isbn)
            .filter(
                Wish.launched.is_(False),
                Wish.isbn.in_(isbn_list),
                Wish.is_deleted.is_(False),
            )
            .group_by(Wish.isbn)
            .all()
        )
        count_list = [{"count": wish[0], "isbn": wish[1]} for wish in wishes]
        return count_list
