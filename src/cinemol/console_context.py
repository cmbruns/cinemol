'''
Created on Jul 29, 2012

@author: cmbruns
'''

from commands import Commands
import cinemol.color as col
from cinemol.color import black, green
import cinemol.model

# This module gets populated programmatically
cm = Commands() # Needs further initialization by app

def _context():
    return globals()

# Below are commands that may be typed at the cinemol python console

def center(position="*"):
    cm.center(position)

def color(colorizer, atoms=cinemol.model.model.selected_atoms):
    cm.color(colorizer, atoms)
    
def load(file_name):
    cm.load(file_name)
    
def refresh():
    cm.refresh()

def select(atom_expression):
    cm.select(atom_expression)

def zap():
    cm.zap()


all = cinemol.atom_expression.AtomExpression("*")
atoms = cinemol.model.model.selected_atoms

