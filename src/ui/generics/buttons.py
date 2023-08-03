import wx

from misc import minus_bm, plus_bm


class AddBtn(wx.Button):
    def __init__(self, parent, label="Thêm mới", *args, **kwargs):
        super().__init__(parent, label=label, *args, **kwargs)
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        self.Add()

    def Add(self):
        ...


class EditBtn(wx.Button):
    def __init__(self, parent, label="Cập nhật", *args, **kwargs):
        super().__init__(parent, label=label, *args, **kwargs)
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        self.Edit()

    def Edit(self):
        ...


class DeleteBtn(wx.Button):
    def __init__(self, parent, label="Xóa", *args, **kwargs):
        super().__init__(parent, label=label, *args, *kwargs)
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        self.Delete()

    def Delete(self):
        ...


class AddBitmapBtn(wx.BitmapButton):
    def __init__(self, parent):
        super().__init__(parent, bitmap=wx.Bitmap(plus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        self.Add()

    def Add(self):
        ...


class DeleteBitMapBtn(wx.BitmapButton):
    def __init__(self, parent):
        super().__init__(parent, bitmap=wx.Bitmap(minus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        self.Delete()

    def Delete(self):
        ...
