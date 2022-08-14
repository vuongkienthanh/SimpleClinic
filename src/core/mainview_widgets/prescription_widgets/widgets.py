from core import mainview as mv
from core.mainview_widgets import order_book
from core.init import (
    config,
    k_tab,
    k_number,
    k_special,
    size,
    tsize,
    drug_list_background_color,
    drug_times_background_color,
    drug_dose_background_color,
    drug_quantity_background_color,
    drug_note_background_color
)
import other_func as otf
from core.generic import NumberTextCtrl, DoseTextCtrl
import wx
import sqlite3


class DrugListItem():
    __slots__ = ["drug_id", "times", "dose", "quantity", "name",
                 "note", "usage", "usage_unit", "sale_unit", "sale_price"]

    def __init__(self,
                 drug_id: int,
                 times: int,
                 dose: str,
                 quantity: int,
                 name: str,
                 note: str | None,
                 usage: str,
                 usage_unit: str,
                 sale_unit: str | None,
                 sale_price: int):
        self.drug_id = drug_id
        self.times = times
        self.dose = dose
        self.quantity = quantity
        self.name = name
        self.note = note
        self.usage = usage
        self.usage_unit = usage_unit
        self.sale_unit = sale_unit
        self.sale_price = sale_price

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'DrugListItem':
        return cls(
            drug_id=int(row['drug_id']),
            times=int(row['times']),
            dose=row['dose'],
            quantity=int(row['quantity']),
            name=row['name'],
            note=row['note'],
            usage=row['usage'],
            usage_unit=row['usage_unit'],
            sale_unit=row['sale_unit'],
            sale_price=int(row['sale_price']),
        )

    @classmethod
    def from_mv(cls, mv: 'mv.MainView') -> 'DrugListItem':
        wh = mv.state.warehouse
        page = mv.order_book.page0
        assert wh is not None
        return cls(
            drug_id=wh.id,
            name=wh.name,
            times=int(page.times.Value.strip()),
            dose=page.dose.Value.strip(),
            quantity=int(page.quantity.Value.strip()),
            usage=wh.usage,
            usage_unit=wh.usage_unit,
            sale_unit=wh.sale_unit,
            sale_price=wh.sale_price,
            note=page.note.GetNote()
        )

    def expand(self) -> 'DrugListItem':
        return DrugListItem(
            drug_id=self.drug_id,
            name=self.name,
            times=self.times,
            dose=self.dose,
            quantity=self.quantity,
            usage=self.usage,
            usage_unit=self.usage_unit,
            sale_unit=self.sale_unit or self.usage_unit,
            sale_price=self.sale_price,
            note=self.note or otf.get_usage_note_str(
                usage=self.usage,
                times=self.times,
                dose=self.dose,
                usage_unit=self.usage_unit
            )
        )


class DrugList(wx.ListCtrl):

    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.SetBackgroundColour(wx.Colour(220, 220, 220))
        self.parent = parent
        self.mv = parent.parent.mv
        self.SetBackgroundColour(drug_list_background_color)
        self.d_list: list[DrugListItem] = []
        self.AppendColumn('STT', width=size(0.02))
        self.AppendColumn('Thuốc', width=size(0.1))
        self.AppendColumn('Số cữ', width=size(0.03))
        self.AppendColumn('Liều', width=size(0.03))
        self.AppendColumn('Tổng cộng', width=size(0.05))
        self.AppendColumn('Cách dùng', width=size(0.15))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def clear(self):
        self.DeleteAllItems()
        self.d_list.clear()

    def rebuild(self, lld: list[sqlite3.Row]):
        self.clear()
        for item in lld:
            self.append(DrugListItem.from_row(item))

    def append(self, item: DrugListItem):
        def append_list(item: DrugListItem):
            self.d_list.append(item)

        def append_ui(item: DrugListItem):
            _item = item.expand()
            assert _item.sale_unit is not None
            assert _item.note is not None
            self.Append([
                self.ItemCount + 1,
                _item.name,
                str(_item.times),
                _item.dose + ' ' + _item.usage_unit,
                str(_item.quantity) + ' ' + _item.sale_unit,
                _item.note
            ])
        append_list(item)
        append_ui(item)

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
            self.SetItem(idx, 3, _item.dose + ' ' + _item.usage_unit)
            self.SetItem(idx, 4, str(_item.quantity) + ' ' + _item.sale_unit)
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
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, size=tsize(0.03))
        self.parent = parent
        self.SetHint('lần')
        self.SetBackgroundColour(drug_times_background_color)
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.FetchQuantity()
            self.parent.note.FetchNote()


class Dose(DoseTextCtrl):
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, size=tsize(0.03))
        self.parent = parent
        self.SetHint('liều')
        self.SetBackgroundColour(drug_dose_background_color)
        self.Bind(wx.EVT_TEXT, self.onText)

    def onText(self, e):
        if self.parent.check_wh_do_ti_filled():
            self.parent.quantity.FetchQuantity()
            self.parent.note.FetchNote()


class Quantity(NumberTextCtrl):

    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, size=tsize(0.03), style=wx.TE_PROCESS_TAB)
        self.parent = parent
        self.SetHint('Enter')
        self.SetBackgroundColour(drug_quantity_background_color)
        self.Bind(wx.EVT_CHAR, self.onChar)

    def FetchQuantity(self):
        mv = self.parent.parent.mv
        times = int(self.parent.times.GetValue())
        dose = self.parent.dose.GetValue()
        days = mv.days.GetValue()
        wh = mv.state.warehouse
        assert wh is not None
        res = otf.calc_quantity(times, dose, days, wh.sale_unit,
                                config['thuoc_ban_mot_don_vi'])
        if res is not None:
            self.SetValue(str(res))
        else:
            self.SetValue('')

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
    def __init__(self, parent: 'order_book.PrescriptionPage'):
        super().__init__(parent, style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.Bind(wx.EVT_CHAR, self.onChar)
        self.SetBackgroundColour(drug_note_background_color)

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
        self.ChangeValue(otf.get_usage_note_str(
            usage=wh.usage,
            times=self.parent.times.GetValue(),
            dose=self.parent.dose.GetValue(),
            usage_unit=wh.usage_unit
        ))

    def SetNote(self, s: str | None):
        if s is None:
            wh = self.parent.parent.mv.state.warehouse
            assert wh is not None
            s = otf.get_usage_note_str(
                usage=wh.usage,
                times=self.parent.times.Value,
                dose=self.parent.dose.Value,
                usage_unit=wh.usage_unit
            )
        self.ChangeValue(s)

    def GetNote(self) -> str | None:
        _s: str = self.GetValue()
        s = _s.strip()
        wh = self.parent.parent.mv.state.warehouse
        assert wh is not None
        if s == '' or s == otf.get_usage_note_str(
            usage=wh.usage,
            times=self.parent.times.Value,
            dose=self.parent.dose.Value,
            usage_unit=wh.usage_unit
        ):
            return None
        else:
            return s
