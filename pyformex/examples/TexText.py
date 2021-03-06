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
"""Text rendering on the OpenGL canvas.

This example illustrates some of the possibilities of text drawing
using textures. Yuo
"""
from __future__ import absolute_import, division, print_function

_status = 'checked'
_level = 'normal'
_topics = ['Text']
_techniques = ['texture']

import pyformex as pf
from pyformex.gui.draw import *

from pyformex.opengl.textext import *

def run():
    #
    # TODO: RESETALL does not properly layout the canvas in the viewport
    #resetAll()
    clear()
    view('front')
    smooth()
    fonts = utils.listMonoFonts()
    ft = FontTexture.default()

    # - draw a square
    # - use the full character set in the default font as a texture
    # - the font textures are currently upside down, therefore we need
    #   to specify texcoords to flip the image
    F = Formex('4:0123').scale(200).toMesh()
    A = draw(F,color=yellow,texture=ft,texcoords=array([[0,1],[1,1],[1,0],[0,0]]),texmode=2)


    # - draw 20 squares
    # - fill with specific text
    # - put this object on top
    G = Formex('4:0123').replic2(10,2).scale(20).rot(30).trl([150,50,0])
    text = [ ' pyFormex ','  rules!  ' ]
    text = text[1] + text[0]
    tc = FontTexture.default().texCoords(text)
    draw(G,color=pyformex_pink,texture=ft,texcoords=tc,texmode=2,ontop=True)


    # draw a cross at the center of the square
    # pos is 3D, therefore values are world coordinates
    decorate(Text('+',pos=(100,100,0),gravity='',size=100,color=red))

    # draw a string using the default_font texture
    # pos is 2D, therefore values are pixel coordinates
    decorate(Text("Hegemony!",pos=(100,100),size=50,offset=(0.0,0.0,1)))

    # the text is currently adjusted horizontally left, vertically centered
    # on the specified point. Adjustement using gravity will be added later.
    # Also, the color is currently not honoured.
    decorate(Text("Hegemony!",(0,10),size=20,color=red))
    decorate(Text("Hegemony!",(10,30),size=20,color=red))

    # use a TextArray to draw text at the corners of the square
    U = TextArray(["Lower left corner","Lower right corner","Upper right corner","Upper left corner"],pos=F.coords[F.elems[0]],size=30,gravity='NE')
    decorate(U)

    #drawViewportAxes3D((0.,0.,0.),color=blue)

    # draw a cross at the upper corners using an image file
    image = os.path.join(pf.cfg['pyformexdir'], 'data', 'mark_cross.png')
    from pyformex.plugins.imagearray import qimage2numpy
    image = qimage2numpy(image, indexed=False)
    X = Formex('4:0123').scale(40).toMesh().align('000')
    # at the right corner using direct texture drawing techniques
    draw(X,texture=image,texcoords=array([[0,1],[1,1],[1,0],[0,0]]),texmode=0,rendertype=-1,opak=False,ontop=True,offset3d=[(200.,200.,0.),(200.,200.,0.),(200.,200.,0.),(200.,200.,0.),])
    # at the left corner, using a Mark
    drawActor(Mark((0,200,0),image,size=40,color=red))

if __name__ == '__draw__':
    run()

# End
