# LibraryFlow — Python Library Management System

A Windows desktop Library Management System built using **Python, Tkinter and SQLite**. Includes a GUI, admin and student login, student records, book catalog, issue/return, borrowing history, and availability search.

## Requirements
- Python 3.11 or newer with Tkinter and sqlite3 (typically included on Windows).
- Windows 11 is the target platform for the no-console launcher.

## Run
- **Windows, no CMD window:** double-click `START_LIBRARYFLOW.vbs`.
- **Debug from PowerShell:** run `python gui.py` from this directory.
- **Original command-line OOP version:** run `python main.py`.
- **Automated tests:** run `python -m unittest test_library.py test_database.py`.

On first run, follow the administrator setup screen. Application data is stored locally in `library.db` and is deliberately **excluded from GitHub** to protect student data and login credentials.

## Project files
- `gui.py` — Tkinter graphical interface
- `database.py` — SQLite storage, authentication, transactions, history
- `book.py`, `library.py` — OOP book/catalog models
- `LibraryFlow.pyw` — GUI-only Python launcher
- `START_LIBRARYFLOW.vbs` — Windows no-console launcher
- `LibraryFlow_Original_Icon.ico` — application shortcut icon
- `main.py` — original CLI practical project
- `test_library.py`, `test_database.py` — unit tests

## GitHub safety
Do not upload `library.db`, `.env`, or password files. The included `.gitignore` excludes local database files, logs, environments and caches. Do not use GitHub Pages for this Tkinter desktop application; GitHub hosts its source code, not a running desktop GUI.

## License
For educational demonstration. No license is implied for third-party reuse.
