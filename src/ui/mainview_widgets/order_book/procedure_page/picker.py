from db import Procedure
from misc import num_to_str_price
from ui.generics.widgets import DatabaseChoice

from . import page


class ProcedurePicker(DatabaseChoice):
    def __init__(self, parent: "page.ProcedurePage"):
        super().__init__(
            parent,
            choices=[],
        )

    def append_ui(self, item: Procedure):
        self.Append(f"{item.name} ({num_to_str_price(item.price)})")
