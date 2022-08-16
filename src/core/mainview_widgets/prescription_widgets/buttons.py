from core.mainview_widgets import order_book
from core.mainview_widgets import prescription_widgets
from db.db_class import Warehouse, LineSamplePrescription
from paths import plus_bm, minus_bm
from core.dialogs.sample_prescription_dialog import SampleDialog
from other_func import calc_quantity
import wx


class AddDrugButton(wx.BitmapButton):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, bitmap=wx.Bitmap(plus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        self.Add()

    def Add(self):
        if self.parent.check_all_filled():
            self.parent.drug_list.upsert()
            self.parent.parent.mv.state.warehouse = None
            self.parent.parent.mv.price.FetchPrice()
            self.parent.drug_picker.SetFocus()


class DelDrugButton(wx.BitmapButton):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, bitmap=wx.Bitmap(minus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        idx = self.parent.drug_list.GetFirstSelected()
        if idx != -1:
            self.parent.drug_list.pop(idx)
            self.parent.parent.mv.state.warehouse = None
            self.parent.parent.mv.price.FetchPrice()


class ReuseDrugListButton(wx.Button):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, label="Lượt khám mới với toa cũ này")
        self.parent = parent
        self.mv = parent.parent.mv
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        lld = self.mv.state.linedruglist
        weight = self.mv.weight.GetWeight()
        self.mv.state.visit = None
        self.mv.weight.SetWeight(weight)
        self.parent.drug_list.rebuild(lld)
        self.mv.updatequantitybtn.update_quantity()


class UseSamplePrescriptionBtn(wx.Button):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, label="Sử dụng toa mẫu")
        self.parent = parent
        self.mv = parent.parent.mv
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, e: wx.CommandEvent):
        dlg = SampleDialog(self.mv)
        if dlg.ShowModal() == wx.ID_OK:
            idx: int = dlg.samplelist.GetFirstSelected()
            if idx != -1:
                self.parent.drug_list.DeleteAllItems()
                sp = self.mv.state.sampleprescriptionlist[idx]
                llsp = self.mv.con.execute(
                    f"""
                    SELECT lsp.drug_id, wh.name, lsp.times, lsp.dose, wh.usage, wh.usage_unit, wh.sale_unit, wh.sale_price
                    FROM (
                        SELECT * FROM {LineSamplePrescription.table_name} 
                        WHERE sample_id = {sp.id}
                    ) AS lsp
                    JOIN {Warehouse.table_name} as wh
                    ON wh.id = lsp.drug_id
                """
                ).fetchall()
                for lsp in llsp:
                    q = calc_quantity(
                        lsp["times"], lsp["dose"], self.mv.days.Value, lsp["sale_unit"]
                    )
                    assert q is not None
                    self.parent.drug_list.append(
                        prescription_widgets.DrugListItem(
                            drug_id=lsp["drug_id"],
                            times=lsp["times"],
                            dose=lsp["dose"],
                            quantity=q,
                            name=lsp["name"],
                            note=None,
                            usage=lsp["usage"],
                            usage_unit=lsp["usage_unit"],
                            sale_unit=lsp["sale_unit"],
                            sale_price=lsp["sale_price"],
                        )
                    )
                    self.mv.price.FetchPrice()
