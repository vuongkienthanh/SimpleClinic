from misc.other_func import note_str
from . import main_state
from dataclasses import dataclass
from db import Connection, Visit, LineDrug, Warehouse


@dataclass(slots=True, match_args=False)
class NewLineDrugListStateItem:
    warehouse_id: int
    times: int
    dose: str
    quantity: int
    usage_note: str | None


@dataclass(slots=True, match_args=False)
class OldLineDrugListStateItem:
    id: int
    warehouse_id: int
    times: int
    dose: str
    quantity: int
    usage_note: str | None


LineDrugListStateItem = OldLineDrugListStateItem | NewLineDrugListStateItem


class LineDrugState:
    def __get__(self, obj: "main_state.State", _) -> LineDrugListStateItem | None:
        return obj._linedrug

    def __set__(
        self, obj: "main_state.State", value: LineDrugListStateItem | None
    ) -> None:
        obj._linedrug = value
        match value:
            case None:
                self.onUnset(obj)
            case item:
                self.onSet(obj, item)

    def onSet(self, obj: "main_state.State", item: LineDrugListStateItem) -> None:
        mv = obj.mv
        page = mv.order_book.prescriptionpage
        obj.warehouse = obj.all_warehouse[item.warehouse_id]
        page.times.ChangeValue(str(item.times))
        page.dose.ChangeValue(item.dose)
        page.quantity.ChangeValue(str(item.quantity))
        page.note.ChangeValue(
            note_str(
                obj.warehouse.usage,
                item.times,
                item.dose,
                obj.warehouse.usage_unit,
                item.usage_note,
            )
        )
        page.SetFocus()

    def onUnset(
        self,
        obj: "main_state.State",
    ) -> None:
        mv = obj.mv
        page = mv.order_book.prescriptionpage
        obj.warehouse = None
        page.times.Clear()
        page.dose.Clear()
        page.quantity.Clear()
        page.note.Clear()
        page.SetFocus()


class NewLineDrugListState:
    def __get__(self, obj: "main_state.State", _) -> list[NewLineDrugListStateItem]:
        return obj._new_linedrug_list


class OldLineDrugListState:
    def __get__(self, obj: "main_state.State", _) -> list[OldLineDrugListStateItem]:
        return obj._old_linedrug_list

    def __set__(self, obj: "main_state.State", _list: list[OldLineDrugListStateItem]):
        obj._old_linedrug_list = _list
        obj.mv.order_book.prescriptionpage.drug_list.rebuild(_list)

    @staticmethod
    def fetch(v: Visit, connection: Connection):
        query = f"""
            SELECT 
                ld.id, ld.drug_id as warehouse_id, 
                ld.times, ld.dose,
                ld.quantity, ld.usage_note
            FROM (SELECT * FROM {LineDrug.__tablename__}
                  WHERE visit_id = {v.id}
            ) AS ld
            JOIN {Warehouse.__tablename__} AS wh
            ON wh.id = ld.drug_id
        """
        rows = connection.execute(query).fetchall()
        return [OldLineDrugListStateItem(*row) for row in rows]
