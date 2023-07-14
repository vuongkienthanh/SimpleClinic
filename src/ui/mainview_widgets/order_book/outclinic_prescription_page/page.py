import wx

from ui.mainview_widgets.order_book.base_page import BasePage

from .buttons import *
from .widgets import *


class OutClinicPrescriptionPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)

        self.drug = wx.TextCtrl(self)
        self.drug.SetHint("Tên thuốc")
        self.quantity = wx.TextCtrl(self)
        self.quantity.SetHint("Số lượng")
        self.add_drug_btn = AddDrugButton(self)
        self.del_drug_btn = DeleteDrugButton(self)
        self.note = wx.TextCtrl(self)
        self.note.SetHint("Cách dùng")
        self.drug_list = DrugListCtrl(self)

        def static(s):
            return (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER | wx.RIGHT, 2)

        def widget(w, p=0, s=2):
            return (w, p, wx.RIGHT, s)

        drug_row = wx.BoxSizer(wx.HORIZONTAL)
        drug_row.AddMany(
            [
                static("Thuốc"),
                widget(self.drug, 10),
                static("Số lượng"),
                widget(self.quantity, 2),
            ]
        )
        note_row = wx.BoxSizer(wx.HORIZONTAL)
        note_row.AddMany(
            [
                static("Cách dùng"),
                widget(self.note, 1),
                widget(self.add_drug_btn),
                widget(self.del_drug_btn),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (drug_row, 0, wx.EXPAND),
                (note_row, 0, wx.EXPAND | wx.TOP, 3),
                (self.drug_list, 1, wx.EXPAND | wx.TOP, 3),
            ]
        )
        self.SetSizer(sizer)

    def check_wh_do_ti_filled(self):
        return all(
            [
                self.parent.mv.state.warehouse is not None,
                self.dose.Value.strip() != "",
                self.times.Value.strip() != "",
            ]
        )

    def check_wh_do_ti_qua_filled(self):
        return all(
            [
                self.parent.mv.state.warehouse is not None,
                self.dose.Value.strip() != "",
                self.times.Value.strip() != "",
                self.quantity.Value.strip() != "",
            ]
        )
