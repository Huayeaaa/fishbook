from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import desc, or_
from sqlalchemy.orm import joinedload

from app.constants import DriftStatus
from app.extensions import db
from app.forms.drift import DriftForm
from app.handlers.drift import DriftCollection
from app.models.drift import Drift
from app.models.gift import Gift
from app.models.user import User
from app.models.wish import Wish
from app.utils.email import send_email

from . import web


@web.route("/drift/<int:gift_id>", methods=["GET", "POST"])
@login_required
def send_drift(gift_id):
    current_gift: Gift = (
        Gift.query.options(joinedload(Gift.user)).filter_by(id=gift_id).first()
    )
    if current_gift.is_yourself_gift(current_user.id):
        flash("这本书是你自己的，不能向自己索要书籍")
        return redirect(url_for("web.book_detail", isbn=current_gift.isbn))
    can = current_user.can_send_drift()
    if not can:
        return render_template("not_enough_beans.html", beans=current_user.beans)
    # 同一请求者针对同一本赠送书籍只能发起一次漂流，避免多个 drift 操作同一个 gift/wish 造成数据错乱
    pending_drift = Drift.query.filter_by(
        requester_id=current_user.id,
        gift_id=current_gift.id,
        status=DriftStatus.WAITING.value,
    ).first()
    if pending_drift:
        flash("你已经向该赠送者请求过这本书了，请等待赠送者操作。")
        return redirect(url_for("web.book_detail", isbn=current_gift.isbn))
    gifter = current_gift.user.summary
    form = DriftForm(request.form)
    if request.method == "POST" and form.validate():
        drift_obj = Drift()
        form.populate_obj(drift_obj)
        with db.auto_commit():
            book = current_gift.book
            form.populate_obj(drift)
            drift_obj.gift_id = current_gift.id
            drift_obj.requester_id = current_user.id
            drift_obj.requester_nickname = current_user.nickname
            drift_obj.gifter_nickname = current_gift.user.nickname
            drift_obj.gifter_id = current_gift.user.id
            drift_obj.book_title = book.title
            drift_obj.book_author = book.book_author
            drift_obj.book_img = book.image
            drift_obj.isbn = book.isbn
            current_user.beans -= current_app.config["BEANS_UPLOAD_ONE_BOOK"]
            drift_obj.status = DriftStatus.WAITING.value
            db.session.add(drift_obj)
        send_email(
            current_gift.user.email,
            "有人向你索要一本书",
            "email/get_gift",
            wisher=current_user,
            gift=current_gift,
        )
        return redirect(url_for("web.drift"))

    return render_template(
        "drift.html", gifter=gifter, user_beans=current_user.beans, form=form
    )


@web.route("/drift")
@login_required
def drift():
    drifts = (
        Drift.query.filter(
            or_(
                Drift.requester_id == current_user.id,
                Drift.gifter_id == current_user.id,
            )
        )
        .order_by(desc(Drift.created_at))
        .all()
    )
    drift_collection = DriftCollection(drifts, current_user.id)
    return render_template("drift_center.html", drifts=drift_collection.data)


@web.route("/drift/<int:did>/reject")
@login_required
def reject_drift(did):
    drift_obj = Drift.query.filter_by(gifter_id=current_user.id, id=did).first_or_404()
    with db.auto_commit():
        drift_obj.status = DriftStatus.REJECT.value
        # 拒绝后，把请求者当初消耗的鱼豆退回
        requester = User.query.filter_by(id=drift_obj.requester_id).first()
        if requester:
            requester.beans += current_app.config["BEANS_UPLOAD_ONE_BOOK"]
    return redirect(url_for("web.drift"))


@web.route("/drift/<int:did>/redraw")
@login_required
def redraw_drift(did):
    drift_obj = Drift.query.filter_by(
        requester_id=current_user.id, id=did
    ).first_or_404()
    with db.auto_commit():
        drift_obj.status = DriftStatus.REVOKE.value
        current_user.beans += current_app.config["BEANS_UPLOAD_ONE_BOOK"]
    return redirect(url_for("web.drift"))


@web.route("/drift/<int:did>/mailed")
@login_required
def mailed_drift(did):
    drift_obj = Drift.query.filter_by(gifter_id=current_user.id, id=did).first_or_404()
    with db.auto_commit():
        drift_obj.status = DriftStatus.SUCCESS.value
        # 完成赠与，给赠送者发鱼豆奖励
        current_user.beans += current_app.config["BEANS_EVERY_DRIFT"]
        Gift.query.filter_by(id=drift_obj.gift_id, launched=False).update(launched=True)
        Wish.query.filter_by(
            isbn=drift_obj.isbn, launched=False, uid=drift_obj.requester_id
        ).update(launched=True)
    return redirect(url_for("web.drift"))
