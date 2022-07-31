from core.init import size
from db.db_class import Procedure
from core import other_func as otf
import wx
import sqlite3
from collections import namedtuple

Proc = namedtuple('Proc', ['pr_id', 'price'])


class ProcedureList(wx.ListCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.AppendColumn("Tên thủ thuật", width=size(0.2))

        self.pr_list: list[Proc] = []

    def append(self, pr: Procedure):
        self.Append((pr.name,))
        self.pr_list.append(Proc(pr.id, pr.price))

    def pop(self, idx: int):
        self.DeleteItem(idx)
        self.pr_list.pop(idx)

    def clear(self):
        self.pr_list.clear()
        self.DeleteAllItems()

    def rebuild(self, llp: list[sqlite3.Row]):
        self.clear()
        for lp in llp:
            self.Append((lp['name'], ))
            self.pr_list.append(Proc(lp['pr_id'], lp['price']))
