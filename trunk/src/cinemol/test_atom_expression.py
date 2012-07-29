'''
Created on Jul 29, 2012

@author: cmbruns
'''

from atom import Atom, AtomExpression
import unittest

class TestAtomExpression(unittest.TestCase):
    def setUp(self):
        self.expr1 = AtomExpression("*")
        self.atom1 = Atom()
        
    def test_star(self):
        self.assertTrue(self.expr1.matches(self.atom1))


if __name__ == '__main__':
    unittest.main()
