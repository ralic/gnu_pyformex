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
"""Formex Structure

This script creates an image of how coordinates are structures in a Formex.
It was intended mainly to create an illustration for the manual.
"""
from __future__ import absolute_import, division, print_function


_status = 'checked'
_level = 'beginner'
_topics = ['illustration']
_techniques = ['draw']

from pyformex.gui.draw import *


def drawAxis(len, dir, text):
    """Draw an axis of given length and direction annotated with text."""
    F = Formex('l:1').scale(len).rotate(dir)
    #T = F[0][1].scale(1.1)
    draw(F, linewidth=2.0)
    drawText(text, F[0][1]+(2., -0.5, 0.), size=18)
    return F

def drawFrame(P):
    """Draw a dashed frame at position P."""
    d, e = (2, 3) # dash length and step
    h = Formex('l:1').scale(d)
    v = h.rotate(-90).replic(4, -e, 1)
    h = h.replic(6, e, 0)
    frame = (h + v).trl(P)
    draw(frame, linewidth=1.0, bbox=None)

def run():
    clear()
    reset()

    drawAxis(30, 0, 'axis 2: coordinates (x,y,z): length = 3')
    drawAxis(30, -90, 'axis 1: points: length = self.nplex()')
    F = drawAxis(50, 30, 'axis 0: elements: length = self.nelems()').divide(8)

    for i in range(1, 5, 2):
        drawFrame(F[i][1])

    zoomAll()

if __name__ == '__draw__':
    run()
# End
