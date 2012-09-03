'''
Created on Aug 9, 2012

@author: cmbruns
'''

from cinemol.imposter import SphereImposterArray, Sphere2Array, AtomGLAttributes, atom_attributes


class BondLines:
    def __init__(self, atoms):
        pass


class SpaceFilling(object):
    def __init__(self):
        # self.imposters = SphereImposterArray(atoms)
        self.imposters = Sphere2Array(atom_attributes)
        
    def add_atoms(self, atoms):
        self.imposters.add_atoms(atoms)
        
    def clear(self):
        self.imposters.clear()
        
    def init_gl(self):
        self.imposters.init_gl()

    def paint_gl(self, camera=None, renderer=None):
        self.imposters.paint_gl(camera, renderer)

    def remove_atoms(self, atoms):
        self.imposters.remove_atoms(atoms)
        
    def update_atom_colors(self):
        self.imposters.update_atom_colors()
