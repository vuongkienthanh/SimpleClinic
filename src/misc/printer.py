import datetime as dt
import textwrap as tw

import wx

from ui import mainview

printdata = wx.PrintData()
printdata.Bin = wx.PRINTBIN_DEFAULT
printdata.Collate = False
printdata.Colour = False
printdata.Duplex = wx.DUPLEX_SIMPLEX
printdata.NoCopies = 1
printdata.Orientation = wx.PORTRAIT
printdata.PrinterName = ""
printdata.Quality = wx.PRINT_QUALITY_LOW
printdata.PaperId = wx.PAPER_A5


class PrintOut(wx.Printout):
    def __init__(self, mv: "mainview.MainView", preview=False):
        super().__init__(title="Toa thuốc")
        self.mv = mv
        self.preview = preview

    def HasPage(self, page):
        "Relative to `num_of_ld`"
        x, y = divmod(
            self.mv.order_book.prescriptionpage.drug_list.ItemCount,
            self.mv.config.max_number_of_drugs_in_one_page,
        )
        if page <= (x + bool(y)):
            return True
        elif page == 1 and (x + y) == 0:
            return True
        else:
            return False

    def GetPageInfo(self):
        "Relative to `num_of_ld`"
        if self.mv.order_book.prescriptionpage.drug_list.ItemCount == 0:
            return (1, 1, 1, 1)
        else:
            x, y = divmod(
                self.mv.order_book.prescriptionpage.drug_list.ItemCount,
                self.mv.config.max_number_of_drugs_in_one_page,
            )
        return (1, x + bool(y), 1, x + bool(y))

    def OnPrintPage(self, page):
        dc: wx.DC = self.GetDC()
        dcx, dcy = dc.Size
        if self.preview:
            scale = self.mv.config.preview_scale
        else:
            scale = self.mv.config.print_scale
        dcx, dcy = round(dcx * scale), round(dcy * scale)
        whitespace = round(dcx * 0.003)

        def atx(f: float) -> int:
            return round(dcx * f)

        def aty(f: float) -> int:
            return round(dcy * f)

        top_margin = aty(0.05)
        block_spacing = aty(0.03)
        left_margin = atx(0.06)
        right_column = atx(0.7)

        num_of_ld = self.mv.config.max_number_of_drugs_in_one_page
        drug_list = self.mv.order_book.prescriptionpage.drug_list

        def draw_centered_text(s: str, x: int, y: int) -> int:
            "x is the middle point"
            size = dc.GetTextExtent(s)
            dc.DrawText(s, round(x - size.x / 2), y)
            return size.y

        def draw_clinic_info(y: int, page: int) -> int:
            point_size = aty(0.012)
            basic_font = wx.Font(wx.FontInfo(point_size))
            clinic_name_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("clinic_name")["bold"])
                .Italic(self.mv.config.get_format("clinic_name")["italic"])
            )
            clinic_address_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("clinic_address")["bold"])
                .Italic(self.mv.config.get_format("clinic_address")["italic"])
            )
            clinic_phone_number_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("clinic_phone_number")["bold"])
                .Italic(self.mv.config.get_format("clinic_phone_number")["italic"])
            )
            row_height = aty(0.02)

            def row(i):
                return y + row_height * i

            with wx.DCFontChanger(dc, clinic_name_font):
                dc.DrawText(self.mv.config.clinic_name, left_margin, row(0))
            with wx.DCFontChanger(dc, clinic_address_font):
                dc.DrawText(
                    "Địa chỉ: " + self.mv.config.clinic_address, left_margin, row(1)
                )
            with wx.DCFontChanger(dc, clinic_phone_number_font):
                dc.DrawText(
                    "SĐT: " + self.mv.config.clinic_phone_number, left_margin, row(2)
                )
            if self.HasPage(2):
                with wx.DCFontChanger(dc, basic_font):
                    right_margin = atx(0.75)
                    draw_centered_text(f"Trang {page}/2", right_margin, row(0))
            return row(2)

        def draw_title(y: int) -> int:
            title = wx.Font(wx.FontInfo(aty(0.02)).Bold())
            with wx.DCFontChanger(dc, title):
                text_height = draw_centered_text("ĐƠN THUỐC", round(dcx / 2), y)
                return round(text_height / 2) + y

        def draw_patient_info(y: int) -> int:
            point_size = aty(0.015)
            basic_info = wx.Font(wx.FontInfo(point_size))
            patient_name_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("patient_name")["bold"])
                .Italic(self.mv.config.get_format("patient_name")["italic"])
            )
            weight_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("weight")["bold"])
                .Italic(self.mv.config.get_format("weight")["italic"])
            )
            gender_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("gender")["bold"])
                .Italic(self.mv.config.get_format("gender")["italic"])
            )
            birthdate_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("birthdate")["bold"])
                .Italic(self.mv.config.get_format("birthdate")["italic"])
            )
            age_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("age")["bold"])
                .Italic(self.mv.config.get_format("age")["italic"])
            )
            diagnosis_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("diagnosis")["bold"])
                .Italic(self.mv.config.get_format("diagnosis")["italic"])
            )
            vnote_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("vnote")["bold"])
                .Italic(self.mv.config.get_format("vnote")["italic"])
            )
            row_height = aty(0.026)
            indent = atx(0.25)
            middle = atx(0.3)
            diagnosis = tw.wrap(self.mv.diagnosis.Value, 50)
            if len(diagnosis) > 2:
                diagnosis = diagnosis[:2]
                diagnosis[-1] = diagnosis[-1][:-3] + "..."
            vnote = tw.wrap(self.mv.vnote.Value, 50)
            if len(vnote) > 2:
                vnote = vnote[:2]
                vnote[-1] = vnote[-1][:-3] + "..."

            def row(i):
                return y + row_height * i

            s1 = "Họ tên:"
            s2 = "CN:"
            s3 = "Giới:"
            s4 = "SN:"
            s5 = "Chẩn đoán:"
            s6 = "Bệnh sử:"
            with wx.DCFontChanger(dc, basic_info):
                dc.DrawText(s1, left_margin, row(0))
                dc.DrawText(s2, right_column, row(0))
                dc.DrawText(s3, left_margin, row(1))
                dc.DrawText(s4, middle, row(1))
                dc.DrawText(s5, left_margin, row(2))
                if self.mv.config.print_vnote:
                    dc.DrawText(s6, left_margin, row(3 + len(diagnosis) - 1))

            with wx.DCFontChanger(dc, patient_name_font):
                dc.DrawText(
                    self.mv.name.Value,
                    left_margin + dc.GetTextExtent(s1).x + whitespace,
                    row(0),
                )
            with wx.DCFontChanger(dc, weight_font):
                dc.DrawText(
                    str(self.mv.weight.Value) + " kg",
                    right_column + dc.GetTextExtent(s2).x + whitespace,
                    row(0),
                )
            with wx.DCFontChanger(dc, gender_font):
                dc.DrawText(
                    str(self.mv.gender.Value),
                    left_margin + dc.GetTextExtent(s3).x + whitespace,
                    row(1),
                )
            with wx.DCFontChanger(dc, birthdate_font):
                dc.DrawText(
                    self.mv.birthdate.Value,
                    middle + dc.GetTextExtent(s4).x + whitespace,
                    row(1),
                )
            with wx.DCFontChanger(dc, age_font):
                dc.DrawText(self.mv.age.Value, right_column, row(1))
            with wx.DCFontChanger(dc, diagnosis_font):
                for i, line in enumerate(diagnosis):
                    dc.DrawText(line, indent, row(2 + i))
            if self.mv.config.print_vnote & (len(vnote) > 0):
                with wx.DCFontChanger(dc, vnote_font):
                    for i, line in enumerate(vnote):
                        dc.DrawText(line, indent, row(len(diagnosis) + 2 + i))
            if self.mv.config.print_vnote:
                return row(1 + len(diagnosis) + max(1, len(vnote)))
            else:
                return row(1 + len(diagnosis))

        def draw_content(y: int, first_page=True) -> int:
            point_size = aty(0.015)
            bigger_point_size = aty(0.018)
            basic_font = wx.Font(wx.FontInfo(point_size))
            drug_name_font = wx.Font(
                wx.FontInfo(bigger_point_size)
                .Bold(self.mv.config.get_format("drug_name")["bold"])
                .Italic(self.mv.config.get_format("drug_name")["italic"])
            )
            drug_quantity_font = wx.Font(
                wx.FontInfo(bigger_point_size)
                .Bold(self.mv.config.get_format("drug_quantity")["bold"])
                .Italic(self.mv.config.get_format("drug_quantity")["italic"])
            )
            drug_usage_note_font = wx.Font(
                wx.FontInfo(point_size)
                .Bold(self.mv.config.get_format("drug_usage_note")["bold"])
                .Italic(self.mv.config.get_format("drug_usage_note")["italic"])
            )

            row_height = aty(0.055 * 8 / self.mv.config.max_number_of_drugs_in_one_page)
            indent = atx(0.12)

            def row(i):
                return y + row_height * i

            def name_only(i: int) -> str:
                return drug_list.GetItemText(i, 1)

            def element_only(i: int) -> str:
                return drug_list.GetItemText(i, 2)

            def name_element(i: int) -> str:
                return f"{drug_list.GetItemText(i, 1)}({drug_list.GetItemText(i,2)})"[
                    :30
                ]

            match self.mv.config.drug_name_print_style:
                case 0:
                    get_drug_name = name_only
                case 1:
                    get_drug_name = element_only
                case 2:
                    get_drug_name = name_element
                case _:
                    raise Exception("cant get drug name print style")

            i = 0
            if first_page:
                _list = [
                    {
                        "name": get_drug_name(i)
                        + (
                            " (TT)"
                            if self.mv.config.outclinic_drug_checkbox
                            & drug_list.IsItemChecked(i)
                            else ""
                        ),
                        "quantity": drug_list.GetItemText(i, 5),
                        "note": drug_list.GetItemText(i, 6),
                    }
                    for i in range(min(num_of_ld, drug_list.ItemCount))
                ]
                added_idx_number = 0
            else:
                _list = [
                    {
                        "name": get_drug_name(i)
                        + (
                            " (TT)"
                            if self.mv.config.outclinic_drug_checkbox
                            & drug_list.IsItemChecked(i)
                            else ""
                        ),
                        "quantity": drug_list.GetItemText(i, 5),
                        "note": drug_list.GetItemText(i, 6),
                    }
                    for i in range(num_of_ld, drug_list.ItemCount)
                ]
                added_idx_number = num_of_ld
            for dl in _list:
                with wx.DCFontChanger(dc, basic_font):
                    dc.DrawText(f"{i+1+added_idx_number}/", left_margin, row(i))
                with wx.DCFontChanger(dc, drug_name_font):
                    dc.DrawText(dl["name"], indent, row(i))
                with wx.DCFontChanger(dc, drug_quantity_font):
                    dc.DrawText(dl["quantity"], right_column, row(i))
                with wx.DCFontChanger(dc, drug_usage_note_font):
                    dc.DrawText(dl["note"], indent, row(i) + round(row_height / 2))
                i += 1
            return row(i - 1) + round(row_height / 2)

        def draw_bottom(y: int) -> None:
            y = aty(0.76)  # comment this out when use dynamic y
            right_point_size = aty(0.015)
            right_font = wx.Font(wx.FontInfo(right_point_size))
            doctor_name_font = wx.Font(
                wx.FontInfo(right_point_size)
                .Bold(self.mv.config.get_format("doctor_name")["bold"])
                .Italic(self.mv.config.get_format("doctor_name")["italic"])
            )
            doctor_license_font = wx.Font(
                wx.FontInfo(right_point_size)
                .Bold(self.mv.config.get_format("doctor_license")["bold"])
                .Italic(self.mv.config.get_format("doctor_license")["italic"])
            )
            if self.mv.state.visit:
                d = self.mv.state.visit.exam_datetime.date()
            else:
                d = dt.date.today()
            row_height = aty(0.03)
            right_margin = atx(0.75)

            def row(i):
                return y + row_height * i

            with wx.DCFontChanger(dc, right_font):
                draw_centered_text(
                    f"Ngày {d.day:02} tháng {d.month:02} năm {d.year:04}",
                    right_margin,
                    row(0),
                )
                draw_centered_text("Bác sĩ khám bệnh", right_margin, row(1))
            with wx.DCFontChanger(dc, doctor_name_font):
                draw_centered_text(self.mv.config.doctor_name, right_margin, row(4))
            with wx.DCFontChanger(dc, doctor_license_font):
                draw_centered_text(self.mv.config.doctor_license, right_margin, row(5))

            left_point_size = aty(0.012)
            left_font = wx.Font(wx.FontInfo(left_point_size))
            recheck_font = wx.Font(
                wx.FontInfo(left_point_size)
                .Bold(self.mv.config.get_format("recheck_date")["bold"])
                .Italic(self.mv.config.get_format("recheck_date")["italic"])
            )
            row_height = aty(0.02)

            with wx.DCFontChanger(dc, left_font):
                if self.mv.config.print_price:
                    t = f"Tổng cộng: {self.mv.price.Value}"
                    if self.mv.order_book.procedurepage.procedure_list.ItemCount > 0:
                        t += " (đã gồm tiền thủ thuật)"
                    dc.DrawText(t, left_margin, row(0))
                if self.mv.recheck.Value != 0:
                    match self.mv.config.recheck_date_print_style:
                        case 0:
                            t = f"Tái khám sau {self.mv.recheck.Value} ngày"
                        case 1:
                            dst = d + dt.timedelta(days=self.mv.recheck.Value)
                            t = f"Tái khám: {dst.strftime('%d/%m/%Y')}"
                        case _:
                            raise Exception("wrong style")
                    with wx.DCFontChanger(dc, recheck_font):
                        dc.DrawText(t, left_margin, row(1))
                follow = tw.wrap(self.mv.follow.expand_when_print(), width=40)
                for i, line in enumerate(follow):
                    dc.DrawText(line, left_margin, row(3 + i))

        if page == 1:
            next_row = draw_clinic_info(top_margin, page) + block_spacing
            next_row = draw_title(next_row) + block_spacing
            next_row = draw_patient_info(next_row) + block_spacing
            if drug_list.ItemCount != 0:
                next_row = draw_content(next_row, first_page=True) + block_spacing
            draw_bottom(next_row)
            return True
        elif page == 2:
            next_row = draw_clinic_info(top_margin, page) + block_spacing
            next_row = draw_title(next_row) + block_spacing
            next_row = draw_patient_info(next_row) + block_spacing
            next_row = draw_content(next_row, first_page=False) + block_spacing
            draw_bottom(next_row)
            return True
        else:
            return False
