'''
Created on Aug 9, 2012

@author: cmbruns
'''

from cinemol.imposter import SphereImposterArray, Sphere2Array, atom_attributes
from shader import WireFrameShader
from OpenGL.GL import *
import numpy


class BondLines:
    def __init__(self):
        self.bond_set = set()
        self.atom_ix_set = set()
        self.index_array = numpy.array([], numpy.uint32)
        self.index_buffer = 0
        self.shader = WireFrameShader()
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
