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
"""Lustrum

This example contains a script that was created to commemmorate the 5 years
existence of the pyFormex project. It was actually included first as an
easter egg, running when the pyFormex GUI started up. Afterwards it was
included as an example.

It uses one of the rulesets of the Lima example to grow a plant, with
different color for each generation. The superimposed '5' is read from
a pyFormex Geometry file, distributed with pyFormex in the 'data' directory.

To create this file we use a Python interface to the ftgl library, allowing
the transformation of a character '5' from a 'blippo' font to be converted
to an OpenGL model. This functionality is currently not included in pyFormex,
but we are working on an equivalent using the 'fontforge' library.
"""
from __future__ import absolute_import, division, print_function


_status = 'checked'
_level = 'normal'
_topics = ['curve', 'drawing', 'illustration']
_techniques = ['color', 'persistence', 'lima', 'import']

from pyformex.gui.draw import *
from pyformex.examples.Lima import *

def run():
    resetAll()
    flat()
    linewidth(2)
    fgcolor(blue)
    grow('Plant1', ngen=7, clearing=False, text=False)
    data = readGeomFile(os.path.join(pf.cfg['datadir'], 'blippo.pgf'))
    curve = data['blippo-0']
    bb = curve.coords.bbox()
    ctr = bb.center()
    siz = bb.sizes()
    curve.coords = curve.coords.trl(0, -ctr[0]).scale(50./siz[0])
    draw(curve, color=pyformex_pink, linewidth=5)

if __name__ == '__draw__':
    run()
# End
