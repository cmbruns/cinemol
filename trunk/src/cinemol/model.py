'''
Created on Jul 29, 2012

@author: cmbruns
'''

import atom

class CinemolModel(object):
    "Model as in model-view-controller"
    def __init__(self):
        self.atoms = atom.AtomList()
        self.bonds = atom.BondList()
        self.selected_atoms = self.atoms

model = CinemolModel()
