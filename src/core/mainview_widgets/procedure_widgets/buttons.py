from core.mainview_widgets import order_book
from misc import plus_bm, minus_bm

import wx


class AddProcedureButton(wx.BitmapButton):
    def __init__(self, parent: "order_book.ProcedurePage"):
        super().__init__(parent, bitmap=wx.Bitmap(plus_bm))
        self.parent = parent
        self.mv = parent.mv
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        idx: int = self.parent.procedure_picker.GetSelection()
        if idx != wx.NOT_FOUND:
            pr = self.mv.state.procedurelist[idx]
            self.parent.procedure_list.append(pr)
            self.mv.price.FetchPrice()
            self.parent.procedure_picker.SetSelection(-1)


class DelProcedureButton(wx.BitmapButton):
    def __init__(self, parent: "order_book.ProcedurePage"):
        super().__init__(parent, bitmap=wx.Bitmap(minus_bm))
        self.parent = parent
        self.mv = parent.mv
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        idx: int = self.parent.procedure_list.GetFirstSelected()
        if idx != -1:
            self.parent.procedure_list.pop(idx)
            self.mv.price.FetchPrice()
