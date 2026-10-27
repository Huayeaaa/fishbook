from app.handlers.book import BookViewModel


class MyGifts:
    def __init__(self, gifts_of_mine, wish_count_list):
        self.gifts = []
        self.gifts_of_mine = gifts_of_mine
        self.wish_count_list = wish_count_list
        self._parse()

    def match_wishes(self, gift):
        count = 0
        for wish_count in self.wish_count_list:
            if gift.isbn == wish_count["isbn"]:
                count = wish_count["count"]
        result = {
            "wishes_count": count,
            "book": BookViewModel(gift.book),
            "id": gift.id,
        }
        return result

    def _parse(self):
        my_gifts = []
        for gift in self.gifts_of_mine:
            result = self.match_wishes(gift)
            my_gifts.append(result)
        self.gifts = my_gifts
