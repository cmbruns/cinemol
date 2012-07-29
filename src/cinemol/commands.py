'''
Created on Jul 29, 2012

@author: cmbruns
'''

from rotation import Vec3

class Commands(object):
    "Command dispatcher for Cinemol command line console and menus"
    def __init__(self, app):
        "Create a new Commands object.  This should be called only once, by the CinemolApp()"
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

    def center(self, pos):
        "Shift the center of rotation and viewing to pos, in nanometers"
        self.focus = pos
        
    def refresh(self):
        "Used in script files to redraw the image"
        self.renderer.update()
