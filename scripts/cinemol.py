#!/usr/bin/env python

# I want "import cinemol" to find the package, not this file
# so remove current directory from front of sys.path
import sys
first = sys.path[0]
sys.path = sys.path[1:]
sys.path.append(first)

from cinemol.cinemol_app import CinemolApp
CinemolApp().launch()
