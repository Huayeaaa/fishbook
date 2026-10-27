from flask import flash, render_template, request
from flask_login import current_user
from sqlalchemy.orm import joinedload

from app.forms.book import SearchForm
from app.handlers.book import BookCollection, BookViewModel, YuShuBook
from app.utils.helper import is_isbn_or_key

from ..handlers.trade import TradeInfo
from ..models import Gift, Wish
from . import web


@web.route("/book/search", methods=["GET", "POST"])
def search():
    """
    书籍搜索接口
    :return:
    """
    form = SearchForm(request.args)
    books = BookCollection()
    if form.validate():
        q = form.q.data.strip()
        page = form.page.data
        yushu_book = YuShuBook()
        if is_isbn_or_key(q) == "isbn":
            # 1、按 ISBN 精准搜索
            yushu_book.search_by_isbn(q)
        else:
            # 2、按关键字模糊匹配：作者 或 书名（或的关系）
            yushu_book.search_by_keyword(q, page)
        # 3、通过 BookCollection 输出到模板
        books.fill(yushu_book, q)
    else:
        flash("搜索关键字不合法，请重新输入")
    return render_template("search_result.html", books=books, form=form)


@web.route("/book/<isbn>/detail")
def book_detail(isbn):
    has_in_gifts = False
    has_in_wishes = False
    yushu_book = YuShuBook()
    yushu_book.search_by_isbn(isbn)
    book = BookViewModel(yushu_book.first)

    if current_user.is_authenticated:
        has_in_gifts = (
            Gift.query.filter_by(isbn=isbn, uid=current_user.id, launched=False).first()
            is not None
        )
        has_in_wishes = (
            Wish.query.filter_by(isbn=isbn, uid=current_user.id, launched=False).first()
            is not None
        )

    trade_gifts = (
        Gift.query.options(joinedload(Gift.user))
        .filter_by(isbn=isbn, launched=False)
        .all()
    )
    trade_wishes = (
        Wish.query.options(joinedload(Wish.user))
        .filter_by(isbn=isbn, launched=False)
        .all()
    )

    trade_wishes_model = TradeInfo(trade_wishes)
    trade_gifts_model = TradeInfo(trade_gifts)
    return render_template(
        "book_detail.html",
        book=book,
        has_in_gifts=has_in_gifts,
        has_in_wishes=has_in_wishes,
        wishes=trade_wishes_model,
        gifts=trade_gifts_model,
    )
