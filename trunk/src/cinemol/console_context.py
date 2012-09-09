'''
Created on Jul 29, 2012

@author: cmbruns
'''

from commands import Commands
cm = Commands() # Needs further initialization by app

import cinemol.color as col
from cinemol.color import black, green
import cinemol.model


def _context():
    return globals()

# Below are commands that may be typed at the cinemol python console

def center(position="*"):
    cm.center(position)
    cm.refresh()

def color(colorizer, atoms=cinemol.model.model.selected_atoms):
    cm.color(colorizer, atoms)
    cm.refresh()

def cpk(param=None):
    cm.cpk(param)
    cm.refresh()

def cpknew(param=None):
    cm.cpknew(param)
    cm.refresh()

def load(file_name):
    cm.load(file_name)
    cm.refresh()
    
def refresh():
    cm.refresh()

def reset():
    cm.reset()
    refresh()

def select(atom_expression):
    cm.select(atom_expression)

def spacefill(param=True):
    cm.spacefill(param)
    cm.refresh()

def wireframe(width=1.0):
    cm.wireframe(width)
    cm.refresh()

def zap():
    cm.zap()
    cm.refresh()


all = cinemol.atom_expression.AtomExpression("*")
atoms = cinemol.model.model.selected_atoms

