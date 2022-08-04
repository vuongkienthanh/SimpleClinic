from paths import MY_DATABASE_PATH
import os
from pathlib import Path
import datetime as dt
import shutil


def make_bak() -> tuple[bool, str]:
    bak = os.path.realpath(MY_DATABASE_PATH) + \
        dt.datetime.now().isoformat() + ".bak"
    try:
        if Path(MY_DATABASE_PATH).exists():
            shutil.copyfile(MY_DATABASE_PATH, bak)
            return True, bak
        else:
            return False, ''
    except Exception as e:
        print(e)
        return False, ''


if __name__ == '__main__':
    b, s = make_bak()
    if b:
        print(f"Backup at {s}")
    else:
        print('Failed')
