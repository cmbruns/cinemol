'''
Created on Jul 29, 2012

@author: cmbruns
'''

import cinemol.element as element
from cinemol.rotation import Vec3
from cinemol.atom_expression import AtomExpression
import gzip
import re

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
    (?P<occupancy>[0-9\. ]{6})
    (?P<temperature_factor>[0-9\. ]{6})
    (?: # final fields are not always present
        (?P<seg_id>.{4})
        (?P<element>.{2})
        (?P<charge>.{2})
    )?
    # $ # end of line varies
    """, flags=re.VERBOSE)


class Atom(object):
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
            # TODO - element, radius, color
        except:
            raise SyntaxError("Bad PDB atom line: " + line)
        # TODO - vdw_radius and element
        


class AtomList(list):
    def box_min_max(self):
        if len(self) < 1:
            return None, None
        box_min = Vec3(self[0].center[:])
        box_max = Vec3(self[0].center[:])
        for atom in self:
            for i in range(3):
                if atom[i] > box_max[i]:
                    box_max[i] = atom[i]
                if atom[i] < box_min[i]:
                    box_min[i] = atom[i]
        return box_min, box_max

    def box_center(self):
        if len(self) < 1:
            return None
        box_min, box_max = self.box_min_max()
        return 0.5 * (box_min + box_max)
    
    def load(self, file_name):
        # Start by assuming its a gzipped file
        fh = gzip.open(file_name, 'rb')
        start_pos = fh.tell()
        try:
            fh.read(1)
            fh.seek(start_pos)
        except IOError:
            # OK, maybe its not a gzipped file
            fh.close()
            fh = open(file_name, 'r')
        with fh as f:
            self.load_stream(f)
            
    def load_stream(self, stream):
        for line in stream:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                atom = Atom()
                atom.from_pdb_atom_string(line)
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                atom = Atom()
                atom.center = Vec3([x, y, z])
                atom.name = line[12:16]
                atom.color = [0.5, 0, 0.5]
                atom.radius = 1.0
                if (atom.name[1:2] == 'H'):
                    atom.color = [1.0, 1.0, 1.0]
                    atom.radius = 1.2
                if (atom.name[1:2] == 'C'):
                    atom.color = [0.5, 0.5, 0.5]
                    atom.radius = 1.70
                if (atom.name[1:2] == 'N'):
                    atom.color = [0.1, 0.1, 0.8]
                    atom.radius = 1.555
                if (atom.name[1:2] == 'O'):
                    atom.color = [0.8, 0.05, 0.05]
                    atom.radius = 1.52
                self.append(atom)

    def select(self, expression):
        expr = AtomExpression(expression)
        result = AtomList()
        result[:] = filter(expr.matches, self)
        return result


class BondList(list):
    pass

