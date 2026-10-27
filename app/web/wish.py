from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.handlers.wish import MyWishes
from app.models.gift import Gift
from app.models.wish import Wish
from app.utils.email import send_email

from . import web


@web.route("/my/wish")
@login_required
def my_wish():
    uid = current_user.id
    wishes_of_mine = Wish.get_user_wishes(uid)
    isbn_list = [wish.isbn for wish in wishes_of_mine]
    gift_count_list = Wish.get_gifts_count(isbn_list)
    data = MyWishes(wishes_of_mine, gift_count_list)

    return render_template("my_wish.html", wishes=data.wishes)


@web.route("/wish/book/<isbn>")
@login_required
def save_to_wish(isbn):
    if current_user.can_save_to_list(isbn):
        with db.auto_commit():
            wish = Wish()
            wish.isbn = isbn
            wish.uid = current_user.id
            db.session.add(wish)
    else:
        flash("这本书已存在于你的赠送清单或心愿清单，请不要重复添加")
    return redirect(url_for("web.book_detail", isbn=isbn))


@web.route("/satisfy/wish/<int:wid>")
@login_required
def satisfy_wish(wid):
    wish: Wish = Wish.query.options(joinedload(Wish.user)).filter_by(id=wid).first()
    gift = Gift.query.filter_by(uid=current_user.id, isbn=wish.isbn).first()
    if not gift:
        flash(
            "你还没有上传此书，请点击<加入到赠送清单>添加此书，添加前请确保可以赠送此书！"
        )
    else:
        send_email(
            wish.user.email,
            "有人向你赠送一本书",
            "email/satisfy_wish",
            wish=wish,
            gift=gift,
        )
        flash("已向Ta发送了一封邮件，如果Ta愿意接受你的赠送，你将收到一个鱼漂。")
    return redirect(url_for("web.book_detail", isbn=wish.isbn))


@web.route("/wish/book/<isbn>/redraw")
@login_required
def redraw_from_wish(isbn):
    wish = Wish.query.filter_by(isbn=isbn, launched=False).first_or_404()
    with db.auto_commit():
        wish.delete()
    return redirect(url_for("web.my_wish"))
