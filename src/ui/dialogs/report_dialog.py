import datetime as dt
import os
import sqlite3

import wx

from db import Connection, LineDrug, LineProcedure, Procedure, Visit, Warehouse
from misc import APP_DIR, Config, num_to_str_price
from ui import mainview as mv


def finance_report(
    connection: Connection,
    config: Config,
    *,
    date: dt.date | None = None,
    month: int | None = None,
    year: int | None = None,
) -> sqlite3.Row:
    """
    Số ca khám
    Doanh thu từ thuốc và tiền công
    Doanh thu thực tế
    Tổng tiền thuốc (giá mua)
    Tổng tiền thuốc (giá bán)
    Lợi nhuận từ thuốc
    Lợi nhuận từ thủ thuật
    """
    match date, month, year:
        case dt.date() as d, None, None:
            visit_where_clause = f"""WHERE DATE(exam_datetime) = '{d.isoformat()}'"""
        case None, int(), int():
            visit_where_clause = f"""
                WHERE (
                    STRFTIME('%m', exam_datetime) = '{month:>02}' AND
                    STRFTIME('%Y', exam_datetime) = '{year}'
                )
            """
        case _:
            raise NotImplementedError
    query = f"""
        SELECT
            COUNT(DISTINCT vid) as visit_count,
            SUM({config.checkup_price} + drug_sale_per_visit + procedure_profit_per_visit) AS revenue,
            SUM(vprice) AS real_revenue,
            SUM(drug_purchase_per_visit) AS drug_purchase,
            SUM(drug_sale_per_visit) AS drug_sale,
            SUM(drug_sale_per_visit - drug_purchase_per_visit) AS drug_profit,
            SUM(procedure_profit_per_visit) AS procedure_profit
        FROM (
            SELECT
                vid,
                vprice,
                CAST(TOTAL(v2.quantity * wh.purchase_price) AS INTEGER) AS drug_purchase_per_visit,
                CAST(TOTAL(v2.quantity * wh.sale_price) AS INTEGER) AS drug_sale_per_visit,
                CAST(TOTAL(pr.price) AS INTEGER) AS procedure_profit_per_visit
            FROM (
                SELECT
                    v.id AS vid,
                    v.price AS vprice,
                    ld.warehouse_id,
                    ld.quantity,
                    lp.procedure_id
                FROM (
                    SELECT id,price FROM {Visit.__tablename__} {visit_where_clause}
                ) AS v
                LEFT JOIN {LineDrug.__tablename__} AS ld
                ON ld.visit_id = v.id
                LEFT JOIN {LineProcedure.__tablename__} AS lp
                ON lp.visit_id = v.id
                WHERE ld.misc ->> '$.outclinic' == FALSE
            ) as v2
            LEFT JOIN {Warehouse.__tablename__} AS wh
            ON v2.warehouse_id = wh.id
            LEFT JOIN {Procedure.__tablename__} AS pr
            ON v2.procedure_id = pr.id
            GROUP BY vid
        )
    """
    ret = connection.execute(query).fetchone()
    assert ret is not None
    return ret


class FinanceReportDialog(wx.Dialog):
    def __init__(self, parent: "mv.MainView", title: str):
        super().__init__(parent, title=title)
        self.mv = parent
        res = self.report()

        def w(s: str):
            return (wx.StaticText(self, label=s), 0, wx.EXPAND | wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                w(f"Số ca khám: {res['visit_count']}"),
                w(
                    f"Doanh thu (tiền công + thuốc + thủ thuật): {num_to_str_price(res['revenue'])}"
                ),
                w(
                    f"Doanh thu (theo giá thu): {num_to_str_price(res['real_revenue'])}"
                ),
                w(
                    f"Tổng tiền thuốc (giá mua): {num_to_str_price(res['drug_purchase'])}"
                ),
                w(
                    f"Tổng tiền thuốc (giá bán): {num_to_str_price(res['drug_sale'])}"
                ),
                w(f"Lợi nhuận từ thuốc: {num_to_str_price(res['drug_profit'])}"),
                w(
                    f"Lợi nhuận từ thủ thuật: {num_to_str_price(res['procedure_profit'])}"
                ),
            ]
        )
        sizer.Add(self.CreateStdDialogButtonSizer(wx.OK), 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(sizer)

    def report(self) -> sqlite3.Row:
        ...


class DayFinanceReportDialog(FinanceReportDialog):
    def __init__(self, parent: "mv.MainView", date: dt.date):
        self.date = date
        super().__init__(parent, title=date.strftime("%d/%m/%Y"))

    def report(self):
        return finance_report(self.mv.connection, self.mv.config, date=self.date)


class MonthFinanceReportDialog(FinanceReportDialog):
    def __init__(self, parent: "mv.MainView", month: int, year: int):
        self.month = month
        self.year = year
        super().__init__(parent, title=f"T{month}/{year}")

    def report(self):
        return finance_report(
            self.mv.connection, self.mv.config, month=self.month, year=self.year
        )


class MonthWarehouseReportDialog(wx.Dialog):
    def __init__(self, parent: "mv.MainView", month: int, year: int):
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
            return (
                (
                    wx.StaticText(self.scroll, label=row["name"]),
                    0,
                    wx.EXPAND | wx.ALL,
                    5,
                ),
                (
                    wx.StaticText(self.scroll, label=row["element"]),
                    0,
                    wx.EXPAND | wx.ALL,
                    5,
                ),
                (
                    wx.StaticText(
                        self.scroll,
                        label=f"{row['quantity']} {row['sale_unit'] or row['usage_unit']}",
                    ),
                    0,
                    wx.EXPAND | wx.ALL,
                    5,
                ),
            )

        self.export_btn = wx.Button(self, label="Xuất file text")
        self.export_btn.Bind(wx.EVT_BUTTON, self.export)

        scroll_sizer = wx.FlexGridSizer(len(self.res), 3, 5, 5)
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
                wh.element AS element,
                SUM(ld.quantity) AS quantity,
                wh.sale_unit AS sale_unit,
                wh.usage_unit AS usage_unit
            FROM {LineDrug.__tablename__} AS ld
            JOIN (
                SELECT id FROM {Visit.__tablename__}
                WHERE (
                    STRFTIME('%m', exam_datetime) = '{month:>02}' AND
                    STRFTIME('%Y', exam_datetime) = '{year}'
                )
            ) AS v
            ON ld.visit_id = v.id
            LEFT JOIN {Warehouse.__tablename__} AS wh
            ON ld.warehouse_id = wh.id
            GROUP BY ld.warehouse_id
        """
        ret = self.mv.connection.execute(query).fetchall()
        return ret

    def export(self, _):
        import sys

        if sys.platform == "win32":
            encoding = "utf-8-sig"
        else:
            encoding = "utf-8"
        path = os.path.join(APP_DIR, "dungthuoctrongthang.csv")
        with open(path, mode="w", encoding=encoding) as f:
            f.write("tên,thành phần,số lượng, đơn vị\n")
            for row in self.res:
                f.write(
                    f"{row['name']},{row['element']},{row['quantity']},"
                    f"{row['sale_unit'] or row['usage_unit']}\n"
                )
        wx.LaunchDefaultApplication(path)
