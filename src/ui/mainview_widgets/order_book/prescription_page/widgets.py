from ui import mainview as mv
from state.linedrug_state import LineDrugListStateItem, LineDrugListState
from ui.mainview_widgets.order_book import order_book
from misc import (
    calc_quantity,
    k_tab,
    k_special,
    k_number,
    times_dose_quantity_note_str,
    note_str,
)
from ui.generic_widgets import NumberTextCtrl, DoseTextCtrl
import wx


class DrugListCtrl(wx.ListCtrl):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.parent = parent
        self.mv = parent.mv
        self.AppendColumn("STT", width=self.mv.config.header_width(0.02))
        self.AppendColumn("Thuốc", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Số cữ", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Liều", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Tổng cộng", width=self.mv.config.header_width(0.05))
        self.AppendColumn("Cách dùng", width=self.mv.config.header_width(0.15))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, _list: LineDrugListState):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: LineDrugListState):
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item: LineDrugListStateItem):
        wh = self.mv.state.all_warehouse[item.warehouse_id]
        times, dose, quantity, note = times_dose_quantity_note_str(
            wh.usage,
            item.times,
            item.dose,
            item.quantity,
            wh.usage_unit,
            wh.sale_unit,
            item.usage_note,
        )

        self.Append(
            [
                self.ItemCount + 1,
                wh.name,
                times,
                dose,
                quantity,
                note,
            ]
        )

    def update_ui(self, idx: int, item: LineDrugListStateItem):
        wh = self.mv.state.all_warehouse[item.warehouse_id]
        times, dose, quantity, note = times_dose_quantity_note_str(
            wh.usage,
            item.times,
            item.dose,
            item.quantity,
            wh.usage_unit,
            wh.sale_unit,
            item.usage_note,
        )
        self.SetItem(idx, 2, times)
        self.SetItem(idx, 3, dose)
        self.SetItem(idx, 4, quantity)
        self.SetItem(idx, 5, note)

    def pop_ui(self, idx: int):
        assert idx >= 0
        self.DeleteItem(idx)
        for i in range(idx, self.ItemCount):
            self.SetItem(i, 0, str(i + 1))

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        old = self.mv.state.old_linedrug_list
        new = self.mv.state.new_linedrug_list
        if idx < len(old):
            target = old
        else:
            idx -= len(old)
            target = new
        item = target[idx]
        state = self.mv.state
        state.warehouse = state.all_warehouse[item.warehouse_id]
        state.linedrug = item

    def onDeselect(self, _):
        self.mv.state.warehouse = None
        self.mv.state.linedrug = None


class Times(NumberTextCtrl):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, size=parent.mv.config.header_size(0.03))
        self.parent = parent
        self.mv = mv
        self.SetHint("lần")
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, _):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.FetchQuantity()
            self.parent.note.FetchNote()


class Dose(DoseTextCtrl):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, size=parent.mv.config.header_size(0.03))
        self.parent = parent
        self.mv = mv
        self.SetHint("liều")
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, _):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.FetchQuantity()
            self.parent.note.FetchNote()


class Quantity(NumberTextCtrl):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(
            parent, size=parent.mv.config.header_size(0.03), style=wx.TE_PROCESS_TAB
        )
        self.parent = parent
        self.mv = parent.mv
        self.SetHint("Enter")
        self.Bind(wx.EVT_CHAR, self.onChar)

    def FetchQuantity(self):
        times = int(self.parent.times.Value)
        dose = self.parent.dose.Value
        days = self.mv.days.Value
        wh = self.mv.state.warehouse
        assert wh is not None
        res = calc_quantity(times, dose, days, wh.sale_unit, self.mv.config)
        if res is not None:
            self.SetValue(str(res))
        else:
            self.Clear()

    def onChar(self, e: wx.KeyEvent):
        kc = e.KeyCode
        if kc in k_tab:
            if e.ShiftDown():
                self.parent.dose.SetFocus()
            else:
                self.parent.note.SetFocus()
                self.parent.note.SetInsertionPointEnd()
        elif kc in k_special + k_number:
            e.Skip()


class Note(wx.TextCtrl):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.Bind(wx.EVT_CHAR, self.onChar)

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.parent.add_drug_btn.Add()
        elif e.KeyCode == k_tab:
            pass
        else:
            e.Skip()

    def FetchNote(self):
        wh = self.parent.parent.mv.state.warehouse
        assert wh is not None
        self.ChangeValue(
            note_str(
                wh.usage,
                self.parent.times.Value,
                self.parent.dose.Value,
                wh.usage_unit,
                None,
            )
        )
