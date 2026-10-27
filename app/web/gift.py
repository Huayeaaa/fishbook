from flask import current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.constants import DriftStatus
from app.extensions import db
from app.handlers.gift import MyGifts
from app.models.drift import Drift
from app.models.gift import Gift

from . import web


@web.route("/my/gifts")
@login_required
def my_gifts():
    uid = current_user.id
    gifts_of_mine = Gift.get_user_gifts(uid)
    isbn_list = [gift.isbn for gift in gifts_of_mine]
    wish_count_list = Gift.get_wishes_count(isbn_list)
    data = MyGifts(gifts_of_mine, wish_count_list)
    return render_template("my_gifts.html", gifts=data.gifts)


@web.route("/gifts/book/<isbn>")
@login_required
def save_to_gifts(isbn):
    if current_user.can_save_to_list(isbn):
        with db.auto_commit():
            gift = Gift()
            gift.isbn = isbn
            gift.uid = current_user.id
            current_user.beans += current_app.config["BEANS_UPLOAD_ONE_BOOK"]
            db.session.add(gift)
    else:
        flash("这本书已存在于你的赠送清单或心愿清单，请不要重复添加")
    return redirect(url_for("web.book_detail", isbn=isbn))


@web.route("/gifts/<gift_id>/redraw")
@login_required
def redraw_from_gifts(gift_id):
    gift = Gift.query.filter_by(id=gift_id, launched=False).first()
    drift = Drift.query.filter_by(
        gift_id=gift_id, status=DriftStatus.WAITING.value
    ).first()
    if drift:
        flash("这个礼物正处于交易状态，请先往鱼漂完成该交易")
    else:
        with db.auto_commit():
            current_user.beans -= current_app.config["BEANS_UPLOAD_ONE_BOOK"]
            gift.delete()
    return redirect(url_for("web.my_gifts"))
