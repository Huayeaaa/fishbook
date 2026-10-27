from datetime import datetime

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db


class Base(db.Model):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    def set_attrs(self, attrs):
        for key, value in attrs.items():
            if hasattr(self, key) and key != "id":
                setattr(self, key, value)

    def delete(self):
        self.is_deleted = True
