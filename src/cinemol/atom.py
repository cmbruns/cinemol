'''
Created on Jul 29, 2012

@author: cmbruns
'''

import cinemol.element as element
import cinemol.color as color
from cinemol.rotation import Vec3
from cinemol.atom_expression import AtomExpression
import urllib
from StringIO import StringIO
import gzip
import math
import re
import os

# ATOM      1  O5' RU5 A   1     144.310 223.220  60.580  1.00  0.00
# 000000000111111111122222222223333333333444444444455555555556666666666
# 123456789012345678901234567890123456789012345678901234567890123456789
# RRRRRRSSSSS AAAALRRR CNNNNN   XXXXXXXXYYYYYYYYZZZZZZZZOOOOOOTTTTTT

pdb_atom_regex = re.compile(r"""^
    (?P<record_name>(?:ATOM\s\s)|(?:HETATM))
    (?P<serial_number>[\s0-9]{6})
    (?P<name>.{4})
    (?P<alternate_location_id>.)
    (?P<residue_name>.{3})
    \s # empty space
    (?P<chain_id>.)
    (?P<residue_number>[ 0-9]{4})
    (?P<insertion_code>.)
    \s{3}
    (?P<x>[-0-9\. ]{8})
    (?P<y>[-0-9\. ]{8})
    (?P<z>[-0-9\. ]{8})
    (?: # allow weird/wrong/missing occupancy and temperature factor
    (?P<occupancy>[0-9\. ]{6})
    (?P<temperature_factor>[0-9\. ]{6})
    (?: # final fields are not always present
        (?P<seg_id>.{4})
        (?P<element>.{2})
        (?P<charge>.{2})
    )?)?
    # $ # end of line varies
    """, flags=re.VERBOSE)

def my_strip(string):
    return string.replace(" ", "")

class Atom(object):
    def __init__(self):
        self.colorizer = color.green_colorizer
        self.element = element.unknown
        self.bonds = set()

    def from_pdb_atom_string(self, line):
        try:
            d = pdb_atom_regex.match(line).groupdict()
            self.full_name = d['name']
            self.name = self.full_name.strip()
            self.full_residue_name = d['residue_name']
            self.residue_name = self.full_residue_name.strip()
            self.chain_id = d['chain_id']
            self.residue_number = int(d['residue_number'])
            nanometers_from_angstroms = 0.10
            x = nanometers_from_angstroms * float(d['x'])
            y = nanometers_from_angstroms * float(d['y'])
            z = nanometers_from_angstroms * float(d['z'])
            self.center = Vec3([x, y, z])
            # Figure out element
            element_symbol = self.full_name[0:2].strip().upper()
            if "H" in element_symbol and len(self.name) == 4:
                element_symbol = "H"
            # Remove digits from element symbol
            element_symbol = element_symbol.strip("0123456789")
            self.element = element.from_symbol(element_symbol)
            if self.element is element.unknown and self.full_name.startswith(" "):
                self.element = element.from_symbol(self.full_name[1:3])
            # TODO - element, radius, color
        except ():
            raise SyntaxError("Bad PDB atom line: " + line)
        
    @property
    def color(self):
        return self.colorizer.color(self).linear
    
    @property
    def radius(self):
        return self.element.vdw_radius


class AtomList(list):
    def __init__(self):
        self.colorizer = color.green_colorizer
    
    def box_min_max(self):
        if len(self) < 1:
            return None, None
        box_min = Vec3(self[0].center[:])
        box_max = Vec3(self[0].center[:])
        for atom in self:
            for i in range(3):
                if atom.center[i] > box_max[i]:
                    box_max[i] = atom.center[i]
                if atom.center[i] < box_min[i]:
                    box_min[i] = atom.center[i]
        return box_min, box_max

    def box_center(self):
        if len(self) < 1:
            return None
        box_min, box_max = self.box_min_max()
        return 0.5 * (box_min + box_max)
    
    def compute_bonds(self):
        bond_count = 0
        hash3d = dict()
        cutoff = 0.17
        cutoffSqr = cutoff * cutoff
        # Insert atoms into hash
        for atom in self:
            cubelet_index = tuple([int(math.floor(x/cutoff)) for x in atom.center])
            # Search for bonded atoms already in hash
            # Examine all neighboring cubelets
            x0, y0, z0 = cubelet_index
            for x in (x0-1, x0, x0+1):
                for y in (y0-1, y0, y0+1):
                    for z in (z0-1, z0, z0+1):
                        v = tuple([x,y,z])
                        if not v in hash3d: # no such cubelet
                            continue
                        cubelet = hash3d[v]
                        for atom2 in cubelet:
                            if atom2 is atom: # same atom
                                continue
                            dv = atom.center - atom2.center
                            d2 = dv.dot(dv)
                            if d2 > cutoffSqr:
                                continue # too far
                            if d2 < 0.003:
                                continue # too close
                            # just right
                            bond_count += 1
                            atom.bonds.add(atom2.index)
                            atom2.bonds.add(atom.index)
                            print "bonding", atom.name, atom2.name, math.sqrt(d2)
            if not cubelet_index in hash3d:
                hash3d[cubelet_index] = list()
            hash3d[cubelet_index].append(atom)
        print bond_count, "bonds found"
        
    def color(self, colorizer):
        if not hasattr(colorizer, 'color'):
            colorizer = color.ConstantColorizer(colorizer)
        for atom in self:
            atom.colorizer = colorizer
        
    def load(self, file_name):
        if hasattr(file_name, 'readline'): # already a python file stream
            self.load_stream(file_name)
            return
        elif os.path.exists(file_name): # ordinary local file name
            fh = gzip.open(file_name, 'rb')
            pos = fh.tell()
            try:
                fh.read(1)
                fh.seek(pos)
            except:
                fh.close()
                fh = open(file_name)
        else: # Is file_name a URL?
            opener = urllib.FancyURLopener()
            fh = opener.open(file_name)
            if file_name.endswith(".gz"): # gzipped file
                buf = StringIO(fh.read())
                fh = gzip.GzipFile(fileobj=buf)
        with fh as f:
            self.load_stream(f)
        print "Computing bonds..."
        self.compute_bonds()
        print "Finished computing bonds"
            
    def load_line(self, line):
        if line[0:4] == "ATOM" or line[0:6] == "HETATM":
            atom = Atom()
            atom.from_pdb_atom_string(line)
            atom.colorizer = self.colorizer
            atom.index = len(self)
            self.append(atom)    
            
    def load_stream(self, stream):
        for line in stream:
            self.load_line(line)

    def select(self, expression):
        expr = AtomExpression(expression)
        result = AtomList()
        result[:] = filter(expr.matches, self)
        return result


class BondList(list):
    pass

