from core import mainview
from core.dialogs import EditPatientDialog
from core.state.queue_state import QueueStateItem
from core.state.seentoday_state import SeenTodayStateItem
from db import Patient, Visit
import wx

StateList = list[QueueStateItem] | list[SeenTodayStateItem]
StateItem = QueueStateItem | SeenTodayStateItem


class PatientBook(wx.Notebook):
    def __init__(self, parent: "mainview.MainView"):
        super().__init__(parent)
        self.mv = parent
        self.queuelistctrl = QueuePatientListCtrl(self)
        self.seentodaylistctrl = SeenTodayListCtrl(self)
        self.AddPage(page=self.queuelistctrl, text="Danh sách chờ khám", select=True)
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

    def build(self, _list: StateList):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: StateList):
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item: StateItem):
        ...

    def onSelect(self, _):
        ...

    def onDeselect(self, _):
        ...

    def onDoubleClick(self, _):
        EditPatientDialog(self.mv).ShowModal()


class QueuePatientListCtrl(BasePatientListCtrl):
    "Set `state.patient` when select item"

    def __init__(self, parent: PatientBook):
        super().__init__(parent)
        self.AppendColumn("Giờ đăng ký", width=self.mv.config.header_width(0.075))

    def append_ui(self, item: QueueStateItem):
        self.Append(
            [
                item.pid,
                item.name,
                str(item.gender),
                item.birthdate.strftime("%d/%m/%Y"),
                item.added_datetime.strftime("%d/%m/%Y %H:%M"),
            ]
        )

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        item = self.mv.state.queue[idx]
        pid = item.pid
        p = self.mv.connection.select(Patient, pid)
        assert p is not None
        self.mv.state.patient = p
        self.SetFocus()

    def onDeselect(self, _):
        self.mv.state.patient = None
        self.SetFocus()


class SeenTodayListCtrl(BasePatientListCtrl):
    "Set `state.patient` and `state.visit` when select item"

    def __init__(self, parent: PatientBook):
        super().__init__(parent)
        self.AppendColumn("Giờ khám", width=self.mv.config.header_width(0.075))

    def append_ui(self, item: SeenTodayStateItem):
        self.Append(
            [
                item.pid,
                item.name,
                str(item.gender),
                item.birthdate.strftime("%d/%m/%Y"),
                item.exam_datetime.strftime("%d/%m/%Y %H:%M"),
            ]
        )

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        target = self.mv.state.seentoday[idx]
        pid: int = target.pid
        vid: int = target.vid

        p = self.mv.connection.select(Patient, pid)
        v = self.mv.connection.select(Visit, vid)
        assert p is not None
        assert v is not None
        self.mv.state.patient = p
        self.mv.state.visit = v
        self.SetFocus()

    def onDeselect(self, _):
        self.mv.state.patient = None
        self.mv.state.visit = None
        self.SetFocus()
