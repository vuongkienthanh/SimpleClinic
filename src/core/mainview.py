from db import db_func
from core.init import config, tsize
import other_func as otf
from core.state import State
from core.generic import AgeCtrl, PhoneTextCtrl, DateTextCtrl, WeightCtrl
from core.mainview_widgets import (
    GetWeightBtn, DaysCtrl, UpdateQuantityBtn,
    RecheckCtrl, NoRecheckBtn, PriceCtrl,
    Follow, NewVisitBtn, SaveBtn,
    PatientBook, VisitList, OrderBook
)
from core.menubar import MyMenuBar
import wx


class MainView(wx.Frame):

    def __init__(self, con: 'db_func.Connection', sample: bool = False):
        super().__init__(
            parent=None,
            pos=(20, 20),
            title='PHẦN MỀM PHÒNG KHÁM TẠI NHÀ')
        self.SetBackgroundColour(otf.get_background_color('mainview'))

        self.con = con
        self.state = State(self)
        self.sample = sample

        if config['maximize_at_start']:
            self.Maximize()

        self.patient_book = PatientBook(self)
        self.visit_list = VisitList(self)
        self.name = wx.TextCtrl(self, size=tsize(
            0.1), name="Họ tên:", style=wx.TE_READONLY)
        self.gender = wx.TextCtrl(self, size=tsize(
            0.025), name="Giới:", style=wx.TE_READONLY)
        self.birthdate = DateTextCtrl(
            self, size=tsize(0.06), name="Ngày sinh:", style=wx.TE_READONLY)
        self.age = AgeCtrl(self, size=tsize(
            0.055), name="Tuổi:", style=wx.TE_READONLY)
        self.address = wx.TextCtrl(self, name="Địa chỉ:", style=wx.TE_READONLY)
        self.phone = PhoneTextCtrl(self, size=tsize(
            0.055), name="Điện thoại:", style=wx.TE_READONLY)
        self.past_history = wx.TextCtrl(
            self, style=wx.TE_MULTILINE, name="Bệnh nền, dị ứng:")
        self.diagnosis = wx.TextCtrl(self, name="Chẩn đoán:")
        self.vnote = wx.TextCtrl(self, style=wx.TE_MULTILINE, name="Bệnh sử")
        self.weight = WeightCtrl(self, max=200, name="Cân nặng (kg):")
        self.get_weight_btn = GetWeightBtn(self)
        self.days = DaysCtrl(self, name="Số ngày cho toa:")
        self.updatequantitybtn = UpdateQuantityBtn(self)
        self.order_book = OrderBook(self)
        self.recheck = RecheckCtrl(self, name="Số ngày tái khám:")
        self.norecheck = NoRecheckBtn(self)
        self.price = PriceCtrl(self, name="Giá tiền:")
        self.follow = Follow(self)
        self.newvisitbtn = NewVisitBtn(self)
        self.savebtn = SaveBtn(self)

        def set_color(widget: wx.Window, name: str):
            widget.SetBackgroundColour(otf.get_background_color(name))
        set_color(self.name, 'name')
        set_color(self.gender, 'gender')
        set_color(self.birthdate, 'birthdate')
        set_color(self.age, 'age')
        set_color(self.address, 'address')
        set_color(self.phone, 'phone')
        set_color(self.diagnosis, 'diagnosis')
        set_color(self.past_history, 'past_history')
        set_color(self.vnote, 'visit_note')

        def widget(w, p, r):
            return (w, p, wx.EXPAND | wx.RIGHT, r)

        def comb(w, p=0, r=5):
            s: str = w.Name
            return (
                (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER | wx.RIGHT, 2),
                widget(w, p, r)
            )

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.AddMany([
            (self.patient_book, 10, wx.EXPAND),
            (wx.StaticText(self, label='Lượt khám cũ:'), 0, wx.EXPAND | wx.ALL, 10),
            (self.visit_list, 4, wx.EXPAND),
        ])
        name_row = wx.BoxSizer(wx.HORIZONTAL)
        name_row.AddMany([
            *comb(self.name, 1),
            *comb(self.gender, 0),
            *comb(self.birthdate, 0),
            *comb(self.age, 0, 0),
        ])
        addr_row = wx.BoxSizer(wx.HORIZONTAL)
        addr_row.AddMany([
            *comb(self.address, 1),
            *comb(self.phone, 0, 0)
        ])
        diag_row = wx.BoxSizer(wx.HORIZONTAL)
        diag_row.AddMany([
            *comb(self.diagnosis, 1, 0)
        ])
        weight_row = wx.BoxSizer(wx.HORIZONTAL)
        weight_row.AddMany([
            *comb(self.weight),
            widget(self.get_weight_btn, 0, 5),
            *comb(self.days),
            widget(self.updatequantitybtn, 0, 0)
        ])
        recheck_row = wx.BoxSizer(wx.HORIZONTAL)
        recheck_row.AddMany([
            *comb(self.recheck),
            widget(self.norecheck, 0, 5),
            (0, 0, 1),
            *comb(self.price, 0, 0)

        ])
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_row.AddMany([
            widget(self.newvisitbtn, 0, 5),
            widget(self.savebtn, 0, 0),
        ])
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.AddMany([
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

        ])
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([
            (left_sizer, 4, wx.EXPAND | wx.ALL, 10),
            (right_sizer, 6, wx.EXPAND | wx.ALL, 10)
        ])
        self.SetSizerAndFit(sizer)

        self.SetMenuBar(MyMenuBar())
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.start()

    def onClose(self, e: wx.CloseEvent):
        print("close sqlite3 connection")
        self.con.close()
        e.Skip()

    def start(self):
        self.patient_book.page0.build(self.state.queuelist)
        self.patient_book.page1.build(self.state.todaylist)

    def check_filled(self) -> bool:
        diagnosis: str = self.diagnosis.GetValue()
        weight = self.weight.GetWeight()
        if diagnosis.strip() == '':
            wx.MessageBox("Chưa nhập chẩn đoán", "Lỗi")
            return False
        elif weight == 0:
            wx.MessageBox(f"Cân nặng = 0", "Lỗi")
            return False
        else:
            return True
