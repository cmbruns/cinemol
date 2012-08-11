'''
Created on Jul 29, 2012

@author: cmbruns
'''

from commands import Commands

# This module gets populated programmatically
cm = Commands() # Needs further initialization by app

def _context():
    return globals()

def load(file_name):
    cm.load(file_name)
