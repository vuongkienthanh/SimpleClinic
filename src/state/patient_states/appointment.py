import datetime as dt
from dataclasses import dataclass

import state
from db import Appointment, Connection, Gender, Patient


@dataclass(slots=True, match_args=False)
class AppointmentStateItem:
    patient_id: int
    name: str
    gender: Gender
    birthdate: dt.date


class AppointmentState:
    def __get__(self, obj: "state.main_state.State", _) -> list[AppointmentStateItem]:
        return obj._appointment

    def __set__(self, obj: "state.main_state.State", _list: list[AppointmentStateItem]):
        obj._appointment = _list
        obj.mv.patient_book.appointmentlistctrl.rebuild(_list)

    @staticmethod
    def fetch(connection: Connection) -> list[AppointmentStateItem]:
        query = f"""
            SELECT
                p.id AS patient_id,
                p.name,
                p.gender,
                p.birthdate
            FROM {Appointment.__tablename__} AS ap
            JOIN {Patient.__tablename__} AS p
            ON ap.patient_id = p.id
            WHERE ap.appointed_date=?
        """
        rows = connection.execute(query, (dt.date.today(),)).fetchall()
        return [AppointmentStateItem(*row) for row in rows]
