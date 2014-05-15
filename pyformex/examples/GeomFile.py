# $Id$
##
##  This file is part of pyFormex 0.9.1  (Tue Oct 15 21:05:25 CEST 2013)
##  pyFormex is a tool for generating, manipulating and transforming 3D
##  geometrical models by sequences of mathematical operations.
##  Home page: http://pyformex.org
##  Project page:  http://savannah.nongnu.org/projects/pyformex/
##  Copyright 2004-2013 (C) Benedict Verhegghe (benedict.verhegghe@ugent.be)
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
"""GeomFile

Test the GeomFile export and import
"""
from __future__ import print_function


_status = 'checked'
_level = 'normal'
_topics = ['geometry']
_techniques = ['color', 'geomfile']

from pyformex.gui.draw import *
from pyformex.examples.Cube import cube_quad


def run():


    colormode = ['None', 'Single', 'Face', 'Full']
    n = len(colormode)
    obj = {}
    layout(2*n,4)
    for vp,color in enumerate(colormode):
        viewport(vp)
        clear()
        reset()
        smooth()
        view('iso')
        obj[color] = cube_quad(color)
        draw(obj[color])

    writeGeomFile('test.pgf', obj, sep=' ')

    oobj = readGeomFile('test.pgf')
    for vp,color in enumerate(colormode[:4]):
        #print(color)
        #print(oobj[color])
        viewport(vp+n)
        clear()
        reset()
        smooth()
        view('iso')
        draw(oobj[color])


if __name__ == 'draw':
    run()
# End