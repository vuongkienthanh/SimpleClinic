from ui import mainview as mv
from ui.generic_widgets import NumberTextCtrl
from db import Procedure
from misc import num_to_str_price
import wx


class ProcedureDialog(wx.Dialog):
    def __init__(self, parent: "mv.MainView"):
        super().__init__(
            parent=parent,
            title="Thủ thuật",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.mv = parent

        self.procedurelist = ProcedureList(self)
        self.addbtn = AddBtn(self)
        self.updatebtn = UpdateBtn(self)
        self.deletebtn = DeleteBtn(self)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany(
            [
                (self.addbtn, 0, wx.ALL, 5),
                (self.updatebtn, 0, wx.ALL, 5),
                (self.deletebtn, 0, wx.ALL, 5),
                (0, 0, 1),
                (self.CreateStdDialogButtonSizer(wx.OK), 0, wx.ALL, 5),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (self.procedurelist, 1, wx.EXPAND | wx.ALL, 5),
                (btn_sizer, 0, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizerAndFit(sizer)
        for pr in self.mv.state.allprocedurelist:
            self.procedurelist.append(pr)


class ProcedureList(wx.ListCtrl):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.parent = parent
        self.mv = parent.mv
        self.AppendColumn("Mã", width=self.mv.config.header_width(0.02))
        self.AppendColumn("Tên thủ thuật", width=self.mv.config.header_width(0.15))
        self.AppendColumn("Giá tiền", width=self.mv.config.header_width(0.05))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def append(self, pr: Procedure):
        self.Append((pr.id, pr.name, num_to_str_price(pr.price)))

    def pop(self, idx: int):
        self.DeleteItem(idx)

    def update(self, idx: int, pr: Procedure):
        self.SetItem(idx, 1, pr.name)
        self.SetItem(idx, 2, num_to_str_price(pr.price))

    def onSelect(self, e):
        self.parent.updatebtn.Enable()
        self.parent.deletebtn.Enable()

    def onDeselect(self, e):
        self.parent.updatebtn.Disable()
        self.parent.deletebtn.Disable()


class AddBtn(wx.Button):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, label="Thêm mới")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        AddDialog(self.parent).ShowModal()


class UpdateBtn(wx.Button):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, label="Cập nhật")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e):
        UpdateDialog(self.parent).ShowModal()


class DeleteBtn(wx.Button):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, label="Xóa")
        self.parent = parent
        self.mv = parent.mv
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, e):
        try:
            idx: int = self.parent.procedurelist.GetFirstSelected()
            assert idx >= 0
            pr = self.mv.state.allprocedurelist.pop(idx)
            self.parent.procedurelist.pop(idx)
            self.mv.order_book.procedurepage.procedure_picker.Delete(idx)
            if self.mv.order_book.procedurepage.procedure_list.ItemCount > 0:
                for i in range(
                    self.mv.order_book.procedurepage.procedure_list.ItemCount
                ):
                    if (
                        self.mv.order_book.procedurepage.procedure_list.GetItemText(
                            i, 0
                        )
                        == pr.name
                    ):
                        self.mv.order_book.procedurepage.procedure_list.DeleteItem(i)
                self.mv.price.FetchPrice()
        except Exception as error:
            wx.MessageBox(f"{error}", "Lỗi")


class BaseDialog(wx.Dialog):
    def __init__(self, parent: ProcedureDialog, title: str):
        super().__init__(parent, title=title)
        self.parent = parent
        self.mv = parent.mv
        self.name = wx.TextCtrl(
            self, size=self.mv.config.header_size(0.15), name="Tên thủ thuật:"
        )
        self.price = NumberTextCtrl(self, name="Giá tiền:")
        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.okbtn = wx.Button(self, id=wx.ID_OK)

        def widget(w):
            return (
                wx.StaticText(self, label=w.Name),
                0,
                wx.ALIGN_CENTER | wx.ALL,
                5,
            ), (w, 1, wx.EXPAND | wx.ALL, 5)

        entry_sizer = wx.FlexGridSizer(2, 2, 5, 5)
        entry_sizer.AddMany([*widget(self.name), *widget(self.price)])
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany(
            [(0, 0, 1), (self.cancelbtn, 0, wx.ALL, 5), (self.okbtn, 0, wx.ALL, 5)]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (entry_sizer, 0, wx.EXPAND | wx.ALL, 5),
                (btn_sizer, 0, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizerAndFit(sizer)

        self.okbtn.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e):
        ...


class AddDialog(BaseDialog):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, title="Thêm thủ thuật mới")

    def onClick(self, e):
        try:
            name = self.name.Value.strip()
            price = int(self.price.Value.strip())
            lastrowid = self.mv.connection.insert(
                Procedure, {"name": name, "price": price}
            )
            assert lastrowid is not None
            new_pr = Procedure(lastrowid, name, price)
            self.parent.procedurelist.append(new_pr)
            self.mv.state.allprocedurelist.append(new_pr)
            self.mv.order_book.procedurepage.procedure_picker.Append(name)
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"{error}", "Lỗi")


class UpdateDialog(BaseDialog):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, title="Thêm thủ thuật mới")
        self.idx: int = self.parent.procedurelist.GetFirstSelected()
        assert self.idx >= 0
        self.pr = self.mv.state.allprocedurelist[self.idx]
        self.name.ChangeValue(self.pr.name)
        self.price.ChangeValue(str(self.pr.price))

    def onClick(self, e):
        try:
            self.pr.name = self.name.Value.strip()
            self.pr.price = int(self.price.Value.strip())
            self.mv.connection.update(self.pr)
            self.parent.procedurelist.update(self.idx, self.pr)
            self.mv.order_book.procedurepage.procedure_picker.SetString(
                self.idx, self.pr.name
            )
            procedurelist = self.mv.order_book.procedurepage.procedure_list
            if len(procedurelist.pr_list) > 0:
                procedurelist.update(self.pr)
                self.mv.price.FetchPrice()
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"{error}", "Lỗi")
