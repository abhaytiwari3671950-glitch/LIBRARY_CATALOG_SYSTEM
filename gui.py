"""Tkinter desktop interface for the SQLite Library Catalog System."""
import tkinter as tk
from tkinter import ttk, messagebox
from database import LibraryDB

BG = '#f4f6ff'
NAV = '#161836'
ACCENT = '#6557f5'
ACCENT_DARK = '#4e42cf'
INK = '#1b2142'
MUTED = '#71809c'
BORDER = '#e2e7f4'
CYAN = '#06b6d4'



class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('LibraryFlow | Smart Library Management')
        self.geometry('1280x790')
        self.minsize(1050, 680)
        self.configure(bg=BG)
        self.db = LibraryDB()
        self.user = None
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview', rowheight=39, font=('Segoe UI', 10), background='#ffffff',
                        fieldbackground='#ffffff', foreground=INK, borderwidth=0)
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background='#eef0ff',
                        foreground='#444778', relief='flat', padding=(9, 12))
        style.map('Treeview', background=[('selected', '#dfdcff')], foreground=[('selected', INK)])
        style.configure('TEntry', padding=7, fieldbackground='#ffffff')
        style.configure('TCombobox', padding=7)
        style.configure('Vertical.TScrollbar', background='#c8c9ea', troughcolor='#f4f6ff')
        self.protocol('WM_DELETE_WINDOW', self.close_app)
        self.show_login()

    def close_app(self):
        self.db.close()
        self.destroy()

    def clear(self):
        for child in self.winfo_children():
            child.destroy()

    def label(self, parent, text, size=11, fg=INK, bold=False, bg='white'):
        return tk.Label(parent, text=text, font=('Segoe UI', size, 'bold' if bold else 'normal'), fg=fg, bg=bg)

    def panel(self, parent):
        return tk.Frame(parent, bg='white', padx=24, pady=20, highlightbackground=BORDER, highlightthickness=1)

    def entry(self, parent, label, show=None):
        self.label(parent, label, 10, fg='#566180', bold=True).pack(anchor='w', pady=(12, 5))
        e = ttk.Entry(parent, show=show, font=('Segoe UI', 11))
        e.pack(fill='x', ipady=5)
        return e

    def action(self, parent, text, command, variant='primary'):
        colors = {
            'primary': (ACCENT, '#ffffff', ACCENT_DARK),
            'secondary': ('#ecebff', '#5044c8', '#dddafe'),
            'danger': ('#fff0f1', '#d43d65', '#ffe0e7'),
            'success': ('#e0faf3', '#087d69', '#bdf4e7'),
        }
        bg, fg, hover = colors[variant]
        b = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                      activebackground=hover, activeforeground=fg, relief='flat', bd=0,
                      font=('Segoe UI', 10, 'bold'), padx=17, pady=11, cursor='hand2')
        b.pack(side='left', padx=(0, 9), pady=2)
        b.bind('<Enter>', lambda _: b.configure(bg=hover))
        b.bind('<Leave>', lambda _: b.configure(bg=bg))
        return b

    def show_login(self):
        self.user = None
        self.clear()
        shell = tk.Frame(self, bg=NAV)
        shell.pack(fill='both', expand=True)
        promo = tk.Frame(shell, bg=NAV, padx=75, pady=80)
        promo.pack(side='left', fill='both', expand=True)
        self.label(promo, '◆   LIBRARYFLOW', 16, '#c1bcff', True, NAV).pack(anchor='w')
        tk.Frame(promo, bg='#7b70fd', width=72, height=5).pack(anchor='w', pady=(95, 24))
        self.label(promo, 'Your library,\nbeautifully organized.', 32, '#ffffff', True, NAV).pack(anchor='w')
        self.label(promo, 'Manage books, students and borrowing\nwith one streamlined desktop workspace.',
                   12, '#b4b9d6', bg=NAV).pack(anchor='w', pady=22)
        self.label(promo, '●  Books     ●  Members     ●  Insights', 11, '#8fe7e6', bg=NAV).pack(anchor='w', pady=26)

        right = tk.Frame(shell, bg=BG, width=510)
        right.pack(side='right', fill='y')
        right.pack_propagate(False)
        outer = tk.Frame(right, bg=BG)
        outer.pack(expand=True, fill='x', padx=42)
        card = self.panel(outer)
        card.pack(fill='x')
        self.label(card, 'Welcome to LibraryFlow', 22, bold=True).pack(anchor='w')
        first_setup = not self.db.admin_exists()
        subtitle = 'Set up your administrator account' if first_setup else 'Sign in to your workspace'
        self.label(card, subtitle, 11, MUTED).pack(anchor='w', pady=(7, 20))
        username = self.entry(card, 'Username')
        password = self.entry(card, 'Password', '*')
        self.label(card, 'Minimum 8 characters for first-time setup', 9, MUTED).pack(anchor='w', pady=(7, 3))
        def submit():
            try:
                if not self.db.admin_exists():
                    self.db.create_first_admin(username.get(), password.get())
                    messagebox.showinfo('Administrator created', 'Administrator account created. Sign in now.')
                    self.show_login()
                    return
                account = self.db.login(username.get(), password.get())
                if not account:
                    raise ValueError('Incorrect username or password.')
                self.user = account
                self.show_page('Dashboard')
            except Exception as exc:
                messagebox.showerror('Sign in', str(exc))
        buttons = tk.Frame(card, bg='white')
        buttons.pack(anchor='w', pady=(22, 0))
        self.action(buttons, 'Create Admin Account' if first_setup else 'Sign In  →', submit)
        password.bind('<Return>', lambda event: submit())
        username.focus_set()

    def show_page(self, page):
        self.clear()
        shell = tk.Frame(self, bg=BG)
        shell.pack(fill='both', expand=True)
        nav = tk.Frame(shell, bg=NAV, width=240)
        nav.pack(side='left', fill='y')
        nav.pack_propagate(False)
        self.label(nav, '◆  LibraryFlow', 19, '#ffffff', True, NAV).pack(anchor='w', padx=23, pady=(32, 4))
        self.label(nav, 'SMART LIBRARY SYSTEM', 9, '#9499c1', True, NAV).pack(anchor='w', padx=25, pady=(0, 43))
        self.label(nav, 'WORKSPACE', 9, '#8d92bd', True, NAV).pack(anchor='w', padx=23, pady=(0, 11))
        pages = (['Dashboard', 'Books', 'Students', 'Issue / Return', 'Borrowing History']
                 if self.user['role'] == 'admin' else ['Dashboard', 'Books', 'My History'])
        icons = {'Dashboard':'▦', 'Books':'▤', 'Students':'◉', 'Issue / Return':'⇄',
                 'Borrowing History':'◷', 'My History':'◷'}
        for name in pages:
            selected = page == name
            button = tk.Button(nav, text=f'  {icons[name]}     {name}', anchor='w', relief='flat', bd=0,
                               bg='#6557f5' if selected else NAV,
                               fg='white' if selected else '#c9cce6',
                               activebackground='#41416f', activeforeground='white',
                               font=('Segoe UI', 11, 'bold' if selected else 'normal'),
                               padx=12, pady=13, command=lambda n=name: self.show_page(n), cursor='hand2')
            button.pack(fill='x', padx=12, pady=4)
        footer = tk.Frame(nav, bg='#222446', padx=13, pady=14)
        footer.pack(side='bottom', fill='x', padx=12, pady=17)
        self.label(footer, f"{self.user['username']}", 11, '#ffffff', True, '#222446').pack(anchor='w')
        self.label(footer, self.user['role'].title() + ' account', 9, '#a9aed5', bg='#222446').pack(anchor='w', pady=3)
        tk.Button(footer, text='↪  Log out', anchor='w', relief='flat', bd=0,
                  bg='#222446', fg='#e0c5fb', font=('Segoe UI', 10, 'bold'),
                  cursor='hand2', command=self.show_login).pack(anchor='w', pady=(10, 0))
        main = tk.Frame(shell, bg=BG, padx=32, pady=26)
        main.pack(side='left', fill='both', expand=True)
        header = tk.Frame(main, bg=BG)
        header.pack(fill='x', pady=(0, 24))
        self.label(header, page, 25, INK, True, BG).pack(side='left')
        pill = tk.Label(header, text='●  ' + self.user['role'].upper(), bg='#e3e1ff', fg=ACCENT_DARK,
                        font=('Segoe UI', 9, 'bold'), padx=15, pady=8)
        pill.pack(side='right')
        {'Dashboard':self.dashboard, 'Books':self.books_page, 'Students':self.students_page,
         'Issue / Return':self.issue_page, 'Borrowing History':self.history_page,
         'My History':self.history_page}[page](main)

    def table(self, parent, headings, rows):
        frame = tk.Frame(parent, bg='white', highlightbackground=BORDER, highlightthickness=1, padx=8, pady=8)
        frame.pack(fill='both', expand=True, pady=12)
        tree = ttk.Treeview(frame, columns=headings, show='headings', selectmode='browse')
        for name in headings:
            tree.heading(name, text=name)
            tree.column(name, width=130, minwidth=85, stretch=True)
        for row in rows:
            tree.insert('', 'end', values=row)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)
        return tree

    def execute(self, operation, refresh):
        try:
            result = operation()
            messagebox.showinfo('Success', f'Operation completed successfully.{" New Book ID: " + str(result) if result is not None else ""}')
            self.show_page(refresh)
        except (ValueError, Exception) as exc:
            messagebox.showerror('Unable to complete', str(exc))

    def dashboard(self, parent):
        stats = self.db.stats()
        strip = tk.Frame(parent, bg=BG)
        strip.pack(fill='x')
        cards = [('TOTAL BOOKS', stats[0], '#e8e6ff', '#5e51e8', '▤'),
                 ('REGISTERED STUDENTS', stats[1], '#dff8ff', '#0893b2', '◉'),
                 ('ACTIVE LOANS', stats[2], '#fff0df', '#e48a26', '⇄')]
        for title, value, tint, fg, symbol in cards:
            card = self.panel(strip)
            card.pack(side='left', fill='both', expand=True, padx=(0, 12))
            badge = tk.Label(card, text=symbol, font=('Segoe UI', 18, 'bold'),
                             bg=tint, fg=fg, width=3, pady=6)
            badge.pack(anchor='w', pady=(0, 18))
            self.label(card, title, 9, MUTED, True).pack(anchor='w')
            self.label(card, str(value), 30, INK, True).pack(anchor='w', pady=(7, 0))
        card = self.panel(parent)
        card.pack(fill='x', pady=24)
        self.label(card, 'Welcome back!  ✨', 19, bold=True).pack(anchor='w')
        desc = ('Your books, members and borrowing activity are all in one place.'
                if self.user['role'] == 'admin' else 'Explore the library catalog and track your reading activity.')
        self.label(card, desc, 11, MUTED).pack(anchor='w', pady=(9, 20))
        buttons = tk.Frame(card, bg='white')
        buttons.pack(anchor='w')
        self.action(buttons, 'Browse Books', lambda: self.show_page('Books'))
        if self.user['role'] == 'admin':
            self.action(buttons, 'Manage Students', lambda: self.show_page('Students'), 'secondary')
            self.action(buttons, 'Issue / Return', lambda: self.show_page('Issue / Return'), 'success')
        else:
            self.action(buttons, 'My History', lambda: self.show_page('My History'), 'secondary')

    def books_page(self, parent):
        controls = self.panel(parent)
        controls.pack(fill='x')
        find = self.entry(controls, 'Search by title, author, or book ID')
        table = None

        def fill_grid(query=''):
            for item in table.get_children():
                table.delete(item)
            for book in self.db.books(query):
                status = ('In-library use only' if book['book_type'] == 'Reference'
                          else ('Available' if book['available'] else 'Borrowed'))
                table.insert('', 'end', values=(book['book_id'], book['title'],
                             book['author'], book['book_type'], book['genre'], status))

        def search_books():
            query = find.get().strip()
            if not query:
                messagebox.showwarning('Search', 'Enter a title, author, or book ID to search.')
                return
            results = self.db.books(query)
            if not results:
                messagebox.showinfo('Book Search', 'No matching book found in the catalog.')
            elif len(results) == 1:
                book = results[0]
                status = ('Available for in-library use only' if book['book_type'] == 'Reference'
                          else ('Available for borrowing' if book['available'] else 'Currently borrowed'))
                messagebox.showinfo('Book Availability', f"{book['title']}\nStatus: {status}")
            else:
                available = sum(bool(b['available']) for b in results)
                messagebox.showinfo('Search Results',
                                    f'{len(results)} matching books found.\n'
                                    f'{available} available (including reference books).\n'
                                    'See the grid for each book’s availability.')
            # This runs only after the user dismisses the modal popup.
            fill_grid(query)

        def clear_search():
            find.delete(0, tk.END)
            fill_grid()
            find.focus_set()

        tools = tk.Frame(controls, bg='white')
        tools.pack(anchor='w', pady=12)
        self.action(tools, 'Search', search_books)
        self.action(tools, 'Clear', clear_search, 'secondary')
        if self.user['role'] == 'admin':
            self.action(tools, 'Add Book', self.add_book_dialog)
            self.action(tools, 'Edit Selected', lambda: self.edit_book_selected(table), 'secondary')
            self.action(tools, 'Remove Selected', lambda: self.remove_book_selected(table), 'danger')
        table = self.table(parent, ('ID', 'Title', 'Author', 'Type', 'Genre', 'Status'), [])
        find.bind('<Return>', lambda _event: search_books())
        fill_grid()

    def add_book_dialog(self):
        win, form = self.dialog('Add a Book')
        fields = [self.entry(form, name) for name in
                  ('Title', 'Author', 'Genre', 'Type detail (fiction genre / subject / reference category)')]
        self.label(form, 'Book type').pack(anchor='w', pady=(12, 3))
        book_type = ttk.Combobox(form, values=['Fiction', 'Non-Fiction', 'Reference'], state='readonly')
        book_type.set('Fiction')
        book_type.pack(fill='x')
        buttons = tk.Frame(form, bg='white')
        buttons.pack(pady=18, anchor='w')

        def save():
            try:
                book_id = self.db.add_book(*(field.get() for field in fields[:3]),
                                           book_type.get(), fields[3].get())
            except (ValueError, Exception) as exc:
                messagebox.showerror('Unable to save', str(exc), parent=win)
                return
            win.destroy()
            messagebox.showinfo('Saved', f'Book added successfully. Book ID: {book_id}')
            self.show_page('Books')

        self.action(buttons, 'Save Book', save)
        self.action(buttons, 'Clear', lambda: [field.delete(0, tk.END) for field in fields])

    def edit_book_selected(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning('Select a book', 'Choose a book from the grid first.')
            return
        book_id = int(tree.item(selected[0], 'values')[0])
        book = self.db.conn.execute('SELECT * FROM books WHERE book_id=?', (book_id,)).fetchone()
        if book is None:
            messagebox.showerror('Missing book', 'This book no longer exists.')
            return
        win, form = self.dialog(f'Edit Book #{book_id}')
        fields = []
        for label, value in (('Title', book['title']), ('Author', book['author']),
                             ('Genre', book['genre']), ('Type detail', book['detail'])):
            field = self.entry(form, label)
            field.insert(0, value)
            fields.append(field)
        self.label(form, 'Book type').pack(anchor='w', pady=(12, 3))
        book_type = ttk.Combobox(form, values=['Fiction', 'Non-Fiction', 'Reference'], state='readonly')
        book_type.set(book['book_type'])
        book_type.pack(fill='x')
        buttons = tk.Frame(form, bg='white')
        buttons.pack(anchor='w', pady=18)

        def save():
            try:
                self.db.update_book(book_id, *(field.get() for field in fields[:3]),
                                    book_type.get(), fields[3].get())
            except (ValueError, Exception) as exc:
                messagebox.showerror('Unable to update', str(exc), parent=win)
                return
            win.destroy()
            messagebox.showinfo('Updated', f'Book #{book_id} updated successfully.')
            self.show_page('Books')

        self.action(buttons, 'Save Changes', save)
        self.action(buttons, 'Clear', lambda: [field.delete(0, tk.END) for field in fields])

    def remove_book_selected(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning('Select a book', 'Choose a book from the table first.'); return
        book_id = int(tree.item(selected[0], 'values')[0])
        if messagebox.askyesno('Remove book', f'Remove book #{book_id}? Books with borrowing history are protected.'):
            self.execute(lambda: self.db.remove_book(book_id), 'Books')

    def dialog(self, title):
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry('520x760' if title == 'Register Student' else '500x600')
        window.configure(bg=BG)
        window.transient(self)
        window.grab_set()
        form = self.panel(window)
        form.pack(fill='both', expand=True, padx=12, pady=12)
        self.label(form, title, 17, bold=True).pack(anchor='w')
        return window, form

    def students_page(self, parent):
        controls = self.panel(parent)
        controls.pack(fill='x')
        tools = tk.Frame(controls, bg='white')
        tools.pack(anchor='w')
        table = None
        self.action(tools, 'Register Student', self.add_student_dialog)
        self.action(tools, 'Edit Selected', lambda: self.edit_student_selected(table), 'secondary')
        search = self.entry(controls, 'Search by student name or ID')

        def update(*args):
            for item in table.get_children():
                table.delete(item)
            for student in self.db.students(search.get()):
                table.insert('', 'end', values=(student['student_id'], student['name'],
                             student['department'], student['email']))

        def clear_search():
            search.delete(0, tk.END)
            update()
            search.focus_set()
        self.action(tools, 'Clear Search', clear_search, 'secondary')
        table = self.table(parent, ('Student ID', 'Name', 'Department', 'Email'), [])
        search.bind('<KeyRelease>', update)
        update()

    def edit_student_selected(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning('Select student', 'Choose a student from the grid first.')
            return
        student_id = str(tree.item(selected[0], 'values')[0])
        student = self.db.conn.execute('SELECT * FROM students WHERE student_id=?',
                                       (student_id,)).fetchone()
        if student is None:
            messagebox.showerror('Missing student', 'Student not found.')
            return
        win, form = self.dialog('Edit Student')
        self.label(form, f'Student ID: {student_id} (cannot be changed)', 10).pack(anchor='w', pady=8)
        fields = []
        for label, value in (('Full Name', student['name']), ('Department', student['department']),
                             ('Email', student['email'])):
            field = self.entry(form, label)
            field.insert(0, value)
            fields.append(field)
        buttons = tk.Frame(form, bg='white')
        buttons.pack(anchor='w', pady=18)

        def save():
            try:
                self.db.update_student(student_id, *(field.get() for field in fields))
            except (ValueError, Exception) as exc:
                messagebox.showerror('Unable to update', str(exc), parent=win)
                return
            win.destroy()
            messagebox.showinfo('Updated', f'Student {student_id} updated successfully.')
            self.show_page('Students')

        self.action(buttons, 'Save Changes', save)
        self.action(buttons, 'Clear', lambda: [field.delete(0, tk.END) for field in fields])

    def add_student_dialog(self):
        win, form = self.dialog('Register Student')
        fields = [self.entry(form, name, '*' if name=='Password' else None) for name in ('Student ID','Full Name','Department','Email','Login Username (optional)','Password')]
        self.label(form, 'Leave login fields empty to register without an account.', 9, '#64748b').pack(anchor='w', pady=5)
        buttons = tk.Frame(form, bg='white'); buttons.pack(pady=12, anchor='w')
        self.action(buttons, 'Register', lambda: (win.destroy(), self.execute(lambda: self.db.add_student(*(e.get() for e in fields)), 'Students')))

    def issue_page(self, parent):
        card = self.panel(parent)
        card.pack(fill='x')
        book_id = self.entry(card, 'Book ID')
        student_id = self.entry(card, 'Student ID (required for issue)')
        self.label(card, 'A loan lasts 14 days. Reference books cannot be issued.', 10, '#64748b').pack(anchor='w', pady=15)
        buttons = tk.Frame(card, bg='white'); buttons.pack(anchor='w')
        def numeric_id():
            try: return int(book_id.get())
            except ValueError: raise ValueError('Enter a valid numeric Book ID.')
        self.action(buttons, 'Issue Book', lambda: self.execute(lambda: self.db.issue_book(numeric_id(), student_id.get()), 'Issue / Return'))
        self.action(buttons, 'Return Book', lambda: self.execute(lambda: self.db.return_book(numeric_id()), 'Issue / Return'))
        self.label(parent, 'Recent transactions', 14, INK, True, BG).pack(anchor='w', pady=(25,0))
        self.history_table(parent, self.db.history()[:25])

    def history_table(self, parent, data):
        def date(s): return s[:16].replace('T',' ') if s else '—'
        rows = [(r['loan_id'],r['book_id'],r['title'],r['student_id'],r['name'],date(r['issued_at']),date(r['due_at']),
                 date(r['returned_at']) if r['returned_at'] else 'On loan') for r in data]
        return self.table(parent, ('Loan #','Book #','Book Title','Student ID','Student Name','Issued (UTC)','Due (UTC)','Returned (UTC)'),rows)

    def history_page(self, parent):
        student_id = None if self.user['role']=='admin' else self.user['student_id']
        self.history_table(parent, self.db.history(student_id))


def main():
    app = LibraryApp()
    app.mainloop()


if __name__ == '__main__':
    main()
