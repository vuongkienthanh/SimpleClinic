import wx

from misc import minus_bm, plus_bm
from ui.mainview_widgets import order_book


class BasePage(wx.Panel):
    def __init__(self, parent: "order_book.OrderBook"):
        super().__init__(parent)
        self.parent = parent
        self.mv = parent.mv


class BaseAddButton(wx.BitmapButton):
    def __init__(self, parent: BasePage):
        super().__init__(parent, bitmap=wx.Bitmap(plus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        self.Add()

    def Add(self):
        pass


class BaseDeleteButton(wx.BitmapButton):
    def __init__(self, parent: BasePage):
        super().__init__(parent, bitmap=wx.Bitmap(minus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        self.Delete()

    def Delete(self):
        pass
