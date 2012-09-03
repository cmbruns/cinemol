'''
Created on Aug 9, 2012

@author: cmbruns
'''

from cinemol.imposter import SphereImposterArray, Sphere2Array, AtomGLAttributes, atom_attributes


class BondLines:
    def __init__(self):
        self.is_initialized = False
    
    def clear(self):
        pass # TODO
    
    def init_gl(self):
        self.is_initialized = True
        
    def paint_gl(self, camera=None, renderer=None):
        if not self.is_initialized:
            self.init_gl()
        pass # TODO


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
        
    def set_radius(self, radius):
        if radius == 0.0: # use vdw
            self.imposters.radius_offset = 0.0
            self.imposters.radius_scale = 1.0
        else:
            self.imposters.radius_offset = radius
            self.imposters.radius_scale = 0.0
            
        
    def update_atom_colors(self):
        self.imposters.update_atom_colors()
