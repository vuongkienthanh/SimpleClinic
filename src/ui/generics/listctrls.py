import wx

from ui import mainview


class StateListCtrl(wx.ListCtrl):
    def __init__(self, parent: wx.Window, *args, mv: "mainview.MainView", **kwargs):
        super().__init__(parent, *args, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, **kwargs)
        self.parent = parent
        self.mv = mv
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick)

    def AppendColumn(self, heading, width: int | float = -1):
        return super().AppendColumn(heading, width=self.mv.config.header_width(width))

    def build(self, _list):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list):
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item):
        "add button"
        ...

    def update_ui(self, idx: int, item):
        "update button"
        ...

    def pop_ui(self, idx: int):
        "delete button"
        assert idx >= 0
        self.DeleteItem(idx)

    def onSelect(self, e: wx.ListEvent):
        ...

    def onDeselect(self, e: wx.ListEvent):
        ...

    def onDoubleClick(self, e: wx.ListEvent):
        ...


class StatelessListCtrl(StateListCtrl):
    "in case of no related state, use this instead"

    def fetch(self) -> list:
        "data to preload"
        ...

    def preload(self):
        self.build(self.fetch())

    def reload(self):
        self.rebuild(self.fetch())
