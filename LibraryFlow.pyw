"""Console-free entrypoint for LibraryFlow on Windows."""
import os
import runpy
import traceback
from pathlib import Path

root = Path(__file__).resolve().parent
os.chdir(root)
try:
    runpy.run_path(str(root / "gui.py"), run_name="__main__")
except Exception:
    (root / "launch_error.log").write_text(traceback.format_exc(), encoding="utf-8")
    try:
        import tkinter.messagebox as messagebox
        messagebox.showerror("LibraryFlow startup error", "Could not start LibraryFlow. Read launch_error.log in the project folder.")
    except Exception:
        pass
