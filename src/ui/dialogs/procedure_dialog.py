import wx

from db import Procedure
from misc import num_to_str_price
from state.all_dict_states.all_procedure_state import AllProcedureState
from ui import mainview as mv
from ui.generics.widgets import GenericListCtrl, NumberTextCtrl


class ProcedureDialog(wx.Dialog):
    def __init__(self, parent: "mv.MainView"):
        super().__init__(
            parent=parent,
            title="Thủ thuật",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.mv = parent

        self.procedurelistctrl = ProcedureListCtrl(self)
        self.addbtn = AddBtn(self)
        self.updatebtn = UpdateBtn(self)
        self.deletebtn = DeleteBtn(self)
        okbtn = wx.Button(self, id=wx.ID_OK)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany(
            [
                (self.addbtn, 0, wx.ALL, 5),
                (self.updatebtn, 0, wx.ALL, 5),
                (self.deletebtn, 0, wx.ALL, 5),
                (0, 0, 1),
                (okbtn, 0, wx.ALL, 5),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (self.procedurelistctrl, 1, wx.EXPAND | wx.ALL, 5),
                (btn_sizer, 0, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onClose, okbtn)
        self.procedurelistctrl.start()

    def onClose(self, e):
        self.mv.order_book.procedurepage.procedure_picker.rebuild(
            self.mv.state.all_procedure
        )
        self.mv.state.new_lineprocedure_list = []
        self.mv.order_book.procedurepage.procedure_list.rebuild(
            self.mv.state.old_lineprocedure_list
        )
        self.mv.price.FetchPrice()
        e.Skip()


class ProcedureListCtrl(GenericListCtrl):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, mv=parent.mv)
        self.parent = parent
        self.AppendColumn("Mã", 0.02)
        self.AppendColumn("Tên thủ thuật", 0.15)
        self.AppendColumn("Giá tiền", 0.05)

    def start(self):
        self.rebuild(self.mv.state.all_procedure.values())

    def append_ui(self, item: Procedure):
        self.Append((item.id, item.name, num_to_str_price(item.price)))

    def update_ui(self, idx: int, item: Procedure):
        self.SetItem(idx, 1, item.name)
        self.SetItem(idx, 2, num_to_str_price(item.price))

    def onSelect(self, _):
        self.parent.updatebtn.Enable()
        self.parent.deletebtn.Enable()

    def onDeselect(self, _):
        self.parent.updatebtn.Disable()
        self.parent.deletebtn.Disable()

    def onDoubleClick(self, _):
        UpdateDialog(self.parent).ShowModal()


class AddBtn(wx.Button):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, label="Thêm mới")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        AddDialog(self.parent).ShowModal()


class UpdateBtn(wx.Button):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, label="Cập nhật")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        UpdateDialog(self.parent).ShowModal()


class DeleteBtn(wx.Button):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, label="Xóa")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        mv = self.parent.mv
        idx: int = self.parent.procedurelistctrl.GetFirstSelected()
        assert idx >= 0
        pr = mv.state.all_procedure[
            int(self.parent.procedurelistctrl.GetItemText(idx, 0))
        ]
        if (
            wx.MessageBox("Xác nhận?", "Xoá thủ thuật", style=wx.OK | wx.CANCEL)
            == wx.ID_OK
        ):
            try:
                mv.connection.delete(pr)
                del mv.state.all_procedure[pr.id]
                self.parent.procedurelistctrl.pop_ui(idx)
            except Exception as error:
                wx.MessageBox(f"Không xoá được\n{error}", "Lỗi")


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

    def onClick(self, _):
        ...


class AddDialog(BaseDialog):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, title="Thêm thủ thuật mới")

    def onClick(self, e):
        new = {
            "name": self.name.Value.strip(),
            "price": int(self.price.Value.strip()),
        }

        try:
            new_pr_id = self.mv.connection.insert(Procedure, new)
            assert new_pr_id is not None
            new_pr = Procedure(new_pr_id, **new)
            self.parent.procedurelistctrl.append_ui(new_pr)
            self.mv.state.all_procedure[new_pr_id] = new_pr
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"Không thêm mới được\n{error}", "Lỗi")


class UpdateDialog(BaseDialog):
    def __init__(self, parent: ProcedureDialog):
        super().__init__(parent, title="Cập nhật thủ thuật")
        self.idx = self.parent.procedurelistctrl.GetFirstSelected()
        assert self.idx >= 0
        self.pr = self.mv.state.all_procedure[
            int(self.parent.procedurelistctrl.GetItemText(self.idx, 0))
        ]
        self.name.ChangeValue(self.pr.name)
        self.price.ChangeValue(str(self.pr.price))

    def onClick(self, e):
        old = {
            "id": self.pr.id,
            "name": self.name.Value.strip(),
            "price": int(self.price.Value.strip()),
        }
        try:
            self.mv.connection.update(Procedure(**old))
            for field in self.pr.fields():
                setattr(self.pr, field, old[field])
            self.parent.procedurelistctrl.update_ui(self.idx, self.pr)
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"Không cập nhật được\n{error}", "Lỗi")
