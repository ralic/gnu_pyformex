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

"""Extrude

This example shows the repeated extrusion of a Geometry.
First a point is created (black). It is extruded in the x-direction
to yield a line (red). The line is extruded in y-direction, resulting in
a rectangle (blue). Finally, an extrusion in the z-direction gives a
cuboid (yellow).
"""
from __future__ import absolute_import, division, print_function


_status = 'checked'
_level = 'beginner'
_topics = ['formex']
_techniques = ['extrude']

from pyformex.gui.draw import *

def run():
    clear()

    smoothwire()
    view('iso')
    delay(1)

    a = Formex([0., 0., 0.])
    draw(a, color='black')


    b = a.extrude(8, 0)
    draw(b, color='red')


    c = b.extrude(8, 1)
    draw(c, color='blue')


    d = c.extrude(7, 2, -1.)
    draw(d, color='yellow')

if __name__ == '__draw__':
    run()
# End
