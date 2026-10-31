"""Unit tests for the Library Catalog System."""
import unittest
from contextlib import redirect_stdout
from io import StringIO
from book import Book, FictionBook, NonFictionBook, ReferenceBook
from library import LibraryCatalog
from main import create_sample_catalog


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = LibraryCatalog()
        self.fiction = FictionBook(101, 'Alpha Story', 'Alice Writer', 'Literature', 'Fantasy')
        self.nonfiction = NonFictionBook(102, 'Science Facts', 'Bob Scientist', 'Education', 'Physics')
        self.reference = ReferenceBook(103, 'Dictionary', 'Oxford', 'Language', 'Dictionary')

    def quiet(self, function, *args):
        with redirect_stdout(StringIO()):
            return function(*args)

    def test_book_creation(self):
        book = Book(1, 'Title', 'Author', 'Genre')
        self.assertTrue(book.check_availability())

    def test_fiction_inheritance(self):
        self.assertIsInstance(self.fiction, Book)
        self.assertEqual(self.fiction.fiction_genre, 'Fantasy')

    def test_nonfiction_inheritance(self):
        self.assertIsInstance(self.nonfiction, Book)
        self.assertEqual(self.nonfiction.subject_area, 'Physics')

    def test_reference_restriction(self):
        self.assertFalse(self.quiet(self.reference.borrow_book))
        self.assertTrue(self.reference.check_availability())
        with self.assertRaises(ValueError):
            self.reference.update_availability(False)

    def test_add_book(self):
        self.assertTrue(self.quiet(self.catalog.add_book, self.fiction))

    def test_duplicate_id(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.assertFalse(self.quiet(self.catalog.add_book, self.nonfiction.__class__(101, 'X', 'Y', 'Z', 'Q')))

    def test_remove_available(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.assertTrue(self.quiet(self.catalog.remove_book, 101))

    def test_remove_borrowed(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.quiet(self.catalog.borrow_book, 101)
        self.assertFalse(self.quiet(self.catalog.remove_book, 101))

    def test_search_title_partial_casefold(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.assertEqual(self.quiet(self.catalog.search_by_title, 'ALPHA'), [self.fiction])

    def test_search_author_partial(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.assertEqual(self.quiet(self.catalog.search_by_author, 'alice'), [self.fiction])

    def test_borrow(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.assertTrue(self.quiet(self.catalog.borrow_book, 101))
        self.assertFalse(self.fiction.check_availability())

    def test_double_borrow(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.quiet(self.catalog.borrow_book, 101)
        self.assertFalse(self.quiet(self.catalog.borrow_book, 101))

    def test_return(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.quiet(self.catalog.borrow_book, 101)
        self.assertTrue(self.quiet(self.catalog.return_book, 101))

    def test_invalid_return(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.assertFalse(self.quiet(self.catalog.return_book, 101))

    def test_availability(self):
        self.quiet(self.catalog.add_book, self.fiction)
        self.assertTrue(self.quiet(self.catalog.check_book_availability, 101))

    def test_missing_id(self):
        self.assertFalse(self.quiet(self.catalog.borrow_book, 999))
        self.assertIsNone(self.quiet(self.catalog.check_book_availability, 999))

    def test_validation(self):
        with self.assertRaises(ValueError):
            Book(1, '', 'A', 'G')
        with self.assertRaises(TypeError):
            self.fiction.update_availability(1)

    def test_unique_ids_after_samples(self):
        catalog = self.quiet(create_sample_catalog)
        self.assertEqual(catalog.generate_book_id(), 106)

    def test_reference_in_available_list(self):
        self.quiet(self.catalog.add_book, self.reference)
        output = StringIO()
        with redirect_stdout(output):
            self.catalog.display_available_books()
        self.assertIn('In-library use only', output.getvalue())


if __name__ == '__main__':
    unittest.main()
