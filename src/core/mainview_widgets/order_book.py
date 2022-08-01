from core.mainview_widgets.prescription_widgets import *
from core.mainview_widgets.procedure_widgets import *
from core import mainview

import wx


class OrderBook(wx.Notebook):
    """Container for PrescriptionPage"""

    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent)
        self.mv = parent
        self.page0 = PrescriptionPage(self)
        self.page1 = ProcedurePage(self)
        self.AddPage(page=self.page0,
                     text='Toa thuốc', select=True)
        self.AddPage(page=self.page1,
                     text='Thủ thuật')


class PrescriptionPage(wx.Panel):

    def __init__(self, parent: OrderBook):
        super().__init__(parent)
        self.parent = parent

        self.drug_picker = DrugPicker(self)
        self.usage = wx.StaticText(
            self, label="{Cách dùng}", style=wx.ALIGN_RIGHT | wx.ST_NO_AUTORESIZE)
        self.times = Times(self)
        self.dose = Dose(self)
        self.quantity = Quantity(self)
        self.usage_unit = wx.StaticText(self, label='{Đơn vị}')
        self.sale_unit = wx.StaticText(self, label='{Đơn vị}')
        self.note = Note(self)
        self.add_drug_btn = AddDrugButton(self)
        self.del_drug_btn = DelDrugButton(self)
        self.drug_list = DrugList(self)
        self.reuse_druglist_btn = ReuseDrugListButton(self)
        self.use_sample_prescription_btn = UseSamplePrescriptionBtn(self)

        def static(s):
            return (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER | wx.RIGHT, 2)

        def widget(w, p=0, s=2):
            return (w, p, wx.RIGHT, s)

        drug_row = wx.BoxSizer(wx.HORIZONTAL)
        drug_row.AddMany([
            static('Thuốc'),
            widget(self.drug_picker, 1),
            (self.usage, 0, wx.ALIGN_CENTER | wx.RIGHT, 2),
            widget(self.times),
            static("lần, lần"),
            widget(self.dose),
            (self.usage_unit, 0, wx.ALIGN_CENTER | wx.RIGHT, 10),
            static(u"\u21D2"),
            widget(self.quantity),
            (self.sale_unit, 0, wx.ALIGN_CENTER | wx.RIGHT, 2),
        ])
        usage_row = wx.BoxSizer(wx.HORIZONTAL)
        usage_row.AddMany([
            static('Cách dùng:'),
            widget(self.note, 1, 5),
            widget(self.add_drug_btn),
            widget(self.del_drug_btn)
        ])
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddMany([
            widget(self.reuse_druglist_btn),
            widget(self.use_sample_prescription_btn),
        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (drug_row, 0, wx.EXPAND),
            (usage_row, 0, wx.EXPAND),
            (self.drug_list, 1, wx.EXPAND | wx.TOP, 3),
            (btn_row, 0, wx.EXPAND | wx.TOP, 3),
        ])
        self.SetSizer(sizer)

    def check_wh_do_ti_filled(self):
        return all([
            self.parent.mv.state.warehouse is not None,
            self.dose.Value.strip() != '',
            self.times.Value.strip() != '',
        ])

    def check_all_filled(self):
        return all([
            self.parent.mv.state.warehouse is not None,
            self.dose.Value.strip() != '',
            self.times.Value.strip() != '',
            self.quantity.Value.strip() != '',
        ])


class ProcedurePage(wx.Panel):
    def __init__(self, parent: OrderBook):
        super().__init__(parent)
        self.parent = parent
        self.mv = parent.mv

        self.choice = wx.Choice(
            self, choices=[pr.name for pr in self.mv.state.procedurelist])
        self.addbtn = AddProcedureButton(self)
        self.delbtn = DelProcedureButton(self)
        self.procedurelistctrl = ProcedureListCtrl(self)

        choice_row = wx.BoxSizer(wx.HORIZONTAL)
        choice_row.AddMany([
            (self.choice, 1, wx.RIGHT, 5),
            (self.addbtn, 0, wx.RIGHT, 5),
            (self.delbtn, 0)
        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (choice_row, 0, wx.EXPAND | wx.ALL, 5),
            (self.procedurelistctrl, 1, wx.EXPAND | wx.ALL, 5)
        ])
        self.SetSizerAndFit(sizer)
