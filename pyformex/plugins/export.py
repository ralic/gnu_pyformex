# $Id$
##
##  This file is part of pyFormex 1.0.2  (Thu Jun 18 15:35:31 CEST 2015)
##  pyFormex is a tool for generating, manipulating and transforming 3D
##  geometrical models by sequences of mathematical operations.
##  Home page: http://pyformex.org
##  Project page:  http://savannah.nongnu.org/projects/pyformex/
##  Copyright 2004-2015 (C) Benedict Verhegghe (benedict.verhegghe@feops.com)
##  Distributed under the GNU General Public License version 3 or later.
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program.  If not, see http://www.gnu.org/licenses/.
##

"""Classes and functions for exporting geometry in various formats.


"""
from __future__ import absolute_import,division, print_function


import pyformex as pf


class ObjFile(object):
    """Export a mesh in OBJ format.

    This class exports a mesh in Wavefront OBJ format
    (see `<http://en.wikipedia.org/wiki/Wavefront_.obj_file>`_).

    Usage::

      fil = ObjFile(PATH_TO_OBJFILE)
      fil.write(MESH)
      fil.close()
    """

    def __init__(self, filename):
        self.file = open(filename, 'w')
        self.file.write("# .obj file written by %s\n" % pf.Version())

    def write(self,mesh,name=None):
        """Write a mesh to file in .obj format.

        mesh is a Mesh instance or another object having compatible
        coords and elems attributes.
        """
        if name is not None:
            self.file.write("o %s\n" % str(name))

        for v in mesh.coords:
            self.file.write("v %s %s %s\n" % tuple(v))

        # element code: p(oint), l(ine) or f(ace)
        nplex = mesh.elems.shape[1]
        code = { 1:'p', 2:'l' }.get(nplex, 'f')
        s = code+(' %s'*nplex)+'\n'
        for e in mesh.elems+1:   # .obj format starts at 1
            self.file.write(s % tuple(e))

    def close(self):
        self.file.write('# End\n')
        self.file.close()
        self.file = None


# End
