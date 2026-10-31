"""Tests for persistence, authentication, and circulation."""
import tempfile
import unittest
from pathlib import Path
from database import LibraryDB


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'test.db'
        self.db = LibraryDB(self.path)
        self.db.create_first_admin('admin', 'securepass123')
        self.db.add_student('S001', 'Asha Sharma', 'MCA', 'asha@example.com', 'asha', 'anotherpass123')

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_login_roles(self):
        self.assertEqual(self.db.login('admin', 'securepass123')['role'], 'admin')
        self.assertEqual(self.db.login('asha', 'anotherpass123')['student_id'], 'S001')
        self.assertIsNone(self.db.login('asha', 'wrong'))

    def test_duplicate_student(self):
        with self.assertRaises(Exception): self.db.add_student('S001', 'Duplicate')

    def test_first_admin_only(self):
        with self.assertRaises(ValueError): self.db.create_first_admin('second', 'securepass123')

    def test_book_search(self):
        self.assertTrue(any(b['title']=='The Alchemist' for b in self.db.books('alchem')))

    def test_book_add_remove(self):
        book_id = self.db.add_book('Sample Book','An Author','General','Fiction','Fantasy')
        self.assertTrue(any(b['book_id']==book_id for b in self.db.books()))
        self.db.remove_book(book_id)
        self.assertFalse(any(b['book_id']==book_id for b in self.db.books()))

    def test_issue_return_history(self):
        self.db.issue_book(1, 'S001')
        self.assertEqual(self.db.history('S001')[0]['book_id'], 1)
        self.assertEqual(self.db.books('Alchemist')[0]['available'], 0)
        with self.assertRaises(ValueError): self.db.issue_book(1, 'S001')
        with self.assertRaises(ValueError): self.db.remove_book(1)
        self.db.return_book(1)
        self.assertIsNotNone(self.db.history('S001')[0]['returned_at'])
        self.assertEqual(self.db.books('Alchemist')[0]['available'], 1)
        with self.assertRaises(ValueError): self.db.return_book(1)
        with self.assertRaises(ValueError): self.db.remove_book(1)

    def test_reference_restricted(self):
        with self.assertRaises(ValueError): self.db.issue_book(3, 'S001')

    def test_invalid_student(self):
        with self.assertRaises(ValueError): self.db.issue_book(1, 'missing')

    def test_persists_after_reopen(self):
        self.db.issue_book(1, 'S001')
        self.db.close()
        self.db = LibraryDB(self.path)
        self.assertEqual(len(self.db.history()), 1)

    def test_student_history_filtered(self):
        self.db.add_student('S002','Other Student')
        self.db.issue_book(1,'S001')
        self.assertEqual(len(self.db.history('S002')), 0)
        self.assertEqual(len(self.db.history('S001')), 1)


if __name__ == '__main__':
    unittest.main()

class EditFeatureTests(unittest.TestCase):
    """Verify edits preserve identifiers, loans, and existing history."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = LibraryDB(Path(self.tmp.name) / 'edit.sqlite3')

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_edit_book(self):
        book_id = self.db.add_book('Old', 'A', 'G', 'Fiction', 'Mystery')
        self.db.update_book(book_id, 'Updated', 'Writer', 'Novel', 'Non-Fiction', 'Science')
        result = self.db.conn.execute('SELECT * FROM books WHERE book_id=?', (book_id,)).fetchone()
        self.assertEqual(result['title'], 'Updated')
        self.assertEqual(result['book_type'], 'Non-Fiction')
        self.assertEqual(result['book_id'], book_id)

    def test_edit_student_preserves_history(self):
        book_id = self.db.add_book('Loan book', 'A', 'G', 'Fiction', 'Drama')
        self.db.add_student('S200', 'Old Name')
        self.db.issue_book(book_id, 'S200')
        self.db.update_student('S200', 'New Name', 'MCA', 'new@example.com')
        history = self.db.history('S200')
        self.assertEqual(history[0]['name'], 'New Name')
        self.assertEqual(history[0]['book_id'], book_id)

    def test_reject_borrowed_conversion_to_reference(self):
        book_id = self.db.add_book('Loan book', 'A', 'G', 'Fiction', 'Drama')
        self.db.add_student('S300', 'Student')
        self.db.issue_book(book_id, 'S300')
        with self.assertRaises(ValueError):
            self.db.update_book(book_id, 'Loan book', 'A', 'G', 'Reference', 'Atlas')
