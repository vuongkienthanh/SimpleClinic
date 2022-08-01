import core.other_func as otf
from core import mainview as mv
import textwrap as tw
import wx


printdata = wx.PrintData()
printdata.Bin = wx.PRINTBIN_DEFAULT
printdata.Collate = False
printdata.Colour = False
printdata.Duplex = wx.DUPLEX_SIMPLEX
printdata.NoCopies = 1
printdata.Orientation = wx.PORTRAIT
printdata.PrinterName = ''
printdata.Quality = wx.PRINT_QUALITY_LOW
printdata.PaperId = wx.PAPER_A5


class PrintOut(wx.Printout):

    def __init__(self, mv: 'mv.MainView', preview=False):
        super().__init__(title="Toa thuốc")

        self.mv = mv
        self.preview = preview

    def HasPage(self, page):
        "Relative to `num_of_ld`"
        x, y = divmod(
            self.mv.order_book.page0.drug_list.ItemCount,
            self.mv.config['so_muc_thuoc_1_toa']
        )
        if page <= (x + bool(y)):
            return True
        elif page == 1 and (x + y) == 0:
            return True
        else:
            return False

    def GetPageInfo(self):
        "Relative to `num_of_ld`"
        if self.mv.order_book.page0.drug_list.ItemCount == 0:
            return (1, 1, 1, 1)
        else:
            x, y = divmod(
                self.mv.order_book.page0.drug_list.ItemCount,
                self.mv.config['so_muc_thuoc_1_toa']
            )
        return (1, x + bool(y), 1, x + bool(y))

    def OnPrintPage(self, page):

        num_of_ld = self.mv.config['so_muc_thuoc_1_toa']
        d_list = self.mv.order_book.page0.drug_list.d_list
        state = self.mv.state
        p = state.patient
        assert p is not None

        dc: wx.DC = self.GetDC()
        dcx, dcy = dc.Size
        if self.preview:
            scale = self.mv.config['preview_scale']
        else:
            scale = self.mv.config['print_scale']
        dcx, dcy = round(dcx * scale), round(dcy * scale)

        space = round(dcx * 0.002)

        # fonts
        title = wx.Font(wx.FontInfo(round(dcy * 0.02)).Bold())
        info = wx.Font(wx.FontInfo(round(dcy * 0.015)))
        info_italic = wx.Font(wx.FontInfo(round(dcy * 0.015)).Italic())
        list_num = wx.Font(wx.FontInfo(round(dcy * 0.015)).Bold())
        drug_name = wx.Font(wx.FontInfo(round(dcy * 0.018)))
        heading = wx.Font(wx.FontInfo(round(dcy * 0.012)))

        def get_text_x(s: str) -> int:
            "return str x"
            return dc.GetTextExtent(s)[0]

        def atx(f: float) -> int:
            "start at x"
            return round(dcx * f)

        def aty(f: float) -> int:
            "start at x"
            return round(dcy * f)

        def draw_centered_text(s: str, x: int, y: int):
            "x is the middle point"
            sx = get_text_x(s)
            dc.DrawText(s, round(x - sx / 2), y)

        def draw_top():

            row_y = round(dcy * 0.017)
            y = aty(0.05)

            def row(i): return y + row_y * i

            with wx.DCFontChanger(dc, heading):
                x = atx(0.085)
                dc.DrawText(self.mv.config['ten_phong_kham'], x, row(0))
                dc.DrawText("Địa chỉ: " + self.mv.config['dia_chi'], x, row(1))
                dc.DrawText(
                    "SĐT: " + self.mv.config['so_dien_thoai'], x, row(2))
            with wx.DCFontChanger(dc, title):
                draw_centered_text('ĐƠN THUỐC', round(
                    dcx / 2), row(3))

            row_y = round(dcy * 0.026)
            y = round(dcy * 0.14)
            s1 = "Họ tên:"
            s2 = "CN:"
            s3 = "Giới:"
            s4 = "SN:"
            s5 = "Chẩn đoán:"
            with wx.DCFontChanger(dc, info):
                dc.DrawText(s1, atx(0.06), row(0))
                dc.DrawText(s2, atx(0.7), row(0))
                dc.DrawText(s3, atx(0.06), row(1))
                dc.DrawText(s4, atx(0.3), row(1))
                dc.DrawText(s5, atx(0.06), row(2))
            with wx.DCFontChanger(dc, info_italic):
                dc.DrawText(
                    p.name,
                    atx(0.06) + get_text_x(s1) + space,
                    row(0))
                dc.DrawText(
                    str(self.mv.weight.Value) + " kg",
                    atx(0.7) + get_text_x(s2) + space,
                    row(0))
                dc.DrawText(
                    str(p.gender),
                    atx(0.06) + get_text_x(s3) + space,
                    row(1))
                dc.DrawText(
                    p.birthdate.strftime("%d/%m/%Y"),
                    atx(0.3) + get_text_x(s4) + space,
                    row(1))
                dc.DrawText(
                    otf.bd_to_age(p.birthdate),
                    atx(0.7),
                    row(1))
                diagnosis = tw.wrap(self.mv.diagnosis.Value,
                                    60, initial_indent=" " * 19)
                if len(diagnosis) > 3:
                    diagnosis = diagnosis[:3]
                    diagnosis[-1] = diagnosis[-1][:-3] + '...'
                for i, line in enumerate(diagnosis):
                    dc.DrawText(line, atx(0.06), i * row_y + row(2))

        def draw_bottom():
            with wx.DCFontChanger(dc, info):
                dc.DrawText("Bác sĩ khám bệnh", atx(0.63), aty(0.735))
                draw_centered_text(
                    self.mv.config['ky_ten_bac_si'], atx(0.75), aty(0.865))

            row_y = round(dcy * 0.02)
            y = aty(0.72)
            def row(i): return y + row_y * i
            with wx.DCFontChanger(dc, heading):
                if self.mv.config['in_gia_tien']:
                    dc.DrawText(
                        f"Tổng cộng: {self.mv.price.GetValue()}", atx(0.06), row(0))
                if self.mv.recheck.GetValue() != 0:
                    dc.DrawText(
                        f"Tái khám sau {self.mv.recheck.GetValue()} ngày", atx(0.06), row(1))
                follow = tw.wrap(self.mv.follow.Value, width=40)
                for i, line in enumerate(follow):
                    dc.DrawText(line, atx(0.06), row(2) + row_y * i)

        def draw_page_count(i: int):
            with wx.DCFontChanger(dc, heading):
                dc.DrawText(f"Trang {i}/2", atx(0.7), aty(0.72))

        def draw_content(first=True):

            row_y = round(dcy * 0.055)
            y = aty(0.28)

            def row(i): return y + row_y * i

            i = 0
            if first:
                _list = d_list[:num_of_ld]
                added = 0
            else:
                _list = d_list[num_of_ld:]
                added = num_of_ld
            for dl in _list:
                with wx.DCFontChanger(dc, list_num):
                    dc.DrawText(f"{i+1+added}/", atx(0.06), row(i))
                with wx.DCFontChanger(dc, drug_name):
                    dc.DrawText(f"{dl.name}", atx(0.12), row(i))
                    t = f"{dl.quantity} {dl.sale_unit or dl.usage_unit}"
                    dc.DrawText(t, atx(0.7), row(i))
                with wx.DCFontChanger(dc, info_italic):
                    t = dl.note or otf.get_usage_note_str(
                        dl.usage,
                        str(dl.times),
                        dl.dose,
                        dl.usage_unit
                    )
                    dc.DrawText(t, atx(0.12), row(i) + round(row_y / 2))
                i += 1

        if page == 1:
            draw_top()
            if len(d_list) != 0:
                draw_content(first=True)
            draw_bottom()
            if self.HasPage(2):
                draw_page_count(1)
            return True

        elif page == 2:
            draw_top()
            draw_content(first=False)
            draw_page_count(2)
            draw_bottom()
            return True
        else:
            return False
