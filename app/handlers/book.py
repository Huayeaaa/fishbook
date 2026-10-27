from typing import List, Optional

from sqlalchemy import or_

from app.models.book import Book


class BookViewModel:
    """把数据库中的 Book 模型转换为模板需要的字段"""

    def __init__(self, book):
        self.title = book.title
        self.author = book.book_author
        self.binding = book.binding
        self.publisher = book.publisher
        self.image = book.image
        self.price = "￥" + book.price if book.price else book.price
        self.isbn = book.isbn
        self.pubdate = book.pubdate
        self.summary = book.summary
        self.pages = book.pages

    @property
    def intro(self):
        intros = filter(
            lambda x: True if x else False, [self.author, self.publisher, self.price]
        )
        return " / ".join(intros)


class BookCollection:
    """搜索结果集合，直接交给模板渲染"""

    def __init__(self):
        self.total: int = 0
        self.books: List[Book] = []
        self.keyword: Optional[str] = None

    def fill(self, yushu_book, keyword):
        self.total = yushu_book.total
        self.books = [BookViewModel(book) for book in yushu_book.books]
        self.keyword = keyword


class YuShuBook:
    """负责从数据库查询数据"""

    per_page = 15  # 与前端 search_result.js 的分页计算保持一致

    def __init__(self):
        self.total: int = 0
        self.books: List[Book] = []

    def search_by_isbn(self, isbn):
        """按 ISBN 精准查询单本"""
        book = Book.query.filter_by(isbn=isbn).first()
        self.fill_single(book)

    def search_by_keyword(self, keyword, page=1):
        """按关键字模糊匹配：书名 或 作者，二者为或的关系"""
        pagination = Book.query.filter(
            or_(
                Book.title.like("%" + keyword + "%"),
                Book.book_author.like("%" + keyword + "%"),
            )
        ).paginate(page=page, per_page=self.per_page, error_out=False)
        self.total = pagination.total
        self.books = pagination.items

    @property
    def first(self) -> Optional[Book]:
        for book in self.books:
            return book
        return None

    def fill_single(self, data: Book):
        """填充单本"""
        if data:
            self.total = 1
            self.books.append(data)
