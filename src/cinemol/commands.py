'''
Created on Jul 29, 2012

@author: cmbruns
'''

from cinemol.rotation import Vec3
from cinemol.model import model
from cinemol.atom_expression import AtomExpression
import cinemol.color as color
import cinemol.atom
import cinemol.imposter
import gzip

class Commands(object):
    "Command dispatcher for Cinemol command line console and menus"
    def __init__(self):
        "Create a new Commands object.  This should be called only once, by the CinemolApp()"
        pass
        
    def _set_app(self, app):
        self.app = app
        self.main_window = app.mainWin
        self.renderer = app.renderer
        self.camera = self.renderer.camera_position

    @property
    def focus(self):
        "The center of rotation and viewing, in nanometers."
        return self.camera.focus_in_ground
    @focus.setter
    def focus(self, value):
        self.camera.focus_in_ground = Vec3(value)
        self.refresh()

    def center(self, pos="*"):
        "Shift the center of rotation and viewing to pos, in nanometers"
        try:
            self.focus = pos
        except TypeError:
            # Not a vector?  Must be an atom expression
            new_focus = Vec3([0,0,0])
            atoms = model.atoms.select(pos)
            if len(atoms) > 0:
                new_focus = atoms.box_center()
            self.focus = new_focus
    centre = center
        
    def load(self, file_name):
        atoms = model.atoms
        atoms[:] = []
        atoms.colorizer = color.ColorByRasmolCpkNewLighter()
        atoms.load(file_name)
        print len(atoms), "atoms found"
        if len(atoms) > 0:
            print "creating representation"
            sphere_array = cinemol.imposter.SphereImposterArray(atoms)
            ren = self.renderer
            ren.actors = []
            self.main_window.bookmarks.clear()
            ren.actors.append(sphere_array)
            print "centering"
            min_pos, max_pos = atoms.box_min_max()
            new_focus = 0.5 * (max_pos + min_pos)
            ren.camera_position.focus_in_ground = new_focus
            ren.camera_position.distance_to_focus = 4.0 * (max_pos - min_pos).norm()            
            ren.update()
        
    def refresh(self):
        "Used in script files to redraw the image"
        self.renderer.update()
        
    def select(self, atom_expression):
        expr = AtomExpression(atom_expression)
        model.selected_atoms = model.atoms.select(expr)
        
