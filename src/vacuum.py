from db.db_func import Connection
from paths import MY_DATABASE_PATH


def vacuum() -> tuple[int, int] | None:
    con = Connection(MY_DATABASE_PATH)
    try:
        pre, post = con.vacuum()
        return pre, post
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    res = vacuum()
    if res is not None:
        pre, post = res
        print(f"File size before vacuum: {pre}")
        print(f"File size after vacuum: {post}")
