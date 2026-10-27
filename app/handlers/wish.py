from app.handlers.book import BookViewModel


class MyWishes:
    def __init__(self, wishes_of_mine, gift_count_list):
        self.wishes = []
        self.wishes_of_mine = wishes_of_mine
        self.gift_count_list = gift_count_list
        self._parse()

    def match_wishes(self, gift):
        count = 0
        for gift_count in self.gift_count_list:
            if gift.isbn == gift_count["isbn"]:
                count = gift_count["count"]
        result = {"gifts_count": count, "book": BookViewModel(gift.book), "id": gift.id}
        return result

    def _parse(self):
        my_wishes = []
        for gift in self.wishes_of_mine:
            result = self.match_wishes(gift)
            my_wishes.append(result)
        self.wishes = my_wishes
