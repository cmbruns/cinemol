'''
Created on Aug 4, 2012

@author: cmbruns
'''

from cinemol.atom import AtomList, pdb_atom_regex
import unittest

class TestAtom(unittest.TestCase):
    def test_pdb(self):
        atom_string1 = "ATOM     43  H6   RU A   2     147.380 222.790  69.790  1.00  0.00"
        atom_string2 = "ATOM      1  O5' RU5 A   1     144.310 223.220  60.580  1.00  0.00"
        match = pdb_atom_regex.match(atom_string1)
        self.assertNotEqual(None, match)
        match = pdb_atom_regex.match(atom_string2)
        self.assertNotEqual(None, match)
