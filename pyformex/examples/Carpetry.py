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

"""Carpetry

This example illustrates the use of the Mesh conversion techniques and the
creation of colored value plots on surfaces.
"""
from __future__ import absolute_import, division, print_function

_status = 'checked'
_level = 'normal'
_topics = ['mesh', 'illustration', 'surface']
_techniques = ['color', 'random', 'image', 'movie', 'extrude']

from pyformex.gui.draw import *
from pyformex.plugins import surface_menu
from pyformex.elements import *

def atExit():
    pf.cfg['gui/autozoomfactor'] = saved_autozoomfactor
    pf.GUI.setBusy(False)


def drawMesh(M):
    clear()
    draw(M)
    drawText("%s %s elements" % (M.nelems(), M.elName()), (20, 20), size=20)

def run():
    # make sure this is a good aspect ratio if you want a movie
    nx, ny = 4, 3
    global saved_autozoomfactor
    saved_autozoomfactor = pf.cfg['gui/autozoomfactor']

    pf.GUI.setBusy()
    pf.cfg['gui/autozoomfactor'] = 2.0

    clear()
    view('front')
    smoothwire()
    transparent()
    linewidth(1)

    M = Formex(origin()).extrude(nx, 0).extrude(ny, 1).toMesh().setProp(1)

    V = surface_menu.SelectableStatsValues
    possible_keys = [ k for k in V.keys() if not V[k][1] ][:-1]
    nkeys = len(possible_keys)

    maxconv = 6
    minconv = 3
    minelems = 6000
    maxelems = 20000

    save = False

    def carpet(M):
        conversions = []
        nconv = random.randint(minconv, maxconv)

        while (len(conversions) < nconv and M.nelems() < maxelems) or M.nelems() < minelems:
            possible_conversions = list(M.elType().conversions)
            i = random.randint(len(possible_conversions))
            conv = possible_conversions[i]
            conversions.append(conv)
            M = M.convert(conv)

        if M.elType() != Tri3:
            M = M.convert('tri3')
            conversions.append('tri3')

        print("%s patches" % M.nelems())
        print("conversions: %s" % conversions)

        # Coloring
        key = possible_keys[random.randint(nkeys)]
        print("colored by %s" % key)
        func = V[key][0]
        S = TriSurface(M)
        val = func(S)
        export({'surface':S})
        surface_menu.selection.set(['surface'])
        surface_menu.showSurfaceValue(S, str(conversions), val, False)
        for a in pf.canvas.scene.decorations+pf.canvas.scene.annotations:
            undraw(a)

    clear()
    flatwire()
    lights(True)
    transparent(False)

    if pf.interactive:
        canvasSize(nx*200, ny*200)
        #canvasSize(720,576)
        print("running interactively")
        res = askItems([
            _I('n',1,text='Number of carpets'),
            _I('save',False,text='Save images'),
            ])
        if not res:
            return

        n = res['n']
        save = res['save']
        if save:
            from pyformex.gui import image
            image.save(filename='Carpetry-000.jpg', window=False, multi=True, hotkey=False, autosave=False, border=False, format=None, quality=95, verbose=False)

        A = None
        for i in range(n):
            carpet(M)
            B = pf.canvas.actors[-1:]
            if A:
                undraw(A)
            A = B
            if save:
                image.saveNext()

        if save:
            files = image.multisave[0].files()
            image.createMovie(files, encoder='convert', delay=1, colors=256)
            image.save()   # reset the multisave mode, disabling further saves

    else:
        import sys
        print(sys.argv)
        print(argv)
        canvasSize(nx*200, ny*200)
        print("just saving image")
        from pyformex.gui import image, guimain
        carpet(M)
        image.save('testje2.png')
        #return(all=True)
        guimain.quitGUI()


if __name__ == '__draw__':
    run()
# End
