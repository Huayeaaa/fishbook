from contextlib import contextmanager
from typing import Any

from flask import current_app
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask_sqlalchemy.query import Query


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self, throw=True):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            current_app.logger.exception(f"{e!r}")
            if throw:
                raise e


class SoftDeleteQuery(Query):
    def filter_by(self, **kwargs: Any):
        if "is_deleted" not in kwargs:
            kwargs["is_deleted"] = False
        return super().filter_by(**kwargs)


db = SQLAlchemy(query_class=SoftDeleteQuery)
mail = Mail()
login_manager = LoginManager()
