from core.init import size
from db.db_class import Procedure
import wx
import sqlite3


class ProcedureListItem:
    __slots__ = "pr_id", "price"

    def __init__(self, pr_id, price):
        self.pr_id = pr_id
        self.price = price


class ProcedureListCtrl(wx.ListCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.AppendColumn("Tên thủ thuật", width=size(0.2))
        self.pr_list: list[ProcedureListItem] = []

    def clear(self):
        self.pr_list.clear()
        self.DeleteAllItems()

    def rebuild(self, llp: list[sqlite3.Row]):
        self.clear()
        for lp in llp:
            self.Append((lp['name'], ))
            self.pr_list.append(ProcedureListItem(lp['pr_id'], lp['price']))

    def append(self, pr: Procedure):
        self.Append((pr.name,))
        self.pr_list.append(ProcedureListItem(pr.id, pr.price))

    def update(self, pr: Procedure):
        for i in range(len(self.pr_list)):
            if self.pr_list[i].pr_id == pr.id:
                self.SetItem(i, 0, pr.name)
                self.pr_list[i].price = pr.price

    def pop(self, idx: int):
        assert idx >= 0
        self.DeleteItem(idx)
        self.pr_list.pop(idx)
