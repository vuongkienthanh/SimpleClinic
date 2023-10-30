import datetime as dt
import os
import os.path
import shutil
import sqlite3
from pathlib import Path
from typing import cast

import wx

from db import LineDrug, Queue, Visit
from misc import APP_DIR, CONFIG_PATH, DEFAULT_CONFIG_PATH, MY_DATABASE_PATH, SRC_DIR
from ui import mainview


class MyMenuBar(wx.MenuBar):
    def __init__(self):
        super().__init__()

        homeMenu = wx.Menu()
        homeMenu.Append(wx.ID_REFRESH, wx.GetStockLabel(wx.ID_REFRESH) + "\tF5")
        homeMenu.Append(wx.ID_ABOUT)
        homeMenu.Append(wx.ID_EXIT)

        editMenu = wx.Menu()

        menuPatient = wx.Menu()
        menuPatient.Append(wx.ID_NEW, "Bệnh nhân mới\tCTRL+N")
        self.menuUpdatePatient: wx.MenuItem = menuPatient.Append(
            wx.ID_EDIT, "Cập nhật thông tin bệnh nhân\tCTRL+U"
        )
        menuPatient.Append(wx.ID_OPEN, "Tìm bệnh nhân cũ\tCTRL+O")
        editMenu.AppendSubMenu(menuPatient, "Bệnh nhân")

        menuVisit = wx.Menu()
        self.menuNewVisit: wx.MenuItem = menuVisit.Append(wx.ID_ANY, "Lượt khám mới")
        self.menuInsertVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Lưu lượt khám\tCTRL+S"
        )
        self.menuUpdateVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Cập nhật lượt khám\tCTRL+Shift+S"
        )
        self.menuDeleteVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Xóa lượt khám cũ"
        )
        editMenu.AppendSubMenu(menuVisit, "Lượt khám")

        menuQueue = wx.Menu()
        self.menuDeleteQueue: wx.MenuItem = menuQueue.Append(
            wx.ID_ANY, "Xóa lượt chờ khám"
        )
        editMenu.AppendSubMenu(menuQueue, "Danh sách chờ")

        menuPrinter = wx.Menu()
        self.menuPrint: wx.MenuItem = menuPrinter.Append(wx.ID_PRINT, "In\tCTRL+P")
        self.menuPreview: wx.MenuItem = menuPrinter.Append(
            wx.ID_PREVIEW, "Xem trước bản in\tCTRL+SHIFT+P"
        )
        editMenu.AppendSubMenu(menuPrinter, "Máy in")

        self.menuCopyVisitInfo: wx.MenuItem = editMenu.Append(
            wx.ID_INFO, "Copy thông tin lượt khám vào Clipboard\tCTRL+SHIFT+C"
        )

        manageMenu = wx.Menu()

        menuWarehouse: wx.MenuItem = manageMenu.Append(wx.ID_ANY, "Kho thuốc")
        menuSample: wx.MenuItem = manageMenu.Append(wx.ID_ANY, "Toa mẫu")
        menuProcedure: wx.MenuItem = manageMenu.Append(wx.ID_ANY, "Thủ thuật")

        menuReport = wx.Menu()
        menuDayReport = menuReport.Append(wx.ID_ANY, "Số lượng bệnh theo ngày")
        menuMonthReport = menuReport.Append(wx.ID_ANY, "Số lượng bệnh theo tháng")
        menuMonthWarehouseReport = menuReport.Append(
            wx.ID_ANY, "Tình hình dùng thuốc theo tháng"
        )
        manageMenu.AppendSubMenu(menuReport, "Báo cáo")

        settingMenu = wx.Menu()

        menuSetupConfig: wx.MenuItem = settingMenu.Append(wx.ID_ANY, "Cài đặt")
        menuOpenConfigFolder: wx.MenuItem = settingMenu.Append(
            wx.ID_ANY, "Mở folder cài đặt + dữ liệu"
        )
        menuReduceDatabaseSize: wx.MenuItem = settingMenu.Append(
            wx.ID_ANY, "Thu nhỏ kích thước dữ liệu"
        )
        menuBackup: wx.MenuItem = settingMenu.Append(wx.ID_ANY, "Sao lưu dữ liệu")
        menuResetConfig: wx.MenuItem = settingMenu.Append(
            wx.ID_ANY, "Khôi phục cài đặt gốc"
        )

        self.Append(homeMenu, "&Home")
        self.Append(editMenu, "&Khám bệnh")
        self.Append(manageMenu, "&Quản lý")
        self.Append(settingMenu, "&Hệ thống")

        self.Bind(wx.EVT_MENU, self.onRefresh, id=wx.ID_REFRESH)
        self.Bind(wx.EVT_MENU, self.onAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.onExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onNewPatient, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.onFindPatient, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.onEditPatient, id=wx.ID_EDIT)
        self.Bind(wx.EVT_MENU, self.onNewVisit, self.menuNewVisit)
        self.Bind(wx.EVT_MENU, self.onInsertVisit, self.menuInsertVisit)
        self.Bind(wx.EVT_MENU, self.onUpdateVisit, self.menuUpdateVisit)
        self.Bind(wx.EVT_MENU, self.onDeleteVisit, self.menuDeleteVisit)
        self.Bind(wx.EVT_MENU, self.onDeleteQueueList, self.menuDeleteQueue)
        self.Bind(wx.EVT_MENU, self.onPrint, id=wx.ID_PRINT)
        self.Bind(wx.EVT_MENU, self.onPreview, id=wx.ID_PREVIEW)
        self.Bind(wx.EVT_MENU, self.onCopyVisitInfo, id=wx.ID_INFO)
        self.Bind(wx.EVT_MENU, self.onWarehouse, menuWarehouse)
        self.Bind(wx.EVT_MENU, self.onSample, menuSample)
        self.Bind(wx.EVT_MENU, self.onProcedure, menuProcedure)
        self.Bind(wx.EVT_MENU, self.onDayReport, menuDayReport)
        self.Bind(wx.EVT_MENU, self.onMonthReport, menuMonthReport)
        self.Bind(wx.EVT_MENU, self.onMonthWarehouseReport, menuMonthWarehouseReport)
        self.Bind(wx.EVT_MENU, self.onSetup, menuSetupConfig)
        self.Bind(wx.EVT_MENU, self.onOpenConfigFolder, menuOpenConfigFolder)
        self.Bind(wx.EVT_MENU, self.onReduceDatabaseSize, menuReduceDatabaseSize)
        self.Bind(wx.EVT_MENU, self.onBackup, menuBackup)
        self.Bind(wx.EVT_MENU, self.onResetConfig, menuResetConfig)

    def onRefresh(self, _):
        mv = cast("mainview.MainView", self.GetFrame())
        mv.state.refresh_all()

    def onAbout(self, _):
        wx.MessageBox(
            "Phần mềm phòng khám Simple Clinic\n"
            "V3.3.8\n"
            "Tác giả: Vương Kiến Thanh\n"
            "Email: thanhstardust@outlook.com",
            style=wx.OK | wx.CENTRE | wx.ICON_NONE,
        )

    def onExit(self, _):
        mv = cast("mainview.MainView", self.GetFrame())
        mv.Close()

    def onNewPatient(self, _):
        from ui.dialogs import NewPatientDialog

        mv = cast("mainview.MainView", self.GetFrame())
        NewPatientDialog(mv).ShowModal()

    def onFindPatient(self, _):
        from ui.dialogs import FindPatientDialog

        mv = cast("mainview.MainView", self.GetFrame())
        FindPatientDialog(mv).ShowModal()

    def onEditPatient(self, _):
        from ui.dialogs import EditPatientDialog

        mv = cast("mainview.MainView", self.GetFrame())
        page: wx.ListCtrl = mv.patient_book.GetPage(mv.patient_book.Selection)
        idx: int = page.GetFirstSelected()
        assert idx >= 0
        assert mv.state.patient is not None
        if EditPatientDialog(mv).ShowModal() == wx.ID_OK:
            page.EnsureVisible(idx)

    def onNewVisit(self, _):
        mv = cast("mainview.MainView", self.GetFrame())
        idx = mv.visit_list.GetFirstSelected()
        mv.visit_list.Select(idx, 0)

    def onInsertVisit(self, _):
        mv = cast("mainview.MainView", self.GetFrame())
        mv.savebtn.insert_visit()

    def onUpdateVisit(self, _):
        mv = cast("mainview.MainView", self.GetFrame())
        mv.savebtn.update_visit()

    def onDeleteVisit(self, _):
        if (
            wx.MessageBox(
                "Xác nhận?",
                "Xóa lượt khám",
                style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE,
            )
            == wx.YES
        ):
            mv = cast("mainview.MainView", self.GetFrame())
            v = mv.state.visit
            assert v is not None
            try:
                mv.connection.delete(Visit, v.id)
                wx.MessageBox(
                    "Xóa thành công", "OK", style=wx.OK_DEFAULT | wx.ICON_NONE
                )
                mv.state.refresh()
            except sqlite3.Error as error:
                wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onDeleteQueueList(self, _):
        if (
            wx.MessageBox(
                "Xác nhận?",
                "Xóa lượt chờ khám",
                style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE,
            )
            == wx.YES
        ):
            mv = cast("mainview.MainView", self.GetFrame())
            p = mv.state.patient
            assert p is not None
            assert mv.patient_book.GetSelection() == 0
            try:
                with mv.connection as con:
                    con.execute(
                        f"DELETE FROM {Queue.__tablename__} WHERE patient_id = {p.id}"
                    )
                    wx.MessageBox(
                        "Xóa thành công", "OK", style=wx.OK_DEFAULT | wx.ICON_NONE
                    )
                    mv.state.refresh()
            except Exception as error:
                wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onPrint(self, _):
        from misc.printer import PrintOut, printdata

        mv = cast("mainview.MainView", self.GetFrame())
        printout = PrintOut(mv)
        printdialog = wx.PrintDialog(mv)
        if printdialog.ShowModal() == wx.ID_OK:
            printdialog.PrintDialogData.SetPrintData(printdata)
            wx.Printer(printdialog.PrintDialogData).Print(mv, printout, False)

    def onPreview(self, _):
        from misc.printer import PrintOut, printdata

        mv = cast("mainview.MainView", self.GetFrame())
        printout = PrintOut(mv, preview=True)
        printdialogdata = wx.PrintDialogData(printdata)
        printpreview = wx.PrintPreview(printout, data=printdialogdata)
        printpreview.SetZoom(100)
        frame = wx.PreviewFrame(printpreview, mv)
        frame.Maximize()
        frame.Initialize()
        frame.Show()

    def onCopyVisitInfo(self, _):
        cb: wx.Clipboard = wx.TheClipboard  # type:ignore
        mv = cast("mainview.MainView", self.GetFrame())
        drug_list = mv.order_book.prescriptionpage.drug_list
        procedure_list = mv.order_book.procedurepage.procedure_list

        if cb.Open():
            intro = "{date}\n{name} ({gender}_{bd})".format(
                date=dt.datetime.now().strftime("%d/%m/%Y, %H:%M"),
                name=f"Tên: {mv.name.Value}",
                gender=f"Giới tính: {mv.gender.Value}",
                bd=f"Ngày sinh: {mv.birthdate.Value}",
            )
            diagnosis = f"Chẩn đoán: {mv.diagnosis.Value}"
            dl = "\n".join(
                [
                    "{}/ {} {} {}".format(
                        i + 1,
                        drug_list.GetItemText(i, 1),
                        drug_list.GetItemText(i, 5),
                        drug_list.GetItemText(i, 6),
                    )
                    for i in range(drug_list.ItemCount)
                ]
            )
            pl = "\n".join(
                "{}".format(procedure_list.GetItemText(i))
                for i in range(procedure_list.ItemCount)
            )
            if dl != "":
                dl = "\n".join([f"Thuốc {mv.days.Value} ngày:", dl])
            else:
                dl = "Không thuốc"
            if pl != "":
                pl = "\n".join(["Thủ thuật:", pl])
            recheck = f"Tái khám sau {mv.recheck.Value} ngày"
            follow = f"Dặn dò: {mv.follow.Value}"
            price = f"Tiền khám: {mv.price.Value}"
            t = "\n".join(
                (
                    intro,
                    diagnosis,
                    dl,
                    pl,
                    recheck,
                    follow,
                    price,
                )
            ).replace("\n\n", "\n")
            cb.SetData(wx.TextDataObject(t))
            cb.Close()

    def onWarehouse(self, _):
        from ui.dialogs import WarehouseDialog

        mv = cast("mainview.MainView", self.GetFrame())
        WarehouseDialog(mv).ShowModal()

    def onSample(self, _):
        from ui.dialogs import SampleDialog

        mv = cast("mainview.MainView", self.GetFrame())
        SampleDialog(mv).ShowModal()

    def onProcedure(self, _):
        from ui.dialogs import ProcedureDialog

        mv = cast("mainview.MainView", self.GetFrame())
        ProcedureDialog(mv).ShowModal()

    def onDayReport(self, _):
        from ui.dialogs import DayFinanceReportDialog
        from ui.generics import DatePickerDialog

        mv = cast("mainview.MainView", self.GetFrame())
        datepickerdialog = DatePickerDialog(mv)
        if datepickerdialog.ShowModal() == wx.ID_OK:
            DayFinanceReportDialog(mv, datepickerdialog.GetDate()).ShowModal()

    def onMonthReport(self, _):
        from ui.dialogs import MonthFinanceReportDialog
        from ui.generics import MonthPickerDialog

        mv = cast("mainview.MainView", self.GetFrame())
        monthpickerdialog = MonthPickerDialog(mv)
        if monthpickerdialog.ShowModal() == wx.ID_OK:
            MonthFinanceReportDialog(
                mv, monthpickerdialog.GetMonth(), monthpickerdialog.GetYear()
            ).ShowModal()

    def onMonthWarehouseReport(self, _):
        from ui.dialogs import MonthWarehouseReportDialog
        from ui.generics import MonthPickerDialog

        mv = cast("mainview.MainView", self.GetFrame())
        monthpickerdialog = MonthPickerDialog(mv)
        if monthpickerdialog.ShowModal() == wx.ID_OK:
            MonthWarehouseReportDialog(
                mv, monthpickerdialog.GetMonth(), monthpickerdialog.GetYear()
            ).ShowModal()

    def onSetup(self, _):
        from ui.dialogs import SetupDialog

        mv = cast("mainview.MainView", self.GetFrame())
        SetupDialog(mv).ShowModal()

    def onOpenConfigFolder(self, _):
        wx.LaunchDefaultApplication(APP_DIR)

    def onReduceDatabaseSize(self, _):
        mv = cast("mainview.MainView", self.GetFrame())
        connection = mv.connection
        pre = os.path.getsize(connection.path) >> 10
        connection.execute("VACUUM")
        connection.commit()
        post = os.path.getsize(connection.path) >> 10
        wx.MessageBox(
            f"Kích thước trước khi thu gọn: {pre} KB"
            f"Kích thước sau khi thu gọn: {post} KB",
            "Thu gọn dữ liệu",
            style=wx.OK_DEFAULT | wx.ICON_NONE,
        )

    def onBackup(self, _):
        bak = (
            os.path.realpath(MY_DATABASE_PATH)
            + dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            + ".bak"
        )
        if Path(MY_DATABASE_PATH).exists():
            shutil.copyfile(MY_DATABASE_PATH, bak)
            wx.MessageBox(
                f"Sao lưu thành công tại {bak}",
                "Sao lưu dữ liệu",
                style=wx.OK_DEFAULT | wx.ICON_NONE,
            )
        else:
            wx.MessageBox("Sao lưu không thành công", "Sao lưu dữ liệu")

    def onResetConfig(self, _):
        try:
            bak = CONFIG_PATH + dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".bak"
            shutil.copyfile(CONFIG_PATH, bak)
            shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)
            wx.MessageBox(
                f"Khôi phục cài đặt gốc thành công\nConfig cũ lưu tại {bak}",
                "Khôi phục cài đặt gốc",
                style=wx.OK_DEFAULT | wx.ICON_NONE,
            )
        except Exception as error:
            wx.MessageBox(f"Lỗi {error}", "Khôi phục cài đặt gốc")
