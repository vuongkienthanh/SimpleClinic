import db.db_func as dbf
from paths import *
import os.path
from pathlib import Path
import shutil
import wx
import argparse
import os
import sys
import json
from typing import Any


class App(wx.App):
    def __init__(self, sample):
        super().__init__()

        from core.mainview import MainView
        if sample:
            # con = dbf.Connection('test.db')
            con = dbf.Connection(':memory:')
            con.make_db()
            con.make_sample()
            config = self.get_config(sample)
        else:
            con = dbf.Connection(MY_DATABASE_PATH)
            con.make_db()
            config = self.get_config(sample)
        mv = MainView(con, config, sample)
        self.SetTopWindow(mv)
        mv.Show()
        self.MainLoop()

    def get_config(self, sample: bool) -> dict[str, Any]:
        if sample:
            p = DEFAULT_CONFIG_PATH
        else:
            p = CONFIG_PATH
        try:
            with open(p, "r", encoding="utf-8") as f:
                config = json.load(f)
                if not isinstance(config, dict):
                    sys.exit("ERROR: Config file is not a dict")
        except json.JSONDecodeError:
            with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        return config


def mainloop(sample=False):
    copy_config()
    platform_settings()
    App(sample)


def make_bak():
    bak = os.path.realpath(MY_DATABASE_PATH) + ".bak"
    if Path(MY_DATABASE_PATH).exists():
        os.rename(MY_DATABASE_PATH, bak)
        print(f"Back up database to: {bak}")
    else:
        print(f"{MY_DATABASE_PATH} not found")


def make_db():
    con = dbf.Connection(MY_DATABASE_PATH)
    con.make_db()
    con.close()
    print(f'New database created: {MY_DATABASE_PATH}')


def copy_config():
    if not Path(CONFIG_PATH).exists():
        shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)
        print(f"Create new {CONFIG_PATH}")
    else:
        print(f"Found {CONFIG_PATH}")


def replace_config():
    shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)
    print(f"Reset to default: {CONFIG_PATH}")


def platform_settings():
    if sys.platform == 'linux':
        # light theme
        os.environ['GTK_THEME'] = "Default " + os.path.join(SRC_DIR, "main.py")
        pass


def vacuum():
    print(f"Database file is at {MY_DATABASE_PATH}")
    print(f"Filesize before vacuum: {os.path.getsize(MY_DATABASE_PATH)} bytes")
    con = dbf.Connection(MY_DATABASE_PATH)
    con.execute("VACUUM")
    con.close()
    print(f"Filesize after vacuum: {os.path.getsize(MY_DATABASE_PATH)} bytes")


if __name__ == "__main__":

    ap = argparse.ArgumentParser(
        description="Phần mềm phòng khám tại nhà",
        epilog="Dùng `python -OO` để tối ưu hóa"
    )

    ap.add_argument("--reset-database", action="store_true",
                    help="Sao lưu và làm trắng dữ liệu")
    ap.add_argument("--reset-config", action="store_true",
                    help="Khôi phục cài đặt gốc")
    ap.add_argument("--sample", action="store_true",
                    help="Chạy demo")
    ap.add_argument("--vacuum", action="store_true",
                    help="Giảm kích thước database")
    ap.add_argument("--version", action="version",
                    help="Hiện thị phiên bản",
                    version="pmpktn v2.0.0")
    args = ap.parse_args()

    if args.reset_database:
        make_bak()
        make_db()
    elif args.reset_config:
        replace_config()
    elif args.sample:
        mainloop(sample=True)
    elif args.vacuum:
        vacuum()
    else:
        mainloop()
