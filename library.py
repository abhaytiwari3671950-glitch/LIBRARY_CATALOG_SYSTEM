"""Catalog management operations."""
from book import Book, ReferenceBook


class LibraryCatalog:
    """Store and manage books by unique integer ID."""

    def __init__(self):
        self.books = {}
        self._next_id = 101

    def generate_book_id(self):
        while self._next_id in self.books:
            self._next_id += 1
        result = self._next_id
        self._next_id += 1
        return result

    def add_book(self, book):
        if not isinstance(book, Book):
            print('Error: Only Book objects can be added.')
            return False
        if type(book.book_id) is not int or book.book_id <= 0:
            print('Error: Invalid book ID.')
            return False
        if book.book_id in self.books:
            print(f'Error: Book ID {book.book_id} already exists.')
            return False
        self.books[book.book_id] = book
        self._next_id = max(self._next_id, book.book_id + 1)
        print(f'Book added successfully! ID: {book.book_id}')
        return True

    def _get_book(self, book_id):
        if type(book_id) is not int or book_id <= 0:
            print('Error: Book ID must be a positive integer.')
            return None
        book = self.books.get(book_id)
        if book is None:
            print(f'Error: No book found with ID {book_id}.')
        return book

    def remove_book(self, book_id):
        book = self._get_book(book_id)
        if book is None:
            return False
        if not book.check_availability():
            print('Error: Borrowed books cannot be removed.')
            return False
        del self.books[book_id]
        print(f'Book {book_id} removed successfully.')
        return True

    def _search(self, field, query):
        if not isinstance(query, str) or not query.strip():
            print('Error: Search text cannot be empty.')
            return []
        matches = [book for book in self.books.values()
                   if query.strip().casefold() in getattr(book, field).casefold()]
        if not matches:
            print('No matching books found.')
        else:
            self._display_books(matches)
        return matches

    def search_by_title(self, title):
        return self._search('title', title)

    def search_by_author(self, author):
        return self._search('author', author)

    @staticmethod
    def _display_books(books):
        for book in books:
            print('-' * 60)
            book.display_details()
        print('-' * 60)

    def display_all_books(self):
        if not self.books:
            print('The library catalog is empty.')
            return
        self._display_books(list(self.books.values()))

    def display_available_books(self):
        available = [book for book in self.books.values() if book.check_availability()]
        if not available:
            print('No books are currently available.')
            return
        self._display_books(available)
        print('Note: Reference books are available for in-library use only.')

    def check_book_availability(self, book_id):
        book = self._get_book(book_id)
        if book is None:
            return None
        if isinstance(book, ReferenceBook):
            print(f'{book.title}: Available (In-library use only; cannot be borrowed).')
        elif book.check_availability():
            print(f'{book.title}: Available for borrowing.')
        else:
            print(f'{book.title}: Currently borrowed.')
        return book.check_availability()

    def borrow_book(self, book_id):
        book = self._get_book(book_id)
        return book.borrow_book() if book is not None else False

    def return_book(self, book_id):
        book = self._get_book(book_id)
        return book.return_book() if book is not None else False
