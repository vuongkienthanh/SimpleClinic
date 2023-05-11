from core import mainview as mv
from db import Visit
import wx
import sqlite3


class VisitListCtrl(wx.ListCtrl):
    """Set `state.visit` when select visit"""

    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.mv = parent
        self.AppendColumn("Mã lượt khám", width=self.mv.config.header_width(0.07))
        self.AppendColumn("Ngày giờ khám", width=self.mv.config.header_width(0.075))
        self.AppendColumn("Chẩn đoán", width=self.mv.config.header_width(0.15))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, lv: list[sqlite3.Row]):
        for row in lv:
            self.append_ui(row)

    def rebuild(self, lv: list[sqlite3.Row]):
        self.DeleteAllItems()
        self.build(lv)

    def append_ui(self, row: sqlite3.Row):
        self.Append(
            [
                row["vid"],
                row["exam_datetime"].strftime("%d/%m/%Y %H:%M"),
                row["diagnosis"],
            ]
        )

    def onSelect(self, e: wx.ListEvent):
        vid: int = self.mv.state.visitlist[e.Index]["vid"]
        self.mv.state.visit = self.mv.connection.select(Visit, vid)

    def onDeselect(self, _):
        self.mv.state.visit = None
