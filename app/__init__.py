from flask import Flask

from app.extensions import login_manager
from app.models.base import db
from app.utils.email import mail


def register_web_blueprint(app: Flask):
    from app.web import web

    app.register_blueprint(web)


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object("app.settings")

    # 注册SQLAlchemy
    db.init_app(app)

    # 注册email模块
    mail.init_app(app)

    # 注册login模块
    login_manager.init_app(app)
    login_manager.login_view = "web.login"
    login_manager.login_message = "请先登录或注册"

    # 注册蓝图
    register_web_blueprint(app)

    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith(".py"):
            app.config.from_pyfile(config)
    return app
