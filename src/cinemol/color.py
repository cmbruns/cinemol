'''
Created on Aug 4, 2012

@author: cmbruns
'''

import cinemol.element as element
import math


class Color(list):
    """
    Color is a list of three sRGB color components.
    With an additional "linear" member with a gamma of 2.2 applied.
    """
    def __init__(self, components):
        self[:] = components # sRGB scale (brighter)
        self.linear = list() # linear scale for opengl (darker)
        for x in self:
            self.linear.append(math.pow(x, 2.2))

def from_hex(hex_string):
    shift = 8
    if len(hex_string) < 6:
        shift = 4 # e.g. "#fff"
    fmax = math.pow(2.0, shift) - 1.0
    imax = int(fmax + 0.5)
    hex_string = hex_string.replace("#", "0x")
    i = int(hex_string, 16)
    blue = (imax & i) / fmax
    i = i >> shift
    green = (imax & i) / fmax
    i = i >> shift
    red = (imax & i) / fmax
    return Color([red, green, blue])


# RGB primaries
black   = Color([0.0, 0.0, 0.0])
blue    = Color([0.0, 0.0, 1.0])
cyan    = Color([0.0, 1.0, 1.0])
# green   = Color([0.0, 1.0, 0.0]) # conflicts with HTML green
gray    = Color([0.5, 0.5, 0.5])
magenta = Color([1.0, 0.0, 1.0])
red     = Color([1.0, 0.0, 0.0])
white   = Color([1.0, 1.0, 1.0])
yellow  = Color([1.0, 1.0, 0.0])

# HTML 4.01 standard has only 16 "official" colors
# Several of those are the primary colors above
aqua    = cyan
fuchsia = magenta
green   = from_hex("#008000")
grey    = gray
lime    = from_hex("#00FF00")
maroon  = from_hex("#800000")
navy    = from_hex("#000080")
olive   = from_hex("#808000")
purple  = from_hex("#800080")
silver  = from_hex("#C0C0C0")
teal    = from_hex("#008080")

alice_blue = from_hex("#f0f8ff")
antique_white = from_hex("#faebd7")
aqua = from_hex("#00ffff")
aquamarine = from_hex("#7fffd4")
azure = from_hex("#f0ffff")
beige = from_hex("#f5f5dc")
bisque = from_hex("#ffe4c4")
black = from_hex("#000000")
blanched_almond = from_hex("#ffebcd")
blue = from_hex("#0000ff")
blue_violet = from_hex("#8a2be2")
brown = from_hex("#a52a2a")
burly_wood = from_hex("#deb887")
cadet_blue = from_hex("#5f9ea0")
chartreuse = from_hex("#7fff00")
chocolate = from_hex("#d2691e")
coral = from_hex("#ff7f50")
cornflower_blue = from_hex("#6495ed")
cornsilk = from_hex("#fff8dc")
crimson = from_hex("#dc143c")
cyan = from_hex("#00ffff")
dark_blue = from_hex("#00008b")
dark_cyan = from_hex("#008b8b")
dark_goldenrod = from_hex("#b8860b")
dark_gray = from_hex("#a9a9a9")
dark_grey = dark_gray
dark_green = from_hex("#006400")
dark_khaki = from_hex("#bdb76b")
dark_magenta = from_hex("#8b008b")
dark_olive_green = from_hex("#556b2f")
dark_orange = from_hex("#ff8c00")
dark_orchid = from_hex("#9932cc")
dark_red = from_hex("#8b0000")
dark_salmon = from_hex("#e9967a")
dark_sea_green = from_hex("#8fbc8f")
dark_slate_blue = from_hex("#483d8b")
dark_slate_gray = from_hex("#2f4f4f")
dark_slate_grey = dark_slate_gray
dark_turquoise = from_hex("#00ced1")
dark_violet = from_hex("#9400d3")
deep_pink = from_hex("#ff1493")
deep_sky_blue = from_hex("#00bfff")
dim_gray = from_hex("#696969")
dim_grey = dim_gray
dodger_blue = from_hex("#1e90ff")
fire_brick = from_hex("#b22222")
floral_white = from_hex("#fffaf0")
forest_green = from_hex("#228b22")
fuchsia = from_hex("#ff00ff")
gainsboro = from_hex("#dcdcdc")
ghost_white = from_hex("#f8f8ff")
gold = from_hex("#ffd700")
goldenrod = from_hex("#daa520")
gray = from_hex("#808080")
grey = gray
green = from_hex("#008000")
green_yellow = from_hex("#adff2f")
honeydew = from_hex("#f0fff0")
hot_pink = from_hex("#ff69b4")
indian_red = from_hex("#cd5c5c")
indigo = from_hex("#4b0082")
ivory = from_hex("#fffff0")
khaki = from_hex("#f0e68c")
lavender = from_hex("#e6e6fa")
lavender_blush = from_hex("#fff0f5")
lawn_green = from_hex("#7cfc00")
lemon_chiffon = from_hex("#fffacd")
light_blue = from_hex("#add8e6")
light_coral = from_hex("#f08080")
light_cyan = from_hex("#e0ffff")
light_goldenrod_yellow = from_hex("#fafad2")
light_green = from_hex("#90ee90")
light_gray = from_hex("#d3d3d3")
light_grey = light_gray
light_pink = from_hex("#ffb6c1")
light_salmon = from_hex("#ffa07a")
light_sea_green = from_hex("#20b2aa")
light_sky_blue = from_hex("#87cefa")
light_slate_gray = from_hex("#778899")
light_slate_grey = light_slate_gray
light_steel_blue = from_hex("#b0c4de")
light_yellow = from_hex("#ffffe0")
lime = from_hex("#00ff00")
lime_green = from_hex("#32cd32")
linen = from_hex("#faf0e6")
magenta = from_hex("#ff00ff")
maroon = from_hex("#800000")
medium_aquamarine = from_hex("#66cdaa")
medium_blue = from_hex("#0000cd")
medium_orchid = from_hex("#ba55d3")
medium_purple = from_hex("#9370db")
medium_sea_green = from_hex("#3cb371")
medium_slate_blue = from_hex("#7b68ee")
medium_spring_green = from_hex("#00fa9a")
medium_turquoise = from_hex("#48d1cc")
medium_violet_red = from_hex("#c71585")
midnight_blue = from_hex("#191970")
mint_cream = from_hex("#f5fffa")
misty_rose = from_hex("#ffe4e1")
moccasin = from_hex("#ffe4b5")
navajo_white = from_hex("#ffdead")
navy = from_hex("#000080")
old_lace = from_hex("#fdf5e6")
olive = from_hex("#808000")
olive_drab = from_hex("#6b8e23")
orange = from_hex("#ffa500")
orange_red = from_hex("#ff4500")
orchid = from_hex("#da70d6")
pale_goldenrod = from_hex("#eee8aa")
pale_green = from_hex("#98fb98")
pale_turquoise = from_hex("#afeeee")
pale_violet_red = from_hex("#db7093")
papaya_whip = from_hex("#ffefd5")
peach_puff = from_hex("#ffdab9")
peru = from_hex("#cd853f")
pink = from_hex("#ffc0cb")
plum = from_hex("#dda0dd")
powder_blue = from_hex("#b0e0e6")
purple = from_hex("#800080")
red = from_hex("#ff0000")
rosy_brown = from_hex("#bc8f8f")
royal_blue = from_hex("#4169e1")
saddle_brown = from_hex("#8b4513")
salmon = from_hex("#fa8072")
sandy_brown = from_hex("#f4a460")
sea_green = from_hex("#2e8b57")
seashell = from_hex("#fff5ee")
sienna = from_hex("#a0522d")
silver = from_hex("#c0c0c0")
sky_blue = from_hex("#87ceeb")
slate_blue = from_hex("#6a5acd")
slate_gray = from_hex("#708090")
slate_grey = slate_gray
snow = from_hex("#fffafa")
spring_green = from_hex("#00ff7f")
steel_blue = from_hex("#4682b4")
tan = from_hex("#d2b48c")
teal = from_hex("#008080")
thistle = from_hex("#d8bfd8")
tomato = from_hex("#ff6347")
turquoise = from_hex("#40e0d0")
violet = from_hex("#ee82ee")
wheat = from_hex("#f5deb3")
white = from_hex("#ffffff")
white_smoke = from_hex("#f5f5f5")
yellow = from_hex("#ffff00")
yellow_green = from_hex("#9acd32")

class ColorByElement(object):
    "Color atoms by the atom type"
    def __init__(self):
        self.default_color = from_hex("#FF1493")
        self._colors = dict()
        # Rasmol CPK colors
        self._add(element.hydrogen, white)
        self._add(element.carbon, from_hex("#C8C8C8"))
        self._add(element.nitrogen, from_hex("#8F8FFF"))
        self._add(element.oxygen, from_hex('#F00000'))
        self._add(element.sulfur, from_hex("#FFC832"))
        
    def _add(self, e, color):
        self._colors[e.atomic_number] = color
        
    def color(self, atom):
        return self._colors.get(atom.element.atomic_number, self.default_color)
