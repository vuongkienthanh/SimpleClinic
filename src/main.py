import db
from misc import SRC_DIR, MY_DATABASE_PATH
import os.path
import wx
import os
import sys


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
    connection.update_last_open_date()
    platform_settings()
    App(connection)
