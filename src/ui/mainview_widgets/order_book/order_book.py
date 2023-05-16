from .prescription_page import PrescriptionPage
from .procedure_page import ProcedurePage
from ui import mainview

import wx


class OrderBook(wx.Notebook):
    """Container for PrescriptionPage"""

    def __init__(self, parent: "mainview.MainView"):
        super().__init__(parent)
        self.mv = parent
        self.prescriptionpage = PrescriptionPage(self)
        self.procedurepage = ProcedurePage(self)
        self.AddPage(page=self.prescriptionpage, text="Toa thuốc", select=True)
        self.AddPage(page=self.procedurepage, text="Thủ thuật")
