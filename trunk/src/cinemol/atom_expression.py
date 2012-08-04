'''
Created on Aug 3, 2012

@author: cmbruns
'''

import re

primitive_regex = re.compile(r"""
    # Rasmol primitive atom expression parsing regular expression.
    # see http://www.umass.edu/microbio/rasmol/distrib/rasman.htm#chexprs
    # There are two types of primitive atom expressions:
    #  1) residue number or range, e.g. "5" or "5-8"
    #  2) sequence of fields, e.g. "ser70.c?"
    # Residue number or range:
    ^(?:
    (?P<residue_number1>-?\d+)           # residue number e.g. "5"; group 1
       (?:-(?P<residue_range_end>-?\d+))?)  # residue number range end e.g. "-10"; group 2
    | (?: # end res numbers, start field sequence
      (?:(?P<residue_name1>[\?A-Za-z]{1,3}|\*) |  # residue name e.g. "cys"; group 3
         (?:\[(?P<residue_name2>.{1,3})\]))? # nonalpha residue name must be in brackets e.g. "[SO4]"; group 4
      (?P<residue_number2>-?[0-9]+)? # residue number, negative numbers permitted e.g. "73"; group 5
      (?:(?P<chain_id1>[A-Za-z]) | # chain id e.g. "A"; group 6
         (?:\:(?P<chain_id2>.)))? # nonalpha chain id permitted with a colon e.g. ":1"; group 7
      (?:\.(?P<atom_name>.{1,4}))? # atom field e.g. ".ca"; group 8
    )$""", flags=re.VERBOSE)


class StringMatcher(dict):
    def __init__(self, string):
        # convert numbers to strings, temporarily
        string = str(string)
        if string == "":
            raise SyntaxError("Empty atom expression")
        try:
            d = primitive_regex.match(string).groupdict()
            for key in d:
                # Merge chain_id1, chain_id2, etc.
                m = re.match(r'^(.*)[12]$', key) # e.g. "chain_id2"
                if m:
                    key0 = m.group(1) # e.g. "chain_id" with 2 removed
                    if (not self.has_key(key0)) or self[key0] is None:
                        self[key0] = d[key]
                else:
                    self[key] = d[key]
            # Convert from strings to int or regex
            for key in ["residue_number", "residue_range_end"]:
                if self[key] is not None:
                    self[key] = int(self[key])
        except:
            raise SyntaxError("Bad atom expression: " + string)
        for key in ['atom_name', 'residue_name', 'chain_id']:
            if self[key] is not None:
                # Treat string as regular expression
                # Convert shell-like wildcards to regex wildcards
                regexp = r'^' + self[key] + r'$'
                regexp = regexp.replace(r'?', r'.') # single character wildcard
                regexp = regexp.replace(r'*', r'.*') # whole string wildcard
                if regexp == r'^.*$':
                    self[key] = None # optimization
                else:
                    self[key] = regexp # for testing
        self.matchers = []
        # Store non-empty rules for faster matching
        for key in self:
            if self[key] is None:
                continue
            elif key == 'residue_range_end':
                self.matchers.append(ResidueRangeMatcher(
                    self['residue_number'], self[key]))
            elif key == 'residue_number':
                if self['residue_range_end'] is not None:
                    continue
                self.matchers.append(ResidueNumberMatcher(self[key]))
            elif key == 'atom_name':
                self.matchers.append(AtomNameMatcher(self[key]))
            elif key == 'residue_name':
                self.matchers.append(ResidueNameMatcher(self[key]))
            elif key == 'chain_id':
                self.matchers.append(ChainIdMatcher(self[key]))
                
    def matches(self, atom):
        # AND together all non-empty fields
        for matcher in self.matchers:
            if not matcher.matches(atom):
                return False
        return True


class AtomNameMatcher(object):
    def __init__(self, restring):
        self.string = restring
        self.re = re.compile(restring, re.IGNORECASE)

    def matches(self, atom):
        return self.re.match(atom.name) is not None


class ChainIdMatcher(object):
    def __init__(self, restring):
        self.string = restring
        # unlike rasmol, chain ID should be case sensitive
        self.re = re.compile(restring)

    def matches(self, atom):
        return self.re.match(atom.chain_id) is not None


class ResidueNameMatcher(object):
    def __init__(self, restring):
        self.string = restring
        self.re = re.compile(restring, re.IGNORECASE)

    def matches(self, atom):
        return self.re.match(atom.residue_name) is not None


class ResidueNumberMatcher(object):
    def __init__(self, number):
        self.number = int(number)

    def matches(self, atom):
        return atom.residue_number == self.number


class ResidueRangeMatcher(object):
    def __init__(self, begin, end):
        self.begin = int(begin)
        self.end = int(end)
        if self.begin > self.end:
            self.begin, self.end = self.end, self.begin
        
    def matches(self, atom):
        if atom.residue_number < self.begin:
            return False
        if atom.residue_number > self.end:
            return False
        return True


class AtomExpression(object):
    '''
    Rasmol atom expression
    '''
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
