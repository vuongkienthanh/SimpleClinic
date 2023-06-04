from db import Warehouse
from misc import check_none_to_blank, check_blank_to_none
from ui import mainview
from ui.generic_widgets import CalendarDatePicker, NumberTextCtrl
import wx


class WarehouseDialog(wx.Dialog):
    def __init__(self, mv: "mainview.MainView"):
        "`_list`: internal list"
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
        self.warehouselistctrl.rebuild()

    def onClose(self, e):
        self.mv.state.new_linedrug_list = []
        self.mv.order_book.prescriptionpage.drug_list.rebuild(
            self.mv.state.old_linedrug_list
        )
        self.mv.price.FetchPrice()
        e.Skip()


class WarehouseListCtrl(wx.ListCtrl):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.parent = parent
        self.mv = parent.mv
        self._list: list[Warehouse] = []
        self.AppendColumn("Mã", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Tên", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Thành phần", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Số lượng", width=self.mv.config.header_width(0.04))
        self.AppendColumn("Đơn vị sử dụng", width=self.mv.config.header_width(0.06))
        self.AppendColumn("Cách sử dụng", width=self.mv.config.header_width(0.06))
        self.AppendColumn("Giá mua", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Giá bán", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Đơn vị bán", width=self.mv.config.header_width(0.04))
        self.AppendColumn("Ngày hết hạn", width=self.mv.config.header_width(0.05))
        self.AppendColumn("Xuất xứ", width=self.mv.config.header_width(0.06))
        self.AppendColumn("Ghi chú", width=self.mv.config.header_width(0.06))
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick)

    def fetch_list(self, s: str):
        match s.strip().casefold():
            case "":
                self._list = list(self.mv.state.all_warehouse.values())
            case s:
                self._list = list(
                    filter(
                        lambda wh: (s in wh.name.casefold())
                        or (s in wh.element.casefold()),
                        self.mv.state.all_warehouse.values(),
                    )
                )

    def build(self):
        for wh in self._list:
            self.append_ui(wh)

    def rebuild(self, s: str = ""):
        self.fetch_list(s)
        self.DeleteAllItems()
        self.build()

    def append_ui(self, wh: Warehouse):
        self.Append(
            [
                str(wh.id),
                wh.name,
                wh.element,
                str(wh.quantity),
                wh.usage_unit,
                wh.usage,
                str(wh.purchase_price),
                str(wh.sale_price),
                wh.sale_unit if wh.sale_unit is not None else wh.usage_unit,
                wh.expire_date.strftime("%d/%m/%Y")
                if wh.expire_date is not None
                else "",
                check_none_to_blank(wh.made_by),
                check_none_to_blank(wh.drug_note),
            ]
        )
        self.check_min_quantity_and_change_color(wh, self.ItemCount - 1)

    def pop_ui(self, idx: int):
        self.DeleteItem(idx)
        del self._list[idx]

    def update_ui(self, idx: int, wh: Warehouse):
        self.SetItem(idx, 1, wh.name)
        self.SetItem(idx, 2, wh.element)
        self.SetItem(idx, 3, str(wh.quantity))
        self.SetItem(idx, 4, wh.usage_unit)
        self.SetItem(idx, 5, wh.usage)
        self.SetItem(idx, 6, str(wh.purchase_price))
        self.SetItem(idx, 7, str(wh.sale_price))
        self.SetItem(
            idx, 8, wh.sale_unit if wh.sale_unit is not None else wh.usage_unit
        )
        self.SetItem(
            idx,
            9,
            wh.expire_date.strftime("%d/%m/%Y") if wh.expire_date is not None else "",
        )
        self.SetItem(idx, 10, check_none_to_blank(wh.made_by))
        self.SetItem(idx, 11, check_none_to_blank(wh.drug_note))
        self.check_min_quantity_and_change_color(wh, idx)

    def check_min_quantity_and_change_color(self, wh: Warehouse, idx: int):
        if wh.quantity <= self.mv.config.minimum_drug_quantity_alert:
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
        self.Bind(wx.EVT_SEARCH, self.onSearchEnter)
        self.Bind(wx.EVT_TEXT, self.onText)

    def onSearchEnter(self, e):
        self.parent.warehouselistctrl.rebuild(self.Value)
        e.Skip()

    def onText(self, e: wx.CommandEvent):
        if len(e.EventObject.Value) == 0:
            self.parent.warehouselistctrl.rebuild()
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

        self.mandatory: tuple = (
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

    def get_sale_unit(self) -> str | None:
        sale_unit: str = self.sale_unit.Value
        sale_unit = sale_unit.strip()
        usage_unit: str = self.usage_unit.Value
        usage_unit = usage_unit.strip()

        match sale_unit:
            case "":
                return None
            case s if s == usage_unit:
                return None
            case _:
                return sale_unit


class AddDialog(BaseDialog):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent, title="Thêm thuốc mới")

    def onClick(self, e):
        if self.is_valid():
            wh = {
                "name": self.name.Value.strip(),
                "element": self.element.Value.strip(),
                "quantity": int(self.quantity.Value.strip()),
                "usage_unit": self.usage_unit.Value.strip(),
                "usage": self.usage.Value.strip(),
                "purchase_price": int(self.purchase_price.Value.strip()),
                "sale_price": int(self.sale_price.Value.strip()),
                "sale_unit": self.get_sale_unit(),
                "expire_date": self.expire_date.checked_GetDate(),
                "made_by": check_blank_to_none(self.made_by.Value),
                "drug_note": check_blank_to_none(self.drug_note.Value),
            }
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
            wh = {
                "name": self.name.Value.strip(),
                "element": self.element.Value.strip(),
                "quantity": int(self.quantity.Value.strip()),
                "usage_unit": self.usage_unit.Value.strip(),
                "usage": self.usage.Value.strip(),
                "purchase_price": int(self.purchase_price.Value.strip()),
                "sale_price": int(self.sale_price.Value.strip()),
                "sale_unit": self.get_sale_unit(),
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
