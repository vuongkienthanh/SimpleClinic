import wx

from state.lineprocedure_state import LineProcedureListState, LineProcedureListStateItem
from ui import mainview
from ui.mainview_widgets.order_book import order_book


class ProcedureListCtrl(wx.ListCtrl):
    def __init__(self, parent: "order_book.ProcedurePage"):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.mv: "mainview.MainView" = parent.mv
        self.AppendColumn("Tên thủ thuật", width=self.mv.config.header_width(0.2))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, _list: LineProcedureListState):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: LineProcedureListState):
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item: LineProcedureListStateItem):
        proc = self.mv.state.all_procedure[item.procedure_id]
        self.Append((proc.name,))

    def pop_ui(self, idx: int):
        assert idx >= 0
        self.DeleteItem(idx)

    def onSelect(self, e: wx.ListEvent) -> None:
        state = self.mv.state
        idx: int = e.Index
        if idx < len(state.old_lineprocedure_list):
            state.lineprocedure = state.old_lineprocedure_list[idx]
        else:
            state.lineprocedure = state.new_lineprocedure_list[
                idx - len(state.old_lineprocedure_list)
            ]

    def onDeselect(self, _) -> None:
        self.mv.state.lineprocedure = None
