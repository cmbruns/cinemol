'''
Created on Aug 4, 2012

@author: cmbruns
'''

class Element(object):
    # In nanometers!
    def __init__(self, atomic_number, symbol, name, mass=10.0, vdw_radius=0.20):
        self.atomic_number = atomic_number
        self.symbol = symbol
        self.name = name


hydrogen   = Element( 1,  "H", "hydrogen")
carbon     = Element( 6,  "C", "carbon")
nitrogen   = Element( 7,  "N", "nitrogen")
oxygen     = Element( 8,  "O", "oxygen")
phosphorus = Element(15,  "P", "phosphorus")
sulfur     = Element(16,  "S", "sulfur")
iron       = Element(26, "Fe", "iron")

unknown    = Element( 0, "??", "unknown element")
