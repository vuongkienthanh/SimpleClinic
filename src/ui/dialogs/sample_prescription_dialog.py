from collections.abc import Iterable

import wx

from db import *
from ui import mainview
from ui.generics.widgets import DoseTextCtrl, NumberTextCtrl


class SampleDialog(wx.Dialog):
    def __init__(self, mv: "mainview.MainView"):
        super().__init__(
            parent=mv,
            title="Toa mẫu",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX,
        )
        self.mv = mv
        self.samplelistctrl = SampleListCtrl(self, name="Danh sách toa mẫu")
        self.addsamplebtn = AddSampleButton(self)
        self.updatesamplebtn = UpdateSampleButton(self)
        self.deletesamplebtn = DeleteSampleButton(self)
        self.sampleitemlistctrl = SampleItemListCtrl(self, name="Nội dung")
        self.picker = Picker(self, name="Thuốc")
        self.times = Times(self, name="Số cữ")
        self.dose = Dose(self, name="Liều")
        self.adddrugbtn = AddDrugButton(self)
        self.deletedrugbtn = DeleteDrugButton(self)

        def widget(w, p=0):
            s: str = w.Name
            return (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER | wx.ALL, 5), (
                w,
                p,
                wx.EXPAND | wx.ALL,
                5,
            )

        btn_row1 = wx.BoxSizer(wx.HORIZONTAL)
        btn_row1.AddMany(
            [
                (self.addsamplebtn, 0, wx.ALL, 5),
                (self.updatesamplebtn, 0, wx.ALL, 5),
                (self.deletesamplebtn, 0, wx.ALL, 5),
                (0, 0, 1),
            ]
        )
        item_row = wx.BoxSizer(wx.HORIZONTAL)
        item_row.AddMany(
            [
                *widget(self.picker, 1),
                *widget(self.times),
                *widget(self.dose),
            ]
        )
        btn_row2 = wx.BoxSizer(wx.HORIZONTAL)
        btn_row2.AddMany(
            [
                (self.adddrugbtn, 0, wx.ALL, 5),
                (self.deletedrugbtn, 0, wx.ALL, 5),
                (0, 0, 1),
            ]
        )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                *widget(self.samplelistctrl, 1),
                (btn_row1, 0, wx.EXPAND),
                *widget(self.sampleitemlistctrl, 1),
                (item_row, 0, wx.EXPAND),
                (btn_row2, 0, wx.EXPAND),
                (self.CreateStdDialogButtonSizer(wx.OK), 0, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizerAndFit(sizer)
        self.samplelistctrl.build(self.mv.state.all_sampleprescription.values())


class SampleListCtrl(wx.ListCtrl):
    def __init__(self, parent: SampleDialog, name: str):
        super().__init__(parent, style=wx.LC_SINGLE_SEL | wx.LC_REPORT, name=name)
        self.parent = parent
        self.mv = parent.mv
        self.AppendColumn("Mã", width=self.mv.config.header_width(0.05))
        self.AppendColumn("Tên", width=self.mv.config.header_width(0.2))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, _list: Iterable[SamplePrescription]):
        for item in _list:
            self.append_ui(item)

    def append_ui(self, sp: SamplePrescription):
        self.Append((sp.id, sp.name))

    def update_ui(self, idx: int, sp: SamplePrescription):
        self.SetItem(idx, 1, sp.name)

    def onSelect(self, e: wx.ListEvent):
        self.parent.deletesamplebtn.Enable()
        self.parent.picker.Enable()
        self.parent.dose.Enable()
        self.parent.times.Enable()
        idx: int = e.GetIndex()
        sp_id = int(self.GetItemText(idx, 0))
        self.parent.sampleitemlistctrl.build(
            self.parent.sampleitemlistctrl.fetch_list(sp_id)
        )

    def onDeselect(self, _):
        self.parent.deletesamplebtn.Disable()
        self.parent.picker.Disable()
        self.parent.dose.Disable()
        self.parent.times.Disable()
        self.parent.sampleitemlistctrl.DeleteAllItems()


class AddSampleButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Thêm toa")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        s = wx.GetTextFromUser("Tên toa mẫu mới", "Thêm toa mẫu")
        if s != "":
            sp = {"name": s}
            new_sampleprescription_id = self.parent.mv.connection.insert(
                SamplePrescription, sp
            )
            assert new_sampleprescription_id is not None
            new_sampleprescription = SamplePrescription(
                id=new_sampleprescription_id, **sp
            )
            self.parent.mv.state.all_sampleprescription[
                new_sampleprescription_id
            ] = new_sampleprescription
            self.parent.samplelistctrl.append_ui(new_sampleprescription)


class UpdateSampleButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Đổi tên")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        s = wx.GetTextFromUser(
            "Tên toa mẫu mới",
            "Đổi tên",
            self.parent.samplelistctrl.GetItemText(
                self.parent.samplelistctrl.GetFirstSelected(), 1
            ),
        )
        if s != "":
            idx = self.parent.samplelistctrl.GetFirstSelected()
            updated_sp = SamplePrescription(
                int(self.parent.samplelistctrl.GetItemText(idx)),
                s,
            )
            self.parent.mv.connection.update(updated_sp)
            self.parent.mv.state.all_sampleprescription[updated_sp.id].name = s
            self.parent.samplelistctrl.update_ui(idx, updated_sp)


class DeleteSampleButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Xóa toa")
        self.parent = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _) -> None:
        idx: int = self.parent.samplelistctrl.GetFirstSelected()
        assert idx >= 0
        sp = self.parent.mv.state.all_sampleprescription[
            int(self.parent.samplelistctrl.GetItemText(idx))
        ]
        try:
            rowcount = self.parent.mv.connection.delete(SamplePrescription, sp.id)
            assert rowcount is not None
            del self.parent.mv.state.all_sampleprescription[sp.id]
            self.parent.samplelistctrl.DeleteItem(idx)
            self.Disable()
        except Exception as error:
            wx.MessageBox(f"Lỗi không xóa được toa mẫu\n{error}", "Lỗi")


class Picker(wx.Choice):
    def __init__(self, parent: SampleDialog, name: str):
        self._choice_to_wh_id: dict[int, int] = {}
        choices = []
        for idx, wh in enumerate(parent.mv.state.all_warehouse.values()):
            choices.append(f"{wh.name}({wh.element})")
            self._choice_to_wh_id[idx] = wh.id

        super().__init__(
            parent,
            choices=choices,
            name=name,
        )
        self.Disable()
        self.Bind(wx.EVT_CHOICE, lambda _: parent.adddrugbtn.check_state())

    def GetSelectionWarehouseID(self):
        return self._choice_to_wh_id[self.GetSelection()]


class Dose(DoseTextCtrl):
    def __init__(self, parent: SampleDialog, name: str):
        super().__init__(parent, name=name)
        self.SetHint("liều")
        self.Disable()
        self.Bind(wx.EVT_TEXT, lambda _: parent.adddrugbtn.check_state())


class Times(NumberTextCtrl):
    def __init__(self, parent: SampleDialog, name: str):
        super().__init__(parent, name=name)
        self.SetHint("lần")
        self.Disable()
        self.Bind(wx.EVT_TEXT, lambda _: parent.adddrugbtn.check_state())


class AddDrugButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Thêm thuốc")
        self.parent = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def check_state(self):
        if (
            self.parent.picker.GetSelection() != wx.NOT_FOUND
            and self.parent.dose.Value != ""
            and self.parent.times.Value != ""
        ):
            self.Enable()
        else:
            self.Disable()

    def onClick(self, _):
        wh_id: int = self.parent.picker.GetSelectionWarehouseID()
        wh = self.parent.mv.state.all_warehouse[wh_id]
        sp_id: int = int(
            self.parent.samplelistctrl.GetItemText(
                self.parent.samplelistctrl.GetFirstSelected()
            )
        )
        sp = self.parent.mv.state.all_sampleprescription[sp_id]

        times: int = int(self.parent.times.Value.strip())
        dose: str = self.parent.dose.Value.strip()
        lsp = {
            "warehouse_id": wh.id,
            "sample_id": sp.id,
            "times": times,
            "dose": dose,
        }
        try:
            new_lsp_id = self.parent.mv.connection.insert(LineSamplePrescription, lsp)
            assert new_lsp_id is not None
            self.parent.sampleitemlistctrl.append_ui(
                {
                    "id": new_lsp_id,
                    "name": wh.name,
                    "element": wh.element,
                    "times": times,
                    "dose": dose,
                }
            )
            self.parent.picker.SetSelection(wx.NOT_FOUND)
            self.parent.times.Clear()
            self.parent.dose.Clear()
            self.Disable()
        except Exception as error:
            wx.MessageBox(f"Không thêm thuốc vào toa mẫu được\n{error}", "Lỗi")


class DeleteDrugButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Xóa thuốc")
        self.parent = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        idx: int = self.parent.sampleitemlistctrl.GetFirstSelected()
        lsp_id = int(self.parent.sampleitemlistctrl.GetItemText(idx))
        try:
            self.parent.mv.connection.delete(LineSamplePrescription, lsp_id)
            self.parent.sampleitemlistctrl.DeleteItem(idx)
            self.Disable()
        except Exception as error:
            wx.MessageBox(f"Không xoá thuốc được\n{error}", "Lỗi")


class SampleItemListCtrl(wx.ListCtrl):
    def __init__(self, parent: SampleDialog, name: str):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, name=name)
        self.parent = parent
        self.mv = parent.mv
        self.AppendColumn("Mã", width=self.mv.config.header_width(0.05))
        self.AppendColumn("Tên thuốc", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Thành phần", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Số cữ", width=self.mv.config.header_width(0.05))
        self.AppendColumn("Liều 1 cữ", width=self.mv.config.header_width(0.05))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def fetch_list(self, sp_id: int):
        return self.parent.mv.connection.execute(
            f"""
            SELECT lsp.id, wh.name, wh.element, lsp.times, lsp.dose
            FROM (
                SELECT * FROM {LineSamplePrescription.__tablename__} 
                WHERE sample_id = {sp_id}
            ) AS lsp
            JOIN {Warehouse.__tablename__} as wh
            ON wh.id = lsp.warehouse_id
        """
        ).fetchall()

    def build(self, _list: list[Mapping[str, Any]]):
        for lsp in _list:
            self.append_ui(lsp)

    def append_ui(self, lsp: Mapping[str, Any]):
        self.Append((lsp["id"], lsp["name"], lsp["element"], lsp["times"], lsp["dose"]))

    def onSelect(self, _):
        self.parent.deletedrugbtn.Enable()

    def onDeselect(self, _):
        self.parent.deletedrugbtn.Disable()
