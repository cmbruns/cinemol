'''
Created on Aug 8, 2012

@author: cmbruns
'''

import cinemol.atom
import os
    
def load_atoms():
    atoms = cinemol.atom.AtomList()
    atoms.load(os.path.join(
        os.path.dirname(__file__),
        "../../../data/structures/ribosome_brandman.pdb.gz"))


if __name__ == "__main__":
    import cProfile
    import pstats
    cProfile.run("load_atoms()", 'loadprof')
    p = pstats.Stats('loadprof')
    p.strip_dirs().sort_stats('cumulative').print_stats()
