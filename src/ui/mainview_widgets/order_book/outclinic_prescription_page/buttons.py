import wx

from ui.mainview_widgets.order_book.base_page import BaseAddButton, BaseDeleteButton
from ui.mainview_widgets.order_book.outclinic_prescription_page import page


class AddDrugButton(BaseAddButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent: page.OutClinicPrescriptionPage


class DeleteDrugButton(BaseDeleteButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent: page.OutClinicPrescriptionPage
