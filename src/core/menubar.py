from paths import APP_DIR, CONFIG_PATH
from db.db_class import *
from core import mainview
from core.dialogs import (
    FindPatientDialog,
    EditPatientDialog,
    NewPatientDialog,
    SetupDialog,
    WarehouseDialog,
    SampleDialog,
    ProcedureDialog,
    DatePickerDialog,
    DayReportDialog,
    MonthPickerDialog,
    MonthReportDialog
)

from core.printer import printdata, PrintOut
import subprocess
import wx
import shutil
import os.path
import sys
import os
import sqlite3
import json


class MyMenuBar(wx.MenuBar):

    def __init__(self):
        super().__init__()

        homeMenu = wx.Menu()
        homeMenu.Append(
            wx.ID_REFRESH,
            wx.GetStockLabel(wx.ID_REFRESH) + "\tF5"
        )
        homeMenu.Append(wx.ID_ABOUT)
        homeMenu.Append(wx.ID_EXIT)

        editMenu = wx.Menu()

        menuPatient = wx.Menu()
        menuPatient.Append(wx.ID_NEW, "Bệnh nhân mới\tCTRL+N")
        self.menuUpdatePatient: wx.MenuItem = menuPatient.Append(
            wx.ID_EDIT, "Cập nhật thông tin bệnh nhân\tCTRL+U")
        self.menuUpdatePatient.Enable(False)
        editMenu.AppendSubMenu(menuPatient, "Bệnh nhân")

        menuVisit = wx.Menu()
        self.menuNewVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Lượt khám mới")
        self.menuInsertVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Lưu lượt khám\tCTRL+S")
        self.menuUpdateVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Cập nhật lượt khám\tCTRL+S")
        self.menuDeleteVisit: wx.MenuItem = menuVisit.Append(
            wx.ID_ANY, "Xóa lượt khám cũ")

        self.menuNewVisit.Enable(False)
        self.menuInsertVisit.Enable(False)
        self.menuUpdateVisit.Enable(False)
        self.menuDeleteVisit.Enable(False)

        editMenu.AppendSubMenu(menuVisit, "Lượt khám")

        menuQueueList = wx.Menu()
        self.menuDeleteQueueList: wx.MenuItem = menuQueueList.Append(
            wx.ID_ANY, "Xóa lượt chờ khám")
        self.menuDeleteQueueList.Enable(False)
        editMenu.AppendSubMenu(menuQueueList, "Danh sách chờ")

        editMenu.AppendSeparator()
        editMenu.Append(wx.ID_OPEN, "Tìm bệnh nhân cũ\tCTRL+O")

        editMenu.AppendSeparator()
        self.menuPrint: wx.MenuItem = editMenu.Append(
            wx.ID_PRINT, "In\tCTRL+P")
        self.menuPreview: wx.MenuItem = editMenu.Append(
            wx.ID_PREVIEW, "Xem trước bản in\tCTRL+SHIFT+P")
        self.menuPrint.Enable(False)
        self.menuPreview.Enable(False)

        editMenu.AppendSeparator()
        self.menuCopyVisitInfo: wx.MenuItem = editMenu.Append(
            wx.ID_INFO, "Copy thông tin lượt khám vào Clipboard\tCTRL+SHIFT+C")

        manageMenu = wx.Menu()
        menuWarehouse: wx.MenuItem = manageMenu.Append(
            wx.ID_ANY, "Kho thuốc")
        menuSample: wx.MenuItem = manageMenu.Append(
            wx.ID_ANY, "Toa mẫu")
        menuProcedure: wx.MenuItem = manageMenu.Append(
            wx.ID_ANY, "Thủ thuật")
        menuReport = wx.Menu()
        menuDayReport = menuReport.Append(wx.ID_ANY, "Theo ngày")
        menuMonthReport = menuReport.Append(wx.ID_ANY, "Theo tháng")
        manageMenu.AppendSubMenu(menuReport, "Báo cáo")

        settingMenu = wx.Menu()
        menuSetup: wx.MenuItem = settingMenu.Append(
            wx.ID_ANY, "Cài đặt hệ thống")
        menuJSON: wx.MenuItem = settingMenu.Append(
            wx.ID_ANY, "Cài đặt qua JSON")
        menuOpenConfig: wx.MenuItem = settingMenu.Append(
            wx.ID_ANY, "Mở folder cài đặt + dữ liệu")

        self.Append(homeMenu, "&Home")
        self.Append(editMenu, "&Khám bệnh")
        self.Append(manageMenu, "&Quản lý")
        self.Append(settingMenu, "&Cài đặt")

        self.Bind(wx.EVT_MENU, self.onRefresh, id=wx.ID_REFRESH)
        self.Bind(wx.EVT_MENU, self.onAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, lambda e: self.Parent.Close(), id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onNewPatient, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.onFindPatient, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.onEditPatient, id=wx.ID_EDIT)
        self.Bind(wx.EVT_MENU, self.onNewVisit, self.menuNewVisit)
        self.Bind(wx.EVT_MENU, self.onInsertVisit, self.menuInsertVisit)
        self.Bind(wx.EVT_MENU, self.onUpdateVisit, self.menuUpdateVisit)
        self.Bind(wx.EVT_MENU, self.onDeleteVisit, self.menuDeleteVisit)
        self.Bind(wx.EVT_MENU, self.onDeleteQueueList,
                  self.menuDeleteQueueList)
        self.Bind(wx.EVT_MENU, self.onPrint, id=wx.ID_PRINT)
        self.Bind(wx.EVT_MENU, self.onPreview, id=wx.ID_PREVIEW)
        self.Bind(wx.EVT_MENU, self.onCopyVisitInfo, id=wx.ID_INFO)
        self.Bind(wx.EVT_MENU, self.onWarehouse, menuWarehouse)
        self.Bind(wx.EVT_MENU, self.onSample, menuSample)
        self.Bind(wx.EVT_MENU, self.onProcedure, menuProcedure)
        self.Bind(wx.EVT_MENU, self.onDayReport, menuDayReport)
        self.Bind(wx.EVT_MENU, self.onMonthReport, menuMonthReport)
        self.Bind(wx.EVT_MENU, self.onSetup, menuSetup)
        self.Bind(wx.EVT_MENU, self.onMenuJSON, menuJSON)
        self.Bind(wx.EVT_MENU, self.onOpenConfig, menuOpenConfig)

    def onRefresh(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        mv.state.refresh()

    def onAbout(self, e):
        wx.MessageBox(
            "Phần mềm phòng khám tại nhà\nTác giả: Vương Kiến Thanh\nEmail: thanhstardust@outlook.com",
            style=wx.OK | wx.CENTRE | wx.ICON_NONE)

    def onNewPatient(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        NewPatientDialog(mv).ShowModal()

    def onFindPatient(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        FindPatientDialog(mv).ShowModal()

    def onEditPatient(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        page: wx.ListCtrl = mv.patient_book.GetPage(mv.patient_book.Selection)
        idx: int = page.GetFirstSelected()
        assert idx >= 0
        assert mv.state.patient is not None
        if EditPatientDialog(mv).ShowModal() == wx.ID_OK:
            page.EnsureVisible(idx)

    def onNewVisit(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        idx = mv.visit_list.GetFirstSelected()
        mv.visit_list.Select(idx, 0)

    def onInsertVisit(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        mv.savebtn.insert_visit()

    def onUpdateVisit(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        mv.savebtn.update_visit()

    def onDeleteVisit(self, e):
        if wx.MessageBox("Xác nhận?", "Xóa lượt khám", style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE) == wx.YES:
            mv: 'mainview.MainView' = self.GetFrame()
            v = mv.state.visit
            p = mv.state.patient
            assert v is not None
            assert p is not None
            try:
                mv.con.delete(Visit, v.id)
                wx.MessageBox("Xóa thành công", "OK")
                mv.state.visitlist = mv.state.get_visits_by_patient_id(p.id)
                mv.state.visit = None
            except sqlite3.Error as error:
                wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onDeleteQueueList(self, e):
        if wx.MessageBox("Xác nhận?", "Xóa lượt chờ khám", style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE) == wx.YES:
            mv: 'mainview.MainView' = self.GetFrame()
            p = mv.state.patient
            assert p is not None
            assert mv.patient_book.GetSelection() == 0
            try:
                with mv.con as con:
                    con.execute(
                        f"DELETE FROM {QueueList.table_name} WHERE patient_id = {p.id}")
                    wx.MessageBox("Xóa thành công", "OK")
                    mv.state.refresh()
            except Exception as error:
                wx.MessageBox("Lỗi không xóa được\n" + str(error), "Lỗi")

    def onPrint(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        printout = PrintOut(mv)
        wx.Printer(wx.PrintDialogData(printdata)).Print(self, printout, True)

    def onPreview(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        printout = PrintOut(mv)
        printdialogdata = wx.PrintDialogData(printdata)
        printpreview = wx.PrintPreview(printout, data=printdialogdata)
        printpreview.SetZoom(85)
        frame = wx.PreviewFrame(printpreview, mv)
        frame.Maximize()
        frame.Initialize()
        frame.Show()

    def onCopyVisitInfo(self, e):
        cb: wx.Clipboard = wx.TheClipboard  # type:ignore
        mv: 'mainview.MainView' = self.GetFrame()
        if cb.Open():
            name = f"Tên: {mv.name.GetValue()}"
            bd = f"Ngày sinh: {mv.birthdate.GetValue()}"
            diagnosis = f"Chẩn đoán: {mv.diagnosis.GetValue()}"
            dl = '\n'.join(tuple(
                "{}/ {} {} ngày {} lần, lần {} {} = {} {}".format(
                    i + 1,
                    d.name,
                    d.usage,
                    d.times,
                    d.dose,
                    d.usage_unit,
                    d.quantity,
                    d.sale_unit or d.usage_unit)
                for i, d in enumerate(
                    mv.order_book.page0.drug_list.d_list)))
            prl = '\n'.join(tuple(
                "{}/ {} x {}".format(
                    i + 1,
                    p[1],
                    p[2]
                )
                for i, p in enumerate(
                    mv.order_book.page1.procedurelistctrl.summary())))
            price = f"Tiền khám: {mv.price.GetValue()}"
            t = '\n'.join([
                name,
                bd,
                diagnosis,
                "Thuốc:",
                dl,
                "Thủ thuật:",
                prl,
                price
            ])
            cb.SetData(wx.TextDataObject(t))
            cb.Close()

    def onWarehouse(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        WarehouseDialog(mv).ShowModal()

    def onSample(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        SampleDialog(mv).ShowModal()

    def onProcedure(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        ProcedureDialog(mv).ShowModal()

    def onDayReport(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        datepickerdialog = DatePickerDialog(mv)
        if datepickerdialog.ShowModal() == wx.ID_OK:
            DayReportDialog(
                mv, datepickerdialog.GetDate()).ShowModal()

    def onMonthReport(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        monthpickerdialog = MonthPickerDialog(mv)
        if monthpickerdialog.ShowModal() == wx.ID_OK:
            MonthReportDialog(
                mv,
                monthpickerdialog.GetMonth(),
                monthpickerdialog.GetYear()
            ).ShowModal()

    def onSetup(self, e):
        mv: 'mainview.MainView' = self.GetFrame()
        SetupDialog(mv).ShowModal()

    def onMenuJSON(self, e):
        def openjson():
            if sys.platform == "win32":
                os.startfile(CONFIG_PATH, "edit")
            elif sys.platform == "linux":
                prog = shutil.which("gedit") or \
                    shutil.which("xed") or \
                    shutil.which("kwrite") or \
                    "xdg-open"
                subprocess.run([prog, CONFIG_PATH])
            elif sys.platform == "darwin":
                subprocess.run(['open', '-e', CONFIG_PATH])

        mv: 'mainview.MainView' = self.GetFrame()
        if mv.sample:
            wx.MessageBox("Đã lưu cài đặt", "Cài đặt")
        else:
            while True:
                openjson()
                mv: 'mainview.MainView' = self.GetFrame()
                try:
                    mv.config = json.load(
                        open(CONFIG_PATH, "r", encoding="utf-8"))
                    wx.MessageBox("Đã lưu cài đặt", "Cài đặt")
                    break
                except json.JSONDecodeError as error:
                    wx.MessageBox(f"Lỗi JSON\n{error}", "Lỗi")

    def onOpenConfig(self, e):
        if sys.platform == "win32":
            os.startfile(APP_DIR)
        elif sys.platform == "linux":
            subprocess.run(["xdg-open", APP_DIR])
        elif sys.platform == "darwin":
            subprocess.run(["start", APP_DIR])
