import state
from misc.other_func import note_str_from_db
from state.linedrug_states.new_linedrug_list import NewLineDrugListStateItem
from state.linedrug_states.old_linedrug_list import OldLineDrugListStateItem

LineDrugListStateItem = OldLineDrugListStateItem | NewLineDrugListStateItem
LineDrugListState = (
    list[NewLineDrugListStateItem]
    | list[OldLineDrugListStateItem]
    | list[NewLineDrugListStateItem | OldLineDrugListStateItem]
)


class LineDrugState:
    def __get__(self, obj: "state.main_state.State", _) -> LineDrugListStateItem | None:
        return obj._linedrug

    def __set__(
        self, obj: "state.main_state.State", value: LineDrugListStateItem | None
    ) -> None:
        obj._linedrug = value
        match value:
            case None:
                self.onUnset(obj)
            case item:
                self.onSet(obj, item)

    def onSet(self, obj: "state.main_state.State", item: LineDrugListStateItem) -> None:
        mv = obj.mv
        page = mv.order_book.prescriptionpage
        obj.warehouse = obj.all_warehouse[item.warehouse_id]
        page.times.ChangeValue(str(item.times))
        page.dose.ChangeValue(item.dose)
        page.quantity.ChangeValue(str(item.quantity))
        page.note.ChangeValue(
            note_str_from_db(
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
        obj: "state.main_state.State",
    ) -> None:
        mv = obj.mv
        page = mv.order_book.prescriptionpage
        obj.warehouse = None
        page.times.Clear()
        page.dose.Clear()
        page.quantity.Clear()
        page.note.Clear()
        page.SetFocus()
