from itertools import chain

import wx
import wx.adv as adv
import wx.grid

from misc import minus_bm, plus_bm
from misc.config import (
    Format,
    drug_name_print_style_choices,
    recheck_date_print_style_choices,
)
from ui import mainview


def widget(w: wx.Window, p: wx.Window):
    return (wx.StaticText(p, label=w.Name), 0, wx.ALIGN_CENTER_VERTICAL), (
        w,
        1,
        wx.EXPAND | wx.ALL ^ wx.LEFT,
        5,
    )


class BasePage(wx.ScrolledWindow):
    def __init__(self, parent: wx.Notebook):
        super().__init__(
            parent,
            style=wx.VSCROLL | wx.ALWAYS_SHOW_SB,
            size=(-1, round(wx.DisplaySize()[1] * 0.5)),
        )
        self.SetScrollRate(0, 20)
        self.dialog: "SetupDialog" = parent.Parent
        self.mv = self.dialog.mv


class InfoPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.clinic_name = wx.TextCtrl(
            self, value=self.mv.config.clinic_name, name="Tên phòng khám"
        )
        self.clinic_address = wx.TextCtrl(
            self, value=self.mv.config.clinic_address, name="Địa chỉ"
        )
        self.clinic_phone_number = wx.TextCtrl(
            self, value=self.mv.config.clinic_phone_number, name="Số điện thoại"
        )
        self.doctor_name = wx.TextCtrl(
            self, value=self.mv.config.doctor_name, name="Tên bác sĩ"
        )
        self.checkup_price = wx.TextCtrl(
            self, value=str(self.mv.config.checkup_price), name="Công khám bệnh"
        )
        self.days = wx.SpinCtrl(
            self,
            initial=self.mv.config.default_days_for_prescription,
            name="Số ngày cho toa mặc định",
        )
        self.unit = adv.EditableListBox(
            self,
            label="Đơn vị bán",
            style=adv.EL_DEFAULT_STYLE | adv.EL_NO_REORDER,
            name="Thuốc bán một đơn vị",
        )
        lc: wx.ListCtrl = self.unit.GetListCtrl()
        lc.DeleteAllItems()
        for item in self.mv.config.single_sale_units:
            lc.Append((item,))
        lc.Append(("",))
        entry_sizer = wx.FlexGridSizer(7, 2, 5, 5)
        entry_sizer.AddGrowableCol(1)
        entry_sizer.AddMany(
            [
                *widget(self.clinic_name, self),
                *widget(self.clinic_address, self),
                *widget(self.clinic_phone_number, self),
                *widget(self.doctor_name, self),
                *widget(self.checkup_price, self),
                *widget(self.days, self),
                *widget(self.unit, self),
            ]
        )
        self.SetSizer(entry_sizer)


class FollowChoicePage(wx.Panel):
    def __init__(self, parent: wx.Notebook):
        super().__init__(parent)
        mv: "mainview.MainView" = parent.Parent.mv
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(8, 2)
        self.grid.SetColLabelValue(0, "Lời dặn dò")
        self.grid.SetColLabelValue(1, "Mở rộng khi in")
        self.grid.SetColSize(0, mv.config.header_width(0.1))
        self.grid.SetColSize(1, mv.config.header_width(0.3))
        self.grid.HideRowLabels()
        addbtn = wx.BitmapButton(self, bitmap=wx.Bitmap(plus_bm))
        deletebtn = wx.BitmapButton(self, bitmap=wx.Bitmap(minus_bm))
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany(
            [
                (0, 0, 1),
                (addbtn, 0, wx.RIGHT, 5),
                (deletebtn, 0, wx.RIGHT, 5),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (self.grid, 1, wx.EXPAND | wx.ALL, 5),
                (btn_sizer, 0, wx.EXPAND | wx.ALL, 5),
            ]
        )
        self.SetSizer(sizer)
        for idx, item in enumerate(
            chain(
                mv.config.follow_choices_dict.keys(),
                mv.config.follow_choices_list,
            )
        ):
            try:
                self.grid.SetCellValue(idx, 0, item)
            except Exception:
                self.grid.AppendRows()
                self.grid.SetCellValue(idx, 0, item)
        for idx, item in enumerate(mv.config.follow_choices_dict.values()):
            try:
                self.grid.SetCellValue(idx, 1, item)
            except Exception:
                self.grid.AppendRows()
                self.grid.SetCellValue(idx, 1, item)
        addbtn.Bind(wx.EVT_BUTTON, lambda _: self.grid.AppendRows())
        deletebtn.Bind(
            wx.EVT_BUTTON, lambda _: self.grid.DeleteRows(self.grid.Table.RowsCount - 1)
        )


class SystemPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.app_font_size = wx.SpinCtrl(
            self,
            name="App font size",
            initial=self.mv.config.app_font_size,
            min=9,
            max=12,
        )
        self.autochange_prescription_quantity_on_day_spin = wx.CheckBox(
            self, name="Tự động cập nhật số lượng thuốc khi thay đổi số ngày của toa"
        )
        self.autochange_prescription_quantity_on_day_spin.SetValue(
            self.mv.config.autochange_prescription_quantity_on_day_spin
        )
        self.ask_print = wx.CheckBox(self, name="Hỏi in toa thuốc")
        self.ask_print.SetValue(self.mv.config.ask_print)
        self.alert = wx.SpinCtrl(
            self,
            initial=self.mv.config.minimum_drug_quantity_alert,
            max=10000,
            name="Lượng thuốc tối thiểu để báo động",
        )
        self.visit_count = wx.SpinCtrl(
            self,
            initial=self.mv.config.display_recent_visit_count,
            min=-1,
            name="Số lượt khám gần nhất được hiển thị\n(-1 là tất cả)",
        )
        self.maximize_at_start = wx.CheckBox(self, name="Phóng to khi khởi động")
        self.maximize_at_start.SetValue(self.mv.config.maximize_at_start)
        self.outclinic_drug_checkbox = wx.CheckBox(
            self, name="Checkbox thuốc mua ngoài"
        )
        self.outclinic_drug_checkbox.SetValue(self.mv.config.outclinic_drug_checkbox)
        entry_sizer = wx.FlexGridSizer(7, 2, 5, 5)
        entry_sizer.AddMany(
            [
                *widget(self.app_font_size, self),
                *widget(self.autochange_prescription_quantity_on_day_spin, self),
                *widget(self.ask_print, self),
                *widget(self.alert, self),
                *widget(self.visit_count, self),
                *widget(self.maximize_at_start, self),
                *widget(self.outclinic_drug_checkbox, self),
            ]
        )
        self.SetSizer(entry_sizer)


class PrintPage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.print_vnote = wx.CheckBox(self, name="In bệnh sử")
        self.print_vnote.SetValue(self.mv.config.print_vnote)
        self.drug_name_print_style = wx.Choice(
            self,
            choices=drug_name_print_style_choices,
            name="Định dạng tên thuốc",
        )
        self.drug_name_print_style.SetSelection(self.mv.config.drug_name_print_style)
        self.recheck_date_print_style = wx.Choice(
            self,
            choices=recheck_date_print_style_choices,
            name="Định dạng tái khám",
        )
        self.recheck_date_print_style.SetSelection(
            self.mv.config.recheck_date_print_style
        )

        def checklistbox(name: str, format: Format) -> wx.CheckListBox:
            w = wx.CheckListBox(self, choices=["In đậm", "In nghiêng"], name=name)
            w.Check(0, format["bold"])
            w.Check(1, format["italic"])
            return w

        self.clinic_name = checklistbox(
            "Tên phòng khám", self.mv.config.get_format("clinic_name")
        )
        self.clinic_address = checklistbox(
            "Địa chỉ phòng khám", self.mv.config.get_format("clinic_address")
        )
        self.clinic_phone_number = checklistbox(
            "SĐT phòng khám", self.mv.config.get_format("clinic_phone_number")
        )
        self.doctor_name = checklistbox(
            "Tên bác sĩ", self.mv.config.get_format("doctor_name")
        )
        self.patient_name = checklistbox(
            "Tên bệnh nhân", self.mv.config.get_format("patient_name")
        )
        self.weight = checklistbox("Cân nặng", self.mv.config.get_format("weight"))
        self.gender = checklistbox("Giới tính", self.mv.config.get_format("gender"))
        self.birthdate = checklistbox(
            "Ngày sinh", self.mv.config.get_format("birthdate")
        )
        self.age = checklistbox("Tuổi", self.mv.config.get_format("age"))
        self.diagnosis = checklistbox(
            "Chẩn đoán", self.mv.config.get_format("diagnosis")
        )
        self.vnote = checklistbox("Bệnh sử", self.mv.config.get_format("vnote"))
        self.drug_name = checklistbox(
            "Tên thuốc", self.mv.config.get_format("drug_name")
        )
        self.drug_quantity = checklistbox(
            "Số lượng thuốc", self.mv.config.get_format("drug_quantity")
        )
        self.drug_usage_note = checklistbox(
            "Cách dùng thuốc", self.mv.config.get_format("drug_usage_note")
        )
        self.recheck_date = checklistbox(
            "Tái khám", self.mv.config.get_format("recheck_date")
        )
        entry_sizer = wx.FlexGridSizer(18, 2, 5, 5)
        entry_sizer.AddMany(
            [
                *widget(self.print_vnote, self),
                *widget(self.drug_name_print_style, self),
                *widget(self.recheck_date_print_style, self),
                *widget(self.clinic_name, self),
                *widget(self.clinic_address, self),
                *widget(self.clinic_phone_number, self),
                *widget(self.doctor_name, self),
                *widget(self.weight, self),
                *widget(self.gender, self),
                *widget(self.birthdate, self),
                *widget(self.age, self),
                *widget(self.patient_name, self),
                *widget(self.diagnosis, self),
                *widget(self.vnote, self),
                *widget(self.drug_name, self),
                *widget(self.drug_quantity, self),
                *widget(self.drug_usage_note, self),
                *widget(self.recheck_date, self),
            ]
        )
        self.SetSizer(entry_sizer)


class BackgroundColorPage(BasePage):
    def __init__(self, parent: wx.Notebook):
        super().__init__(parent)
        self.mainview_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("mainview"),
            name="Màu nền chính",
        )
        self.queue_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("queue"),
            name="Màu nền danh sách bệnh nhân\n(Đang chờ)",
        )
        self.seentoday_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("seentoday"),
            name="Màu nền danh sách bệnh nhân\n(Đã khám hôm nay)",
        )
        self.appointment_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("seentoday"),
            name="Màu nền danh sách bệnh nhân\n(Hẹn khám hôm nay)",
        )
        self.visit_list_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("visit_list"),
            name="Màu nền danh sách lượt khám cũ",
        )
        self.name_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("name"),
            name="Màu nền họ tên",
        )
        self.gender_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("gender"),
            name="Màu nền giới tính",
        )
        self.birthdate_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("birthdate"),
            name="Màu nền ngày sinh",
        )
        self.age_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("age"),
            name="Màu nền tuổi",
        )
        self.address_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("address"),
            name="Màu nền địa chỉ",
        )
        self.phone_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("phone"),
            name="Màu nền điện thoại",
        )
        self.diagnosis_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("diagnosis"),
            name="Màu nền chẩn đoán",
        )
        self.price_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("price"),
            name="Màu nền giá tiền",
        )
        self.drug_list_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("drug_list"),
            name="Màu nền danh sách thuốc",
        )
        self.past_history_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("past_history"),
            name="Màu nền tiền căn",
        )
        self.visit_note_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("visit_note"),
            name="Màu nền bệnh sử",
        )
        self.weight_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("weight"),
            name="Màu nền cân nặng",
        )
        self.days_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("days"),
            name="Màu nền số ngày toa về",
        )
        self.drug_picker_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("drug_picker"),
            name="Màu nền chọn danh mục thuốc",
        )
        self.drug_times_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("drug_times"),
            name="Màu nền số lần dùng thuốc",
        )
        self.drug_dose_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("drug_dose"),
            name="Màu nền liều thuốc",
        )
        self.drug_quantity_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("drug_quantity"),
            name="Màu nền số lượng thuốc",
        )
        self.drug_note_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("drug_note"),
            name="Màu nền cách sử dụng thuốc",
        )
        self.recheck_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("recheck"),
            name="Màu nền tái khám",
        )
        self.follow_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("follow"),
            name="Màu nền lời dặn dò",
        )
        self.procedure_picker_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("procedure_picker"),
            name="Màu nền chọn danh mục thủ thuật",
        )
        self.procedure_list_color = wx.ColourPickerCtrl(
            self,
            colour=self.mv.config.get_background_color("procedure_list"),
            name="Màu nền danh sách thủ thuật",
        )
        entry_sizer = wx.FlexGridSizer(27, 2, 5, 5)
        entry_sizer.AddMany(
            [
                *widget(self.mainview_color, self),
                *widget(self.queue_color, self),
                *widget(self.seentoday_color, self),
                *widget(self.appointment_color, self),
                *widget(self.visit_list_color, self),
                *widget(self.name_color, self),
                *widget(self.gender_color, self),
                *widget(self.birthdate_color, self),
                *widget(self.age_color, self),
                *widget(self.address_color, self),
                *widget(self.phone_color, self),
                *widget(self.diagnosis_color, self),
                *widget(self.price_color, self),
                *widget(self.drug_list_color, self),
                *widget(self.past_history_color, self),
                *widget(self.visit_note_color, self),
                *widget(self.weight_color, self),
                *widget(self.days_color, self),
                *widget(self.drug_picker_color, self),
                *widget(self.drug_times_color, self),
                *widget(self.drug_dose_color, self),
                *widget(self.drug_quantity_color, self),
                *widget(self.drug_note_color, self),
                *widget(self.recheck_color, self),
                *widget(self.follow_color, self),
                *widget(self.procedure_picker_color, self),
                *widget(self.procedure_list_color, self),
            ]
        )
        self.SetSizer(entry_sizer)


class SetupDialog(wx.Dialog):
    def __init__(self, parent: "mainview.MainView"):
        super().__init__(parent, title="Cài đặt hệ thống")
        self.mv = parent
        self.book = wx.Notebook(self)
        self.infopage = InfoPage(self.book)
        self.followchoicepage = FollowChoicePage(self.book)
        self.systempage = SystemPage(self.book)
        self.printpage = PrintPage(self.book)
        self.backgroundcolorpage = BackgroundColorPage(self.book)
        self.book.AddPage(self.infopage, text="Thông tin")
        self.book.AddPage(self.followchoicepage, text="Lời dặn")
        self.book.AddPage(self.systempage, text="Hệ thống")
        self.book.AddPage(self.printpage, text="Toa in")
        self.book.AddPage(self.backgroundcolorpage, text="Màu nền")

        cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        okbtn = wx.Button(self, id=wx.ID_OK)

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
                (self.book, 1, wx.EXPAND),
                (btn_sizer, 0, wx.EXPAND),
            ]
        )
        self.SetSizerAndFit(sizer)

        okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)

    def onOkBtn(self, e: wx.CommandEvent):
        try:
            infopage = self.infopage
            self.mv.config.clinic_name = infopage.clinic_name.Value
            self.mv.config.clinic_address = infopage.clinic_address.Value
            self.mv.config.clinic_phone_number = infopage.clinic_phone_number.Value
            self.mv.config.doctor_name = infopage.doctor_name.Value
            self.mv.config.checkup_price = int(infopage.checkup_price.Value)
            self.mv.config.default_days_for_prescription = infopage.days.Value
            lc: wx.ListCtrl = infopage.unit.GetListCtrl()
            self.mv.config.single_sale_units = [
                lc.GetItemText(idx).strip().lower()
                for idx in range(lc.ItemCount)
                if lc.GetItemText(idx).strip() != ""
            ]

            grid = self.followchoicepage.grid
            follow_choices_dict = {}
            follow_choices_list = []
            for idx in range(0, grid.Table.RowsCount):
                k = grid.GetCellValue(idx, 0).strip()
                v = grid.GetCellValue(idx, 1).strip()
                if k != "":
                    if v == "":
                        follow_choices_list.append(k)
                    else:
                        follow_choices_dict[k] = v
            self.mv.config.follow_choices_dict = follow_choices_dict
            self.mv.config.follow_choices_list = follow_choices_list
            self.mv.follow.Clear()
            for item in chain(follow_choices_dict.keys(), follow_choices_list):
                self.mv.follow.Append(item)

            systempage = self.systempage
            self.mv.config.app_font_size = systempage.app_font_size.Value
            self.mv.config.autochange_prescription_quantity_on_day_spin = (
                systempage.autochange_prescription_quantity_on_day_spin.Value
            )
            self.mv.config.ask_print = systempage.ask_print.Value
            self.mv.config.minimum_drug_quantity_alert = systempage.alert.Value
            self.mv.config.display_recent_visit_count = systempage.visit_count.Value
            self.mv.config.maximize_at_start = systempage.maximize_at_start.Value
            self.mv.config.outclinic_drug_checkbox = (
                systempage.outclinic_drug_checkbox.Value
            )

            printpage = self.printpage
            self.mv.config.print_vnote = printpage.print_vnote.Value
            self.mv.config.drug_name_print_style = (
                printpage.drug_name_print_style.Selection
            )
            self.mv.config.recheck_date_print_style = (
                printpage.recheck_date_print_style.Selection
            )

            def set_format(name: str, widget: wx.CheckListBox):
                self.mv.config.prescription_formats[name] = {
                    "bold": widget.IsChecked(0),
                    "italic": widget.IsChecked(1),
                }

            set_format("clinic_name", printpage.clinic_name)
            set_format("clinic_address", printpage.clinic_address)
            set_format("clinic_phone_number", printpage.clinic_phone_number)
            set_format("doctor_name", printpage.doctor_name)
            set_format("patient_name", printpage.patient_name)
            set_format("weight", printpage.weight)
            set_format("gender", printpage.gender)
            set_format("birthdate", printpage.birthdate)
            set_format("age", printpage.age)
            set_format("diagnosis", printpage.diagnosis)
            set_format("vnote", printpage.vnote)
            set_format("drug_name", printpage.drug_name)
            set_format("drug_quantity", printpage.drug_quantity)
            set_format("drug_usage_note", printpage.drug_usage_note)
            set_format("recheck_date", printpage.recheck_date)

            def set_color(name: str, widget: wx.ColourPickerCtrl):
                self.mv.config.background_colors[name] = widget.Colour.GetIM()[:3]

            bgcolorpage = self.backgroundcolorpage
            set_color("mainview", bgcolorpage.mainview_color)
            set_color("queue", bgcolorpage.queue_color)
            set_color("seentoday", bgcolorpage.seentoday_color)
            set_color("appointment", bgcolorpage.appointment_color)
            set_color("visit_list", bgcolorpage.visit_list_color)
            set_color("name", bgcolorpage.name_color)
            set_color("gender", bgcolorpage.gender_color)
            set_color("birthdate", bgcolorpage.birthdate_color)
            set_color("age", bgcolorpage.age_color)
            set_color("address", bgcolorpage.address_color)
            set_color("phone", bgcolorpage.phone_color)
            set_color("diagnosis", bgcolorpage.diagnosis_color)
            set_color("price", bgcolorpage.price_color)
            set_color("drug_list", bgcolorpage.drug_list_color)
            set_color("past_history", bgcolorpage.past_history_color)
            set_color("visit_note", bgcolorpage.visit_note_color)
            set_color("weight", bgcolorpage.weight_color)
            set_color("days", bgcolorpage.days_color)
            set_color("drug_picker", bgcolorpage.drug_picker_color)
            set_color("drug_times", bgcolorpage.drug_times_color)
            set_color("drug_dose", bgcolorpage.drug_dose_color)
            set_color("drug_quantity", bgcolorpage.drug_quantity_color)
            set_color("drug_note", bgcolorpage.drug_note_color)
            set_color("recheck", bgcolorpage.recheck_color)
            set_color("follow", bgcolorpage.follow_color)
            set_color("procedure_picker", bgcolorpage.procedure_picker_color)
            set_color("procedure_list", bgcolorpage.procedure_list_color)

            self.mv.config.dump()
            wx.MessageBox("Đã lưu cài đặt", "Cài đặt")
            self.mv.refresh_color()
            self.mv.Refresh()  # refresh_color require
            self.mv.order_book.prescriptionpage.drug_list.EnableCheckBoxes(
                self.mv.config.outclinic_drug_checkbox
            )
            self.mv.order_book.prescriptionpage.outclinic_reminder.Show(
                self.mv.config.outclinic_drug_checkbox
            )
            self.mv.order_book.prescriptionpage.Layout()
            self.mv.state.refresh_all()
            self.mv.price.FetchPrice()
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"Lỗi không lưu được\n{error}", "Lỗi")
