import datetime as dt
from dataclasses import dataclass

import state
from db import Connection, Patient, Visit
from misc import Config


@dataclass(slots=True, match_args=False)
class VisitListStateItem:
    visit_id: int
    exam_datetime: dt.datetime
    diagnosis: str


class VisitListState:
    def __get__(self, obj: "state.main_state.State", _) -> list[VisitListStateItem]:
        return obj._visit_list

    def __set__(self, obj: "state.main_state.State", _list: list[VisitListStateItem]):
        obj._visit_list = _list
        obj.mv.visit_list.rebuild(_list)

    @staticmethod
    def fetch(p: Patient, connection: Connection, config: Config):
        query = f"""
            SELECT id AS visit_id, exam_datetime,diagnosis
            FROM {Visit.__tablename__}
            WHERE {Visit.__tablename__}.patient_id = {p.id}
            ORDER BY exam_datetime DESC
        """
        if config.display_recent_visit_count >= 0:
            query += f"""
                LIMIT {config.display_recent_visit_count}
            """
        rows = connection.execute(query).fetchall()
        return [VisitListStateItem(*row) for row in rows]
