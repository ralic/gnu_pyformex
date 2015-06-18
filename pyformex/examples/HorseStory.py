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
"""Horse

This script reads horse.pgf, transforms it into a surface,
loads the surface plugin and cuts the horse in a number of surfaces.
"""
from __future__ import print_function


_status = 'checked'
_level = 'normal'
_topics = ['surface']
_techniques = ['animation', 'colors']

from pyformex.gui.draw import *


def run():
    global y
    reset()
    smooth()

    x = 20
    y = pf.canvas.height()-100

    def say(text):
        global y
        drawText(text, (x, y))
        y -=20

    print('Click Step to continue')

    say('A Horse Story...')
    y -= 10
    F = Formex.read(getcfg('datadir')+'/horse.pgf')
    A = draw(F)
    pause()

    say('It\'s rather sad, but')
    pause()


    say('the horse was badly cut;')
    T = F.cutWithPlane([0., 0., 0.], [-1., 0., 0.], '+')
    undraw(A)
    A = draw(T)
    pause()


    say('to keep it stable,')
    undraw(A)
    A = draw(T.rotate(-80))
    pause()


    say('the doctors were able')
    undraw(A)
    A = draw(T)
    pause()


    say('to add a mirrored clone:')
    T += T.reflect(0)
    undraw(A)
    A = draw(T)
    pause()

    say('A method as yet unknown!')
    colors = 0.1 * random.random((10, 3))
    for color in colors:
        B = draw(T, color=color)
        undraw(A)
        A = B
        sleep(0.5)

if __name__ == '__draw__':
    run()
# End
