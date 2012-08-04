'''
Created on Aug 4, 2012

@author: cmbruns
'''

from cinemol.atom_expression import StringMatcher as Pae
from atom import Atom
import unittest

class TestAtomExpression(unittest.TestCase):
    def setUp(self):
        self.atom1 = Atom()
        self.atom1.residue_name = "CYS"
        self.atom1.name = "CA"
        self.atom1.residue_number = 70
        self.atom1.chain_id = "p"
        
    def test_numbers(self):
        p = Pae("5")
        self.assertEqual(5, p['residue_number'])
        self.assertEqual(None, p['residue_range_end'])
        p = Pae("5-15")
        self.assertEqual(5, p['residue_number'])
        self.assertEqual(15, p['residue_range_end'])
        p = Pae("ser70.c?")
        self.assertEqual(70, p['residue_number'])
        
    def test_misc(self):
        self.assertRaises(SyntaxError, Pae, "x5x5x5x5")
        self.assertRaises(SyntaxError, Pae, "")
        p = Pae("*")
        self.assertTrue(p.matches(9)) # it matches everything!
        # self.assertEqual(None, p['residue_name'])
        
    def test_residue_name(self):
        p = Pae("*")
        self.assertTrue(p.matches(self.atom1))
        p = Pae("cys")
        self.assertTrue(p.matches(self.atom1))
        p = Pae("ser")
        self.assertFalse(p.matches(self.atom1))
        self.atom1.residue_name = "ASN"
        self.assertTrue(Pae("as?").matches(self.atom1))
        self.atom1.residue_name = "SER"
        self.assertFalse(Pae("as?").matches(self.atom1))
        self.assertTrue(Pae("ser70.c?").matches(self.atom1))
        
    def test_chain_id(self):
        self.assertTrue(Pae("*p").matches(self.atom1))
        self.assertFalse(Pae("*a").matches(self.atom1))
        

if __name__ == '__main__':
    unittest.main()
