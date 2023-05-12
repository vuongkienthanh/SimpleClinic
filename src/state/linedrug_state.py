from .linedrugs_list_state import LineDrugListStateItem
from . import main_state
from .warehouse_state import  WarehouseState


class LineDrugState:
    def __get__(self, obj: "main_state.State", objtype=None) -> LineDrugListStateItem | None:
        return obj._linedrug

    def __set__(self, obj: "main_state.State", value: LineDrugListStateItem | None):
        obj._linedrug = value
        if value:
            self.onSet(obj, value)
        else:
            self.onUnset(obj)

    def onSet(self, obj: "main_state.State", item: LineDrugListStateItem) -> None:
        mv = obj.mv
        page = mv.order_book.prescriptionpage
        obj.warehouse =  WarehouseState.get_from_state(item.drug_id, obj)
        
        page.SetFocus()

    def onUnset(
        self,
        obj: "main_state.State",
    ) -> None:
        mv = obj.mv
        page = mv.order_book.prescriptionpage
        page.SetFocus()
