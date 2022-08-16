from core import mainview as mv
from core.init import size
import other_func as otf
from db.db_class import Visit
import wx
import sqlite3


class VisitList(wx.ListCtrl):
    """Set `state.visit` when selected"""

    def __init__(self, parent: 'mv.MainView'):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.mv = parent
        self.SetBackgroundColour(otf.get_background_color('visit_list'))
        self.AppendColumn('Mã lượt khám', width=size(0.07))
        self.AppendColumn('Ngày giờ khám', width=size(0.075))
        self.AppendColumn('Chẩn đoán', width=size(0.15))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, lv: list[sqlite3.Row]):
        for row in lv:
            self.append_ui(row)

    def rebuild(self, lv: list[sqlite3.Row]):
        self.DeleteAllItems()
        self.build(lv)

    def append_ui(self, row: sqlite3.Row):
        self.Append([
            row['vid'],
            row['exam_datetime'].strftime("%d/%m/%Y %H:%M"),
            row['diagnosis']
        ])

    def onSelect(self, e: wx.ListEvent):
        vid = self.mv.state.visitlist[e.Index]['vid']
        self.mv.state.visit = self.mv.con.select(Visit, vid)

    def onDeselect(self, e: wx.ListEvent):
        self.mv.state.visit = None
