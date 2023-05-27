from db.classes import Gender, BASE
from db.sql import *
import os.path
import sqlite3
from decimal import Decimal
import datetime as dt


class Connection:
    def __init__(self, path: str):
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
        self.sqlcon = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.sqlcon.row_factory = sqlite3.Row
        self.path = path
        self.sqlcon.execute("PRAGMA foreign_keys=ON")

    def execute(self, *arg, **kwarg):
        return self.sqlcon.execute(*arg, **kwarg)

    def executemany(self, *arg, **kwarg):
        return self.sqlcon.executemany(*arg, **kwarg)

    def executescript(self, *arg, **kwarg):
        return self.sqlcon.executescript(*arg, **kwarg)

    def commit(self):
        return self.sqlcon.commit()

    def rollback(self):
        return self.sqlcon.rollback()

    def __enter__(self):
        return self.sqlcon.__enter__()

    def __exit__(self, *arg, **kwarg):
        return self.sqlcon.__exit__(*arg, **kwarg)

    def close(self):
        self.execute("PRAGMA optimize")
        self.sqlcon.close()

    def make_db(self):
        self.executescript(create_table_sql)
        self.executescript(create_index_sql)
        self.executescript(create_view_sql)
        self.executescript(create_trigger_sql)
        self.executescript(finalized_sql)

    def update_last_open_date(self) -> dt.date | None:
        self.execute("UPDATE singleton SET last_open_date = ?", (dt.date.today(),))
        self.commit()

    def insert(self, t: type[T], base: dict) -> int:
        with self:
            cur = self.execute(
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
        with self:
            return self.execute(
                f"DELETE FROM {t.__tablename__} WHERE id = {id}"
            ).rowcount

    def update(self, base: BASE) -> int | None:
        t = type(base)
        with self:
            return self.execute(
                f"""
                UPDATE {t.__tablename__} SET ({t.commna_joined_field_names()})
                = ({t.qmark_style_placeholders()})
                WHERE id = {base.id}
            """,
                base.qmark_style_sql_params(),
            ).rowcount
