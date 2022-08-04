from paths import MY_DATABASE_PATH
from db.db_func import Connection
import os
from pathlib import Path
import datetime as dt
import shutil


def reset_database() -> bool:
    try:
        os.remove(MY_DATABASE_PATH)
        con = Connection(MY_DATABASE_PATH)
        con.make_db()
        con.close()
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    if reset_database():
        print(f"Reset database")
    else:
        print('Failed')

