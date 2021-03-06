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
"""Grid

"""
from __future__ import absolute_import, division, print_function


_status = 'checked'
_level = 'beginner'
_topics = ['geometry']
_techniques = ['dialog', 'actor']

from pyformex.gui.draw import *
from pyformex.opengl.decors import Grid


def run():
    clear()
    res = askItems([
        _I('nx', 4),
        _I('ny', 3),
        _I('nz', 2),
        _I('Grid type', itemtype='radio', choices=['Box', 'Plane']),
        _I('alpha', 0.3)
        ])

    if not res:
        return

    nx = (res['nx'], res['ny'], res['nz'])
    gridtype = res['Grid type']
    alpha = res['alpha']

    t = 'b' if gridtype == 'Box' else 'f'
    G = Grid(nx=nx, linewidth=0.2, alpha=alpha, lines=t, planes=t)

    smooth()
    draw(G)

if __name__ == '__draw__':
    run()
# End
