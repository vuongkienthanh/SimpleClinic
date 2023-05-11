from dataclasses import dataclass
import datetime as dt
from core import state
from db import Connection, Visit, Patient
from misc import Config


@dataclass(slots=True, match_args=False)
class VisitListStateItem:
    vid: int
    exam_datetime: dt.datetime
    diagnosis: str


class VisitListState:
    def __get__(self, obj: "state.State", objtype=None) -> list[VisitListStateItem]:
        return obj._visit_list

    def __set__(self, obj: "state.State", lv: list[VisitListStateItem]):
        obj._visit_list = lv
        obj.mv.visit_list.rebuild(lv)

    @staticmethod
    def fetch(p: Patient, connection: Connection, config: Config):
        query = f"""
            SELECT id AS vid, exam_datetime,diagnosis
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
