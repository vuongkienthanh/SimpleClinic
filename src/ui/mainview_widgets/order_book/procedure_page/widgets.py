from ui import mainview
from ui.mainview_widgets.order_book import order_book
from state.lineprocedure_state import (
    LineProcedureListStateItem,
    OldLineProcedureListStateItem,
)
import wx


class ProcedureListCtrl(wx.ListCtrl):
    def __init__(self, parent: "order_book.ProcedurePage"):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.mv: "mainview.MainView" = parent.mv
        self.AppendColumn("Tên thủ thuật", width=self.mv.config.header_width(0.2))

    def build(self, _list: list[OldLineProcedureListStateItem]):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: list[OldLineProcedureListStateItem]):
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item: LineProcedureListStateItem):
        proc = self.mv.state.all_procedure[item.procedure_id]
        self.Append((proc.name,))

    def pop_ui(self, idx: int):
        assert idx >= 0
        self.DeleteItem(idx)

    def onSelect(self, e:wx.ListEvent) -> None:
        ...

    def OnDeselect(self, e:wx.ListEvent) -> None:
        ...
