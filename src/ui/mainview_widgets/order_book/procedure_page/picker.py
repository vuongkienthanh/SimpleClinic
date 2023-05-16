from . import page
from misc import num_to_str_price
import wx


class ProcedurePicker(wx.Choice):
    def __init__(self, parent: "page.ProcedurePage"):
        self.parent = parent
        self.mv = parent.mv
        self._choice_to_pr: dict[int, int] = {}
        self._pr_to_choice: dict[int, int] = {}
        for choice_id, pr_id in enumerate(self.mv.state.all_procedure.keys()):
            self._choice_to_pr[choice_id] = pr_id
            self._pr_to_choice[pr_id] = choice_id

        super().__init__(
            parent,
            choices=[
                f"{pr.name} ({num_to_str_price(pr.price)})"
                for pr in self.mv.state.all_procedure.values()
            ],
        )

    def GetSelectionProcedureID(self):
        return self._choice_to_pr[self.GetSelection()]

    def SetSelectionProcedureID(self, pr_id: int):
        self.SetSelection(self._pr_to_choice[pr_id])
