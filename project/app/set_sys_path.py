# -*- coding: utf-8 -*-
"""Sets sys.path for the library directories.

The purpose of this file is to define extra paths in a single place. This is
convenient in case many entry points are used instead of a single main.py.
"""
import os
import sys

current_path = os.path.abspath(os.path.dirname(__file__))
lib_path = os.path.join(current_path, 'lib')

def set_path():
    # Add lib as primary libraries directory, with fallback to lib/dist
    # and optionally to lib/dist.zip, loaded using zipimport.
    if lib not in sys.path:
        sys.path[0:0] = [
            lib_path,
            os.path.join(lib_path, 'dist'),
            os.path.join(lib_path, 'dist.zip'),
        ]

set_path()
