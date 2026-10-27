from flask import current_app
from flask_login import UserMixin
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from app.constants import DriftStatus
from app.extensions import db, login_manager
from app.handlers.book import YuShuBook
from app.models.base import Base
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.wish import Wish
from app.utils.helper import is_isbn_or_key


class User(UserMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(32), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(18), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # 鱼豆
    beans: Mapped[float] = mapped_column(Float, default=0)
    # 送出去的书本数量
    send_counter: Mapped[int] = mapped_column(Integer, default=0)
    # 收到的书本的数量
    receive_counter: Mapped[int] = mapped_column(Integer, default=0)
    wx_open_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    wx_name: Mapped[str | None] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(255))

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw)

    def generate_token(self):
        s = Serializer(current_app.config["SECRET_KEY"])
        return s.dumps({"id": self.id})

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, max_age=9000)
        except SignatureExpired:
            # token 超过有效期
            return "expired"
        except BadSignature:
            # 签名被篡改或 token 格式错误
            return False
        user = User.query.filter_by(id=data.get("id")).first()
        if not user:
            return False
        user.password = new_password
        db.session.commit()
        return True

    def can_save_to_list(self, isbn: str):
        if is_isbn_or_key(isbn) != "isbn":
            return False
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(isbn)
        if not yushu_book.first:
            return False
        # 不允许一个用户同时赠送多本相同的书
        # 一个用户不可能同时成为赠送者和索要者
        # 总结： 既不在赠送清单，也不在心愿清单才能添加
        in_gift = Gift.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()
        in_wish = Wish.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()
        if not in_gift and not in_wish:
            return True
        return False

    def can_send_drift(self):
        if self.beans < 1:
            return False
        success_gifts_count = Gift.query.filter_by(uid=self.id, launched=True).count()
        success_wishes_count = Drift.query.filter_by(
            requester_id=self.id, status=DriftStatus.SUCCESS.value
        ).count()
        # 每索取两本书，自身必须送出一本
        return success_wishes_count // 2 <= success_gifts_count

    @property
    def summary(self):
        return dict(
            nickname=self.nickname,
            beans=self.beans,
            email=self.email,
            send_receive=str(self.send_counter) + "/" + str(self.receive_counter),
        )


@login_manager.user_loader
def get_user(uid):
    return User.query.get(int(uid))
