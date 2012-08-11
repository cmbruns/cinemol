'''
Created on Aug 9, 2012

@author: cmbruns
'''

from cinemol.imposter import SphereImposterArray

class BondLines:
    pass

class SpaceFilling:
    def __init__(self, atoms):
        self.imposters = SphereImposterArray(atoms)
        
    def init_gl(self):
        self.imposters.init_gl()
        
    def paint_gl(self):
        self.imposters.paint_gl()
        
    def update_atom_colors(self):
        self.imposters.update_atom_colors()
