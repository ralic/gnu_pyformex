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
"""Torus

"""
from __future__ import absolute_import, division, print_function


_status = 'checked'
_level = 'beginner'
_topics = ['geometry']
_techniques = ['color', 'dialog', 'transform', 'function']

from pyformex.gui.draw import *

def addFlares(F,dir=[0, 2]):
    """Adds flares at both ends of the structure.

    The flare parameters are hardcoded, a real-life example would
    make them adjustable.
    Returns the flared structure.
    """
    F = F.flare(m/4., -1., dir, 0, 0.5)
    F = F.flare(m/4., 1.5, dir, 1, 2.)
    return F

def run():
    # Some named colors (they should exist in /etc/X11/rgb.txt)
    color_choice = ['red', 'blue', 'orange', 'indianred', 'gold', 'pink', 'orchid', 'steelblue', 'turquoise', 'aquamarine', 'aquamarine1', 'aquamarine2', 'aquamarine3', 'aquamarine4', 'navy blue', 'royal blue']

    # Ask data from the user
    data = [
        _I('m', 36, text='number of cells in longest grid direction'),
        _I('n', 12, text='number of cells in shortes grid direction'),
        _I('f0', True, text='add flares on rectangle'),
        _I('f1', False, text='add flares on cylinder'),
        _I('f2', False, text='add flares on torus'),
        _I('geom', 'cylinder', itemtype='radio', choices=['rectangle', 'cylinder', 'torus'], text='geometry'),
        _I('color0', 'red', choices=color_choice),
        _I('color1', 'blue', choices=color_choice),
        ]
    res = askItems(data)
    if not res:
        return

    # Add the returned data to the global variables
    globals().update(res)

    # Construct the geometry
    F = Formex('3:.12.34', [0, 1]).replic2(m, n, 1, 1)
    if f0:
        F = addFlares(F)

    if geom != 'rectangle':
        F = F.translate(2, 1).cylindrical([2, 1, 0], [1., 360./n, 1.])
        if f1:
            F = addFlares(F, dir=[2, 0])
        if geom == 'torus':
            F = F.translate(0, 5).cylindrical([0, 2, 1], [1., 360./m, 1.])
            if f2:
                F = addFlares(F)

    # Draw the structure
    clear()
    view('iso')
    draw(F, colormap=[color0, color1])

if __name__ == '__draw__':
    run()
# End
