from db.db_class import *
import os.path
import sqlite3
from decimal import Decimal


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

    def get_last_open_date(self) -> dt.date | None:
        return self.sqlcon.execute("SELECT last_open_date FROM last_open_date").fetchone()

    def insert(self, t: type[T], base: dict) -> int | None:
        with self.sqlcon as con:
            cur = con.execute(
                f"""
                INSERT INTO {t.table_name} ({t.commna_joined_field_names()})
                VALUES ({t.named_style_placeholders()})
            """,
                base,
            )
            assert cur.lastrowid is not None
            return cur.lastrowid

    def select(self, t: type[T], id: int) -> T | None:
        row = self.execute(
            f"SELECT * FROM {t.table_name} WHERE id={id}",
        ).fetchone()
        if row is None:
            return None
        else:
            return t.parse(row)

    def selectall(self, t: type[T]) -> list[T]:
        rows = self.execute(f"SELECT * FROM {t.table_name}").fetchall()
        return [t.parse(row) for row in rows]

    def delete(self, t: type[BASE], id: int) -> int | None:
        with self.sqlcon as con:
            return con.execute(f"DELETE FROM {t.table_name} WHERE id = {id}").rowcount

    def update(self, base: BASE) -> int | None:
        t = type(base)
        with self.sqlcon as con:
            return con.execute(
                f"""
                UPDATE {t.table_name} SET ({t.commna_joined_field_names()})
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
