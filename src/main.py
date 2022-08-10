import db.db_func as dbf
from other_func import get_config
from paths import *
import os.path
from pathlib import Path
import shutil
import wx
import os
import sys
import ctypes


class App(wx.App):
    def __init__(self, con: dbf.Connection):
        super().__init__()
        from core.mainview import MainView
        config = get_config()
        mv = MainView(con, config)
        self.SetTopWindow(mv)
        mv.Show()
        self.MainLoop()


def copy_config() -> bool:
    if not Path(CONFIG_PATH).exists():
        try:
            shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)
            return True
        except Exception as e:
            print(e)
            return False
    else:
        return True


def mainloop(con):
    copy_config()
    platform_settings()
    App(con)


def platform_settings():
    if sys.platform == 'win32':
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    elif sys.platform == 'linux':
        # light theme
        os.environ['GTK_THEME'] = "Default " + os.path.join(SRC_DIR, "main.py")
        pass


if __name__ == "__main__":
    con = dbf.Connection(MY_DATABASE_PATH)
    con.make_db()
    mainloop(con)
