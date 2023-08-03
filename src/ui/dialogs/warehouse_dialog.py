import wx

from db import Warehouse
from misc import check_blank_to_none, check_none_to_blank, sale_unit_to_db
from ui import mainview
from ui.generics import CalendarDatePicker, NumberTextCtrl, StatelessListCtrl


class WarehouseDialog(wx.Dialog):
    def __init__(self, mv: "mainview.MainView"):
        super().__init__(
            mv,
            title="Kho thuốc",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX,
        )
        self.mv = mv
        self.search = DrugSearchCtrl(self)
        self.warehouselistctrl = WarehouseListCtrl(self)
        self.addbtn = AddBtn(self)
        self.updatebtn = UpdateBtn(self)
        self.deletebtn = DeleteBtn(self)
        okbtn = wx.Button(self, id=wx.ID_OK)

        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        search_sizer.AddMany(
            [
                (wx.StaticText(self, label="Tìm kiếm"), 0, wx.ALL | wx.ALIGN_CENTER, 5),
                (self.search, 1, wx.ALL, 5),
            ]
        )
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany(
            [
                (self.addbtn, 0, wx.RIGHT, 5),
                (self.updatebtn, 0, wx.RIGHT, 5),
                (self.deletebtn, 0, wx.RIGHT, 5),
                (0, 0, 1),
                (okbtn, 0, wx.RIGHT, 5),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (search_sizer, 0, wx.EXPAND),
                (self.warehouselistctrl, 1, wx.EXPAND | wx.ALL, 5),
                (btn_sizer, 0, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onClose, okbtn)
        self.Maximize()
        self.warehouselistctrl.preload()

    def onClose(self, e):
        self.mv.state.new_linedrug_list = []
        self.mv.order_book.prescriptionpage.drug_list.rebuild(
            self.mv.state.old_linedrug_list
        )
        self.mv.price.FetchPrice()
        e.Skip()


class WarehouseListCtrl(StatelessListCtrl):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent, mv=parent.mv)
        self.parent = parent
        self.AppendColumn("Mã", 0.03)
        self.AppendColumn("Tên", 0.1)
        self.AppendColumn("Thành phần", 0.1)
        self.AppendColumn("Số lượng", 0.04)
        self.AppendColumn("Đơn vị sử dụng", 0.06)
        self.AppendColumn("Cách sử dụng", 0.06)
        self.AppendColumn("Giá mua", 0.03)
        self.AppendColumn("Giá bán", 0.03)
        self.AppendColumn("Đơn vị bán", 0.04)
        self.AppendColumn("Ngày hết hạn", 0.05)
        self.AppendColumn("Xuất xứ", 0.06)
        self.AppendColumn("Ghi chú", 0.06)

    def fetch(self):
        return self.mv.state.all_warehouse.values()

    def append_ui(self, item: Warehouse):
        self.Append(
            [
                str(item.id),
                item.name,
                item.element,
                str(item.quantity),
                item.usage_unit,
                item.usage,
                str(item.purchase_price),
                str(item.sale_price),
                item.sale_unit if item.sale_unit is not None else item.usage_unit,
                item.expire_date.strftime("%d/%m/%Y")
                if item.expire_date is not None
                else "",
                check_none_to_blank(item.made_by),
                check_none_to_blank(item.drug_note),
            ]
        )
        self.check_min_quantity_and_change_color(self.ItemCount - 1, item)

    def update_ui(self, idx: int, item: Warehouse):
        self.SetItem(idx, 1, item.name)
        self.SetItem(idx, 2, item.element)
        self.SetItem(idx, 3, str(item.quantity))
        self.SetItem(idx, 4, item.usage_unit)
        self.SetItem(idx, 5, item.usage)
        self.SetItem(idx, 6, str(item.purchase_price))
        self.SetItem(idx, 7, str(item.sale_price))
        self.SetItem(
            idx, 8, item.sale_unit if item.sale_unit is not None else item.usage_unit
        )
        self.SetItem(
            idx,
            9,
            item.expire_date.strftime("%d/%m/%Y")
            if item.expire_date is not None
            else "",
        )
        self.SetItem(idx, 10, check_none_to_blank(item.made_by))
        self.SetItem(idx, 11, check_none_to_blank(item.drug_note))
        self.check_min_quantity_and_change_color(idx, item)

    def check_min_quantity_and_change_color(self, idx: int, item: Warehouse):
        if item.quantity <= self.mv.config.minimum_drug_quantity_alert:
            self.SetItemTextColour(idx, wx.Colour(252, 3, 57))

    def onSelect(self, _):
        self.parent.updatebtn.Enable()
        self.parent.deletebtn.Enable()

    def onDeselect(self, _):
        self.parent.updatebtn.Disable()
        self.parent.deletebtn.Disable()

    def onDoubleClick(self, _):
        UpdateDialog(self.parent).ShowModal()


class DrugSearchCtrl(wx.SearchCtrl):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent)
        self.SetHint("Tên thuốc hoặc thành phần thuốc")
        self.parent = parent
        self.mv = parent.mv
        self.Bind(wx.EVT_SEARCH, self.onSearchEnter)
        self.Bind(wx.EVT_TEXT, self.onText)

    def onSearchEnter(self, e):
        match self.Value.strip().casefold():
            case "":
                self.parent.warehouselistctrl.reload()
            case s:
                self.parent.warehouselistctrl.rebuild(
                    filter(
                        lambda wh: (s in wh.name.casefold())
                        or (s in wh.element.casefold()),
                        self.mv.state.all_warehouse.values(),
                    )
                )
        e.Skip()

    def onText(self, e: wx.CommandEvent):
        if len(e.EventObject.Value) == 0:
            self.parent.warehouselistctrl.reload()
        e.Skip()


class AddBtn(wx.Button):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent, label="Thêm mới")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        AddDialog(self.parent).ShowModal()


class UpdateBtn(wx.Button):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent, label="Cập nhật")
        self.parent = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        UpdateDialog(self.parent).ShowModal()


class DeleteBtn(wx.Button):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent, label="Xóa")
        self.parent = parent
        self.mv = parent.mv
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        idx: int = self.parent.warehouselistctrl.GetFirstSelected()
        assert idx >= 0
        wh = self.mv.state.all_warehouse[
            int(self.parent.warehouselistctrl.GetItemText(idx, 0))
        ]
        if (
            wx.MessageBox(
                f"Xoá thuốc {wh.name}",
                "Xoá thuốc",
                style=wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL,
            )
            == wx.YES
        ):
            try:
                self.mv.connection.delete(wh)
                del self.mv.state.all_warehouse[wh.id]
                self.parent.warehouselistctrl.pop_ui(idx)
            except Exception as error:
                wx.MessageBox(f"Không xoá được\n{error}", "Lỗi")


class BaseDialog(wx.Dialog):
    def __init__(self, parent: WarehouseDialog, title: str):
        super().__init__(
            parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, title=title
        )
        self.parent = parent
        self.mv = parent.mv
        self.title = title

        self.name = wx.TextCtrl(self, name="Tên thuốc")
        self.element = wx.TextCtrl(self, name="Thành phần")
        self.quantity = NumberTextCtrl(self, name="Số lượng")
        self.usage_unit = wx.TextCtrl(self, name="Đơn vị sử dụng")
        self.usage = wx.TextCtrl(self, name="Cách sử dụng")
        self.purchase_price = NumberTextCtrl(self, name="Giá mua")
        self.sale_price = NumberTextCtrl(self, name="Giá bán")
        self.sale_unit = wx.TextCtrl(self, name="Đơn vị bán")
        self.expire_date = CalendarDatePicker(self, name="Hạn sử dụng")
        self.made_by = wx.TextCtrl(self, name="Xuất xứ")
        self.drug_note = wx.TextCtrl(self, style=wx.TE_MULTILINE, name="Ghi chú")
        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.okbtn = wx.Button(self, id=wx.ID_OK)

        self.mandatory = (
            self.name,
            self.element,
            self.quantity,
            self.usage_unit,
            self.usage,
            self.purchase_price,
            self.sale_price,
        )

        def widget(w):
            s: str = w.Name
            if w in self.mandatory:
                s += "*"
            return (
                wx.StaticText(self, label=s),
                0,
                wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                3,
            ), (w, 1, wx.EXPAND | wx.ALL, 3)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany(
            [(0, 0, 1), (self.cancelbtn, 0, wx.ALL, 5), (self.okbtn, 0, wx.ALL, 5)]
        )
        entry_sizer = wx.FlexGridSizer(11, 2, 3, 3)
        entry_sizer.AddGrowableCol(1, 3)
        entry_sizer.AddGrowableRow(10, 2)
        entry_sizer.AddMany(
            [
                *widget(self.name),
                *widget(self.element),
                *widget(self.quantity),
                *widget(self.usage_unit),
                *widget(self.usage),
                *widget(self.purchase_price),
                *widget(self.sale_price),
                *widget(self.sale_unit),
                *widget(self.expire_date),
                *widget(self.made_by),
                *widget(self.drug_note),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (entry_sizer, 1, wx.EXPAND | wx.ALL, 5),
                (
                    wx.StaticText(
                        self, label="* là bắt buộc; Không có hạn sử dụng thì để hôm nay"
                    ),
                    0,
                    wx.EXPAND | wx.ALL,
                    5,
                ),
                (btn_sizer, 0, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizerAndFit(sizer)
        self.okbtn.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        ...

    def is_valid(self) -> bool:
        for widget in self.mandatory:
            val: str = widget.Value
            name: str = widget.Name
            if val.strip() == "":
                wx.MessageBox(f"Chưa nhập đủ thông tin\n{name}", self.title)
                return False
        else:
            return True

    def get_wh(self):
        return {
            "name": self.name.Value.strip(),
            "element": self.element.Value.strip(),
            "quantity": int(self.quantity.Value.strip()),
            "usage_unit": self.usage_unit.Value.strip(),
            "usage": self.usage.Value.strip(),
            "purchase_price": int(self.purchase_price.Value.strip()),
            "sale_price": int(self.sale_price.Value.strip()),
            "sale_unit": sale_unit_to_db(self.sale_unit.Value, self.usage_unit.Value),
            "expire_date": self.expire_date.checked_GetDate(),
            "made_by": check_blank_to_none(self.made_by.Value),
            "drug_note": check_blank_to_none(self.drug_note.Value),
        }


class AddDialog(BaseDialog):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent, title="Thêm thuốc mới")

    def onClick(self, e):
        if self.is_valid():
            wh = self.get_wh()
            try:
                new_wh_id = self.mv.connection.insert(Warehouse, wh)
                assert new_wh_id is not None
                new_wh = Warehouse(id=new_wh_id, **wh)
                s = self.parent.search.Value.strip().casefold()
                if s in new_wh.name.casefold() or s in new_wh.element.casefold():
                    self.parent.warehouselistctrl.append_ui(new_wh)
                self.mv.state.all_warehouse[new_wh_id] = new_wh
                e.Skip()
            except Exception as error:
                wx.MessageBox(f"Thêm mới thất bại\n{error}", "Thêm mới")


class UpdateDialog(BaseDialog):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent, title="Cập nhật thuốc")
        self.idx = self.parent.warehouselistctrl.GetFirstSelected()
        assert self.idx >= 0
        self.wh = self.mv.state.all_warehouse[
            int(self.parent.warehouselistctrl.GetItemText(self.idx, 0))
        ]
        self.name.ChangeValue(self.wh.name)
        self.element.ChangeValue(self.wh.element)
        self.quantity.ChangeValue(str(self.wh.quantity))
        self.usage_unit.ChangeValue(self.wh.usage_unit)
        self.usage.ChangeValue(self.wh.usage)
        self.purchase_price.ChangeValue(str(self.wh.purchase_price))
        self.sale_price.ChangeValue(str(self.wh.sale_price))
        if self.wh.sale_unit is None:
            self.sale_unit.ChangeValue(self.wh.usage_unit)
        else:
            self.sale_unit.ChangeValue(self.wh.sale_unit)
        if self.wh.expire_date is not None:
            self.expire_date.SetDate(self.wh.expire_date)
        self.made_by.ChangeValue(check_none_to_blank(self.wh.made_by))
        self.drug_note.ChangeValue(check_none_to_blank(self.wh.drug_note))

    def onClick(self, e):
        if self.is_valid():
            wh = self.get_wh()
            wh = {
                "name": self.name.Value.strip(),
                "element": self.element.Value.strip(),
                "quantity": int(self.quantity.Value.strip()),
                "usage_unit": self.usage_unit.Value.strip(),
                "usage": self.usage.Value.strip(),
                "purchase_price": int(self.purchase_price.Value.strip()),
                "sale_price": int(self.sale_price.Value.strip()),
                "sale_unit": sale_unit_to_db(
                    self.sale_unit.Value, self.usage_unit.Value
                ),
                "expire_date": self.expire_date.checked_GetDate(),
                "made_by": check_blank_to_none(self.made_by.Value),
                "drug_note": check_blank_to_none(self.drug_note.Value),
            }
            try:
                self.mv.connection.update(Warehouse(id=self.wh.id, **wh))
                for field in self.wh.fields():
                    setattr(self.wh, field, wh[field])
                self.parent.warehouselistctrl.update_ui(self.idx, self.wh)
                e.Skip()
            except Exception as error:
                wx.MessageBox(f"Cập nhật thất bại\n{error}", "Cập nhật")
