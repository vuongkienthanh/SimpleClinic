import wx

import state

from .new_lineprocedure_list import NewLineProcedureListStateItem
from .old_lineprocedure_list import OldLineProcedureListStateItem

LineProcedureListStateItem = (
    OldLineProcedureListStateItem | NewLineProcedureListStateItem
)
LineProcedureListState = (
    list[NewLineProcedureListStateItem]
    | list[OldLineProcedureListStateItem]
    | list[LineProcedureListStateItem]
)


class LineProcedureState:
    def __get__(
        self, obj: "state.main_state.State", _
    ) -> LineProcedureListStateItem | None:
        return obj._lineprocedure

    def __set__(
        self, obj: "state.main_state.State", value: LineProcedureListStateItem | None
    ) -> None:
        obj._lineprocedure = value
        match value:
            case None:
                self.onUnset(obj)
            case item:
                self.onSet(obj, item)

    def onSet(self, obj: "state.main_state.State", item: LineProcedureListStateItem):
        page = obj.mv.order_book.procedurepage
        page.procedure_picker.SetDBID(item.procedure_id)
        page.SetFocus()

    def onUnset(self, obj: "state.main_state.State") -> None:
        page = obj.mv.order_book.procedurepage
        page.procedure_picker.SetSelection(wx.NOT_FOUND)
        page.SetFocus()
