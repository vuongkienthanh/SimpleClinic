from db.classes import *
from db.sql import create_table_sql
import os.path
import sqlite3
from decimal import Decimal
import datetime as dt


class Connection:
    def __init__(self, path: str):
        self.path = path
        self.sqlcon = self._get_db_connection(path)

    def close(self):
        self.sqlcon.execute("PRAGMA optimize")
        self.sqlcon.close()

    def register_custom_type(self):
        def custom_type_decimal():
            def adapt(decimal: Decimal) -> str:
                return str(decimal)

            def convert(b: bytes) -> Decimal:
                return Decimal(b.decode())

            sqlite3.register_adapter(Decimal, adapt)
            sqlite3.register_converter("DECIMAL", convert)

        def custom_type_gender():
            def adapt(gender: Gender) -> int:
                return gender.value

            def convert(b: bytes) -> Gender:
                return Gender(int(b))

            sqlite3.register_adapter(Gender, adapt)
            sqlite3.register_converter("GENDER", convert)

        custom_type_decimal()
        custom_type_gender()

    def _get_db_connection(self, path: str) -> sqlite3.Connection:
        self.register_custom_type()
        con = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def make_db(self):
        self.sqlcon.executescript(create_table_sql)

    def __enter__(self):
        return self.sqlcon.__enter__()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.sqlcon.__exit__(exc_type, exc_value, exc_traceback)

    def execute(self, sql, *parameters):
        return self.sqlcon.execute(sql, *parameters)

    def update_last_open_date(self) -> dt.date | None:
        with self.sqlcon as con:
            con.execute("UPDATE singleton SET last_open_date = ?", (dt.date.today(),))

    def insert(self, t: type[T], base: dict) -> int | None:
        with self.sqlcon as con:
            cur = con.execute(
                f"""
                INSERT INTO {t.__tablename__} ({t.commna_joined_field_names()})
                VALUES ({t.named_style_placeholders()})
            """,
                base,
            )
            assert cur.lastrowid is not None
            return cur.lastrowid

    def select(self, t: type[T], id: int) -> T | None:
        row = self.execute(
            f"SELECT * FROM {t.__tablename__} WHERE id={id}",
        ).fetchone()
        if row is None:
            return None
        else:
            return t.parse(row)

    def selectall(self, t: type[T]) -> dict[int, T]:
        rows = self.execute(f"SELECT * FROM {t.__tablename__}").fetchall()
        return {row["id"]: t.parse(row) for row in rows}

    def delete(self, t: type[BASE], id: int) -> int | None:
        with self.sqlcon as con:
            return con.execute(
                f"DELETE FROM {t.__tablename__} WHERE id = {id}"
            ).rowcount

    def update(self, base: BASE) -> int | None:
        t = type(base)
        with self.sqlcon as con:
            return con.execute(
                f"""
                UPDATE {t.__tablename__} SET ({t.commna_joined_field_names()})
                = ({t.qmark_style_placeholders()})
                WHERE id = {base.id}
            """,
                base.qmark_style_sql_params(),
            ).rowcount

    def vacuum(self):
        pre = os.path.getsize(self.path)
        self.execute("VACUUM")
        post = os.path.getsize(self.path)
        return pre, post
