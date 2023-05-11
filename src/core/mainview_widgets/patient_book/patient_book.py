from core import mainview
from core.dialogs import EditPatientDialog
from db import Patient, Visit
import wx
import sqlite3


class PatientBook(wx.Notebook):

    def __init__(self, parent: "mainview.MainView"):
        super().__init__(parent)
        self.mv = parent
        self.queuepatientlistctrl = QueuePatientListCtrl(self)
        self.seentodaylistctrl = SeenTodayPatientListCtrl(self)
        self.AddPage(page=self.queuepatientlistctrl, text="Danh sách chờ khám", select=True)
        self.AddPage(page=self.seentodaylistctrl, text="Danh sách đã khám hôm nay")
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onChanging)

    def onChanging(self, e: wx.BookCtrlEvent):
        """Deselect before page changed"""
        old: int = e.GetOldSelection()
        assert old != wx.NOT_FOUND
        oldpage: wx.ListCtrl = self.GetPage(old)
        item: int = oldpage.GetFirstSelected()
        oldpage.Select(item, 0)


class BasePatientListCtrl(wx.ListCtrl):

    def __init__(self, parent: PatientBook):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.parent = parent
        self.mv = parent.mv
        self.AppendColumn("Mã BN", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Họ tên", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Giới", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Ngày sinh", width=self.mv.config.header_width(0.05))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick)

    def build(self, _list: list[sqlite3.Row]):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: list[sqlite3.Row]):
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item: sqlite3.Row):
        ...

    def onSelect(self, e: wx.ListEvent):
        ...

    def onDeselect(self, e: wx.ListEvent):
        ...

    def onDoubleClick(self, e: wx.ListEvent):

        EditPatientDialog(self.mv).ShowModal()


class QueuePatientListCtrl(BasePatientListCtrl):
    "First page, set `state.patient` when selected"

    def __init__(self, parent: PatientBook):
        super().__init__(parent)
        self.AppendColumn("Giờ đăng ký", width=self.mv.config.header_width(0.075))

    def append_ui(self, row: sqlite3.Row):
        self.Append(
            [
                row["pid"],
                row["name"],
                str(row["gender"]),
                row["birthdate"].strftime("%d/%m/%Y"),
                row["added_datetime"].strftime("%d/%m/%Y %H:%M"),
            ]
        )

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        pid: int = self.mv.state.queue[idx]["pid"]
        self.mv.state.patient = self.mv.connection.select(Patient, pid)

    def onDeselect(self, _):
        self.mv.state.patient = None


class SeenTodayPatientListCtrl(BasePatientListCtrl):
    """Set `state.patient` and `state.visit` when select patient"""

    def __init__(self, parent: PatientBook):
        super().__init__(parent)
        self.AppendColumn("Giờ khám", width=self.mv.config.header_width(0.075))

    def append_ui(self, row: sqlite3.Row):
        self.Append(
            [
                row["pid"],
                row["name"],
                str(row["gender"]),
                row["birthdate"].strftime("%d/%m/%Y"),
                row["exam_datetime"].strftime("%d/%m/%Y %H:%M"),
            ]
        )

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        target = self.mv.state.seentoday[idx]
        pid: int = target["pid"]
        vid: int = target["vid"]
        self.mv.state.patient = self.mv.connection.select(Patient, pid)
        self.mv.state.visit = self.mv.connection.select(Visit, vid)
        self.SetFocus()

    def onDeselect(self, _):
        self.mv.state.patient = None
        self.mv.state.visit = None
        self.SetFocus()
