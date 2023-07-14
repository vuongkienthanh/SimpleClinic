import wx

from ui.mainview_widgets.order_book.outclinic_prescription_page import page


class DrugListCtrl(wx.ListCtrl):
    def __init__(self, parent: "page.OutClinicPrescriptionPage"):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.parent = parent
        self.mv = parent.mv
        self.AppendColumn("STT", width=self.mv.config.header_width(0.02))
        self.AppendColumn("Thuốc", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Số lượng", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Cách dùng", width=self.mv.config.header_width(0.15))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

    def build(self, _list: LineDrugListState):
        for item in _list:
            self.append_ui(item)

    def rebuild(self, _list: LineDrugListState):
        self.DeleteAllItems()
        self.build(_list)

    def append_ui(self, item: LineDrugListStateItem):
        wh = self.mv.state.all_warehouse[item.warehouse_id]
        times, dose, quantity, note = times_dose_quantity_note_str(
            wh.usage,
            item.times,
            item.dose,
            item.quantity,
            wh.usage_unit,
            wh.sale_unit,
            item.usage_note,
        )

        self.Append(
            [
                self.ItemCount + 1,
                wh.name,
                times,
                dose,
                quantity,
                note,
            ]
        )

    def update_ui(self, idx: int, item: LineDrugListStateItem):
        wh = self.mv.state.all_warehouse[item.warehouse_id]
        times, dose, quantity, note = times_dose_quantity_note_str(
            wh.usage,
            item.times,
            item.dose,
            item.quantity,
            wh.usage_unit,
            wh.sale_unit,
            item.usage_note,
        )
        self.SetItem(idx, 2, times)
        self.SetItem(idx, 3, dose)
        self.SetItem(idx, 4, quantity)
        self.SetItem(idx, 5, note)

    def pop_ui(self, idx: int):
        assert idx >= 0
        self.DeleteItem(idx)
        for i in range(idx, self.ItemCount):
            self.SetItem(i, 0, str(i + 1))

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        old = self.mv.state.old_linedrug_list
        new = self.mv.state.new_linedrug_list
        if idx < len(old):
            target = old
        else:
            idx -= len(old)
            target = new
        item = target[idx]
        state = self.mv.state
        state.warehouse = state.all_warehouse[item.warehouse_id]
        state.linedrug = item

    def onDeselect(self, _):
        self.mv.state.warehouse = None
        self.mv.state.linedrug = None
