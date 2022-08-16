from core.init import size
import other_func as otf
from db.db_class import Procedure
import wx
import sqlite3


class ProcedureListItem:
    __slots__ = "pr_id", "name", "price"

    def __init__(self, pr_id, name, price):
        self.pr_id = pr_id
        self.name = name
        self.price = price


class ProcedureListCtrl(wx.ListCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.SetBackgroundColour(otf.get_background_color('procedure_list'))
        self.AppendColumn("Tên thủ thuật", width=size(0.2))
        self.pr_list: list[ProcedureListItem] = []

    def clear(self):
        self.pr_list.clear()
        self.DeleteAllItems()

    def rebuild(self, llp: list[sqlite3.Row]):
        self.clear()
        for lp in llp:
            self.Append((lp['name'], ))
            self.pr_list.append(ProcedureListItem(
                lp['pr_id'],
                lp['name'],
                lp['price']))

    def append(self, pr: Procedure):
        self.Append((pr.name,))
        self.pr_list.append(ProcedureListItem(
            pr.id,
            pr.name,
            pr.price))

    def update(self, pr: Procedure):
        for i in range(len(self.pr_list)):
            if self.pr_list[i].pr_id == pr.id:
                self.SetItem(i, 0, pr.name)
                self.pr_list[i].price = pr.price

    def pop(self, idx: int):
        assert idx >= 0
        self.DeleteItem(idx)
        self.pr_list.pop(idx)

    def summary(self) -> tuple[tuple[int, str, int]]:
        count = dict()
        name = dict()
        for pr in self.pr_list:
            if pr.pr_id not in count.keys():
                count[pr.pr_id] = 1
                name[pr.pr_id] = pr.name
            else:
                count[pr.pr_id] += 1
        return tuple(
            (
                pr.pr_id,
                name[pr.pr_id],
                count[pr.pr_id],
            )
            for pr in self.pr_list
        )
