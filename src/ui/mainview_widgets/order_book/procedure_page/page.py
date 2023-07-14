import wx

from ui.mainview_widgets.order_book.base_page import BasePage

from .buttons import *
from .picker import *
from .widgets import *


class ProcedurePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)

        self.procedure_picker = ProcedurePicker(self)
        self.addbtn = AddProcedureButton(self)
        self.delbtn = DelProcedureButton(self)
        self.procedure_list = ProcedureListCtrl(self)

        choice_row = wx.BoxSizer(wx.HORIZONTAL)
        choice_row.AddMany(
            [
                (self.procedure_picker, 1, wx.RIGHT, 5),
                (self.addbtn, 0, wx.RIGHT, 5),
                (self.delbtn, 0),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (choice_row, 0, wx.EXPAND | wx.ALL, 5),
                (self.procedure_list, 1, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizerAndFit(sizer)
