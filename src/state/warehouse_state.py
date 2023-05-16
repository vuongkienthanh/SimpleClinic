from db import Warehouse
from . import main_state


class WarehouseState:
    def __get__(self, obj: "main_state.State", objtype=None) -> Warehouse | None:
        return obj._warehouse

    def __set__(self, obj: "main_state.State", value: Warehouse | None):
        obj._warehouse = value
        if value:
            self.onSet(obj, value)
        else:
            self.onUnset(obj)

    def onSet(self, obj: "main_state.State", wh: Warehouse) -> None:
        pg = obj.mv.order_book.prescriptionpage
        pg.drug_picker.SetValue(wh.name)
        pg.usage.SetLabel(wh.usage)
        pg.usage_unit.SetLabel(wh.usage_unit)
        pg.sale_unit.SetLabel(wh.sale_unit if wh.sale_unit else wh.usage_unit)
        pg.drug_picker.SelectAll()

    def onUnset(self, obj: "main_state.State") -> None:
        pg = obj.mv.order_book.prescriptionpage
        pg.drug_picker.ChangeValue("")
        pg.usage.SetLabel("{Cách dùng}")
        pg.usage_unit.SetLabel("{Đơn vị}")
        pg.sale_unit.SetLabel("{Đơn vị}")
