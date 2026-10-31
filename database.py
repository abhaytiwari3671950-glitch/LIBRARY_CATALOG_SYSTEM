"""SQLite persistence, accounts, and circulation rules for the desktop GUI."""
import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / 'library.db'


def hash_password(password, salt=None):
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError('Password must contain at least 8 characters.')
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 260_000)
    return f'{salt.hex()}${digest.hex()}'


def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split('$')
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt_hex), 260_000)
        return hmac.compare_digest(actual, bytes.fromhex(digest_hex))
    except (ValueError, TypeError):
        return False


class LibraryDB:
    """Manage authenticated accounts, inventory, student records and loan history."""

    def __init__(self, filename=DB_FILE):
        self.conn = sqlite3.connect(str(filename))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('PRAGMA foreign_keys=ON')
        self._setup()

    def close(self):
        self.conn.close()

    def _setup(self):
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','student')),
                student_id TEXT UNIQUE REFERENCES students(student_id)
            );
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT NOT NULL,
                book_type TEXT NOT NULL CHECK(book_type IN ('Fiction','Non-Fiction','Reference')),
                detail TEXT NOT NULL,
                available INTEGER NOT NULL DEFAULT 1 CHECK(available IN (0,1))
            );
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE RESTRICT,
                student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE RESTRICT,
                issued_at TEXT NOT NULL,
                due_at TEXT NOT NULL,
                returned_at TEXT
            );
            CREATE UNIQUE INDEX IF NOT EXISTS one_active_loan
                ON loans(book_id) WHERE returned_at IS NULL;
        ''')
        with self.conn:
            if not self.conn.execute('SELECT 1 FROM books LIMIT 1').fetchone():
                samples = [
                    ('The Alchemist', 'Paulo Coelho', 'Novel', 'Fiction', 'Adventure'),
                    ('A Brief History of Time', 'Stephen Hawking', 'Science', 'Non-Fiction', 'Cosmology'),
                    ('Oxford English Dictionary', 'Oxford University Press', 'Language', 'Reference', 'Dictionary'),
                    ("Harry Potter and the Philosopher's Stone", 'J. K. Rowling', 'Fantasy', 'Fiction', 'Fantasy'),
                    ('Wings of Fire', 'A. P. J. Abdul Kalam', 'Biography', 'Non-Fiction', 'Autobiography'),
                ]
                self.conn.executemany('INSERT INTO books(title,author,genre,book_type,detail) VALUES(?,?,?,?,?)', samples)

    def admin_exists(self):
        return self.conn.execute("SELECT 1 FROM users WHERE role='admin' LIMIT 1").fetchone() is not None

    def create_first_admin(self, username, password):
        if self.admin_exists():
            raise ValueError('An administrator already exists.')
        self._required(username, 'Username')
        with self.conn:
            self.conn.execute('INSERT INTO users VALUES(?,?,?,NULL)', (username.strip(), hash_password(password), 'admin'))

    def login(self, username, password):
        account = self.conn.execute('SELECT * FROM users WHERE username=?', (username.strip(),)).fetchone()
        if account and verify_password(password, account['password_hash']):
            return dict(account)
        return None

    @staticmethod
    def _required(value, label):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{label} is required.')
        return value.strip()

    def add_student(self, student_id, name, department='', email='', username='', password=''):
        student_id = self._required(student_id, 'Student ID')
        name = self._required(name, 'Student name')
        if bool(username.strip()) != bool(password):
            raise ValueError('Provide both a username and password, or neither.')
        password_hash = hash_password(password) if username.strip() else None
        with self.conn:
            self.conn.execute('INSERT INTO students VALUES(?,?,?,?)', (student_id, name, department.strip(), email.strip()))
            if password_hash:
                self.conn.execute('INSERT INTO users VALUES(?,?,?,?)', (username.strip(), password_hash, 'student', student_id))

    def students(self, search=''):
        q = f'%{search.strip()}%'
        return self.conn.execute('SELECT * FROM students WHERE name LIKE ? OR student_id LIKE ? ORDER BY name', (q,q)).fetchall()

    def add_book(self, title, author, genre, book_type, detail):
        values = [self._required(v, label) for v, label in zip((title,author,genre,detail), ('Title','Author','Genre','Type detail'))]
        if book_type not in ('Fiction', 'Non-Fiction', 'Reference'):
            raise ValueError('Choose a valid book type.')
        with self.conn:
            return self.conn.execute('INSERT INTO books(title,author,genre,book_type,detail) VALUES(?,?,?,?,?)', (*values[:3],book_type,values[3])).lastrowid

    def update_book(self, book_id, title, author, genre, book_type, detail):
        """Edit metadata without changing book IDs or borrowing history."""
        values = [self._required(v, label) for v, label in zip(
            (title, author, genre, detail), ('Title', 'Author', 'Genre', 'Type detail'))]
        if book_type not in ('Fiction', 'Non-Fiction', 'Reference'):
            raise ValueError('Choose a valid book type.')
        with self.conn:
            book = self.conn.execute('SELECT * FROM books WHERE book_id=?', (book_id,)).fetchone()
            if book is None:
                raise ValueError('Book ID not found.')
            if not book['available'] and book_type == 'Reference':
                raise ValueError('Cannot change a borrowed book into a Reference book.')
            self.conn.execute('UPDATE books SET title=?, author=?, genre=?, book_type=?, detail=? WHERE book_id=?', (*values[:3], book_type, values[3], book_id))

    def update_student(self, student_id, name, department='', email=''):
        """Edit student details while keeping their permanent ID and history."""
        name = self._required(name, 'Student name')
        with self.conn:
            if not self.conn.execute('SELECT 1 FROM students WHERE student_id=?',
                                     (student_id,)).fetchone():
                raise ValueError('Student ID not found.')
            self.conn.execute('UPDATE students SET name=?, department=?, email=? WHERE student_id=?',
                              (name, department.strip(), email.strip(), student_id))

    def books(self, search='', available_only=False):
        q = f'%{search.strip()}%'
        query = '''SELECT * FROM books WHERE (title LIKE ? OR author LIKE ? OR CAST(book_id AS TEXT) LIKE ?)'''
        if available_only:
            query += ' AND available=1'
        return self.conn.execute(query + ' ORDER BY book_id', (q,q,q)).fetchall()

    def remove_book(self, book_id):
        with self.conn:
            book = self.conn.execute('SELECT available FROM books WHERE book_id=?', (book_id,)).fetchone()
            if not book:
                raise ValueError('Book ID not found.')
            if not book['available']:
                raise ValueError('Cannot remove a borrowed book.')
            if self.conn.execute('SELECT 1 FROM loans WHERE book_id=?', (book_id,)).fetchone():
                raise ValueError('Cannot delete a book with borrowing history.')
            self.conn.execute('DELETE FROM books WHERE book_id=?', (book_id,))

    def issue_book(self, book_id, student_id):
        student_id = self._required(student_id, 'Student ID')
        with self.conn:
            student = self.conn.execute('SELECT 1 FROM students WHERE student_id=?', (student_id,)).fetchone()
            if not student:
                raise ValueError('Student ID not found.')
            book = self.conn.execute('SELECT * FROM books WHERE book_id=?', (book_id,)).fetchone()
            if not book:
                raise ValueError('Book ID not found.')
            if book['book_type'] == 'Reference':
                raise ValueError('Reference books are for in-library use only.')
            if not book['available']:
                raise ValueError('This book has already been issued.')
            now = datetime.now(timezone.utc)
            self.conn.execute('INSERT INTO loans(book_id,student_id,issued_at,due_at) VALUES(?,?,?,?)',
                              (book_id,student_id,now.isoformat(timespec='seconds'),(now+timedelta(days=14)).isoformat(timespec='seconds')))
            self.conn.execute('UPDATE books SET available=0 WHERE book_id=?', (book_id,))

    def return_book(self, book_id):
        with self.conn:
            active = self.conn.execute('SELECT loan_id FROM loans WHERE book_id=? AND returned_at IS NULL', (book_id,)).fetchone()
            if not active:
                raise ValueError('No active loan for this book.')
            self.conn.execute('UPDATE loans SET returned_at=? WHERE loan_id=?',
                              (datetime.now(timezone.utc).isoformat(timespec='seconds'),active['loan_id']))
            self.conn.execute('UPDATE books SET available=1 WHERE book_id=?', (book_id,))

    def history(self, student_id=None):
        query = '''SELECT l.loan_id,l.book_id,b.title,s.student_id,s.name,l.issued_at,l.due_at,l.returned_at
                   FROM loans l JOIN books b ON b.book_id=l.book_id
                   JOIN students s ON s.student_id=l.student_id'''
        args = ()
        if student_id is not None:
            query += ' WHERE s.student_id=?'
            args = (student_id,)
        return self.conn.execute(query+' ORDER BY l.loan_id DESC', args).fetchall()

    def stats(self):
        return (self.conn.execute('SELECT COUNT(*) FROM books').fetchone()[0],
                self.conn.execute('SELECT COUNT(*) FROM students').fetchone()[0],
                self.conn.execute('SELECT COUNT(*) FROM loans WHERE returned_at IS NULL').fetchone()[0])
