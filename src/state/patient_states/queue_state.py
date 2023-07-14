import datetime as dt
from dataclasses import dataclass

import state
from db import Connection, Gender, Patient, Queue


@dataclass(slots=True, match_args=False)
class QueueStateItem:
    patient_id: int
    name: str
    gender: Gender
    birthdate: dt.date
    added_datetime: dt.datetime


class QueueState:
    def __get__(self, obj: "state.main_state.State", _) -> list[QueueStateItem]:
        return obj._queue

    def __set__(self, obj: "state.main_state.State", _list: list[QueueStateItem]):
        obj._queue = _list
        obj.mv.patient_book.queuelistctrl.rebuild(_list)

    @staticmethod
    def fetch(connection: Connection):
        query = f"""
        SELECT
            p.id AS patient_id,
            p.name,
            p.gender,
            p.birthdate,
            q.added_datetime
        FROM {Queue.__tablename__} AS q
        JOIN {Patient.__tablename__} AS p
        ON q.patient_id = p.id
        ORDER BY q.added_datetime ASC
        """
        rows = connection.execute(query).fetchall()
        return [QueueStateItem(*row) for row in rows]
