from ui import mainview
from ui.generic_widgets import DoseTextCtrl, NumberTextCtrl
from db import *
import wx
import sqlite3
from typing import Any


class SampleDialog(wx.Dialog):
    def __init__(self, mv: "mainview.MainView"):
        super().__init__(
            parent=mv,
            title="Toa mẫu",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX,
        )
        self.mv = mv

        self.samplelist = SampleList(self, name="Danh sách toa mẫu")
        self.addsamplebtn = AddSampleButton(self)
        self.deletesamplebtn = DeleteSampleButton(self)
        self.itemlist = ItemList(self, name="Nội dung")
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
                *widget(self.samplelist, 1),
                (btn_row1, 0, wx.EXPAND),
                *widget(self.itemlist, 1),
                (item_row, 0, wx.EXPAND),
                (btn_row2, 0, wx.EXPAND),
                (self.CreateStdDialogButtonSizer(wx.OK), 0, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizerAndFit(sizer)


class SampleList(wx.ListCtrl):
    def __init__(self, parent: SampleDialog, name: str):
        super().__init__(
            parent, style=wx.LC_SINGLE_SEL | wx.LC_REPORT | wx.LC_NO_HEADER, name=name
        )
        self.parent = parent
        self.mv = parent.mv
        self.AppendColumn("name", width=self.mv.config.header_width(0.2))
        self.DeleteAllItems()
        for sp in self.parent.mv.state.all_sampleprescription.values():
            self.append_ui(sp)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def append_ui(self, sp: SamplePrescription) -> None:
        self.Append((sp.name,))

    def onSelect(self, e: wx.ListEvent):
        self.parent.deletesamplebtn.Enable()
        self.parent.picker.Enable()
        self.parent.dose.Enable()
        self.parent.times.Enable()
        idx: int = e.GetIndex()
        sp = self.parent.mv.state.all_sampleprescription[idx]
        self.parent.itemlist.build(sp.id)

    def onDeselect(self, _):
        self.parent.deletesamplebtn.Disable()
        self.parent.picker.Disable()
        self.parent.dose.Disable()
        self.parent.times.Disable()
        self.parent.itemlist.DeleteAllItems()


class AddSampleButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Thêm toa")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _) -> None:
        s = wx.GetTextFromUser("Tên toa mẫu mới", "Thêm toa mẫu")
        if s != "":
            sp = {"name": s}
            lastrowid = self.parent.mv.connection.insert(SamplePrescription, sp)
            assert lastrowid is not None
            sp = SamplePrescription(id=lastrowid, name=s)
            self.parent.mv.state.all_sampleprescription[lastrowid] = sp
            self.parent.samplelist.append_ui(sp)


class DeleteSampleButton(wx.Button):
    def __init__(self, parent: SampleDialog):
        super().__init__(parent, label="Xóa toa")
        self.parent = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _) -> None:
        idx: int = self.parent.samplelist.GetFirstSelected()
        assert idx >= 0
        sp = self.parent.mv.state.all_sampleprescription[idx]
        try:
            rowcount = self.parent.mv.connection.delete(SamplePrescription, sp.id)
            assert rowcount is not None
            del self.parent.mv.state.all_sampleprescription[idx]
            self.parent.samplelist.DeleteItem(idx)
            self.Disable()
        except Exception as error:
            wx.MessageBox(f"Lỗi không xóa được toa mẫu\n{error}", "Lỗi")


class Picker(wx.Choice):
    def __init__(self, parent: SampleDialog, name: str):
        super().__init__(
            parent,
            choices=[
                f"{wh.name}({wh.element})" for wh in parent.mv.state.all_warehouse.values()
            ],
            name=name,
        )
        self.Disable()
        self.Bind(wx.EVT_CHOICE, lambda _: parent.adddrugbtn.check_state())


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
            and self.parent.dose.GetValue() != ""
            and self.parent.times.GetValue() != ""
        ):
            self.Enable()
        else:
            self.Disable()

    def onClick(self, _):
        idx: int = self.parent.picker.GetCurrentSelection()
        wh = self.parent.mv.state.all_warehouse[idx]
        idx: int = self.parent.samplelist.GetFirstSelected()
        sp = self.parent.mv.state.all_sampleprescription[idx]

        times_str: str = self.parent.times.GetValue()
        times = int(times_str.strip())
        dose_str: str = self.parent.dose.GetValue()
        dose = dose_str.strip()
        lsp = {
            "drug_id": wh.id,
            "sample_id": sp.id,
            "times": times,
            "dose": dose,
        }
        try:
            lastrowid = self.parent.mv.connection.insert(LineSamplePrescription, lsp)
            assert lastrowid is not None
            self.parent.itemlist.append(
                {
                    "id": lastrowid,
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
        idx: int = self.parent.itemlist.GetFirstSelected()
        lsp_id = self.parent.itemlist.pop(idx)
        self.parent.mv.connection.delete(LineSamplePrescription, lsp_id)
        self.Disable()


class ItemList(wx.ListCtrl):
    def __init__(self, parent: SampleDialog, name: str):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, name=name)
        self.parent = parent
        self.mv = parent.mv
        self._list_id: list[int] = []
        self.AppendColumn("Tên thuốc", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Thành phần", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Số cữ", width=self.mv.config.header_width(0.05))
        self.AppendColumn("Liều 1 cữ", width=self.mv.config.header_width(0.05))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, sp_id: int):
        for lsp in self.parent.mv.connection.execute(
            f"""
            SELECT lsp.id, wh.name, wh.element, lsp.times, lsp.dose
            FROM (
                SELECT * FROM {LineSamplePrescription.__tablename__} 
                WHERE sample_id = {sp_id}
            ) AS lsp
            JOIN {Warehouse.__tablename__} as wh
            ON wh.id = lsp.drug_id
        """
        ).fetchall():
            self.append(lsp)

    def append(self, lsp: sqlite3.Row | dict[str, Any]):
        self.Append((lsp["name"], lsp["element"], lsp["times"], lsp["dose"]))
        self._list_id.append(lsp["id"])

    def pop(self, idx: int) -> int:
        assert idx >= 0
        self.DeleteItem(idx)
        lsp_id = self._list_id.pop(idx)
        return lsp_id

    def onSelect(self, _):
        self.parent.deletedrugbtn.Enable()

    def onDeselect(self, _):
        self.parent.deletedrugbtn.Disable()
