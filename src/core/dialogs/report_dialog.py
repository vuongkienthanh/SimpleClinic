from misc import APP_DIR
from core import mainview as mv
from db import LineDrug, LineProcedure, Visit, Warehouse, Procedure
from misc import num_to_str_price
import wx
import datetime as dt
import sqlite3
import sys
import os
import subprocess


class DayReportDialog(wx.Dialog):
    def __init__(self, parent: "mv.MainView", date: dt.date):
        super().__init__(parent, title=date.strftime("%d/%m/%Y"))
        self.mv = parent
        res = self.get_report(date)

        def w(s: str):
            return (wx.StaticText(self, label=s), 0, wx.EXPAND | wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                w(f"Số ca khám: {res['visit_count']}"),
                w(f"Doanh thu: {num_to_str_price(res['revenue'])}"),
                w(f"Tổng tiền thuốc (giá mua): {num_to_str_price(res['drug_purchase'])}"),
                w(f"Tổng tiền thuốc (giá bán): {num_to_str_price(res['drug_sale'])}"),
                w(f"Lợi nhuận từ thuốc: {num_to_str_price(res['profit_from_drug'])}"),
                w(f"Lợi nhuận từ thủ thuật: {num_to_str_price(res['procedure'])}"),
            ]
        )
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
                ({self.mv.config.checkup_price} * visit_count) + drug_sale + procedure AS revenue,
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
                        SELECT id FROM {Visit.__tablename__}
                        WHERE DATE(exam_datetime) = '{date.isoformat()}'
                    ) AS v
                    LEFT JOIN {LineDrug.__tablename__} AS ld
                    ON ld.visit_id = v.id
                    LEFT JOIN {LineProcedure.__tablename__} AS lp
                    ON lp.visit_id = v.id
                ) as vdp
                LEFT JOIN {Warehouse.__tablename__} AS wh
                ON vdp.lddrug_id = wh.id
                LEFT JOIN {Procedure.__tablename__} AS pr
                ON vdp.lpprocedure_id = pr.id
            )
        """
        ret = self.mv.connection.execute(query).fetchone()
        assert ret is not None
        return ret


class MonthReportDialog(wx.Dialog):
    def __init__(self, parent, month: int, year: int):
        super().__init__(parent, title=f"T{month}/{year}")
        self.mv = parent
        res = self.get_report(month, year)

        def w(s: str):
            return (wx.StaticText(self, label=s), 0, wx.EXPAND | wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                w(f"Số ca khám: {res['visit_count']}"),
                w(f"Doanh thu: {num_to_str_price(res['revenue'])}"),
                w(f"Tổng tiền thuốc (giá mua): {num_to_str_price(res['drug_purchase'])}"),
                w(f"Tổng tiền thuốc (giá bán): {num_to_str_price(res['drug_sale'])}"),
                w(f"Lợi nhuận từ thuốc: {num_to_str_price(res['profit_from_drug'])}"),
                w(f"Lợi nhuận từ thủ thuật: {num_to_str_price(res['procedure'])}"),
            ]
        )
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
                ({self.mv.config.checkup_price} * visit_count) + drug_sale + procedure AS revenue,
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
                        SELECT id FROM {Visit.__tablename__}
                        WHERE (
                            STRFTIME('%m', exam_datetime) = '{month:>02}' AND
                            STRFTIME('%Y', exam_datetime) = '{year}'
                        )
                    ) AS v
                    LEFT JOIN {LineDrug.__tablename__} AS ld
                    ON ld.visit_id = v.id
                    LEFT JOIN {LineProcedure.__tablename__} AS lp
                    ON lp.visit_id = v.id
                ) as vdp
                LEFT JOIN {Warehouse.__tablename__} AS wh
                ON vdp.lddrug_id = wh.id
                LEFT JOIN {Procedure.__tablename__} AS pr
                ON vdp.lpprocedure_id = pr.id
            )
        """
        ret = self.mv.con.execute(query).fetchone()
        assert ret is not None
        return ret


class MonthWarehouseReportDialog(wx.Dialog):
    def __init__(self, parent, month: int, year: int):
        super().__init__(parent, title=f"T{month}/{year}")
        self.mv = parent
        self.res = self.get_report(month, year)

        self.scroll = wx.ScrolledWindow(
            self,
            style=wx.VSCROLL | wx.ALWAYS_SHOW_SB,
            size=(round(wx.DisplaySize()[0] * 0.4), round(wx.DisplaySize()[1] * 0.4)),
        )
        self.scroll.SetScrollRate(0, 20)

        def w(row: sqlite3.Row):
            name = row["name"]
            quantity = row["quantity"]
            sale_unit = row["sale_unit"] or row["usage_unit"]
            s = f"{quantity} {sale_unit}"
            return (
                wx.StaticText(self.scroll, label=name),
                0,
                wx.EXPAND | wx.ALL,
                5,
            ), (
                wx.StaticText(self.scroll, label=s),
                0,
                wx.EXPAND | wx.ALL,
                5,
            )

        self.export_btn = wx.Button(self, label="Xuất file text")
        self.export_btn.Bind(wx.EVT_BUTTON, self.export)

        scroll_sizer = wx.FlexGridSizer(len(self.res), 2, 5, 5)
        for row in self.res:
            scroll_sizer.AddMany([*w(row)])

        self.scroll.SetSizer(scroll_sizer)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.scroll)
        sizer.Add(self.export_btn, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(sizer)

    def get_report(self, month: int, year: int) -> list[sqlite3.Row]:
        query = f"""
            SELECT
                wh.name AS name,
                SUM(ld.quantity) AS quantity,
                wh.sale_unit AS sale_unit,
                wh.usage_unit AS usage_unit
            FROM {LineDrug.__tablename__} AS ld
            LEFT JOIN (
                SELECT id FROM {Visit.__tablename__}
                WHERE (
                    STRFTIME('%m', exam_datetime) = '{month:>02}' AND
                    STRFTIME('%Y', exam_datetime) = '{year}'
                )
            ) AS v
            ON ld.visit_id = v.id
            LEFT JOIN {Warehouse.__tablename__} AS wh
            ON ld.drug_id = wh.id
            GROUP BY wh.name
        """
        ret = self.mv.con.execute(query).fetchall()
        return ret

    def export(self, e):
        path = os.path.join(APP_DIR, "dungthuoctrongthang.txt")
        with open(path, mode="w", encoding="utf-8") as f:
            for row in self.res:
                name = row["name"]
                quantity = row["quantity"]
                sale_unit = row["sale_unit"] or row["usage_unit"]
                s = f"{name:<30}: {quantity:>3} {sale_unit}\n"
                f.write(s)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "linux":
            subprocess.run(["xdg-open", path])
        elif sys.platform == "darwin":
            subprocess.run(["start", path])
