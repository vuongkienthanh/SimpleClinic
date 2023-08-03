import state
from db import Connection, Procedure


class AllProcedureState:
    def __get__(self, obj: "state.main_state.State", _) -> dict[int, Procedure]:
        return obj._all_procedure

    def __set__(self, obj: "state.main_state.State", _dict: dict[int, Procedure]):
        obj._all_procedure = _dict
        obj.mv.order_book.procedurepage.procedure_picker.rebuild(_dict)

    @staticmethod
    def fetch(connection: Connection):
        return connection.selectall(Procedure)
