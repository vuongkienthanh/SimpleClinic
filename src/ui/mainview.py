import db
from misc import Config, vn_weekdays
from state import State
from ui.generic_widgets import (
    ReadonlyVNAgeCtrl,
    PhoneTextCtrl,
    DateTextCtrl,
    WeightCtrl,
)
from ui.mainview_widgets import (
    GetWeightBtn,
    DaysCtrl,
    UpdateQuantityBtn,
    RecheckCtrl,
    NoRecheckBtn,
    PriceCtrl,
    Follow,
    NewVisitBtn,
    SaveBtn,
    PatientBook,
    VisitListCtrl,
    OrderBook,
)
from ui.menubar import MyMenuBar
import wx


class MainView(wx.Frame):
    def __init__(self, connection: "db.Connection"):
        super().__init__(
            parent=None, pos=(20, 20), title="PHẦN MỀM PHÒNG KHÁM SIMPLE CLINIC"
        )

        self.connection = connection
        self.config = Config.load()
        self.state = State(self)

        if self.config.maximize_at_start:
            self.Maximize()

        self.patient_book = PatientBook(self)
        self.visit_list = VisitListCtrl(self)
        self.name = wx.TextCtrl(
            self,
            size=self.config.header_size(0.1),
            name="Họ tên:",
            style=wx.TE_READONLY,
        )
        self.gender = wx.TextCtrl(
            self,
            size=self.config.header_size(0.025),
            name="Giới:",
            style=wx.TE_READONLY,
        )
        self.birthdate = DateTextCtrl(
            self,
            size=self.config.header_size(0.06),
            name="Ngày sinh:",
            style=wx.TE_READONLY,
        )
        self.age = ReadonlyVNAgeCtrl(
            self,
            size=self.config.header_size(0.055),
            name="Tuổi:",
        )
        self.address = wx.TextCtrl(self, name="Địa chỉ:", style=wx.TE_READONLY)
        self.phone = PhoneTextCtrl(
            self,
            size=self.config.header_size(0.055),
            name="Điện thoại:",
            style=wx.TE_READONLY,
        )
        self.past_history = wx.TextCtrl(
            self, style=wx.TE_MULTILINE, name="Bệnh nền, dị ứng:"
        )
        self.diagnosis = wx.TextCtrl(self, name="Chẩn đoán:")
        self.vnote = wx.TextCtrl(self, style=wx.TE_MULTILINE, name="Bệnh sử")
        self.weight = WeightCtrl(self, max=200, name="Cân nặng (kg):")
        self.get_weight_btn = GetWeightBtn(self)
        self.days = DaysCtrl(self, name="Số ngày cho toa:")
        self.updatequantitybtn = UpdateQuantityBtn(self)
        self.recheck_weekday = wx.StaticText(
            self, label=vn_weekdays(self.config.default_days_for_prescription)
        )
        self.order_book = OrderBook(self)
        self.recheck = RecheckCtrl(self, name="Số ngày tái khám:")
        self.norecheck = NoRecheckBtn(self)
        self.price = PriceCtrl(self, name="Giá tiền:")
        self.follow = Follow(self)
        self.newvisitbtn = NewVisitBtn(self)
        self.savebtn = SaveBtn(self)

        def set_color(p: list[tuple[wx.Window, str]]):
            for widget, name in p:
                widget.SetBackgroundColour(self.config.get_background_color(name))

        set_color(
            [
                (self, "mainview"),
                (self.name, "name"),
                (self.gender, "gender"),
                (self.birthdate, "birthdate"),
                (self.age, "age"),
                (self.address, "address"),
                (self.phone, "phone"),
                (self.diagnosis, "diagnosis"),
                (self.past_history, "past_history"),
                (self.vnote, "visit_note"),
                (self.days, "days"),
                (self.recheck, "recheck"),
                (self.price, "price"),
                (self.weight, "weight"),
                (self.follow, "follow"),
                (self.visit_list, "visit_list"),
                (self.patient_book.queuelistctrl, "patient_queuelist"),
                (self.patient_book.seentodaylistctrl, "patient_seenlist"),
                (self.order_book.prescriptionpage.drug_list, "drug_list"),
                (self.order_book.prescriptionpage.drug_picker, "drug_picker"),
                (self.order_book.prescriptionpage.times, "drug_times"),
                (self.order_book.prescriptionpage.dose, "drug_dose"),
                (self.order_book.prescriptionpage.quantity, "drug_quantity"),
                (self.order_book.prescriptionpage.note, "drug_note"),
                # (self.order_book.procedurepage.procedure_picker, "procedure_picker"),
                # (self.order_book.procedurepage.procedure_list, "procedure_list"),
            ]
        )

        def widget(w, p, r):
            return (w, p, wx.EXPAND | wx.RIGHT, r)

        def comb(w, p=0, r=5):
            s: str = w.Name
            return (
                (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER | wx.RIGHT, 2),
                widget(w, p, r),
            )

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.AddMany(
            [
                (self.patient_book, 10, wx.EXPAND),
                (wx.StaticText(self, label="Lượt khám cũ:"), 0, wx.EXPAND | wx.ALL, 10),
                (self.visit_list, 4, wx.EXPAND),
            ]
        )
        name_row = wx.BoxSizer(wx.HORIZONTAL)
        name_row.AddMany(
            [
                *comb(self.name, 1),
                *comb(self.gender, 0),
                *comb(self.birthdate, 0),
                *comb(self.age, 0, 0),
            ]
        )
        addr_row = wx.BoxSizer(wx.HORIZONTAL)
        addr_row.AddMany([*comb(self.address, 1), *comb(self.phone, 0, 0)])
        diag_row = wx.BoxSizer(wx.HORIZONTAL)
        diag_row.AddMany([*comb(self.diagnosis, 1, 0)])
        weight_row = wx.BoxSizer(wx.HORIZONTAL)
        weight_row.AddMany(
            [
                *comb(self.weight),
                widget(self.get_weight_btn, 0, 5),
                *comb(self.days),
                widget(self.updatequantitybtn, 0, 5),
                (self.recheck_weekday, 0, wx.ALIGN_CENTER, 0),
            ]
        )
        recheck_row = wx.BoxSizer(wx.HORIZONTAL)
        recheck_row.AddMany(
            [
                *comb(self.recheck),
                widget(self.norecheck, 0, 5),
                (0, 0, 1),
                *comb(self.price, 0, 0),
            ]
        )
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddMany(
            [
                widget(self.newvisitbtn, 0, 5),
                widget(self.savebtn, 0, 0),
            ]
        )
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.AddMany(
            [
                (name_row, 0, wx.EXPAND),
                (addr_row, 0, wx.EXPAND),
                (wx.StaticText(self, label=self.past_history.Name), 0, wx.EXPAND),
                widget(self.past_history, 1, 0),
                (diag_row, 0, wx.EXPAND),
                (wx.StaticText(self, label=self.vnote.Name), 0, wx.EXPAND),
                widget(self.vnote, 1, 0),
                (weight_row, 0, wx.EXPAND),
                (self.order_book, 3, wx.EXPAND),
                (recheck_row, 0, wx.EXPAND),
                (self.follow, 0, wx.EXPAND),
                (btn_row, 0, wx.EXPAND),
            ]
        )
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany(
            [
                (left_sizer, 4, wx.EXPAND | wx.ALL, 10),
                (right_sizer, 6, wx.EXPAND | wx.ALL, 10),
            ]
        )
        self.SetSizerAndFit(sizer)

        self.SetMenuBar(MyMenuBar())
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.state.refresh()

    def onClose(self, e: wx.CloseEvent):
        print("close sqlite3 connection")
        self.connection.close()
        e.Skip()

    def check_diag_wt_filled(self) -> bool:
        diagnosis: str = self.diagnosis.GetValue()
        weight = self.weight.GetWeight()
        if diagnosis.strip() == "":
            wx.MessageBox("Chưa nhập chẩn đoán", "Lỗi")
            return False
        elif weight == 0:
            wx.MessageBox(f"Cân nặng = 0", "Lỗi")
            return False
        else:
            return True
