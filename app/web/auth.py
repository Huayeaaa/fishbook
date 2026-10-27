from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms.auth import (
    ChangePasswordForm,
    EmailForm,
    LoginForm,
    RegisterForm,
    ResetPasswordForm,
)
from app.models.user import User
from app.utils.email import send_email

from . import web


@web.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        user = User()
        user.set_attrs(form.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, False)
        return redirect(url_for("web.index"))
    return render_template("auth/register.html", form=form)


@web.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            target: str = request.args.get("next")
            if not target or not target.startswith("/"):
                target = url_for("web.index")
            return redirect(target)
        else:
            flash("账号不存在或密码错误", category="login_error")
    return render_template("auth/login.html", form=form)


@web.route("/reset/password", methods=["GET", "POST"])
def forget_password_request():
    if request.method == "POST":
        form = EmailForm(request.form)
        if form.validate():
            account_email = form.email.data
            user = User.query.filter_by(email=account_email).first_or_404()
            send_email(
                form.email.data,
                "重置你的密码",
                "email/reset_password",
                user=user,
                token=user.generate_token(),
            )
            flash("一封邮件已发送到邮箱" + account_email + "，请及时查收")
            return redirect(url_for("web.login"))
    return render_template("auth/forget_password_request.html")


@web.route("/reset/password/<token>", methods=["GET", "POST"])
def forget_password(token):
    # 重置密码完全基于 token 校验用户身份，与当前登录态无关，无需任何会话判断
    form = ResetPasswordForm(request.form)
    if request.method == "POST" and form.validate():
        result = User.reset_password(token, form.password1.data)
        if result is True:
            flash("你的密码已更新,请使用新密码登录")
            return redirect(url_for("web.login"))
        elif result == "expired":
            flash("重置链接已过期，请重新获取重置邮件")
            return redirect(url_for("web.forget_password_request"))
        else:
            flash("重置链接无效，请重新获取重置邮件")
            return redirect(url_for("web.login"))
    return render_template("auth/forget_password.html")


@web.route("/change/password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == "POST" and form.validate():
        current_user.password = form.new_password1.data
        db.session.commit()
        flash("密码已更新成功")
        return redirect(url_for("web.personal"))
    return render_template("auth/change_password.html", form=form)


@web.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("web.index"))
