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

"""Elements

This example is intended for testing the drawing functions for each of the
implemented element types.
"""
from __future__ import absolute_import, division, print_function


_status = 'checked'
_level = 'normal'
_topics = ['geometry', 'mesh']
_techniques = ['dialog', 'elements']

from pyformex.gui.draw import *

from pyformex.elements import elementType,elementTypes
from pyformex.mesh import Mesh
from pyformex import utils
from pyformex import olist


colors = [black, blue, yellow, red]

def showElement(eltype, options):
    print(eltype)
    clear()
    drawText("Element type: %s" %eltype, (100, 200), size=18, color=black)
    el = elementType(eltype)
    print(el)

    if options['Show report']:
        print(el.report())

    M = el.toMesh()

    ndim = el.ndim

    if ndim == 3:
        view('iso')
        smooth()
    else:
        view('front')
        if options['Force dimensionality']:
            flatwire()
        else:
            smoothwire()

    #print options['Deformed']
    if options['Deformed']:
        M.coords = M.coords.addNoise(rsize=0.1)
        if options['Force dimensionality']:
            if ndim < 3:
                M.coords[..., 2] = 0.0
            if ndim < 2:
                M.coords[..., 1] = 0.0

    i = 'xyz'.find(options['Mirrored'])
    if i>=0:
        M = M.trl(i, 0.2)
        M = M + M.reflect(i)

    M.setProp([5, 6])

    if options['Draw as'] == 'Formex':
        M = M.toFormex()
    elif options['Draw as'] == 'Border':
        M = M.getBorderMesh()

    draw(M.coords)#,color=None,wait=False)
    drawNumbers(M.coords, color=None)


    if options['Color setting'] == 'prop':
        draw(M)
    else:
        draw(M, color=red, bkcolor=blue)



def run():
    ElemList = []
    for ndim in [0, 1, 2, 3]:
        ElemList += elementTypes(ndim)

    res = {
        'Deformed': True,
        'Mirrored': 'No',
        'Draw as': 'Mesh',
        'Color setting': 'direct',
        'Force dimensionality': False,
        'Show report': False,
        }
    res.update(pf.PF.get('Elements_data', {}))
    #print res

    res = askItems(
        store=res,
        items=[
            _I('Element Type', choices=['All',]+ElemList),
            _I('Deformed', itemtype='bool'),
            _I('Mirrored', itemtype='radio', choices=['No', 'x', 'y', 'z']),
            _I('Draw as', itemtype='radio', choices=['Mesh', 'Formex', 'Border']),
            _I('Color setting', itemtype='radio', choices=['direct', 'prop']),
            _I('Force dimensionality', itemtype='bool'),
            _I('Show report', itemtype='bool'),
            ])
    if not res:
        return

    # save the results for persistence
    pf.PF['Elements_data'] = res

    eltype = res['Element Type']
    if eltype == 'All':
        ellist = ElemList
    else:
        ellist = [eltype]
    clear()
    #delay(1)
    for el in ellist:
        showElement(el, res)


if __name__ == '__draw__':
    run()
# End
