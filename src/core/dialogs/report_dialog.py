from core.generic import DatePicker
from core import mainview as mv
from db.db_class import LineDrug, LineProcedure, Visit, Warehouse, Procedure
from core import other_func as otf
from core.generic import NumberTextCtrl
import wx
import datetime as dt
import sqlite3


class DatePickerDialog(wx.Dialog):
    def __init__(self, parent: 'mv.MainView'):
        super().__init__(parent, title="Chọn ngày báo cáo")
        self.datepicker = DatePicker(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (self.datepicker, 0, wx.EXPAND | wx.ALL, 10),
            (self.CreateStdDialogButtonSizer(
                wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.ALL, 10)
        ])
        self.SetSizerAndFit(sizer)

    def GetDate(self) -> dt.date:
        return self.datepicker.GetDate()


class MonthPickerDialog(wx.Dialog):
    def __init__(self, parent: 'mv.MainView'):
        super().__init__(parent, title="Chọn tháng báo cáo")
        self.month = wx.SpinCtrl(
            self, min=1, max=12, initial=dt.date.today().month, name="Tháng:")
        self.year = NumberTextCtrl(self, value=str(
            dt.date.today().year), name="Năm:")
        self.year.SetHint("YYYY")

        def widget(w):
            return (wx.StaticText(self, label=w.Name), 0, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5), (w, 0, wx.EXPAND | wx.ALL, 5)

        entry_sizer = wx.FlexGridSizer(2, 2, 5, 5)
        entry_sizer.AddMany([
            *widget(self.month),
            *widget(self.year)
        ])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            (entry_sizer, 0, wx.EXPAND | wx.ALL, 5),
            (self.CreateStdDialogButtonSizer(
                wx.OK | wx.CANCEL), 0, wx.EXPAND | wx.ALL, 10)
        ])
        self.SetSizerAndFit(sizer)

    def GetMonth(self) -> int:
        return self.month.GetValue()

    def GetYear(self) -> int:
        return int(self.year.GetValue())


class DayReportDialog(wx.Dialog):
    def __init__(self, parent: 'mv.MainView', date: dt.date):
        super().__init__(parent, title="Báo cáo ngày")
        self.mv = parent
        res = self.get_report(date)

        def w(s: str):
            return (wx.StaticText(self, label=s), 0, wx.EXPAND | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            w(f"Số ca khám: {res['visit_count']}"),
            w(f"Doanh thu: {otf.num_to_str(res['revenue'])}"),
            w(f"Tổng tiền thuốc (giá mua): {otf.num_to_str(res['drug_purchase'])}"),
            w(f"Tổng tiền thuốc (giá bán): {otf.num_to_str(res['drug_sale'])}"),
            w(f"Lợi nhuận từ thuốc: {otf.num_to_str(res['profit_from_drug'])}"),
            w(f"Lợi nhuận từ thủ thuật: {otf.num_to_str(res['procedure'])}"),
        ])
        self.SetSizerAndFit(sizer)

    def get_report(self, date: dt.date) -> sqlite3.Row:
        """
        Số ca khám
        Doanh thu
        Tổng tiền thuốc (giá mua)
        Tổng tiền thuốc (giá bán)
        Lợi nhuận từ thuốc
        Lợi nhuận từ thủ thuật
        """
        query = f"""
            SELECT
                visit_count,
                ({self.mv.config['cong_kham_benh']} * visit_count) + drug_sale + procedure AS revenue,
                drug_purchase,
                drug_sale,
                (drug_sale - drug_purchase) AS profit_from_drug,
                procedure
            FROM (
                SELECT
                    COUNT(DISTINCT vdp.vid) AS visit_count,
                    CAST(TOTAL(vdp.ldquantity * wh.purchase_price) AS INTEGER) AS drug_purchase,
                    CAST(TOTAL(vdp.ldquantity * wh.sale_price) AS INTEGER) AS drug_sale,
                    CAST(TOTAL(pr.price) AS INTEGER) AS procedure
                FROM (
                    SELECT
                        v.id AS vid,
                        ld.drug_id AS lddrug_id,
                        ld.quantity AS ldquantity,
                        lp.procedure_id AS lpprocedure_id
                    FROM (
                        SELECT id FROM {Visit.table_name}
                        WHERE DATE(exam_datetime) = '{date.isoformat()}'
                    ) AS v
                    LEFT JOIN {LineDrug.table_name} AS ld
                    ON ld.visit_id = v.id
                    LEFT JOIN {LineProcedure.table_name} AS lp
                    ON lp.visit_id = v.id
                ) as vdp
                LEFT JOIN {Warehouse.table_name} AS wh
                ON vdp.lddrug_id = wh.id
                LEFT JOIN {Procedure.table_name} AS pr
                ON vdp.lpprocedure_id = pr.id
            )
        """
        ret = self.mv.con.execute(query).fetchone()
        assert ret is not None
        return ret


class MonthReportDialog(wx.Dialog):
    def __init__(self, parent, month: int, year: int):
        super().__init__(parent)
        self.mv = parent
        res = self.get_report(month, year)

        def w(s: str):
            return (wx.StaticText(self, label=s), 0, wx.EXPAND | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([
            w(f"Số ca khám: {res['visit_count']}"),
            w(f"Doanh thu: {otf.num_to_str(res['revenue'])}"),
            w(f"Tổng tiền thuốc (giá mua): {otf.num_to_str(res['drug_purchase'])}"),
            w(f"Tổng tiền thuốc (giá bán): {otf.num_to_str(res['drug_sale'])}"),
            w(f"Lợi nhuận từ thuốc: {otf.num_to_str(res['profit_from_drug'])}"),
            w(f"Lợi nhuận từ thủ thuật: {otf.num_to_str(res['procedure'])}"),
        ])
        self.SetSizerAndFit(sizer)

    def get_report(self, month: int, year: int) -> sqlite3.Row:
        """
        Số ca khám
        Doanh thu
        Tổng tiền thuốc (giá mua)
        Tổng tiền thuốc (giá bán)
        Lợi nhuận từ thuốc
        Lợi nhuận từ thủ thuật
        """
        query = f"""
            SELECT
                visit_count,
                ({self.mv.config['cong_kham_benh']} * visit_count) + drug_sale + procedure AS revenue,
                drug_purchase,
                drug_sale,
                (drug_sale - drug_purchase) AS profit_from_drug,
                procedure
            FROM (
                SELECT
                    COUNT(DISTINCT vdp.vid) AS visit_count,
                    CAST(TOTAL(vdp.ldquantity * wh.purchase_price) AS INTEGER) AS drug_purchase,
                    CAST(TOTAL(vdp.ldquantity * wh.sale_price) AS INTEGER) AS drug_sale,
                    CAST(TOTAL(pr.price) AS INTEGER) AS procedure
                FROM (
                    SELECT
                        v.id AS vid,
                        ld.drug_id AS lddrug_id,
                        ld.quantity AS ldquantity,
                        lp.procedure_id AS lpprocedure_id
                    FROM (
                        SELECT id FROM {Visit.table_name}
                        WHERE (
                            STRFTIME('%m', exam_datetime) = '{month:>02}' AND
                            STRFTIME('%Y', exam_datetime) = '{year}'
                        )
                    ) AS v
                    LEFT JOIN {LineDrug.table_name} AS ld
                    ON ld.visit_id = v.id
                    LEFT JOIN {LineProcedure.table_name} AS lp
                    ON lp.visit_id = v.id
                ) as vdp
                LEFT JOIN {Warehouse.table_name} AS wh
                ON vdp.lddrug_id = wh.id
                LEFT JOIN {Procedure.table_name} AS pr
                ON vdp.lpprocedure_id = pr.id
            )
        """
        ret = self.mv.con.execute(query).fetchone()
        assert ret is not None
        return ret
