'''
Created on Jul 29, 2012

@author: cmbruns
'''

from cinemol.imposter import atom_attributes
from cinemol.rotation import Vec3
from cinemol.model import model
from cinemol.atom_expression import AtomExpression
import cinemol.color as color
import cinemol.atom as atom

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

    def center(self, pos="*"):
        "Shift the center of rotation and viewing to pos, in nanometers"
        try:
            self.focus = pos
        except (TypeError, IndexError):
            # Not a vector?  Must be an atom expression
            new_focus = Vec3([0,0,0])
            atoms = model.atoms.select(pos)
            if len(atoms) > 0:
                new_focus = atoms.box_center()
            self.focus = new_focus
    centre = center
        
    def color(self, colorizer, atoms=model.selected_atoms):
        if not hasattr(colorizer, 'color'):
            colorizer = color.ConstantColorizer(colorizer)
        for atom in atoms:
            atom.colorizer = colorizer
        self.renderer.gl_widget.makeCurrent()
        model.update_atom_colors()

    def cpk(self, param):
        self.spacefill(param)
        self.color(color.ColorByRasmolCpk())

    def cpknew(self, param):
        self.spacefill(param)
        self.color(color.ColorByRasmolCpkNewLighter())
        
    def load(self, file_name):
        atoms = model.atoms
        atoms[:] = []
        atoms.colorizer = color.ColorByRasmolCpk()
        atoms.load(file_name)
        print len(atoms), "atoms found"
        if len(atoms) > 0:
            atom_attributes.add_atoms(atoms)
            print "creating representation"
            rep = model.default_representation
            model.representations[rep].add_atoms(atoms)
            self.reset()

    def refresh(self):
        "Used in script files to redraw the image"
        self.renderer.update()
        
    def reset(self):
        atoms = model.atoms
        if len(atoms) < 1:
            return
        ren = self.renderer
        print "centering"
        min_pos, max_pos = atoms.box_min_max()
        new_focus = 0.5 * (max_pos + min_pos)
        ren.camera_position.focus_in_ground = new_focus
        ren.camera_position.distance_to_focus = 4.0 * ((max_pos - min_pos).norm() + 0.3)           

    def select(self, atom_expression):
        expr = AtomExpression(atom_expression)
        model.selected_atoms[:] = model.atoms.select(expr)[:]
        num = len(model.selected_atoms)
        if num == 1:
            print num, "atom selected"
        else:
            print num, "atoms selected."

    def spacefill(self, param=True):
        self.use_representation('spacefill', param)
    
    def sticks(self, radius=0.025):
        self.use_representation('sticks', radius)        
    
    def use_representation(self, rep_name, param):
        rep = model.representations[rep_name]
        if param is False: # hide atoms
            rep.remove_atoms(model.selected_atoms)
        else:
            model.default_representation = rep_name
            rep.add_atoms(model.selected_atoms)
            if param is True: # radius value
                rep.set_radius(0.0)
            else:
                radius = float(param)
                rep.set_radius(radius)      
        
    def wireframe(self, width=0.02):
        # print "wireframe"
        self.use_representation('wireframe', width)        
    
    def zap(self):
        print "clearing everything"
        self.main_window.bookmarks.clear()
        self.renderer.actors[:] = []
        model.atoms[:] = []
        model.bonds[:] = []
        model.selected_atoms[:] = model.atoms[:]
        for rep in model.representations.values():
            rep.clear()
        atom_attributes.clear()
