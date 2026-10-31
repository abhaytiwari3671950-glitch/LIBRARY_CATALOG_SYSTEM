"""Book models demonstrating inheritance and polymorphism."""


class Book:
    """Represent one physical book in the catalog."""

    def __init__(self, book_id, title, author, genre, is_available=True):
        if type(book_id) is not int or book_id <= 0:
            raise ValueError('Book ID must be a positive integer.')
        for label, value in [('Title', title), ('Author', author), ('Genre', genre)]:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f'{label} cannot be empty.')
        if type(is_available) is not bool:
            raise TypeError('Availability must be a Boolean.')
        self.book_id = book_id
        self.title = title.strip()
        self.author = author.strip()
        self.genre = genre.strip()
        self._is_available = is_available

    @property
    def is_available(self):
        return self._is_available

    @property
    def book_type(self):
        return 'Book'

    def check_availability(self):
        return self._is_available

    def update_availability(self, status):
        if type(status) is not bool:
            raise TypeError('Availability status must be True or False.')
        self._is_available = status

    def borrow_book(self):
        if not self.check_availability():
            print('This book is already borrowed.')
            return False
        self.update_availability(False)
        print(f'Successfully borrowed: {self.title}')
        return True

    def return_book(self):
        if self.check_availability():
            print('This book is already available; it cannot be returned.')
            return False
        self.update_availability(True)
        print(f'Successfully returned: {self.title}')
        return True

    def display_details(self):
        status = 'Available' if self.check_availability() else 'Borrowed'
        print(f'ID: {self.book_id} | Title: {self.title} | Author: {self.author}')
        print(f'Genre: {self.genre} | Type: {self.book_type} | Status: {status}')


class FictionBook(Book):
    """A fiction title with a specific fiction genre."""

    def __init__(self, book_id, title, author, genre, fiction_genre, is_available=True):
        super().__init__(book_id, title, author, genre, is_available)
        if not isinstance(fiction_genre, str) or not fiction_genre.strip():
            raise ValueError('Fiction genre cannot be empty.')
        self.fiction_genre = fiction_genre.strip()

    @property
    def book_type(self):
        return 'Fiction'

    def display_details(self):
        super().display_details()
        print(f'Fiction genre: {self.fiction_genre}')


class NonFictionBook(Book):
    """A non-fiction title with a subject area."""

    def __init__(self, book_id, title, author, genre, subject_area, is_available=True):
        super().__init__(book_id, title, author, genre, is_available)
        if not isinstance(subject_area, str) or not subject_area.strip():
            raise ValueError('Subject area cannot be empty.')
        self.subject_area = subject_area.strip()

    @property
    def book_type(self):
        return 'Non-Fiction'

    def display_details(self):
        super().display_details()
        print(f'Subject area: {self.subject_area}')


class ReferenceBook(Book):
    """A reference title that cannot leave the library."""

    def __init__(self, book_id, title, author, genre, reference_category):
        super().__init__(book_id, title, author, genre, True)
        if not isinstance(reference_category, str) or not reference_category.strip():
            raise ValueError('Reference category cannot be empty.')
        self.reference_category = reference_category.strip()

    @property
    def book_type(self):
        return 'Reference'

    def update_availability(self, status):
        if type(status) is not bool:
            raise TypeError('Availability status must be True or False.')
        if not status:
            raise ValueError('Reference books must remain available for in-library use.')
        super().update_availability(True)

    def borrow_book(self):
        print('Reference books cannot be borrowed. In-library use only.')
        return False

    def display_details(self):
        super().display_details()
        print(f'Reference category: {self.reference_category} | In-library use only')
