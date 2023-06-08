import wx

from misc import minus_bm, plus_bm
from state.lineprocedure_state import NewLineProcedureListStateItem
from ui.mainview_widgets.order_book import order_book


class AddProcedureButton(wx.BitmapButton):
    def __init__(self, parent: "order_book.ProcedurePage"):
        super().__init__(parent, bitmap=wx.Bitmap(plus_bm))
        self.parent = parent
        self.mv = parent.mv
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        choice_idx: int = self.parent.procedure_picker.GetSelection()
        if choice_idx != wx.NOT_FOUND:
            pr_id = self.parent.procedure_picker.GetSelectionProcedureID()
            item = NewLineProcedureListStateItem(pr_id)
            self.mv.state.new_lineprocedure_list.append(item)
            self.parent.procedure_list.append_ui(item)
            self.mv.price.FetchPrice()
            self.parent.procedure_picker.SetSelection(wx.NOT_FOUND)


class DelProcedureButton(wx.BitmapButton):
    def __init__(self, parent: "order_book.ProcedurePage"):
        super().__init__(parent, bitmap=wx.Bitmap(minus_bm))
        self.parent = parent
        self.mv = parent.mv
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        pr_list_idx: int = self.parent.procedure_list.GetFirstSelected()
        if pr_list_idx != -1:
            pr_id = self.parent.procedure_picker.GetSelectionProcedureID()
            new_pr = NewLineProcedureListStateItem(pr_id)
            if new_pr in self.mv.state.new_lineprocedure_list:
                self.mv.state.new_lineprocedure_list.remove(new_pr)
            else:
                for old_pr in self.mv.state.old_lineprocedure_list:
                    if old_pr.procedure_id == pr_id:
                        self.mv.state.to_delete_old_lineprocedure_list.append(old_pr)
                        self.mv.state.old_lineprocedure_list.remove(old_pr)
                        break
            self.parent.procedure_list.pop_ui(pr_list_idx)
            self.mv.price.FetchPrice()
