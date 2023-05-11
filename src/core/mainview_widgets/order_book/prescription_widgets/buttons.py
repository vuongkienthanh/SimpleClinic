from core.mainview_widgets.order_book import order_book
from core.mainview_widgets.order_book import prescription_widgets
from db import Warehouse, LineSamplePrescription
from misc import plus_bm, minus_bm, calc_quantity
from core.dialogs.sample_prescription_dialog import SampleDialog
import wx


class AddDrugButton(wx.BitmapButton):
    def __init__(self, parent: "order_book.PrescriptionPage"):
        super().__init__(parent, bitmap=wx.Bitmap(plus_bm))
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
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
                sp = self.mv.state.allsampleprescriptionlist[idx]
                llsp = self.mv.connection.execute(
                    f"""
                    SELECT lsp.drug_id, wh.name, lsp.times, lsp.dose, wh.usage, wh.usage_unit, wh.sale_unit, wh.sale_price
                    FROM (
                        SELECT * FROM {LineSamplePrescription.__tablename__} 
                        WHERE sample_id = {sp.id}
                    ) AS lsp
                    JOIN {Warehouse.__tablename__} as wh
                    ON wh.id = lsp.drug_id
                """
                ).fetchall()
                for lsp in llsp:
                    q = calc_quantity(
                        lsp["times"],
                        lsp["dose"],
                        self.mv.days.Value,
                        lsp["sale_unit"],
                        self.mv.config,
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
