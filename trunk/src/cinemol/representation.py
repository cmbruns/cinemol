'''
Created on Aug 9, 2012

@author: cmbruns
'''

from cinemol.imposter import SphereImposterArray, Sphere2Array, AtomGLAttributes


class BondLines:
    def __init__(self, atoms):
        pass


class SpaceFilling(object):
    def __init__(self, atoms):
        # self.imposters = SphereImposterArray(atoms)
        self.attributes = AtomGLAttributes(atoms)
        self.imposters = Sphere2Array(self.attributes)
        
    def init_gl(self):
        self.imposters.init_gl()
        
    def paint_gl(self, camera=None, renderer=None):
        self.imposters.paint_gl(camera, renderer)

    def update_atom_colors(self):
        self.imposters.update_atom_colors()
