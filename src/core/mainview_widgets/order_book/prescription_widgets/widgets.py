from core import mainview as mv
from core.state.linedrugs_list_state import LineDrugListStateItem
from core.mainview_widgets.order_book import order_book
from misc import get_usage_note_str, calc_quantity, k_tab, k_special, k_number
from core.generic_widgets import NumberTextCtrl, DoseTextCtrl
import wx
import sqlite3


# class DrugListItem:
#
#
#     @classmethod
#     def from_mv(cls, mv: "mv.MainView") -> "DrugListItem":
#         wh = mv.state.warehouse
#         page = mv.order_book.prescriptionpage
#         assert wh is not None
#         return cls(
#             drug_id=wh.id,
#             name=wh.name,
#             times=int(page.times.Value.strip()),
#             dose=page.dose.Value.strip(),
#             quantity=int(page.quantity.Value.strip()),
#             usage=wh.usage,
#             usage_unit=wh.usage_unit,
#             sale_unit=wh.sale_unit,
#             sale_price=wh.sale_price,
#             note=page.note.GetNote(),
#         )
#


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

    def build(self, _list: list[LineDrugListStateItem]):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: list[LineDrugListStateItem]):
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item: LineDrugListStateItem):
        self.Append(
            [
                self.ItemCount + 1,
                item.name,
                str(item.times),
                item.dose + " " + item.usage_unit,
                str(item.quantity) + " " + item.sale_unit,
                item.note,
            ]
        )

    def update(self, idx: int, item: DrugListItem):
        def update_list(idx: int, item: DrugListItem):
            self.d_list[idx].name = item.name
            self.d_list[idx].times = item.times
            self.d_list[idx].dose = item.dose
            self.d_list[idx].quantity = item.quantity
            self.d_list[idx].usage = item.usage
            self.d_list[idx].usage_unit = item.usage_unit
            self.d_list[idx].sale_price = item.sale_price
            self.d_list[idx].sale_unit = item.sale_unit
            self.d_list[idx].note = item.note

        def update_ui(idx: int, item: DrugListItem):
            _item = item.expand()
            assert _item.sale_unit is not None
            assert _item.note is not None
            self.SetItem(idx, 2, str(_item.times))
            self.SetItem(idx, 3, _item.dose + " " + _item.usage_unit)
            self.SetItem(idx, 4, str(_item.quantity) + " " + _item.sale_unit)
            self.SetItem(idx, 5, _item.note)

        assert idx >= 0
        update_list(idx, item)
        update_ui(idx, item)

    def pop(self, idx: int):
        assert idx >= 0
        self.d_list.pop(idx)
        self.DeleteItem(idx)
        for i in range(self.ItemCount):
            self.SetItem(i, 0, str(i + 1))

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        item = self.d_list[idx]
        state = self.mv.state
        state.warehouse = state.get_wh_by_id(item.drug_id)
        assert state.warehouse is not None
        self.parent.times.ChangeValue(str(item.times))
        self.parent.dose.ChangeValue(item.dose)
        self.parent.quantity.ChangeValue(str(item.quantity))
        self.parent.note.SetNote(item.note)

    def onDeselect(self, e: wx.ListEvent):
        self.mv.state.warehouse = None

    def upsert(self):
        wh = self.mv.state.warehouse
        assert wh is not None
        item = DrugListItem.from_mv(self.mv)
        try:
            # update
            index: int = [d.drug_id for d in self.d_list].index(wh.id)
            self.update(index, item)
        except ValueError:
            # insert
            self.append(item)


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
        times = int(self.parent.times.GetValue())
        dose = self.parent.dose.GetValue()
        days = self.mv.days.GetValue()
        wh = self.mv.state.warehouse
        assert wh is not None
        res = calc_quantity(times, dose, days, wh.sale_unit, self.mv.config)
        if res is not None:
            self.SetValue(str(res))
        else:
            self.SetValue("")

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
            get_usage_note_str(
                usage=wh.usage,
                times=self.parent.times.GetValue(),
                dose=self.parent.dose.GetValue(),
                usage_unit=wh.usage_unit,
            )
        )

    def SetNote(self, s: str | None):
        if s is None:
            wh = self.parent.parent.mv.state.warehouse
            assert wh is not None
            s = get_usage_note_str(
                usage=wh.usage,
                times=self.parent.times.Value,
                dose=self.parent.dose.Value,
                usage_unit=wh.usage_unit,
            )
        self.ChangeValue(s)

    def GetNote(self) -> str | None:
        _s: str = self.GetValue()
        s = _s.strip()
        wh = self.parent.parent.mv.state.warehouse
        assert wh is not None
        if s == "" or s == get_usage_note_str(
            usage=wh.usage,
            times=self.parent.times.Value,
            dose=self.parent.dose.Value,
            usage_unit=wh.usage_unit,
        ):
            return None
        else:
            return s
