import os
import os.path
import sys

import wx

import db
from misc import MY_DATABASE_PATH, SRC_DIR


class App(wx.App):
    def __init__(self, con: db.Connection):
        super().__init__()
        from ui.mainview import MainView

        mv = MainView(con)
        self.SetTopWindow(mv)
        mv.Show()
        self.MainLoop()


def platform_settings():
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    elif sys.platform == "linux":
        # light theme
        os.environ["GTK_THEME"] = "Default " + os.path.join(SRC_DIR, "main.py")
        pass


if __name__ == "__main__":
    connection = db.Connection(MY_DATABASE_PATH)
    try:
        connection.update_last_open_date()
    except Exception:
        connection.make_db()
        connection.update_last_open_date()
    finally:
        platform_settings()
        App(connection)
