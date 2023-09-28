import wx

from misc import (
    calc_quantity,
    note_str_from_db,
    times_dose_quantity_note_str,
)
from state.linedrug_states import LineDrugListStateItem
from ui.generics import DoseTextCtrl, NumberTextCtrl, StateListCtrl
from ui.mainview_widgets.order_book.prescription_page import page


class DrugListCtrl(StateListCtrl):
    def __init__(self, parent: "page.PrescriptionPage"):
        super().__init__(parent, mv=parent.mv)
        self.AppendColumn("STT", 0.04)
        self.AppendColumn("Thuốc", 0.1)
        self.AppendColumn("Thành phần", 0.1)
        self.AppendColumn("Số cữ", 0.03)
        self.AppendColumn("Liều", 0.03)
        self.AppendColumn("Tổng cộng", 0.05)
        self.AppendColumn("Cách dùng", 0.15)
        if self.mv.config.outclinic_drug_checkbox:
            self.EnableCheckBoxes()
        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self.onCheck)
        self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.onUnCheck)

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
                wh.element,
                times,
                dose,
                quantity,
                note,
            ]
        )
        if item.outclinic:
            self.CheckItem(self.ItemCount - 1)

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
        self.SetItem(idx, 3, times)
        self.SetItem(idx, 4, dose)
        self.SetItem(idx, 5, quantity)
        self.SetItem(idx, 6, note)

    def pop_ui(self, idx: int):
        super().pop_ui(idx)
        # reset STT
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

    def onCheck(self, e: wx.ListEvent):
        idx: int = e.Index
        old = self.mv.state.old_linedrug_list
        new = self.mv.state.new_linedrug_list
        if idx < len(old):
            target = old
        else:
            idx -= len(old)
            target = new
        item = target[idx]
        item.outclinic = True
        self.mv.price.FetchPrice()
        e.Skip()

    def onUnCheck(self, e: wx.ListEvent):
        idx: int = e.Index
        old = self.mv.state.old_linedrug_list
        new = self.mv.state.new_linedrug_list
        if idx < len(old):
            target = old
        else:
            idx -= len(old)
            target = new
        item = target[idx]
        item.outclinic = False
        self.mv.price.FetchPrice()
        e.Skip()


class Times(NumberTextCtrl):
    def __init__(self, parent: "page.PrescriptionPage"):
        super().__init__(
            parent, size=parent.mv.config.header_size(0.03), style=wx.TE_PROCESS_ENTER
        )
        self.parent = parent
        self.SetHint("lần")
        self.Bind(wx.EVT_TEXT, self.onText)
        self.Bind(wx.EVT_TEXT_ENTER, self.focus_next)

    def onText(self, _):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.FetchQuantity()
            self.parent.note.FetchNote()

    def focus_next(self, _):
        self.parent.dose.SetFocus()


class Dose(DoseTextCtrl):
    def __init__(self, parent: "page.PrescriptionPage"):
        super().__init__(
            parent, size=parent.mv.config.header_size(0.03), style=wx.TE_PROCESS_ENTER
        )
        self.parent = parent
        self.SetHint("liều")
        self.Bind(wx.EVT_TEXT, self.onText)
        self.Bind(wx.EVT_TEXT_ENTER, self.focus_next)

    def onText(self, _):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.FetchQuantity()
            self.parent.note.FetchNote()

    def focus_next(self, _):
        self.parent.quantity.SetFocus()
        self.parent.quantity.SetInsertionPointEnd()


class Quantity(NumberTextCtrl):
    def __init__(self, parent: "page.PrescriptionPage"):
        super().__init__(
            parent, size=parent.mv.config.header_size(0.03), style=wx.TE_PROCESS_ENTER
        )
        self.parent = parent
        self.SetHint("Enter")
        self.Bind(wx.EVT_TEXT_ENTER, self.focus_next)

    def FetchQuantity(self):
        times = int(self.parent.times.Value)
        dose = self.parent.dose.Value
        days = self.parent.mv.days.Value
        wh = self.parent.mv.state.warehouse
        assert wh is not None
        res = calc_quantity(times, dose, days, wh.sale_unit, self.parent.mv.config)
        if res is not None:
            self.SetValue(str(res))
        else:
            self.Clear()

    def focus_next(self, _):
        self.parent.note.SetFocus()
        self.parent.note.SetInsertionPointEnd()


class NoteCtrl(wx.TextCtrl):
    def __init__(self, parent: "page.PrescriptionPage"):
        super().__init__(parent, style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.Bind(wx.EVT_TEXT_ENTER, self.onEnter)

    def onEnter(self, _):
        self.parent.add_drug_btn.Add()

    def FetchNote(self):
        wh = self.parent.parent.mv.state.warehouse
        assert wh is not None
        self.ChangeValue(
            note_str_from_db(
                wh.usage,
                self.parent.times.Value,
                self.parent.dose.Value,
                wh.usage_unit,
                None,
            )
        )
