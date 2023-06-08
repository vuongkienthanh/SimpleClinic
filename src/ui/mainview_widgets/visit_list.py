import wx

from db import Visit
from state.visit_list_state import VisitListStateItem
from ui import mainview as mv


class VisitListCtrl(wx.ListCtrl):
    "Set `state.visit` when select item"

    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.mv = parent
        self.AppendColumn("Mã lượt khám", width=self.mv.config.header_width(0.07))
        self.AppendColumn("Ngày giờ khám", width=self.mv.config.header_width(0.075))
        self.AppendColumn("Chẩn đoán", width=self.mv.config.header_width(0.15))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, _list: list[VisitListStateItem]):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: list[VisitListStateItem]):
        self.DeleteAllItems()
        self.build(_list)

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
