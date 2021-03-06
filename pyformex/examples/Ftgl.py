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

"""Ftgl

This example demonstrates the use of FTGL library to render text as 3D objects.
To be able to run it, you need to have the FTGL library and its Python bindings
installed.

The pyFormex source repository contains a directory pyformex/extra/pyftgl
containing a Makefile to install the libraries.
"""
from __future__ import absolute_import, division, print_function


_status = 'checked'
_level = 'advanced'
_topics = ['text']
_techniques = ['ftgl', 'font']

from pyformex.gui.draw import *

warning("The Ftgl example is not usable with the current pyFormex version")


## try:
##     import FTGL

## except ImportError:
##     warning("You do not have FTGL and its Python bindings (pyftgl).\nSee the pyformex/extra/pyftgl directory in the pyFormex source tree for instructions.")

## from pyformex.opengl import colors
## from pyformex.gui import image
## from pyformex.odict import OrderedDict
## from pyformex.opengl.actors import Text3DActor


## extra_fonts = [
##     getcfg('datadir')+"/blippok.ttf",
##     ]

## fonts = [ f for f in utils.listAllFonts() if f.endswith('.ttf') ]
## fonts += [ f for f in extra_fonts if os.path.exists(f) ]
## fonts.sort()
## print("Number of available fonts: %s" % len(fonts))

## fonttypes = OrderedDict([
##     ('polygon', FTGL.PolygonFont),
##     ('outline', FTGL.OutlineFont),
##     ('texture', FTGL.TextureFont),
## #    ('extrude',FTGL.ExtrudeFont),
##     ('bitmap', FTGL.BitmapFont),
## #    ('buffer',FTGL.BufferFont),
##     ])

## def showSquare():
##     F = Formex(pattern('1234'))
##     draw(F)


## def showText(text, font, fonttype, facesize, color, pos):
##     #utils.warn("Text3DActor is currently inactive")
##     #return
##     #font = fonttypes[fonttype](font)
##     #t = Text3DActor(text, font, facesize, color, pos)
##     #t.nolight=True
##     #drawAny(t)
##     #zoomAll()  #  !! Removing this may cause errors
##     print(fonts)
##     # - draw a square
##     # - use the full character set in the default font as a texture
##     # - the font textures are currently upside down, therefore we need
##     #   to specify texcoords to flip the image
##     from pyformex.opengl.textext import FontTexture
##     F = Formex('4:0123').scale(200).toMesh()
##     fontfile = getcfg('datadir')+"/blippok.ttf"
##     tex = FontTexture.default()
##     A = draw(F,color=yellow,texture=tex,texcoords=array([[0,1],[1,1],[1,0],[0,0]]),texmode=2)

##     #return t


## def rotate():
##     sleeptime = 0.1
##     n = 1
##     m = 5
##     val = m * 360. / n
##     for i in range(n):
##         pf.canvas.camera.rotate(val, 0., 1., 0.)
##         pf.canvas.update()
##         sleep(sleeptime)
##         sleeptime *= 0.98



## _items = [
##     _I('text', 'pyFormex'),
##     _I('font', choices=fonts),
##     _I('fonttype', choices=fonttypes.keys()),
##     _I('facesize', (24, 36)),
##     _I('color', colors.pyformex_pink),
##     _I('pos', (0., 0., 0.)),
##     ]

## dialog = None


## def close():
##     global dialog
##     if dialog:
##         dialog.close()
##         dialog = None
##     # Release script lock
##     scriptRelease(__file__)


## def show(all=False):
##     global text, font, facesize, color
##     dialog.acceptData()
##     globals().update(dialog.results)
##     export({'_Ftgl_data_':dialog.results})

##     clear()
##     print(dialog.results)
##     view('front')
##     showText(**dialog.results)
##     zoomAll()

##     #image.save("test.eps")


## def timeOut():
##     showAll()
##     wait()
##     close()


## def run():
##     global dialog
##     dialog = Dialog(
##         items=_items,
## #        enablers=_enablers,
##         caption='Ftgl parameters',
##         actions = [('Close', close), ('Clear', clear), ('Show', show)],
##         default='Show')

##     if '_Ftgl_data_' in pf.PF:
##         dialog.updateData(pf.PF['_Ftgl_data_'])

##     dialog.timeout = timeOut
##     dialog.show()
##     # Block other scripts
##     scriptLock(__file__)


## if __name__ == '__draw__':
##     chdir(__file__)
##     clear()
##     reset()
##     #view('iso')
##     smooth()
##     lights(False)
##     run()

def run():
    pass

if __name__ == '__draw__':
    run()

# End
