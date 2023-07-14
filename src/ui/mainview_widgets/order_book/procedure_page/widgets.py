import wx

from state import LineProcedureListStateItem
from ui.generics.widgets import GenericListCtrl
from ui.mainview_widgets.order_book import order_book


class ProcedureListCtrl(GenericListCtrl):
    def __init__(self, parent: "order_book.ProcedurePage"):
        super().__init__(parent, mv=parent.mv)
        self.AppendColumn("Tên thủ thuật", 0.2)

    def append_ui(self, item: LineProcedureListStateItem):
        proc = self.mv.state.all_procedure[item.procedure_id]
        self.Append((proc.name,))

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
