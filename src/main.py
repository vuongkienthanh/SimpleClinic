import db.db_func as dbf
from paths import *
import os.path
import wx
import os
import sys


class App(wx.App):
    def __init__(self, con: dbf.Connection):
        super().__init__()
        from core.mainview import MainView

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
    con = dbf.Connection(MY_DATABASE_PATH)
    con.make_db()
    platform_settings()
    App(con)
