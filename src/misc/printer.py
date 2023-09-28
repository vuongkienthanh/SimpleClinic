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
        self.num_of_ld = 7

    def HasPage(self, page):
        "Relative to `num_of_ld`"
        x, y = divmod(
            self.mv.order_book.prescriptionpage.drug_list.ItemCount,
            self.num_of_ld,
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
                self.mv.order_book.prescriptionpage.drug_list.ItemCount, self.num_of_ld
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

        top_margin = aty(0.03)
        block_spacing = aty(0.03)
        left_margin = atx(0.06)
        right_column = atx(0.7)

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
                # .Bold()
                # .Italic()
            )
            clinic_address_font = wx.Font(
                wx.FontInfo(point_size)
                # .Bold()
                # .Italic()
            )
            clinic_phone_number_font = wx.Font(
                wx.FontInfo(point_size)
                # .Bold()
                # .Italic()
            )
            row_height = aty(0.017)

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
            basic = wx.Font(wx.FontInfo(aty(0.015)))
            row_height = aty(0.026)
            diagnosis = tw.wrap(self.mv.diagnosis.Value, 50)[0]
            vnote = tw.wrap(self.mv.vnote.Value, 50)[0]

            def row(i):
                return y + row_height * i

            with wx.DCFontChanger(dc, basic):
                t = "Họ tên:"
                dc.DrawText(t, left_margin, row(0))
                with wx.DCFontChanger(dc, basic.Bold()):
                    dc.DrawText(
                        self.mv.name.Value,
                        left_margin + dc.GetTextExtent(t).x + whitespace,
                        row(0),
                    )
                t = "GT:"
                indent = atx(0.55)
                dc.DrawText(t, indent, row(0))
                dc.DrawText(
                    str(self.mv.gender.Value),
                    indent + dc.GetTextExtent(t).x + whitespace,
                    row(0),
                )
                t = "Tuổi:"
                indent = atx(0.7)
                dc.DrawText(t, indent, row(0))
                dc.DrawText(
                    self.mv.age.Value,
                    indent + dc.GetTextExtent(t).x + whitespace,
                    row(0),
                )
                t = "Địa chỉ:"
                dc.DrawText(t, left_margin, row(1))
                dc.DrawText(
                    self.mv.address.Value,
                    left_margin + dc.GetTextExtent(t).x + whitespace,
                    row(1),
                )
                t = "SĐT:"
                dc.DrawText(t, left_margin, row(2))
                dc.DrawText(
                    self.mv.phone.Value,
                    left_margin + dc.GetTextExtent(t).x + whitespace,
                    row(2),
                )
                t = "Biểu hiện lâm sàng:"
                dc.DrawText(t, left_margin, row(3))
                dc.DrawText(
                    vnote, left_margin + dc.GetTextExtent(t).x + whitespace, row(3)
                )
                t = "Nhiệt độ:"
                dc.DrawText(t, left_margin, row(4))
                t = "Cân nặng:"
                indent = atx(0.3)
                dc.DrawText(t, indent, row(4))
                dc.DrawText(
                    str(self.mv.weight.Value) + " kg",
                    indent + dc.GetTextExtent(t).x + whitespace,
                    row(4),
                )
                t = "Chiều cao:"
                indent = atx(0.6)
                dc.DrawText(t, indent, row(4))
                t = "Chẩn đoán:"
                dc.DrawText(t, left_margin, row(5))
                dc.DrawText(
                    diagnosis,
                    left_margin + dc.GetTextExtent(t).x + whitespace,
                    row(5),
                )
                return row(5)

        def draw_content(y: int, first_page=True) -> int:
            basic = wx.Font(wx.FontInfo(aty(0.015)))
            bigger = wx.Font(wx.FontInfo(aty(0.018)))

            row_height = aty(0.055)
            indent = atx(0.12)

            def row(i):
                return y + row_height * i

            def name(i: int) -> str:
                return drug_list.GetItemText(i, 1)

            def element(i: int) -> str:
                return drug_list.GetItemText(i, 2)

            def name_element(i: int) -> str:
                return f"{name(i)}({element(i)})"

            def element_name(i: int) -> str:
                return f"{element(i)}({name(i)})"

            match self.mv.config.drug_name_print_style:
                case 0:
                    get_drug_name = name
                case 1:
                    get_drug_name = element
                case 2:
                    get_drug_name = name_element
                case 3:
                    get_drug_name = element_name
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
                    for i in range(min(self.num_of_ld, drug_list.ItemCount))
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
                    for i in range(self.num_of_ld, drug_list.ItemCount)
                ]
                added_idx_number = self.num_of_ld
            for dl in _list:
                with wx.DCFontChanger(dc, basic.Bold()):
                    dc.DrawText(f"{i+1+added_idx_number}/", left_margin, row(i))
                    dc.DrawText(dl["name"], indent, row(i))
                with wx.DCFontChanger(dc, bigger.Bold()):
                    dc.DrawText(dl["quantity"], right_column, row(i))
                with wx.DCFontChanger(dc, basic):
                    dc.DrawText(dl["note"], indent, row(i) + round(row_height / 2))
                i += 1
            return row(i - 1) + round(row_height / 2)

        def draw_bottom(y: int ) -> None:
            y = aty(0.76)  # comment this out when use dynamic y

            right_basic = wx.Font(wx.FontInfo(aty(0.015)))
            date_text = self.mv.visit_list.GetItemText(
                self.mv.visit_list.GetFirstSelected(), 1
            )
            d = dt.datetime.strptime(date_text, "%d/%m/%Y %H:%M").date()

            row_height = aty(0.03)
            right_margin = atx(0.75)

            def row(i):
                return y + row_height * i

            with wx.DCFontChanger(dc, right_basic.Bold()):
                dc.DrawText("Ghi chú:", left_margin, row(-1))
            with wx.DCFontChanger(dc, right_basic):
                follow = tw.wrap(self.mv.follow.Value, width=50)[:2]
                indent = atx(0.2)
                for i, line in enumerate(follow):
                    dc.DrawText(line, indent, row(i - 1))
                draw_centered_text(
                    f"Ngày {d.day:02} tháng {d.month:02} năm {d.year:04}",
                    right_margin,
                    row(1),
                )
                draw_centered_text("Bác sĩ khám bệnh", right_margin, row(2))
            with wx.DCFontChanger(dc, right_basic.Bold()):
                draw_centered_text(self.mv.config.doctor_name, right_margin, row(5))

            left_basic = wx.Font(wx.FontInfo(aty(0.012)))
            left_bigger = wx.Font(wx.FontInfo(aty(0.015)))
            row_height = aty(0.025)

            if self.mv.recheck.Value != 0:
                match self.mv.config.recheck_date_print_style:
                    case 0:
                        t = f"Tái khám sau {self.mv.recheck.Value} ngày"
                    case 1:
                        dst = d + dt.timedelta(days=self.mv.recheck.Value)
                        t = f"Tái khám: {dst.strftime('%d/%m/%Y')}"
                    case _:
                        raise Exception("wrong style")
                with wx.DCFontChanger(dc, left_bigger.Bold()):
                    dc.DrawText(t, left_margin, row(1))
            with wx.DCFontChanger(dc, left_basic.Bold()):
                dc.DrawText("Tái khám ngay khi:", left_margin, row(3))
            with wx.DCFontChanger(dc, left_basic):
                second_col = left_margin + atx(0.23)
                dc.DrawText("*Lau mát khi sốt", left_margin, row(2))
                dc.DrawText("*Uống nhiều nước", second_col, row(2))
                dc.DrawText("*Sốt cao không giảm", left_margin, row(4))
                dc.DrawText("*Thở bất thường", left_margin, row(5))
                dc.DrawText("*Bệnh nặng hơn", left_margin, row(6))
                dc.DrawText("*Tím tái", second_col, row(4))
                dc.DrawText("*Ói nhiều", second_col, row(5))
                dc.DrawText("*Bỏ ăn uống", second_col, row(6))
                dc.DrawText("*Khát nước", left_margin, row(7))
                dc.DrawText("*Tiểu máu", second_col, row(7))

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
