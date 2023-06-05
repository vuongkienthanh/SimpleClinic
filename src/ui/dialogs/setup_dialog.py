from ui import mainview
from misc import plus_bm, minus_bm
from itertools import chain
import wx
import wx.adv as adv
import wx.grid


def widget(w: wx.Window, p: wx.Window):
    s: str = w.GetName()
    return (wx.StaticText(p, label=s), 0, wx.ALIGN_CENTER_VERTICAL), (
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
    def __init__(self, parent: wx.Notebook):
        super().__init__(parent)
        self.clinic_name = wx.TextCtrl(
            self, value=self.mv.config.clinic_name, name="Tên phòng khám"
        )
        self.doctor_name = wx.TextCtrl(
            self, value=self.mv.config.doctor_name, name="Tên bác sĩ"
        )
        self.clinic_address = wx.TextCtrl(
            self, value=self.mv.config.clinic_address, name="Địa chỉ"
        )
        self.clinic_phone_number = wx.TextCtrl(
            self, value=self.mv.config.clinic_phone_number, name="Số điện thoại"
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
                *widget(self.doctor_name, self),
                *widget(self.clinic_address, self),
                *widget(self.clinic_phone_number, self),
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
            except:
                self.grid.AppendRows()
                self.grid.SetCellValue(idx, 0, item)
        for idx, item in enumerate(mv.config.follow_choices_dict.values()):
            try:
                self.grid.SetCellValue(idx, 1, item)
            except:
                self.grid.AppendRows()
                self.grid.SetCellValue(idx, 1, item)
        addbtn.Bind(wx.EVT_BUTTON, lambda _: self.grid.AppendRows())
        deletebtn.Bind(
            wx.EVT_BUTTON, lambda _: self.grid.DeleteRows(self.grid.Table.RowsCount - 1)
        )


class SystemPage(BasePage):
    def __init__(self, parent: wx.Notebook):
        super().__init__(parent)
        self.ask_print = wx.CheckBox(self, name="Hỏi in toa thuốc")
        self.ask_print.SetValue(self.mv.config.ask_print)
        self.print_price = wx.CheckBox(self, name="In giá tiền trên toa")
        self.print_price.SetValue(self.mv.config.print_price)
        self.alert = wx.SpinCtrl(
            self,
            initial=self.mv.config.minimum_drug_quantity_alert,
            max=10000,
            name="Lượng thuốc tối thiểu để báo động",
        )
        self.num_of_ld = wx.SpinCtrl(
            self,
            initial=self.mv.config.max_number_of_drugs_in_one_page,
            name="Số lượng thuốc được in trong một toa\n(Tối đa: 8)",
            min=4,
            max=8,
        )
        self.visit_count = wx.SpinCtrl(
            self,
            initial=self.mv.config.display_recent_visit_count,
            min=-1,
            name="Số lượt khám gần nhất được hiển thị\n(-1 là tất cả)",
        )
        self.maximize_at_start = wx.CheckBox(self, name="Phóng to khi khởi động")
        self.maximize_at_start.SetValue(self.mv.config.maximize_at_start)
        entry_sizer = wx.FlexGridSizer(6, 2, 5, 5)
        entry_sizer.AddMany(
            [
                *widget(self.ask_print, self),
                *widget(self.print_price, self),
                *widget(self.alert, self),
                *widget(self.num_of_ld, self),
                *widget(self.visit_count, self),
                *widget(self.maximize_at_start, self),
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
        self.backgroundcolorpage = BackgroundColorPage(self.book)
        self.book.AddPage(self.infopage, text="Thông tin")
        self.book.AddPage(self.followchoicepage, text="Lời dặn")
        self.book.AddPage(self.systempage, text="Hệ thống")
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
            self.mv.config.doctor_name = infopage.doctor_name.Value
            self.mv.config.clinic_address = infopage.clinic_address.Value
            self.mv.config.clinic_phone_number = infopage.clinic_phone_number.Value
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
            self.mv.config.ask_print = systempage.ask_print.Value
            self.mv.config.print_price = systempage.print_price.Value
            self.mv.config.minimum_drug_quantity_alert = systempage.alert.Value
            self.mv.config.max_number_of_drugs_in_one_page = systempage.num_of_ld.Value
            self.mv.config.display_recent_visit_count = systempage.visit_count.Value
            self.mv.config.maximize_at_start = systempage.maximize_at_start.Value

            def set_color(name: str, widget: wx.ColourPickerCtrl):
                self.mv.config.background_color[name] = widget.Colour.GetIM()[:3]

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
            wx.MessageBox("Đã lưu cài đặt\nKhởi động lại để thay đổi màu", "Cài đặt")
            self.mv.price.FetchPrice()
            e.Skip()
        except Exception as error:
            wx.MessageBox(f"Lỗi không lưu được\n{error}", "Lỗi")
