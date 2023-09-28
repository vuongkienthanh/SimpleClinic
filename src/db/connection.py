import datetime as dt
import sqlite3
from typing import overload

from db.models import BASE, Gender
from db.sql import *


class Connection:
    def __init__(self, path: str):
        def custom_type_date():
            def adapt(date: dt.date) -> str:
                return date.isoformat()

            def convert(b: bytes) -> dt.date:
                return dt.date.fromisoformat(b.decode())

            sqlite3.register_adapter(dt.date, adapt)
            sqlite3.register_converter("date", convert)

        def custom_type_datetime():
            def adapt(datetime: dt.datetime) -> str:
                return datetime.isoformat()

            def convert(b: bytes) -> dt.datetime:
                return dt.datetime.fromisoformat(b.decode())

            sqlite3.register_adapter(dt.datetime, adapt)
            sqlite3.register_converter("timestamp", convert)

        def custom_type_gender():
            def adapt(gender: Gender) -> int:
                return gender.value

            def convert(b: bytes) -> Gender:
                return Gender(int(b))

            sqlite3.register_adapter(Gender, adapt)
            sqlite3.register_converter("GENDER", convert)

        custom_type_date()
        custom_type_datetime()
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

    def update_last_open_date(self) -> None:
        self.execute("UPDATE singleton SET last_open_date = ?", (dt.date.today(),))
        self.commit()

    def insert(self, t: type[T], base_without_id_dict: dict) -> int:
        with self:
            cur = self.execute(
                f"""
                INSERT INTO {t.__tablename__} ({t.commna_joined_fields()})
                VALUES ({t.named_style_placeholders()})
            """,
                base_without_id_dict,
            )
            assert cur.lastrowid is not None
            return cur.lastrowid

    def select(self, t: type[T], id: int) -> T | None:
        row = self.execute(
            f"""
            SELECT id, {t.commna_joined_select_fields()}
            FROM {t.__tablename__} WHERE id={id}""",
        ).fetchone()
        if row is None:
            return None
        else:
            return t.parse(row)

    def selectall(self, t: type[T]) -> dict[int, T]:
        rows = self.execute(
            f"""
            SELECT id, {t.commna_joined_select_fields()}
            FROM {t.__tablename__}"""
        ).fetchall()
        return {row["id"]: t.parse(row) for row in rows}

    @overload
    def delete(self, target: BASE) -> int:
        ...

    @overload
    def delete(self, target: type[BASE], id: int) -> int:
        ...

    def delete(
        self,
        target,
        id: int | None = None,
    ) -> int:
        match id:
            case None:
                with self:
                    return self.execute(
                        f"DELETE FROM {target.__tablename__} WHERE id = {target.id}"
                    ).rowcount
            case _:
                with self:
                    return self.execute(
                        f"DELETE FROM {target.__tablename__} WHERE id = {id}"
                    ).rowcount

    def update(self, item: BASE) -> int:
        with self:
            return self.execute(
                f"""
                UPDATE {item.__tablename__} SET ({item.commna_joined_fields()})
                = ({item.qmark_style_placeholders()})
                WHERE id = {item.id}
            """,
                item.qmark_style_sql_params(),
            ).rowcount
