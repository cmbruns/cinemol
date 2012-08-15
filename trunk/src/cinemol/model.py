'''
Created on Jul 29, 2012

@author: cmbruns
'''

import atom
import cinemol.representation

class CinemolModel(object):
    "Model as in model-view-controller"
    def __init__(self):
        self.atoms = atom.AtomList()
        self.bonds = atom.BondList()
        self.selected_atoms = atom.AtomList()
        self.selected_atoms[:] = self.atoms[:]
        self.representations = list()
        self.default_representation = cinemol.representation.SpaceFilling

    def update_atom_colors(self):
        for rep in self.representations:
            rep.update_atom_colors()
        

model = CinemolModel()
