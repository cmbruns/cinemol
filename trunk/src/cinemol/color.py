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

AliceBlue = from_hex("#F0F8FF")
AntiqueWhite = from_hex("#FAEBD7")
Aqua = from_hex("#00FFFF")
Aquamarine = from_hex("#7FFFD4")
Azure = from_hex("#F0FFFF")
Beige = from_hex("#F5F5DC")
Bisque = from_hex("#FFE4C4")
Black = from_hex("#000000")
BlanchedAlmond = from_hex("#FFEBCD")
Blue = from_hex("#0000FF")
BlueViolet = from_hex("#8A2BE2")
Brown = from_hex("#A52A2A")
BurlyWood = from_hex("#DEB887")
CadetBlue = from_hex("#5F9EA0")
Chartreuse = from_hex("#7FFF00")
Chocolate = from_hex("#D2691E")
Coral = from_hex("#FF7F50")
CornflowerBlue = from_hex("#6495ED")
Cornsilk = from_hex("#FFF8DC")
Crimson = from_hex("#DC143C")
Cyan = from_hex("#00FFFF")
DarkBlue = from_hex("#00008B")
DarkCyan = from_hex("#008B8B")
DarkGoldenrod = from_hex("#B8860B")
DarkGray = from_hex("#A9A9A9")
DarkGrey = DarkGray
DarkGreen = from_hex("#006400")
DarkKhaki = from_hex("#BDB76B")
DarkMagenta = from_hex("#8B008B")
DarkOliveGreen = from_hex("#556B2F")
DarkOrange = from_hex("#FF8C00")
DarkOrchid = from_hex("#9932CC")
DarkRed = from_hex("#8B0000")
DarkSalmon = from_hex("#E9967A")
DarkSeaGreen = from_hex("#8FBC8F")
DarkSlateBlue = from_hex("#483D8B")
DarkSlateGray = from_hex("#2F4F4F")
DarkSlateGrey = DarkSlateGray
DarkTurquoise = from_hex("#00CED1")
DarkViolet = from_hex("#9400D3")
DeepPink = from_hex("#FF1493")
DeepSkyBlue = from_hex("#00BFFF")
DimGray = from_hex("#696969")
DimGrey = DimGray
DodgerBlue = from_hex("#1E90FF")
FireBrick = from_hex("#B22222")
FloralWhite = from_hex("#FFFAF0")
ForestGreen = from_hex("#228B22")
Fuchsia = from_hex("#FF00FF")
Gainsboro = from_hex("#DCDCDC")
GhostWhite = from_hex("#F8F8FF")
Gold = from_hex("#FFD700")
Goldenrod = from_hex("#DAA520")
Gray = from_hex("#808080")
Grey = Gray
Green = from_hex("#008000")
GreenYellow = from_hex("#ADFF2F")
Honeydew = from_hex("#F0FFF0")
HotPink = from_hex("#FF69B4")
IndianRed = from_hex("#CD5C5C")
Indigo = from_hex("#4B0082")
Ivory = from_hex("#FFFFF0")
Khaki = from_hex("#F0E68C")
Lavender = from_hex("#E6E6FA")
LavenderBlush = from_hex("#FFF0F5")
LawnGreen = from_hex("#7CFC00")
LemonChiffon = from_hex("#FFFACD")
LightBlue = from_hex("#ADD8E6")
LightCoral = from_hex("#F08080")
LightCyan = from_hex("#E0FFFF")
LightGoldenrodYellow = from_hex("#FAFAD2")
LightGreen = from_hex("#90EE90")
LightGray = from_hex("#D3D3D3")
LightGrey = LightGray
LightPink = from_hex("#FFB6C1")
LightSalmon = from_hex("#FFA07A")
LightSeaGreen = from_hex("#20B2AA")
LightSkyBlue = from_hex("#87CEFA")
LightSlateGray = from_hex("#778899")
LightSlateGrey = LightSlateGray
LightSteelBlue = from_hex("#B0C4DE")
LightYellow = from_hex("#FFFFE0")
Lime = from_hex("#00FF00")
LimeGreen = from_hex("#32CD32")
Linen = from_hex("#FAF0E6")
Magenta = from_hex("#FF00FF")
Maroon = from_hex("#800000")
MediumAquamarine = from_hex("#66CDAA")
MediumBlue = from_hex("#0000CD")
MediumOrchid = from_hex("#BA55D3")
MediumPurple = from_hex("#9370DB")
MediumSeaGreen = from_hex("#3CB371")
MediumSlateBlue = from_hex("#7B68EE")
MediumSpringGreen = from_hex("#00FA9A")
MediumTurquoise = from_hex("#48D1CC")
MediumVioletRed = from_hex("#C71585")
MidnightBlue = from_hex("#191970")
MintCream = from_hex("#F5FFFA")
MistyRose = from_hex("#FFE4E1")
Moccasin = from_hex("#FFE4B5")
NavajoWhite = from_hex("#FFDEAD")
Navy = from_hex("#000080")
OldLace = from_hex("#FDF5E6")
Olive = from_hex("#808000")
OliveDrab = from_hex("#6B8E23")
Orange = from_hex("#FFA500")
OrangeRed = from_hex("#FF4500")
Orchid = from_hex("#DA70D6")
PaleGoldenrod = from_hex("#EEE8AA")
PaleGreen = from_hex("#98FB98")
PaleTurquoise = from_hex("#AFEEEE")
PaleVioletRed = from_hex("#DB7093")
PapayaWhip = from_hex("#FFEFD5")
PeachPuff = from_hex("#FFDAB9")
Peru = from_hex("#CD853F")
Pink = from_hex("#FFC0CB")
Plum = from_hex("#DDA0DD")
PowderBlue = from_hex("#B0E0E6")
Purple = from_hex("#800080")
Red = from_hex("#FF0000")
RosyBrown = from_hex("#BC8F8F")
RoyalBlue = from_hex("#4169E1")
SaddleBrown = from_hex("#8B4513")
Salmon = from_hex("#FA8072")
SandyBrown = from_hex("#F4A460")
SeaGreen = from_hex("#2E8B57")
Seashell = from_hex("#FFF5EE")
Sienna = from_hex("#A0522D")
Silver = from_hex("#C0C0C0")
SkyBlue = from_hex("#87CEEB")
SlateBlue = from_hex("#6A5ACD")
SlateGray = from_hex("#708090")
SlateGrey = SlateGray
Snow = from_hex("#FFFAFA")
SpringGreen = from_hex("#00FF7F")
SteelBlue = from_hex("#4682B4")
Tan = from_hex("#D2B48C")
Teal = from_hex("#008080")
Thistle = from_hex("#D8BFD8")
Tomato = from_hex("#FF6347")
Turquoise = from_hex("#40E0D0")
Violet = from_hex("#EE82EE")
Wheat = from_hex("#F5DEB3")
White = from_hex("#FFFFFF")
WhiteSmoke = from_hex("#F5F5F5")
Yellow = from_hex("#FFFF00")
YellowGreen = from_hex("#9ACD32")

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
