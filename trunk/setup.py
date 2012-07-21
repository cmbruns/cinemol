#!/usr/bin/env python

from setuptools import setup

setup(name = 'cinemol',
      version = '0.2.0',
      description = 'Cinemol molecule structure viewer',
      author = 'Christopher M. Bruns',
      author_email = 'cmbruns@rotatingpenguin.com',
      url = 'http://cinemol.rotatingpenguin.com/',
      download_url = 'http://code.google.com/p/cinemol/downloads/list',
      package_dir = {'cinemol' : 'src/cinemol'}, 
      packages = ['cinemol'], 
      requires = ["PySide", "PyOpenGL", "numpy"],
      scripts = ['scripts/cinemol']
      )

