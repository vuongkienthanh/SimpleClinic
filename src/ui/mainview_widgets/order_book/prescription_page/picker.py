import wx

from db import Warehouse
from ui import mainview
from ui.mainview_widgets.order_book import order_book


class DrugPopup(wx.ComboPopup):
    def __init__(self):
        super().__init__()
        self._list: list[Warehouse] = []

    def Create(self, parent):
        self.mv: "mainview.MainView" = self.ComboCtrl.mv
        self.lc = wx.ListCtrl(
            parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.SIMPLE_BORDER
        )
        self.lc.AppendColumn("Thuốc", width=self.mv.config.header_width(0.08))
        self.lc.AppendColumn("Thành phần", width=self.mv.config.header_width(0.08))
        self.lc.AppendColumn("Số lượng", width=self.mv.config.header_width(0.035))
        self.lc.AppendColumn("Đơn vị", width=self.mv.config.header_width(0.03))
        self.lc.AppendColumn("Đơn giá", width=self.mv.config.header_width(0.03))
        self.lc.AppendColumn("Cách dùng", width=self.mv.config.header_width(0.04))
        self.lc.AppendColumn("Hạn sử dụng", width=self.mv.config.header_width(0.055))
        self.lc.Bind(wx.EVT_MOTION, self.OnMotion)
        self.lc.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.lc.Bind(wx.EVT_CHAR, self.onChar)
        return True

    def GetControl(self):
        return self.lc

    def Init(self):
        self.curitem = -1

    def SetStringValue(self, val):
        self.Init()
        if self.lc.ItemCount > 0:
            self.curitem += 1
            self.lc.Select(self.curitem)

    def GetStringValue(self):
        return ""

    def GetAdjustedSize(self, minWidth, prefHeight, maxHeight):
        return super().GetAdjustedSize(self.mv.config.header_width(0.4), -1, -1)

    def fetch_list(self, s: str):
        s = s.strip().casefold()
        self._list = list(
            filter(
                lambda item: (s in item.name.casefold())
                or (s in item.element.casefold()),
                self.mv.state.all_warehouse.values(),
            )
        )

    def build(self):
        for index, item in enumerate(self._list):
            self.append_ui(item)
            self.check_min_quantity_and_color(item, index)

    def append_ui(self, item: Warehouse):
        if item.expire_date is None:
            expire_date = ""
        else:
            expire_date = item.expire_date.strftime("%d/%m/%Y")
        self.lc.Append(
            [
                item.name,
                item.element,
                str(item.quantity),
                item.usage_unit,
                int(item.sale_price),
                item.usage,
                expire_date,
            ]
        )

    def check_min_quantity_and_color(self, item, index):
        if item.quantity <= self.mv.config.minimum_drug_quantity_alert:
            self.lc.SetItemTextColour(index, wx.Colour(252, 3, 57))

    def OnPopup(self):
        self.lc.DeleteAllItems()
        cc: DrugPicker = self.ComboCtrl
        s: str = cc.Value
        self.fetch_list(s)
        self.build()

    def OnMotion(self, e):
        index, _ = self.lc.HitTest(e.GetPosition())
        if index >= 0:
            self.lc.Select(index)
            self.curitem = index

    def OnLeftDown(self, _):
        self.select_drug()

    def select_drug(self):
        cc: DrugPicker = self.ComboCtrl
        curitem = self.curitem
        self.Dismiss()
        self.mv.state.warehouse = self._list[curitem]
        cc.parent.times.SetFocus()

    def onChar(self, e: wx.KeyEvent):
        c = e.KeyCode
        if c == wx.WXK_DOWN:
            self.KeyDown()
        elif c == wx.WXK_UP:
            self.KeyUp()
        elif c == wx.WXK_ESCAPE:
            self.KeyESC()
        elif c == wx.WXK_RETURN:
            self.KeyReturn()

    def KeyDown(self):
        if self.lc.ItemCount > 0:
            if self.curitem < (self.lc.ItemCount - 1):
                self.curitem += 1
            self.lc.Select(self.curitem)
            self.lc.EnsureVisible(self.curitem)

    def KeyUp(self):
        if self.lc.ItemCount > 0:
            if self.curitem > 0:
                self.curitem -= 1
            self.lc.Select(self.curitem)
            self.lc.EnsureVisible(self.curitem)

    def KeyReturn(self):
        if self.lc.ItemCount > 0:
            self.select_drug()

    def KeyESC(self):
        self.mv.state.warehouse = None
        self.mv.state.linedrug = None
        self.Dismiss()


class DrugPicker(wx.ComboCtrl):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.mv = parent.mv
        self.SetPopupControl(DrugPopup())
        self.Bind(wx.EVT_CHAR, self.onChar)
        self.Bind(wx.EVT_TEXT, self.onText)
        self.SetHint("Enter để search thuốc")

    def onChar(self, e: wx.KeyEvent):
        if e.KeyCode == wx.WXK_RETURN:
            self.Popup()
        else:
            e.Skip()

    def onText(self, e: wx.CommandEvent):
        if self.Value == "":
            self.mv.state.warehouse = None
            self.mv.state.linedrug = None
        else:
            e.Skip()
