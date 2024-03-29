import state
from db import Warehouse
from misc import sale_unit_from_db


class WarehouseState:
    def __get__(self, obj: "state.main_state.State", _) -> Warehouse | None:
        return obj._warehouse

    def __set__(self, obj: "state.main_state.State", value: Warehouse | None):
        obj._warehouse = value
        match value:
            case None:
                self.onUnset(obj)
            case val:
                self.onSet(obj, val)

    def onSet(self, obj: "state.main_state.State", wh: Warehouse) -> None:
        pg = obj.mv.order_book.prescriptionpage
        pg.drug_picker.SetValue(wh.name)
        pg.usage.SetLabel(wh.usage)
        pg.usage_unit.SetLabel(wh.usage_unit)
        pg.sale_unit.SetLabel(sale_unit_from_db(wh.sale_unit, wh.usage_unit))

    def onUnset(self, obj: "state.main_state.State") -> None:
        pg = obj.mv.order_book.prescriptionpage
        pg.drug_picker.ChangeValue("")
        pg.usage.SetLabel("{Cách dùng}")
        pg.usage_unit.SetLabel("{Đơn vị}")
        pg.sale_unit.SetLabel("{Đơn vị}")
