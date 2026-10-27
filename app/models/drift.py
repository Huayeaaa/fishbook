from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Drift(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 邮寄信息
    recipient_name: Mapped[str] = mapped_column(String(32), nullable=False)
    address: Mapped[str] = mapped_column(String(128), nullable=False)
    message: Mapped[str] = mapped_column(String(128), nullable=False)
    mobile: Mapped[str] = mapped_column(String(32), nullable=False)
    # 书籍信息
    isbn: Mapped[str] = mapped_column(String(32), nullable=False)
    book_title: Mapped[str] = mapped_column(String(64), nullable=False)
    book_author: Mapped[str] = mapped_column(String(64), nullable=False)
    book_img: Mapped[str] = mapped_column(String(128), nullable=False)
    # 请求者信息
    requester_id: Mapped[int] = mapped_column(Integer)
    requester_nickname: Mapped[str] = mapped_column(String(32), nullable=False)
    # 赠送者信息
    gift_id: Mapped[int] = mapped_column(Integer)
    gifter_id: Mapped[int] = mapped_column(Integer)
    gifter_nickname: Mapped[str] = mapped_column(String(32), nullable=False)
    # 交易状态
    status: Mapped[str] = mapped_column(String(32), nullable=False)
