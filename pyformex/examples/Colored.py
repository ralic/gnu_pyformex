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
"""Colored

"""
from __future__ import absolute_import, division, print_function


_status = 'checked'
_level = 'beginner'
_topics = ['surface']
_techniques = ['color']

from pyformex.gui.draw import *
from pyformex.opengl.drawable import GeomActor


def run():
    reset()
    smooth()
    lights(False)

    Rendermode = [ 'wireframe', 'flat', 'smooth' ]
    Lights = [ False, True ]
    Shapes = [ '3:012', '4:0123', ]

    color0 = None  # no color: current fgcolor
    color1 = 'red'   # single color
    color2 = ['red', 'green', 'blue'] # 3 colors: will be repeated

    delay(0)
    i=0
    for shape in Shapes:
        F = Formex(shape).replic2(4, 2)
        color3 = resize(color2, F.shape) # full color
        #print F.shape,color3
        #print [ GLcolor(c) for c in color3]
        #continue
        for c in [ color0, color1, color2, color3]:
            for mode in Rendermode:
                clear()
                renderMode(mode)
                FA = GeomActor(F, color=c)
                drawActor(FA)
                ### For some modes, draw(F,color=c) does not work!!
                zoomAll()
                for light in Lights:
                    lights(light)
                    print("%s: color %s, mode %s, lights %s" % (i, str(c), mode, light))
                    i += 1
                    pause()


if __name__ == '__draw__':
    run()
# End
