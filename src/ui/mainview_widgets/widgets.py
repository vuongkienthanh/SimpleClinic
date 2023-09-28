from itertools import chain

import wx

from misc import num_to_str_price, str_to_int_price, vn_weekdays
from ui import mainview as mv
from ui.generics import NumberTextCtrl, DecimalSpinCtrl


class WeightCtrl(DecimalSpinCtrl):
    def __init__(self, mv: "mv.MainView", **kwargs):
        super().__init__(mv, **kwargs)
        self.Disable()

    def GetWeight(self) -> int:
        return int(self.Value * 10)

    def SetWeight(self, value: int):
        super().SetValue(value / 10)


class TemperatureCtrl(DecimalSpinCtrl):
    def __init__(self, mv: "mv.MainView", **kwargs):
        super().__init__(mv, **kwargs)
        self.Disable()

    def GetTemperature(self) -> int | None:
        match self.Value:
            case 0:
                return None
            case v:
                return int(v * 10)

    def SetTemperature(self, value: int|None):
        match value:
            case int(v):
                super().SetValue(v / 10)
            case None:
                super().SetValue(0)

class HeightCtrl(wx.SpinCtrl):
    def __init__(self, mv: "mv.MainView", **kwargs):
        super().__init__(mv, **kwargs)
        self.Disable()

    def GetHeight(self) -> int | None:
        match self.Value:
            case 0:
                return None
            case v:
                return int(v)

    def SetHeight(self, value: int|None):
        match value:
            case int(v):
                super().SetValue(v)
            case None:
                super().SetValue(0)

class DaysCtrl(wx.SpinCtrl):
    """
    + RecheckCtrl Value
    - DrugList quantity
    """

    def __init__(self, mv: "mv.MainView", **kwargs):
        super().__init__(
            mv,
            style=wx.SP_ARROW_KEYS,
            initial=mv.config.default_days_for_prescription,
            **kwargs,
        )
        self.mv = mv
        self.SetRange(0, 100)
        self.Disable()
        self.Bind(wx.EVT_SPINCTRL, self.onSpin)

    def onSpin(self, e: wx.SpinEvent):
        self.set_recheck_and_curr_drug_quantity(e)
        self.mv.updatequantitybtn.Enable()

    def set_recheck_and_curr_drug_quantity(self, e: wx.SpinEvent):
        self.mv.recheck.SetValue(e.GetPosition())
        self.mv.recheck_weekday.SetLabel(vn_weekdays(e.GetPosition()))
        if self.mv.order_book.prescriptionpage.check_wh_do_ti_filled():
            self.mv.order_book.prescriptionpage.quantity.FetchQuantity()


class DaysCtrlWithAutoChangePrescriptionQuantity(DaysCtrl):
    """
    + RecheckCtrl Value
    + DrugList quantity
    """

    def onSpin(self, e: wx.SpinEvent):
        super().set_recheck_and_curr_drug_quantity(e)
        self.mv.updatequantitybtn.update_quantity()


class RecheckCtrl(wx.SpinCtrl):
    "Independant of DaysCtrl"

    def __init__(self, mv: "mv.MainView", **kwargs):
        super().__init__(
            mv,
            style=wx.SP_ARROW_KEYS,
            initial=mv.config.default_days_for_prescription,
            **kwargs,
        )
        self.SetRange(0, 100)
        self.Disable()


class PriceCtrl(NumberTextCtrl):
    """A TextCtrl with proper Vietnamese currency format
    with default set according to config"""

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(parent, **kwargs)
        self.mv = parent
        self.Clear()

    def FetchPrice(self):
        state = self.mv.state
        price: int = self.mv.config.checkup_price
        price += sum(
            state.all_warehouse[item.warehouse_id].sale_price * item.quantity
            for item in chain(state.old_linedrug_list, state.new_linedrug_list)
            if not item.outclinic
        )
        price += sum(
            state.all_procedure[item.procedure_id].price
            for item in chain(
                state.old_lineprocedure_list, state.new_lineprocedure_list
            )
        )
        self.ChangeValue(num_to_str_price(price))

    def Clear(self):
        self.ChangeValue(num_to_str_price(self.mv.config.checkup_price))

    def SetPrice(self, price: int):
        self.ChangeValue(num_to_str_price(price))

    def GetPrice(self) -> int:
        return str_to_int_price(self.Value)


class Follow(wx.ComboBox):
    """A Combobox which is able to:
    - use only the `key` in `follow_choices_dict` and `follow_choices_list`
    """

    def __init__(self, mv: "mv.MainView", **kwargs):
        super().__init__(
            mv,
            style=wx.CB_DROPDOWN,
            choices=list(
                chain(
                    mv.config.follow_choices_dict.keys(), mv.config.follow_choices_list
                )
            ),
            **kwargs,
        )
        self.mv = mv
        self.SetDefault()

    def expand_when_print(self) -> str:
        "expand `key` -> `key: value` in config"
        k = self.Value.strip()
        if k in self.mv.config.follow_choices_dict.keys():
            return f"{k}: {self.mv.config.follow_choices_dict[k]}"
        else:
            return k

    def SetDefault(self):
        "use when visit is `None`"
        self.SetSelection(0)
