from dataclasses import dataclass

import state
from db import Connection, LineProcedure, Procedure, Visit

_cache = dict()


@dataclass(slots=True, match_args=False)
class OldLineProcedureListStateItem:
    id: int
    procedure_id: int


class OldLineProcedureListState:
    def __get__(
        self, obj: "state.main_state.State", _
    ) -> list[OldLineProcedureListStateItem]:
        return obj._old_lineprocedure_list

    def __set__(
        self, obj: "state.main_state.State", _list: list[OldLineProcedureListStateItem]
    ):
        obj._old_lineprocedure_list = _list
        obj.mv.order_book.procedurepage.procedure_list.rebuild(_list)

    @staticmethod
    def fetch(v: Visit, connection: Connection) -> list[OldLineProcedureListStateItem]:
        if v.id in _cache:
            return _cache[v.id]
        else:
            query = f"""
                SELECT 
                    lp.id, pr.id AS procedure_id
                FROM 
                    (SELECT * FROM {LineProcedure.__tablename__}
                        WHERE visit_id = {v.id}
                    ) AS lp
                JOIN {Procedure.__tablename__} AS pr
                ON pr.id = lp.procedure_id
            """
            rows = connection.execute(query).fetchall()
            result = [OldLineProcedureListStateItem(*row) for row in rows]
            _cache[v.id] = result
            return result

    @staticmethod
    def clear_cache():
        _cache.clear()
