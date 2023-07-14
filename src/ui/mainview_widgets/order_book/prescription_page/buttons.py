import wx

from db import LineSamplePrescription
from misc import calc_quantity, note_str
from state.linedrug_state import LineDrugListStateItem, NewLineDrugListStateItem
from ui.dialogs.sample_prescription_dialog import SampleDialog
from ui.mainview_widgets.order_book.base_page import BaseAddButton, BaseDeleteButton
from ui.mainview_widgets.order_book.prescription_page import page


class AddDrugButton(BaseAddButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent: page.PrescriptionPage

    def Add(self):
        page = self.parent
        mv = self.parent.mv
        state = mv.state
        wh = state.warehouse
        ld = state.linedrug
        if wh is None:
            return
        note: str | None
        match page.note.Value:
            case n if n == note_str(
                wh.usage, int(page.times.Value), page.dose.Value, wh.usage_unit, None
            ):
                note = None
            case n:
                note = n
        if page.check_wh_do_ti_qua_filled():
            if ld is None:
                new_ld = NewLineDrugListStateItem(
                    wh.id,
                    int(page.times.Value),
                    page.dose.Value,
                    int(page.quantity.Value),
                    note,
                )
                state.new_linedrug_list.append(new_ld)
                page.drug_list.append_ui(new_ld)
            elif isinstance(ld, LineDrugListStateItem):
                ld.times = int(page.times.Value)
                ld.dose = page.dose.Value
                ld.quantity = int(page.quantity.Value)
                ld.usage_note = note
                idx: int = page.drug_list.GetFirstSelected()
                page.drug_list.update_ui(idx, ld)
            state.warehouse = None
            state.linedrug = None
            mv.price.FetchPrice()
            page.drug_picker.SetFocus()


class DeleteDrugButton(BaseDeleteButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent: page.PrescriptionPage

    def Delete(self):
        idx: int = self.parent.drug_list.GetFirstSelected()
        if idx != -1:
            old = self.parent.mv.state.old_linedrug_list
            new = self.parent.mv.state.new_linedrug_list
            if idx < len(old):
                self.parent.mv.state.to_delete_old_linedrug_list.append(old[idx])
                old.pop(idx)
            else:
                idx -= len(old)
                new.pop(idx)
            self.parent.drug_list.pop_ui(idx)
            self.parent.mv.state.warehouse = None
            self.parent.mv.state.linedrug = None
            self.parent.mv.price.FetchPrice()


class ReuseDrugListButton(wx.Button):
    def __init__(self, parent: "page.PrescriptionPage"):
        super().__init__(parent, label="Lượt khám mới với toa cũ này")
        self.parent = parent
        self.mv = parent.parent.mv
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        _list = self.mv.state.old_linedrug_list
        weight = self.mv.weight.GetWeight()
        self.mv.state.visit = None
        self.mv.weight.SetWeight(weight)
        self.parent.drug_list.rebuild(_list)
        for old_linedrug in _list:
            self.mv.state.new_linedrug_list.append(
                NewLineDrugListStateItem(
                    warehouse_id=old_linedrug.warehouse_id,
                    times=old_linedrug.times,
                    dose=old_linedrug.dose,
                    quantity=old_linedrug.quantity,
                    usage_note=old_linedrug.usage_note,
                )
            )
        self.mv.updatequantitybtn.update_quantity()


class UseSamplePrescriptionBtn(wx.Button):
    def __init__(self, parent: "page.PrescriptionPage"):
        super().__init__(parent, label="Sử dụng toa mẫu")
        self.parent = parent
        self.mv = parent.parent.mv
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        dlg = SampleDialog(self.mv)
        if dlg.ShowModal() == wx.ID_OK:
            idx: int = dlg.samplelistctrl.GetFirstSelected()
            sp_id: int = int(dlg.samplelistctrl.GetItemText(idx))
            if idx != -1:
                self.parent.drug_list.DeleteAllItems()
                self.mv.state.to_delete_old_linedrug_list.extend(
                    self.mv.state.old_linedrug_list.copy()
                )
                self.mv.state.old_linedrug_list.clear()
                self.mv.state.new_linedrug_list.clear()
                sp = self.mv.state.all_sampleprescription[sp_id]
                for lsp in (
                    LineSamplePrescription(*row)
                    for row in self.mv.connection.execute(
                        f"SELECT * FROM {LineSamplePrescription.__tablename__} WHERE sample_id = {sp.id}"
                    ).fetchall()
                ):
                    item = NewLineDrugListStateItem(
                        warehouse_id=lsp.warehouse_id,
                        times=lsp.times,
                        dose=lsp.dose,
                        quantity=calc_quantity(
                            lsp.times,
                            lsp.dose,
                            self.mv.days.Value,
                            self.mv.state.all_warehouse[lsp.warehouse_id].sale_unit,
                            self.mv.config,
                        ),
                        usage_note=None,
                    )
                    self.parent.drug_list.append_ui(item)
                    self.mv.state.new_linedrug_list.append(item)
                self.mv.price.FetchPrice()
