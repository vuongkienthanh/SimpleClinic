from dataclasses import dataclass
import datetime as dt
from . import main_state
from db import SeenToday, Patient, Connection, Gender, Visit
import datetime as dt


@dataclass(slots=True, match_args=False)
class SeenTodayStateItem:
    pid: int
    name: str
    gender: Gender
    birthdate: dt.date
    vid: int
    exam_datetime: dt.datetime


class SeenTodayState:
    def __get__(self, obj: "main_state.State", objtype=None) -> list[SeenTodayStateItem]:
        return obj._seentoday

    def __set__(self, obj: "main_state.State", _list: list[SeenTodayStateItem]):
        obj._seentoday = _list
        obj.mv.patient_book.seentodaylistctrl.rebuild(_list)

    @staticmethod
    def fetch(connection: Connection):
        query = f"""
            SELECT
                p.id AS pid,
                p.name,
                p.gender,
                p.birthdate,
                v.id as vid,
                v.exam_datetime
            FROM {SeenToday.__tablename__} AS st
            JOIN {Patient.__tablename__} AS p
            ON st.patient_id = p.id
            JOIN {Visit.__tablename__} as v
            ON st.visit_id = v.id
            ORDER BY v.exam_datetime DESC
        """
        rows = connection.execute(query).fetchall()
        return [SeenTodayStateItem(*row) for row in rows]
