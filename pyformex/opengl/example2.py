# Example script for testing opengl2
##
##  This file is part of the pyFormex project.
##  pyFormex is a tool for generating, manipulating and transforming 3D
##  geometrical models by sequences of mathematical operations.
##  Home page: http://pyformex.org
##  Project page:  http://savannah.nongnu.org/projects/pyformex/
##  Copyright (C) Benedict Verhegghe (benedict.verhegghe@ugent.be)
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
#
#

_clear = clear

def clearall():
    if pf.options.opengl2:
        pf.canvas.renderer.clear()
    _clear()


if pf.options.opengl2:
    def draw(o,**kargs):
        o.attrib(**kargs)
        pf.canvas.renderer.add(o)


clearall()


#transparent()

from simple import sphere

S = sphere(6)
S = S.toSurface().fixNormals().toFormex()
print(S.npoints())
col = [red,red]*81
print(len(col))
draw(S,lighting=True,ambient=0.0,diffuse=1.0,color=red,opacity=0.7,light=(0.,1.,1.))


T = Formex('4:0123').replic2(2,3).toMesh().align('-00')
draw(T,lighting=False,ambient=0.5,diffuse=0.5,specular=0.0,color=blue,opacity=1.0)

zoomAll()
exit()

# End
