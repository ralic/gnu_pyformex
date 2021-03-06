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
"""Pattern

This example shows the predefined geometries from simple.Pattern.
"""
from __future__ import absolute_import, division, print_function


_status = 'checked'
_level = 'beginner'
_topics = ['geometry']
_techniques = ['color', 'pattern']

from pyformex.gui.draw import *
from pyformex import simple
from pyformex.opengl.decors import Grid


def run():
    reset()
    setDrawOptions(dict(view='front', linewidth=5, fgcolor='red'))
    grid = Grid(nx=(4, 4, 0), ox=(-2.0, -2.0, 0.0), dx=(1.0, 1.0, 1.0), planes='n', linewidth=1)
    draw(grid)
    linewidth(3)
    FA = None
    setDrawOptions({'bbox':None})
    for n, p in simple.Pattern.items():
        print("%s = %s" % (n, p))
        FB = draw(Formex(p), bbox=None, color='red')
        if FA:
            undraw(FA)
        FA = FB
        pause()

if __name__ == '__draw__':
    run()
# End
