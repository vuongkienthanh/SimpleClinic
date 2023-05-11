from db import Warehouse
from core import state
from core import menubar
from misc import bd_to_vn_age
import wx


class WarehouseState:
    def __get__(self, obj: "state.State", objtype=None) -> Warehouse | None:
        return obj._warehouse

    def __set__(self, obj: "state.State", value: Warehouse | None):
        obj._warehouse = value
        if value:
            self.onSet(obj, value)
        else:
            self.onUnset(obj)

    def onSet(self, obj: "state.State", wh: Warehouse) -> None:
        pg = obj.mv.order_book.prescriptionpage
        pg.drug_picker.SetValue(wh.name)
        pg.usage.SetLabel(wh.usage)
        pg.usage_unit.SetLabel(wh.usage_unit)
        pg.sale_unit.SetLabel(wh.sale_unit if wh.sale_unit else wh.usage_unit)
        pg.drug_picker.SelectAll()

    def onUnset(self, obj: "state.State") -> None:
        pg = obj.mv.order_book.prescriptionpage
        pg.drug_picker.ChangeValue("")
        pg.usage.SetLabel("{Cách dùng}")
        pg.usage_unit.SetLabel("{Đơn vị}")
        pg.sale_unit.SetLabel("{Đơn vị}")
        pg.times.Clear()
        pg.dose.Clear()
        pg.quantity.Clear()
        pg.note.Clear()
