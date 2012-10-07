'''
Created on Jul 29, 2012

@author: cmbruns
'''

import atom
import cinemol.representation
import cinemol.imposter as imposter

class CinemolModel(object):
    "Model as in model-view-controller"
    def __init__(self):
        self.atoms = atom.AtomList()
        self.bonds = atom.BondList()
        self.selected_atoms = atom.AtomList()
        self.selected_atoms[:] = self.atoms[:]
        self.representations = dict()
        self.representations['backbone'] = cinemol.representation.Backbone()
        self.representations['ball_and_stick'] = cinemol.representation.BallAndStick()
        self.representations['spacefill'] = cinemol.representation.SpaceFilling()
        self.representations['sticks'] = cinemol.representation.Sticks()
        self.representations['wireframe'] = cinemol.representation.BondLines()
        self.atom_attributes = imposter.atom_attributes
        self.atom_scale = 1.0
        self.default_representation = 'spacefill'

    def update_atom_colors(self):
        for rep in self.representations.values():
            rep.update_atom_colors()
        

model = CinemolModel()
