'''
Created on Jul 29, 2012

@author: cmbruns
'''

from cinemol.rotation import Vec3
from cinemol.model import model

class Commands(object):
    "Command dispatcher for Cinemol command line console and menus"
    def __init__(self):
        "Create a new Commands object.  This should be called only once, by the CinemolApp()"
        self.atoms = model.atoms
        
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
            atoms = self.atoms.select(pos)
            if len(atoms) > 0:
                new_focus = atoms.box_center()
            self.focus = new_focus
    centre = center
        
    def refresh(self):
        "Used in script files to redraw the image"
        self.renderer.update()
