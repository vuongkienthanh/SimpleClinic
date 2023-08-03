from dataclasses import dataclass
from misc.config import Config

import state
from db import Connection, LineDrug, Visit, Warehouse

_cache = dict()


@dataclass(slots=True, match_args=False)
class OldLineDrugListStateItem:
    id: int
    warehouse_id: int
    times: int
    dose: str
    quantity: int
    usage_note: str | None
    outclinic: bool


class OldLineDrugListState:
    def __get__(
        self, obj: "state.main_state.State", _
    ) -> list[OldLineDrugListStateItem]:
        return obj._old_linedrug_list

    def __set__(
        self, obj: "state.main_state.State", _list: list[OldLineDrugListStateItem]
    ):
        obj._old_linedrug_list = _list
        obj.mv.order_book.prescriptionpage.drug_list.rebuild(_list)

    @staticmethod
    def fetch(v: Visit, connection: Connection):
        if v.id in _cache:
            return _cache[v.id]
        else:
            query = f"""
                SELECT
                    ld.id, ld.warehouse_id,
                    ld.times, ld.dose,
                    ld.quantity, ld.usage_note, (ld.miscs ->> '$.outclinic' IS NOT NULL) AS outclinic
                FROM (SELECT * FROM {LineDrug.__tablename__}
                      WHERE visit_id = {v.id}
                ) AS ld
                JOIN {Warehouse.__tablename__} AS wh
                ON wh.id = ld.warehouse_id
            """
            rows = connection.execute(query).fetchall()
            result = [OldLineDrugListStateItem(*row) for row in rows]
            _cache[v.id] = result
            return result

    @staticmethod
    def clear_cache():
        _cache.clear()
