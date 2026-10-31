"""Interactive command-line application for the library catalog."""
from book import FictionBook, NonFictionBook, ReferenceBook
from library import LibraryCatalog


def create_sample_catalog():
    catalog = LibraryCatalog()
    samples = [
        FictionBook(101, 'The Alchemist', 'Paulo Coelho', 'Literature', 'Adventure'),
        NonFictionBook(102, 'A Brief History of Time', 'Stephen Hawking', 'Educational', 'Science'),
        ReferenceBook(103, 'Oxford English Dictionary', 'Oxford University Press', 'Language', 'Dictionary'),
        FictionBook(104, "Harry Potter and the Philosopher's Stone", 'J. K. Rowling', 'Literature', 'Fantasy'),
        NonFictionBook(105, 'Wings of Fire', 'A. P. J. Abdul Kalam', 'Biography', 'Autobiography'),
    ]
    for book in samples:
        catalog.add_book(book)
    return catalog


def required_text(label):
    while True:
        value = input(label).strip()
        if value:
            return value
        print('Input cannot be empty. Please try again.')


def read_book_id():
    while True:
        raw = input('Enter book ID: ').strip()
        try:
            value = int(raw)
            if value > 0:
                return value
        except ValueError:
            pass
        print('Please enter a valid positive numeric book ID.')


def add_new_book(catalog):
    print('\nChoose book type: 1. Fiction  2. Non-Fiction  3. Reference')
    choice = input('Select type: ').strip()
    if choice not in ('1', '2', '3'):
        print('Invalid book type selection.')
        return
    title = required_text('Title: ')
    author = required_text('Author: ')
    genre = required_text('Genre: ')
    extra = {'1': 'Fiction genre', '2': 'Subject area', '3': 'Reference category'}
    detail = required_text(extra[choice] + ': ')
    book_id = catalog.generate_book_id()
    if choice == '1':
        book = FictionBook(book_id, title, author, genre, detail)
    elif choice == '2':
        book = NonFictionBook(book_id, title, author, genre, detail)
    else:
        book = ReferenceBook(book_id, title, author, genre, detail)
    catalog.add_book(book)


def show_menu():
    print('''\n===================================================
            LIBRARY CATALOG SYSTEM
===================================================
  1. Add New Book
  2. Remove Book
  3. Search Book by Title
  4. Search Book by Author
  5. Display All Books
  6. Display Available Books
  7. Check Book Availability
  8. Borrow Book
  9. Return Book
  0. Exit
===================================================''')


def main():
    catalog = create_sample_catalog()
    print('\nWelcome! Five sample books have been loaded.')
    while True:
        try:
            show_menu()
            choice = input('Enter your choice: ').strip()
            if choice == '1':
                add_new_book(catalog)
            elif choice == '2':
                catalog.remove_book(read_book_id())
            elif choice == '3':
                catalog.search_by_title(required_text('Enter title or part of title: '))
            elif choice == '4':
                catalog.search_by_author(required_text('Enter author or part of name: '))
            elif choice == '5':
                catalog.display_all_books()
            elif choice == '6':
                catalog.display_available_books()
            elif choice == '7':
                catalog.check_book_availability(read_book_id())
            elif choice == '8':
                catalog.borrow_book(read_book_id())
            elif choice == '9':
                catalog.return_book(read_book_id())
            elif choice == '0':
                print('Thank you for using Library Catalog System. Goodbye!')
                break
            else:
                print('Invalid menu selection. Please choose 0-9.')
        except (EOFError, KeyboardInterrupt):
            print('\nApplication closed gracefully. Goodbye!')
            break
        except (ValueError, TypeError) as error:
            print(f'Input error: {error}')


if __name__ == '__main__':
    main()
