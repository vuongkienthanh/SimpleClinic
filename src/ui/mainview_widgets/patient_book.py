import wx

from db import Patient, Visit
from state import AppointmentStateItem, QueueStateItem, SeenTodayStateItem
from ui import mainview
from ui.dialogs import EditPatientDialog
from ui.generics.widgets import GenericListCtrl

StateList = list[QueueStateItem] | list[SeenTodayStateItem] | list[AppointmentStateItem]
StateItem = QueueStateItem | SeenTodayStateItem | AppointmentStateItem


class PatientBook(wx.Notebook):
    def __init__(self, parent: "mainview.MainView"):
        super().__init__(parent)
        self.mv = parent
        self.queuelistctrl = QueuePatientListCtrl(self)
        self.seentodaylistctrl = SeenTodayListCtrl(self)
        self.appointmentlistctrl = AppointmentListCtrl(self)
        self.AddPage(page=self.queuelistctrl, text="Danh sách chờ khám", select=True)
        self.AddPage(page=self.seentodaylistctrl, text="Danh sách đã khám hôm nay")
        self.AddPage(page=self.appointmentlistctrl, text="Danh sách tái khám")
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onChanging)

    def onChanging(self, e: wx.BookCtrlEvent):
        """Deselect before page changed"""
        old: int = e.GetOldSelection()
        assert old != wx.NOT_FOUND
        oldpage: wx.ListCtrl = self.GetPage(old)
        item: int = oldpage.GetFirstSelected()
        oldpage.Select(item, 0)


class BasePatientListCtrl(GenericListCtrl):
    def __init__(self, parent: PatientBook):
        super().__init__(parent, mv=parent.mv)
        self.AppendColumn("Mã BN", 0.03)
        self.AppendColumn("Họ tên", 0.1)
        self.AppendColumn("Giới", 0.03)
        self.AppendColumn("Ngày sinh", 0.05)

    def onDoubleClick(self, _):
        EditPatientDialog(self.mv).ShowModal()


class QueuePatientListCtrl(BasePatientListCtrl):
    "Set `state.patient` when select item"

    def __init__(self, parent):
        super().__init__(parent)
        self.AppendColumn("Giờ đăng ký", 0.075)

    def append_ui(self, item: QueueStateItem):
        self.Append(
            [
                item.patient_id,
                item.name,
                str(item.gender),
                item.birthdate.strftime("%d/%m/%Y"),
                item.added_datetime.strftime("%d/%m/%Y %H:%M"),
            ]
        )

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        item = self.mv.state.queue[idx]
        pid = item.patient_id
        p = self.mv.connection.select(Patient, pid)
        assert p is not None
        self.mv.state.patient = p
        self.SetFocus()

    def onDeselect(self, _):
        self.mv.state.patient = None
        self.SetFocus()


class SeenTodayListCtrl(BasePatientListCtrl):
    "Set `state.patient` and `state.visit` when select item"

    def __init__(self, parent):
        super().__init__(parent)
        self.AppendColumn("Giờ khám", 0.075)

    def append_ui(self, item: SeenTodayStateItem):
        self.Append(
            [
                item.patient_id,
                item.name,
                str(item.gender),
                item.birthdate.strftime("%d/%m/%Y"),
                item.exam_datetime.strftime("%d/%m/%Y %H:%M"),
            ]
        )

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        target = self.mv.state.seentoday[idx]
        pid: int = target.patient_id
        vid: int = target.visit_id

        p = self.mv.connection.select(Patient, pid)
        v = self.mv.connection.select(Visit, vid)
        assert p is not None
        assert v is not None
        self.mv.state.patient = p
        self.mv.state.visit = v
        self.SetFocus()

    def onDeselect(self, _):
        self.mv.state.patient = None
        self.SetFocus()


class AppointmentListCtrl(BasePatientListCtrl):
    "Set `state.patient` when select item"

    def __init__(self, parent):
        super().__init__(parent)

    def append_ui(self, item: AppointmentStateItem):
        self.Append(
            [
                item.patient_id,
                item.name,
                str(item.gender),
                item.birthdate.strftime("%d/%m/%Y"),
            ]
        )

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        target = self.mv.state.appointment[idx]
        pid: int = target.patient_id
        p = self.mv.connection.select(Patient, pid)
        assert p is not None
        self.mv.state.patient = p
        self.SetFocus()

    def onDeselect(self, _):
        self.mv.state.patient = None
        self.SetFocus()
