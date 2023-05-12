from ui import mainview
import wx
import wx.adv as adv


class SetupDialog(wx.Dialog):
    def __init__(self, parent: "mainview.MainView"):
        super().__init__(parent, title="Cài đặt hệ thống")
        self.mv = parent
        self.scroll = wx.ScrolledWindow(
            self,
            style=wx.VSCROLL | wx.ALWAYS_SHOW_SB,
            size=(-1, round(wx.DisplaySize()[1] * 0.5)),
        )
        self.scroll.SetScrollRate(0, 20)
        self.clinic_name = wx.TextCtrl(
            self.scroll, value=self.mv.config.clinic_name, name="Tên phòng khám"
        )
        self.doctor_name = wx.TextCtrl(
            self.scroll, value=self.mv.config.doctor_name, name="Tên bác sĩ"
        )
        self.clinic_address = wx.TextCtrl(
            self.scroll, value=self.mv.config.clinic_address, name="Địa chỉ"
        )
        self.clinic_phone_number = wx.TextCtrl(
            self.scroll, value=self.mv.config.clinic_phone_number, name="Số điện thoại"
        )
        self.checkup_price = wx.TextCtrl(
            self.scroll, value=str(self.mv.config.checkup_price), name="Công khám bệnh"
        )
        self.ask_print = wx.CheckBox(self.scroll, name="Hỏi in toa thuốc")
        self.ask_print.SetValue(self.mv.config.ask_print)
        self.print_price = wx.CheckBox(self.scroll, name="In giá tiền")
        self.print_price.SetValue(self.mv.config.print_price)
        self.days = wx.SpinCtrl(
            self.scroll,
            initial=self.mv.config.default_days_for_prescription,
            name="Số ngày toa về mặc định",
        )
        self.alert = wx.SpinCtrl(
            self.scroll,
            initial=self.mv.config.minimum_drug_quantity_alert,
            max=10000,
            name="Lượng thuốc tối thiểu để báo động",
        )
        self.unit = adv.EditableListBox(
            self.scroll,
            label="Đơn vị bán",
            style=adv.EL_DEFAULT_STYLE | adv.EL_NO_REORDER,
            name="Thuốc bán một đơn vị",
        )
        lc: wx.ListCtrl = self.unit.GetListCtrl()
        lc.DeleteAllItems()
        for item in self.mv.config.single_sale_units:
            lc.Append((item,))
        lc.Append(("",))
        self.num_of_ld = wx.SpinCtrl(
            self.scroll,
            initial=self.mv.config.number_of_drugs_in_one_page,
            name="Số lượng thuốc trong một toa\n)Tối đa: 8)",
            min=4,
            max=8,
        )
        self.visit_count = wx.SpinCtrl(
            self.scroll,
            initial=self.mv.config.display_recent_visit_count,
            min=-1,
            name="Số lượt khám gần nhất được hiển thị\n(-1 là tất cả)",
        )
        self.maximize_at_start = wx.CheckBox(self.scroll, name="Phóng to khi khởi động")
        self.maximize_at_start.SetValue(self.mv.config.maximize_at_start)
        self.mainview_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("mainview"),
            name="Màu nền chính",
        )
        self.patient_queuelist_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("patient_queuelist"),
            name="Màu nền danh sách bệnh nhân\n(Đang chờ)",
        )
        self.patient_seenlist_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("patient_seenlist"),
            name="Màu nền danh sách bệnh nhân\n(Đã khám hôm nay)",
        )
        self.visit_list_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("visit_list"),
            name="Màu nền danh sách lượt khám cũ",
        )
        self.name_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("name"),
            name="Màu nền họ tên",
        )
        self.gender_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("gender"),
            name="Màu nền giới tính",
        )
        self.birthdate_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("birthdate"),
            name="Màu nền ngày sinh",
        )
        self.age_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("age"),
            name="Màu nền tuổi",
        )
        self.address_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("address"),
            name="Màu nền địa chỉ",
        )
        self.phone_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("phone"),
            name="Màu nền điện thoại",
        )
        self.diagnosis_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("diagnosis"),
            name="Màu nền chẩn đoán",
        )
        self.price_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("price"),
            name="Màu nền giá tiền",
        )
        self.drug_list_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("drug_list"),
            name="Màu nền danh sách thuốc",
        )
        self.procedure_list_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("procedure_list"),
            name="Màu nền danh sách thủ thuật",
        )
        self.past_history_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("past_history"),
            name="Màu nền tiền căn",
        )
        self.visit_note_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("visit_note"),
            name="Màu nền bệnh sử",
        )
        self.weight_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("weight"),
            name="Màu nền cân nặng",
        )
        self.days_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("days"),
            name="Màu nền số ngày toa về",
        )
        self.drug_picker_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("drug_picker"),
            name="Màu nền chọn danh mục thuốc",
        )
        self.drug_times_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("drug_times"),
            name="Màu nền số lần dùng thuốc",
        )
        self.drug_dose_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("drug_dose"),
            name="Màu nền liều thuốc",
        )
        self.drug_quantity_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("drug_quantity"),
            name="Màu nền số lượng thuốc",
        )
        self.drug_note_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("drug_note"),
            name="Màu nền cách sử dụng thuốc",
        )
        self.recheck_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("recheck"),
            name="Màu nền tái khám",
        )
        self.follow_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("follow"),
            name="Màu nền lời dặn dò",
        )
        self.procedure_picker_color = wx.ColourPickerCtrl(
            self.scroll,
            colour=self.mv.config.get_background_color("procedure_picker"),
            name="Màu nền chọn danh mục thủ thuật",
        )

        cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        okbtn = wx.Button(self, id=wx.ID_OK)

        def widget(w: wx.Window):
            s: str = w.GetName()
            return (
                wx.StaticText(self.scroll, label=s),
                0,
                wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                5,
            ), (w, 1, wx.EXPAND | wx.ALL, 5)

        entry_sizer = wx.FlexGridSizer(40, 2, 5, 5)
        entry_sizer.AddMany(
            [
                *widget(self.clinic_name),
                *widget(self.doctor_name),
                *widget(self.clinic_address),
                *widget(self.clinic_phone_number),
                *widget(self.checkup_price),
                *widget(self.ask_print),
                *widget(self.print_price),
                *widget(self.days),
                *widget(self.alert),
                *widget(self.unit),
                *widget(self.num_of_ld),
                *widget(self.visit_count),
                *widget(self.maximize_at_start),
                *widget(self.mainview_color),
                *widget(self.patient_queuelist_color),
                *widget(self.patient_seenlist_color),
                *widget(self.visit_list_color),
                *widget(self.name_color),
                *widget(self.gender_color),
                *widget(self.birthdate_color),
                *widget(self.age_color),
                *widget(self.address_color),
                *widget(self.phone_color),
                *widget(self.diagnosis_color),
                *widget(self.price_color),
                *widget(self.drug_list_color),
                *widget(self.procedure_list_color),
                *widget(self.past_history_color),
                *widget(self.visit_note_color),
                *widget(self.weight_color),
                *widget(self.days_color),
                *widget(self.drug_picker_color),
                *widget(self.drug_times_color),
                *widget(self.drug_dose_color),
                *widget(self.drug_quantity_color),
                *widget(self.drug_note_color),
                *widget(self.recheck_color),
                *widget(self.follow_color),
                *widget(self.procedure_picker_color),
            ]
        )
        self.scroll.SetSizer(entry_sizer)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany(
            [
                (
                    wx.StaticText(self, label="**Còn nhiều tùy chọn trong file JSON"),
                    0,
                    wx.ALIGN_CENTER,
                ),
                (0, 0, 1),
                (cancelbtn, 0, wx.ALL, 5),
                (okbtn, 0, wx.ALL, 5),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (self.scroll, 0, wx.EXPAND),
                (btn_sizer, 0, wx.EXPAND),
            ]
        )
        self.SetSizerAndFit(sizer)

        okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)

    def onOkBtn(self, e: wx.CommandEvent):
        try:
            lc: wx.ListCtrl = self.unit.GetListCtrl()

            self.mv.config.clinic_name = self.clinic_name.Value
            self.mv.config.doctor_name = self.doctor_name.Value
            self.mv.config.clinic_address = self.clinic_address.Value
            self.mv.config.clinic_phone_number = self.clinic_phone_number.Value
            self.mv.config.ask_print = self.ask_print.Value
            self.mv.config.print_price = self.print_price.Value
            self.mv.config.checkup_price = int(self.checkup_price.Value)
            self.mv.config.default_days_for_prescription = self.days.GetValue()
            self.mv.config.minimum_drug_quantity_alert = self.alert.GetValue()
            self.mv.config.single_sale_units = [
                lc.GetItemText(idx).strip()
                for idx in range(lc.ItemCount)
                if lc.GetItemText(idx).strip() != ""
            ]
            self.mv.config.number_of_drugs_in_one_page = self.num_of_ld.GetValue()
            self.mv.config.display_recent_visit_count = self.visit_count.GetValue()
            self.mv.config.maximize_at_start = self.maximize_at_start.Value

            def set_color(name: str, widget: wx.ColourPickerCtrl):
                self.mv.config.background_color[name] = widget.Colour.GetIM()[:3]

            set_color("mainview", self.mainview_color)
            set_color("patient_queuelist", self.patient_queuelist_color)
            set_color("patient_seenlist", self.patient_seenlist_color)
            set_color("visit_list", self.visit_list_color)
            set_color("name", self.name_color)
            set_color("gender", self.gender_color)
            set_color("birthdate", self.birthdate_color)
            set_color("age", self.age_color)
            set_color("address", self.address_color)
            set_color("phone", self.phone_color)
            set_color("diagnosis", self.diagnosis_color)
            set_color("price", self.price_color)
            set_color("drug_list", self.drug_list_color)
            set_color("procedure_list", self.procedure_list_color)
            set_color("past_history", self.past_history_color)
            set_color("visit_note", self.visit_note_color)
            set_color("weight", self.weight_color)
            set_color("days", self.days_color)
            set_color("drug_picker", self.drug_picker_color)
            set_color("drug_times", self.drug_times_color)
            set_color("drug_dose", self.drug_dose_color)
            set_color("drug_quantity", self.drug_quantity_color)
            set_color("drug_note", self.drug_note_color)
            set_color("recheck", self.recheck_color)
            set_color("follow", self.follow_color)
            set_color("procedure_picker", self.procedure_picker_color)

            self.mv.config.dump()
            wx.MessageBox("Đã lưu cài đặt\nKhởi động lại để thay đổi màu", "Cài đặt")
            self.mv.price.FetchPrice()
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"Lỗi không lưu được\n{error}", "Lỗi")
