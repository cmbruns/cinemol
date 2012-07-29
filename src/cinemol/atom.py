'''
Created on Jul 29, 2012

@author: cmbruns
'''

from cinemol.rotation import Vec3

class AtomExpression(object):
    def __init__(self, expression):
        self.expression = expression
        if "*" == expression:
            self.always_matches = True
            return
        if "" == expression:
            self.never_matches = True
            return
        raise SyntaxError

    def matches(self, atom):
        if self.always_matches:
            return True
        if self.never_matches:
            return False
        # TODO
        return False


class Atom(object):
    pass

    
class AtomList(list):
    def select(self, expression):
        expr = AtomExpression(expression)
        result = AtomList()
        result[:] = filter(expr.matches, self)
        return result   
    
    def box_min_max(self):
        if len(self) < 1:
            return None, None
        min = Vec3(self[0].center[:])
        max = Vec3(self[0].center[:])
        for atom in self:
            for i in range(3):
                if atom[i] > max[i]:
                    max[i] = atom[i]
                if atom[i] < min[i]:
                    min[i] = atom[i]
        return min, max

    def box_center(self):
        if len(self) < 1:
            return None
        min, max = self.box_min_max()
        return 0.5 * (min + max)


class BondList(list):
    pass

