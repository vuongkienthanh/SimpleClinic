from paths import MY_DATABASE_PATH
import os
from pathlib import Path
import datetime as dt
import shutil
import time


def make_bak() -> tuple[bool, str]:
    bak = os.path.realpath(MY_DATABASE_PATH) + \
        dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".bak"
    try:
        if Path(MY_DATABASE_PATH).exists():
            shutil.copyfile(MY_DATABASE_PATH, bak)
            return True, bak
        else:
            return False, "database doesn't exist"
    except Exception as e:
        print(e)
        return False, ''


if __name__ == '__main__':
    b, s = make_bak()
    if b:
        print(f"Backup at {s}")
    else:
        print('Failed:', s)
    for i in range(5):
        time.sleep(1)
        print('closing in' , 4-i)
