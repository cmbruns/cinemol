'''
Created on Aug 9, 2012

@author: cmbruns
'''

from cinemol.imposter import SphereImposterArray, Sphere2Array, atom_attributes
from shader import WireFrameShader, BondCylinderShader, Sphere2Shader
from OpenGL.GL import *
import numpy


class BondRepBase:
    "Base class for BondLines and BondCylinders"
    def __init__(self):
        self.bond_set = set()
        self.atom_ix_set = set()
        self.index_array = numpy.array([], numpy.uint32)
        self.index_buffer = 0
        self.bonds_changed = False
        self.is_initialized = False
        self.atom_attributes = atom_attributes

    def add_atoms(self, atoms):
        if len(atoms) < 1:
            return
        for atom in atoms:
            self.atom_ix_set.add(atom.index)
        for atom in atoms:
            for bond in atom.bonds:
                if not bond in self.atom_ix_set:
                    continue # bonded atom not in list
                bond_tuple = tuple([atom.index, bond])
                if bond < atom.index:
                    # only use one of two bond directions
                    bond_tuple = tuple([bond, atom.index])
                if not bond_tuple in self.bond_set:
                    self.bond_set.add(bond_tuple)
                    self.bonds_changed = True
        if self.bonds_changed:
            bond_indices = list()
            for bond in self.bond_set:
                bond_indices.extend(bond)
            self.index_array = numpy.array(bond_indices, numpy.uint32)
            
    def clear(self):
        self.bond_set.clear()
        self.atom_ix_set.clear()
        self.index_array = numpy.array([], numpy.uint32)
    
    def init_gl(self):
        if self.is_initialized:
            return
        atom_attributes.init_gl()
        self.index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)
        self.bonds_changed = False
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glLineWidth(4)
        self.is_initialized = True
        
    def paint_gl(self, camera=None, renderer=None):
        if len(self.index_array) == 0:
            return
        if not self.is_initialized:
            self.init_gl()
        with self.shader:
            self.atom_attributes.paint_gl()
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
            if self.bonds_changed:
                glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_array, GL_STATIC_DRAW)
                self.bonds_changed = False
            glDrawElements(GL_LINES, len(self.index_array), GL_UNSIGNED_INT, None)            
            # clean up
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            
    def remove_atoms(self, atoms):
        if len(atoms) < 1:
            return
        removed_atom_ix = set()
        for atom in atoms:
            if not atom.index in self.atom_ix_set:
                continue
            removed_atom_ix.add(atom.index)
        self.atom_ix_set -= removed_atom_ix
        removed_bonds = set()
        for bond in self.bond_set:
            for ix in bond:
                if ix in removed_atom_ix:
                    removed_bonds.add(bond)
        self.bond_set = self.bond_set - removed_bonds
        if len(removed_bonds) > 1:
            self.bonds_changed = True
            bond_indices = list()
            for bond in self.bond_set:
                bond_indices.extend(bond)
            self.index_array = numpy.array(bond_indices, numpy.uint32)

    def set_radius(self, width):
        # TODO set line width
        pass
    
    def update_atom_colors(self):
        self.atom_attributes.update_atom_colors()

class Backbone(BondRepBase):
    pass

class BondCylinders(BondRepBase):
    def __init__(self, radius=0.02):
        BondRepBase.__init__(self)
        self.shader = BondCylinderShader()
        self.shader.radius = radius
        
    def paint_gl(self, camera=None, renderer=None):
        if renderer is not None:
            self.shader.light_direction = renderer.light_direction
        BondRepBase.paint_gl(self, camera, renderer)
        
    def set_radius(self, radius):
        self.shader.radius = radius


class BondLines(BondRepBase):
    def __init__(self):
        BondRepBase.__init__(self)
        self.shader = WireFrameShader()


class Sticks():
    def __init__(self, radius=0.02):
        self.bond_rep = BondCylinders()
        self.atom_rep = SpaceFilling()
        self.set_radius(radius)

    def add_atoms(self, atoms):
        self.bond_rep.add_atoms(atoms)
        self.atom_rep.add_atoms(atoms)
        
    def clear(self):
        self.bond_rep.clear()
        self.atom_rep.clear()
        
    def init_gl(self):
        self.bond_rep.init_gl()
        self.atom_rep.init_gl()

    def paint_gl(self, camera=None, renderer=None):
        self.bond_rep.paint_gl(camera, renderer)
        self.atom_rep.paint_gl(camera, renderer)
        
    def remove_atoms(self, atoms):
        self.bond_rep.remove_atoms(atoms)
        self.atom_rep.remove_atoms(atoms)
        
    def set_radius(self, radius):
        self.radius = radius
        self.bond_rep.set_radius(radius)
        self.atom_rep.set_radius(radius)

    def update_atom_colors(self):
        self.bond_rep.update_atom_colors()
        self.atom_rep.update_atom_colors()


class BallAndStick(Sticks):
    def __init__(self, ball_radius=0.050, stick_radius=0.015):
        Sticks.__init__(self, ball_radius)
        self.ball_radius = ball_radius
        self.stick_radius = stick_radius
        self.set_radius(ball_radius, stick_radius)

    def set_radius(self, ball_radius, stick_radius=None):
        if ball_radius > 0.0:
            self.ball_radius = ball_radius
            if stick_radius is None:
                self.stick_radius = 0.3 * ball_radius
            self.bond_rep.set_radius(self.stick_radius)
            self.atom_rep.set_radius(self.ball_radius)


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
