import wx

from state.lineprocedure_states import (
    NewLineProcedureListState,
    NewLineProcedureListStateItem,
)
from ui.generics import AddBitmapBtn, DeleteBitMapBtn
from ui.mainview_widgets.order_book.procedure_page import page


class AddProcedureButton(AddBitmapBtn):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent: page.ProcedurePage

    def Add(self):
        choice_idx: int = self.parent.procedure_picker.GetSelection()
        if choice_idx != wx.NOT_FOUND:
            pr_id = self.parent.procedure_picker.GetDBID()
            new_pr = NewLineProcedureListStateItem(pr_id)
            NewLineProcedureListState.append_state(self.parent.mv, new_pr)
            self.parent.mv.price.FetchPrice()
            self.parent.procedure_picker.SetSelection(wx.NOT_FOUND)


class DelProcedureButton(DeleteBitMapBtn):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent: page.ProcedurePage

    def onClick(self, _):
        pr_list_idx: int = self.parent.procedure_list.GetFirstSelected()
        if pr_list_idx != -1:
            pr_id = self.parent.procedure_picker.GetDBID()
            new_pr = NewLineProcedureListStateItem(pr_id)
            if new_pr in self.parent.mv.state.new_lineprocedure_list:
                self.parent.mv.state.new_lineprocedure_list.remove(new_pr)
            else:
                for old_pr in self.parent.mv.state.old_lineprocedure_list:
                    if old_pr.procedure_id == pr_id:
                        self.parent.mv.state.to_delete_old_lineprocedure_list.append(
                            old_pr
                        )
                        self.parent.mv.state.old_lineprocedure_list.remove(old_pr)
                        break
            self.parent.procedure_list.pop_ui(pr_list_idx)
            self.parent.mv.price.FetchPrice()
