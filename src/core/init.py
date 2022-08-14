from other_func import get_config
import wx

config = get_config()

mainview_background_color = wx.Colour(
    *config['mainview_background_color'])
patient_list_background_color = wx.Colour(
    *config['patient_list_background_color'])
visit_list_background_color = wx.Colour(
    *config['visit_list_background_color'])
name_background_color = wx.Colour(
    *config['name_background_color'])
gender_background_color = wx.Colour(
    *config['gender_background_color'])
birthdate_background_color = wx.Colour(
    *config['birthdate_background_color'])
age_background_color = wx.Colour(
    *config['age_background_color'])
diagnosis_background_color = wx.Colour(
    *config['diagnosis_background_color'])
phone_background_color = wx.Colour(
    *config['phone_background_color'])
address_background_color = wx.Colour(
    *config['address_background_color'])
price_background_color = wx.Colour(
    *config['price_background_color'])
drug_list_background_color = wx.Colour(
    *config['drug_list_background_color'])
procedure_list_background_color = wx.Colour(
    *config['procedure_list_background_color'])
past_history_background_color = wx.Colour(
    *config['past_history_background_color'])
visit_note_background_color = wx.Colour(
    *config['visit_note_background_color'])
weight_background_color = wx.Colour(
    *config['weight_background_color'])
days_background_color = wx.Colour(
    *config['days_background_color'])
drug_picker_background_color = wx.Colour(
    *config['drug_picker_background_color'])
drug_times_background_color = wx.Colour(
    *config['drug_times_background_color'])
drug_dose_background_color = wx.Colour(
    *config['drug_dose_background_color'])
drug_quantity_background_color = wx.Colour(
    *config['drug_quantity_background_color'])
drug_note_background_color = wx.Colour(
    *config['drug_note_background_color'])
recheck_background_color = wx.Colour(
    *config['recheck_background_color'])
follow_background_color = wx.Colour(
    *config['follow_background_color'])
procedure_picker_background_color = wx.Colour(
    *config['procedure_picker_background_color'])

# some size
w: tuple[int, int] = wx.DisplaySize()[0]


def size(p):
    return round(w*p*config['listctrl_header_scale'])


def tsize(p):
    return (size(p), -1)


# keycode
# back, del, home, end, left,right
k_special: tuple[int, ...] = (8, 314, 316, 127, 313, 312)
k_number: tuple[int, ...] = tuple(range(48, 58))
k_decimal: tuple[int] = (46,)
k_hash: tuple[int] = (35,)
k_slash: tuple[int] = (47,)
k_tab: tuple[int] = (9,)
