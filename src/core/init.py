from other_func import get_config
import wx

config = get_config()

mainview_background_color = wx.Colour(
    *config['background_color']['mainview'])
patient_list_background_color = wx.Colour(
    *config['background_color']['patient_list'])
visit_list_background_color = wx.Colour(
    *config['background_color']['visit_list'])
name_background_color = wx.Colour(
    *config['background_color']['name'])
gender_background_color = wx.Colour(
    *config['background_color']['gender'])
birthdate_background_color = wx.Colour(
    *config['background_color']['birthdate'])
age_background_color = wx.Colour(
    *config['background_color']['age'])
diagnosis_background_color = wx.Colour(
    *config['background_color']['diagnosis'])
phone_background_color = wx.Colour(
    *config['background_color']['phone'])
address_background_color = wx.Colour(
    *config['background_color']['address'])
price_background_color = wx.Colour(
    *config['background_color']['price'])
drug_list_background_color = wx.Colour(
    *config['background_color']['drug_list'])
procedure_list_background_color = wx.Colour(
    *config['background_color']['procedure_list'])
past_history_background_color = wx.Colour(
    *config['background_color']['past_history'])
visit_note_background_color = wx.Colour(
    *config['background_color']['visit_note'])
weight_background_color = wx.Colour(
    *config['background_color']['weight'])
days_background_color = wx.Colour(
    *config['background_color']['days'])
drug_picker_background_color = wx.Colour(
    *config['background_color']['drug_picker'])
drug_times_background_color = wx.Colour(
    *config['background_color']['drug_times'])
drug_dose_background_color = wx.Colour(
    *config['background_color']['drug_dose'])
drug_quantity_background_color = wx.Colour(
    *config['background_color']['drug_quantity'])
drug_note_background_color = wx.Colour(
    *config['background_color']['drug_note'])
recheck_background_color = wx.Colour(
    *config['background_color']['recheck'])
follow_background_color = wx.Colour(
    *config['background_color']['follow'])
procedure_picker_background_color = wx.Colour(
    *config['background_color']['procedure_picker'])

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
