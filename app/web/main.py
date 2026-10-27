from flask import render_template
from flask_login import current_user, login_required

from app.handlers.book import BookViewModel
from app.models.gift import Gift

from . import web


@web.route("/")
def index():
    gift_list = Gift.recent()
    books = [BookViewModel(gift.book) for gift in gift_list]
    return render_template("index.html", recent=books)


@web.route("/personal")
@login_required
def personal_center():
    return render_template("personal.html", user=current_user.summary)
