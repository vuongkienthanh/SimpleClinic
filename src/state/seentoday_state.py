import datetime as dt
from dataclasses import dataclass

from db import Connection, Gender, Patient, SeenToday, Visit

from . import main_state


@dataclass(slots=True, match_args=False)
class SeenTodayStateItem:
    patient_id: int
    name: str
    gender: Gender
    birthdate: dt.date
    visit_id: int
    exam_datetime: dt.datetime


class SeenTodayState:
    def __get__(self, obj: "main_state.State", _) -> list[SeenTodayStateItem]:
        return obj._seentoday

    def __set__(self, obj: "main_state.State", _list: list[SeenTodayStateItem]):
        obj._seentoday = _list
        obj.mv.patient_book.seentodaylistctrl.rebuild(_list)

    @staticmethod
    def fetch(connection: Connection):
        query = f"""
            SELECT
                p.id AS patient_id,
                p.name,
                p.gender,
                p.birthdate,
                v.id as visit_id,
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
