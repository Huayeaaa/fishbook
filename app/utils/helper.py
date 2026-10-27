def is_isbn_or_key(word: str):
    if len(word) == 13 and word.isdigit():
        return "isbn"
    if "-" in word and len(word.replace("-", "")) == 10:
        return "isbn"
    return "keyword"
