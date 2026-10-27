import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()
mysql_username = os.environ.get("MYSQL_USERNAME", "root")
mysql_password = os.environ.get("MYSQL_PASSWORD", "")
mysql_host = os.environ.get("MYSQL_HOST", "localhost")
mysql_port = os.environ.get("MYSQL_PORT", 3306)

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/fishbook"
SECRET_KEY = os.environ.get("SECRET_KEY", "")


# Email 配置
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TSL = False
MAIL_USERNAME = "1151627903@qq.com"
# 请自备邮箱授权码
MAIL_PASSWORD = "zdynuiiegugchkfc"
MAIL_DEFAULT_SENDER = "Jason<1151627903@qq.com>"

# 开启数据库查询性能测试
SQLALCHEMY_RECORD_QUERIES = True

# 性能测试的阀值
DATABASE_QUERY_TIMEOUT = 0.5

SQLALCHEMY_TRACK_MODIFICATIONS = True

WTF_CSRF_CHECK_DEFAULT = False

SQLALCHEMY_ECHO = True


REMEMBER_COOKIE_DURATION = timedelta(days=30)


RECENT_BOOK_PER_PAGE = 60

BEANS_EVERY_DRIFT = 1

BEANS_UPLOAD_ONE_BOOK = 0.5
