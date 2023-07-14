import wx

from db import Visit
from state import VisitListStateItem
from ui import mainview as mv
from ui.generics.widgets import GenericListCtrl


class VisitListCtrl(GenericListCtrl):
    "Set `state.visit` when select item"

    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, mv=parent)
        self.AppendColumn("Mã lượt khám", 0.07)
        self.AppendColumn("Ngày giờ khám", 0.075)
        self.AppendColumn("Chẩn đoán", 0.15)

    def append_ui(self, item: VisitListStateItem):
        self.Append(
            [
                item.visit_id,
                item.exam_datetime.strftime("%d/%m/%Y %H:%M"),
                item.diagnosis,
            ]
        )

    def onSelect(self, e: wx.ListEvent):
        item: VisitListStateItem = self.mv.state.visit_list[e.Index]
        v = self.mv.connection.select(Visit, item.visit_id)
        assert v is not None
        self.mv.state.visit = v
        self.SetFocus()

    def onDeselect(self, _):
        self.mv.state.visit = None
        self.SetFocus()
