from paths import CONFIG_PATH
from core.init import config
from core import mainview
import wx
import wx.adv as adv
import json


class SetupDialog(wx.Dialog):
    def __init__(self, parent: 'mainview.MainView'):
        super().__init__(parent, title="Cài đặt hệ thống")
        self.mv = parent
        self.clinic = wx.TextCtrl(
            self, value=config['clinic_name'], name="Tên phòng khám")
        self.address = wx.TextCtrl(
            self, value=config['clinic_address'], name="Địa chỉ")
        self.phone = wx.TextCtrl(
            self, value=config['clinic_phone_number'], name="Số điện thoại")
        self.doctor = wx.TextCtrl(
            self, value=config['doctor_name'], name="Ký tên bác sĩ")
        self.price = wx.TextCtrl(
            self, value=str(config["initial_price"]), name="Công khám bệnh")
        self.display_price = wx.CheckBox(self, name="In giá tiền")
        self.display_price.SetValue(config['print_price'])
        self.days = wx.SpinCtrl(
            self, initial=config["default_days_for_prescription"], name="Số ngày toa về mặc định")
        self.alert = wx.SpinCtrl(
            self, initial=config["minumum_drug_quantity_alert"], max=10000, name="Lượng thuốc tối thiểu để báo động")
        self.unit = adv.EditableListBox(
            self, label="Đơn vị bán", style=adv.EL_DEFAULT_STYLE | adv.EL_NO_REORDER, name="Thuốc bán một đơn vị")
        lc: wx.ListCtrl = self.unit.GetListCtrl()
        lc.DeleteAllItems()
        for item in config["single_sale_units"]:
            lc.Append((item,))
        lc.Append(("",))

        cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        okbtn = wx.Button(self, id=wx.ID_OK)

        def widget(w: wx.Window):
            s: str = w.GetName()
            return (wx.StaticText(self, label=s), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5), (w, 1, wx.EXPAND | wx.ALL, 5)

        entry_sizer = wx.FlexGridSizer(11, 2, 5, 5)
        entry_sizer.AddMany([
            *widget(self.clinic),
            *widget(self.address),
            *widget(self.phone),
            *widget(self.doctor),
            *widget(self.price),
            *widget(self.display_price),
            *widget(self.days),
            *widget(self.alert),
            *widget(self.unit),
        ])
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany([
            (wx.StaticText(self, label="**Còn nhiều tùy chọn trong file JSON"),
             0, wx.ALIGN_CENTER),
            (0, 0, 1),
            (cancelbtn, 0, wx.ALL, 5),
            (okbtn, 0, wx.ALL, 5),
        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (entry_sizer, 0, wx.EXPAND),
            (btn_sizer, 0, wx.EXPAND),
        ])
        self.SetSizerAndFit(sizer)

        okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)

    def onOkBtn(self, e: wx.CommandEvent):
        try:
            lc: wx.ListCtrl = self.unit.GetListCtrl()

            config['clinic_name'] = self.clinic.Value
            config['doctor_name'] = self.doctor.Value
            config['clinic_address'] = self.address.Value
            config['clinic_phone_number'] = self.phone.Value
            config['print_price'] = self.display_price.Value
            config['initial_price'] = int(self.price.Value)
            config['default_days_for_prescription'] = self.days.GetValue()
            config["minumum_drug_quantity_alert"] = self.alert.GetValue(
            )
            config["single_sale_units"] = [
                lc.GetItemText(idx).strip()
                for idx in range(lc.ItemCount)
                if lc.GetItemText(idx).strip() != ''
            ]
            with open(CONFIG_PATH, mode='w', encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            wx.MessageBox("Đã lưu cài đặt", "Cài đặt")
            self.mv.price.FetchPrice()
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"Lỗi không lưu được\n{error}", "Lỗi")
