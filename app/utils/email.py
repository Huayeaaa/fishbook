from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from app.extensions import mail


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error("发送邮件失败: %s", e)
            raise


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        "[鱼书]" + " " + subject,
        sender=app.config["MAIL_DEFAULT_SENDER"],
        recipients=[to],
    )
    msg.html = render_template(template + ".html", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
