import wx
from ui.generic_widgets import CalendarDatePicker, NumberTextCtrl
import datetime as dt


class DatePickerDialog(wx.Dialog):
    def __init__(self, parent: wx.Window):
        super().__init__(parent, title="Chọn ngày")
        self.datepicker = CalendarDatePicker(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (self.datepicker, 0, wx.EXPAND | wx.ALL, 10),
                (
                    self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL),
                    0,
                    wx.EXPAND | wx.ALL,
                    10,
                ),
            ]
        )
        self.SetSizerAndFit(sizer)

    def GetDate(self) -> dt.date:
        return self.datepicker.GetDate()


class MonthPickerDialog(wx.Dialog):
    def __init__(self, parent: wx.Window):
        super().__init__(parent, title="Chọn tháng")
        self.month = wx.SpinCtrl(
            self, min=1, max=12, initial=dt.date.today().month, name="Tháng:"
        )
        self.year = NumberTextCtrl(self, value=str(dt.date.today().year), name="Năm:")
        self.year.SetHint("YYYY")

        def widget(w):
            return (
                wx.StaticText(self, label=w.Name),
                0,
                wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_VERTICAL,
                5,
            ), (w, 0, wx.EXPAND | wx.ALL, 5)

        entry_sizer = wx.FlexGridSizer(2, 2, 5, 5)
        entry_sizer.AddMany([*widget(self.month), *widget(self.year)])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (entry_sizer, 0, wx.EXPAND | wx.ALL, 5),
                (
                    self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL),
                    0,
                    wx.EXPAND | wx.ALL,
                    10,
                ),
            ]
        )
        self.SetSizerAndFit(sizer)

    def GetMonth(self) -> int:
        return self.month.GetValue()

    def GetYear(self) -> int:
        return int(self.year.GetValue())
