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
        self._list: list[Warehouse] = []

        self.search = wx.SearchCtrl(self)
        self.search.SetHint("Tên thuốc hoặc thành phần thuốc")

        self.lc = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.lc.AppendColumn("Mã", width=self.mv.config.header_width(0.03))
        self.lc.AppendColumn("Tên", width=self.mv.config.header_width(0.1))
        self.lc.AppendColumn("Thành phần", width=self.mv.config.header_width(0.1))
        self.lc.AppendColumn("Số lượng", width=self.mv.config.header_width(0.04))
        self.lc.AppendColumn("Đơn vị sử dụng", width=self.mv.config.header_width(0.06))
        self.lc.AppendColumn("Cách sử dụng", width=self.mv.config.header_width(0.06))
        self.lc.AppendColumn("Giá mua", width=self.mv.config.header_width(0.03))
        self.lc.AppendColumn("Giá bán", width=self.mv.config.header_width(0.03))
        self.lc.AppendColumn("Đơn vị bán", width=self.mv.config.header_width(0.04))
        self.lc.AppendColumn("Ngày hết hạn", width=self.mv.config.header_width(0.05))
        self.lc.AppendColumn("Xuất xứ", width=self.mv.config.header_width(0.06))
        self.lc.AppendColumn("Ghi chú", width=self.mv.config.header_width(0.06))

        self.newbtn = wx.Button(self, label="Thêm mới")
        self.editbtn = wx.Button(self, label="Cập nhật")
        self.delbtn = wx.Button(self, label="Xóa")
        cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.editbtn.Disable()
        self.delbtn.Disable()

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
                (0, 0, 1),
                (self.newbtn, 0, wx.RIGHT, 5),
                (self.editbtn, 0, wx.RIGHT, 5),
                (self.delbtn, 0, wx.RIGHT, 5),
                (cancelbtn, 0, wx.RIGHT, 5),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (search_sizer, 0, wx.EXPAND),
                (self.lc, 1, wx.EXPAND | wx.ALL, 5),
                (btn_sizer, 0, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizerAndFit(sizer)

        self.search.Bind(wx.EVT_SEARCH, self.onSearchEnter)
        self.lc.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.lc.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)
        self.lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEdit)
        self.newbtn.Bind(wx.EVT_BUTTON, self.onNew)
        self.editbtn.Bind(wx.EVT_BUTTON, self.onEdit)
        self.delbtn.Bind(wx.EVT_BUTTON, self.onDelete)
        self.Maximize()
        self.filtered_build()

    def append(self, wh: Warehouse):
        "append to internal list and ui, also conditional recolor"
        self._list.append(wh)
        self.lc.Append(
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
                check_none_to_blank(wh.note),
            ]
        )
        self.check_min_quantity_and_change_color(wh, len(self._list) - 1)

    def delete(self, idx: int):
        "delete from internal list and ui"
        self.lc.DeleteItem(idx)
        self._list.pop(idx)

    def clear(self):
        "clear display and internal list"
        self._list.clear()
        self.lc.DeleteAllItems()

    def filtered_build(self, s: str = ""):
        self.clear()
        if s == "":
            for wh in self.mv.state.all_warehouse.values():
                self.append(wh)
        else:
            for wh in filter(
                lambda wh: self.check_search_str_in_wh(wh, s),
                self.mv.state.all_warehouse.values(),
            ):
                self.append(wh)

    def check_search_str_in_wh(self, wh: Warehouse, s: str) -> bool:
        s = s.strip().casefold()
        return (s in wh.name.casefold()) or (s in wh.element.casefold())

    def check_min_quantity_and_change_color(self, wh: Warehouse, idx: int):
        if wh.quantity <= self.mv.config.minimum_drug_quantity_alert:
            self.lc.SetItemTextColour(idx, wx.Colour(252, 3, 57))

    def onSearchEnter(self, e: wx.CommandEvent):
        self.filtered_build(self.search.Value)
        e.Skip()

    def onSelect(self, _):
        self.editbtn.Enable()
        self.delbtn.Enable()

    def onDeselect(self, _):
        self.editbtn.Disable()
        self.delbtn.Disable()

    def onNew(self, _):
        NewDialog(self).ShowModal()

    def onEdit(self, _):
        idx = self.lc.GetFirstSelected()
        wh = self._list[idx]
        EditDialog(self, wh).ShowModal()

    def onDelete(self, _):
        """Delete Warehouse in sql, refresh state, delete in self.lc, delete in prescriptionpage.druglist
        Note: there are restrict constrain on Warehouse"""
        idx: int = self.lc.GetFirstSelected()
        wh = self._list[idx]
        try:
            rowcount = self.mv.connection.delete(Warehouse, wh.id)
            assert rowcount == 1
            del self.mv.state.all_warehouse[wh.id]
            self.delete(idx)
            for state_list in (
                self.mv.state.old_linedrug_list,
                self.mv.state.new_linedrug_list,
                self.mv.state.to_delete_old_linedrug_list,
            ):
                for idx, item in enumerate(state_list):
                    if item.warehouse_id == wh.id:
                        state_list.pop(idx)
                        break

            drug_list = self.mv.order_book.prescriptionpage.drug_list
            drug_list.rebuild(
                self.mv.state.old_linedrug_list + self.mv.state.new_linedrug_list
            )
            self.mv.price.FetchPrice()
            wx.MessageBox(f"Xoá thuốc thành công\n{rowcount}", "Xóa")
        except Exception as error:
            wx.MessageBox(f"Lỗi không xóa được\n{error}", "Lỗi")


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
        self.note = wx.TextCtrl(self, style=wx.TE_MULTILINE, name="Ghi chú")
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
                *widget(self.note),
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

        self.okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)

    def onOkBtn(self, e: wx.CommandEvent):
        ...

    def is_valid(self) -> bool:
        "valid when all fields in mandatory are filled"
        for widget in self.mandatory:
            val: str = widget.GetValue()
            name: str = widget.GetName()
            if val.strip() == "":
                wx.MessageBox(f"Chưa nhập đủ thông tin\n{name}", self.title)
                return False
        else:
            return True

    def get_sale_unit(self) -> str | None:
        "return sale_unit or usage_unit if none"
        sale_unit: str = self.sale_unit.GetValue()
        sale_unit = sale_unit.strip()
        usage_unit: str = self.usage_unit.GetValue()
        usage_unit = usage_unit.strip()

        if (sale_unit == "") or (sale_unit == usage_unit):
            return None
        else:
            return sale_unit


class NewDialog(BaseDialog):
    def __init__(self, parent: WarehouseDialog):
        super().__init__(parent, title="Thêm mới")

    def onOkBtn(self, e):
        "sql insert, append to state.warehouselist, rebuild with search str"
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
                "note": check_blank_to_none(self.note.Value),
            }
            try:
                lastrowid = self.mv.connection.insert(Warehouse, wh)
                assert lastrowid is not None
                wx.MessageBox("Thêm mới thành công", "Thêm mới")
                new_wh = Warehouse(id=lastrowid, **wh)
                self.mv.state.all_warehouse.append(new_wh)
                if self.parent.check_search_str_in_wh(new_wh, self.parent.search.Value):
                    self.parent.append(new_wh)
                e.Skip()
            except Exception as error:
                wx.MessageBox(f"Thêm mới thất bại\n{error}", "Thêm mới")


class EditDialog(BaseDialog):
    def __init__(self, parent: WarehouseDialog, wh: Warehouse):
        super().__init__(parent, title="Cập nhật")
        self.wh = wh
        self.build(wh)

    def build(self, wh: Warehouse):
        self.name.ChangeValue(wh.name)
        self.element.ChangeValue(wh.element)
        self.quantity.ChangeValue(str(wh.quantity))
        self.usage_unit.ChangeValue(wh.usage_unit)
        self.usage.ChangeValue(wh.usage)
        self.purchase_price.ChangeValue(str(wh.purchase_price))
        self.sale_price.ChangeValue(str(wh.sale_price))
        if wh.sale_unit is None:
            self.sale_unit.ChangeValue(wh.usage_unit)
        else:
            self.sale_unit.ChangeValue(wh.sale_unit)
        if wh.expire_date is not None:
            self.expire_date.SetDate(wh.expire_date)
        self.made_by.ChangeValue(check_none_to_blank(wh.made_by))
        self.note.ChangeValue(check_none_to_blank(wh.note))

    def onOkBtn(self, e):
        if self.is_valid():
            self.wh.name = self.name.Value.strip()
            self.wh.element = self.element.Value.strip()
            self.wh.quantity = int(self.quantity.Value)
            self.wh.usage_unit = self.usage_unit.Value.strip()
            self.wh.usage = self.usage.Value.strip()
            self.wh.purchase_price = int(self.purchase_price.Value)
            self.wh.sale_price = int(self.sale_price.Value)
            self.wh.sale_unit = self.get_sale_unit()
            self.wh.expire_date = self.expire_date.checked_GetDate()
            self.wh.made_by = check_blank_to_none(self.made_by.Value)
            self.wh.note = check_blank_to_none(self.note.Value)
            try:
                self.mv.connection.update(self.wh)
                wx.MessageBox("Cập nhật thành công", "Cập nhật")
                self.parent.filtered_build(self.parent.search.Value)
                drug_list = self.mv.order_book.prescriptionpage.drug_list
                if drug_list.ItemCount > 0:
                    for i, d in enumerate(drug_list.d_list):
                        if d.drug_id == self.wh.id:
                            _item = d.expand()
                            _item.name = self.wh.name
                            _item.usage = self.wh.usage
                            _item.usage_unit = self.wh.usage_unit
                            _item.sale_price = self.wh.sale_price
                            _item.sale_unit = self.wh.sale_unit
                            drug_list.update(i, _item)
                    self.mv.price.FetchPrice()
                e.Skip()
            except Exception as error:
                wx.MessageBox(f"Cập nhật thất bại\n{error}", "Cập nhật")
