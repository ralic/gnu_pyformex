# $Id$
##
##  This file is part of pyFormex 0.8.9  (Fri Nov  9 10:49:51 CET 2012)
##  pyFormex is a tool for generating, manipulating and transforming 3D
##  geometrical models by sequences of mathematical operations.
##  Home page: http://pyformex.org
##  Project page:  http://savannah.nongnu.org/projects/pyformex/
##  Copyright 2004-2012 (C) Benedict Verhegghe (benedict.verhegghe@ugent.be) 
##  Distributed under the GNU General Public License version 3 or later.
##
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

"""Extended functionality of the Mesh class.

This module defines extended Mesh functionality which is considered to be
experimental, maybe incomplete or even buggy.

The functions in this module can be called as functions operating on a
Mesh object, but are also available as Mesh methods.
"""
from __future__ import print_function

from mesh import Mesh
from elements import elementType,_default_facetype
from formex import *
from utils import deprecation, warn


##############################################################################

#
# What is a ring
# What is returned?

def rings(self, sources=0, nrings=-1):
    """_
    It finds rings of elements connected to sources by a node.
    
    Sources can be a single element index (integer) or a list of element indices.
    A list of rings is returned, from zero (ie. the sources) to nrings.
    If nrings is negative (default), all rings are returned.
    """
#
# TODO: this should be made an example
#
    ## Example:
    
    ## S=Sphere(2)
    ## smooth()
    ## draw(S, mode='wireframe')
    ## drawNumbers(S, ontop=True, color='white')
    ## r=S.rings(sources=[2, 6], nrings=2)
    ## print(r)
    ## for i, ri in enumerate(r):
    ##     draw(S.select(ri).setProp(i), mode='smooth')
    
    if nrings == 0:
        return [array(sources)]
    r=self.frontWalk(startat=sources,maxval=nrings-1, frontinc=1)
    ar, rr= arange(len(r)), range(r.max()+1)
    return [ar[r==i] for i in rr ]


@utils.deprecation("depr_correctNegativeVolumes")
def correctNegativeVolumes(self):
    """_Modify the connectivity of negative-volume elements to make
    positive-volume elements.

    Negative-volume elements (hex or tet with inconsistent face orientation)
    may appear by error during geometrical trnasformations
    (e.g. reflect, sweep, extrude, revolve).
    This function fixes those elements.
    Currently it only works with linear tet and hex.
    """
    vol=self.volumes()<0.
    if self.elName()=='tet4':
        self.elems[vol]=self.elems[vol][:,  [0, 2, 1, 3]]
    if self.elName()=='hex8':
        self.elems[vol]=self.elems[vol][:,  [4, 5, 6, 7, 0, 1, 2, 3]]
    return self


def scaledJacobian(self, scaled=True):
    """
    Returns a quality measure for volume meshes.
    
    If scaled if False, it returns the Jacobian at the corners of each element.
    If scaled is True, it returns a quality metrics, being
    the minumum value of the scaled Jacobian in each element (at one corner, 
    the Jacobian divided by the volume of a perfect brick).
    Each tet or hex element gives a value between -1 and 1. 
    Acceptable elements have a positive scaled Jacobian. However, good 
    quality requires a minimum of 0.2.
    Quadratic meshes are first converted to linear.
    If the mesh contain mainly negative Jacobians, it probably has negative
    volumes and can be fixed with the  correctNegativeVolumes.
    """
    ne = self.nelems()
    if self.elName()=='hex20':
        self = self.convert('hex8')
    if self.elName()=='tet10':
        self = self.convert('tet4')      
    if self.elName()=='tet4':
        iacre=array([
        [[0, 1], [1, 2],[2, 0],[3, 2]],
        [[0, 2], [1, 0],[2, 1],[3, 1]],
        [[0, 3], [1, 3],[2, 3],[3, 0]],
        ], dtype=int)
        nc = 4
    if self.elName()=='hex8':
        iacre=array([
        [[0, 4], [1, 5],[2, 6],[3, 7], [4, 7], [5, 4],[6, 5],[7, 6]],
        [[0, 1], [1, 2],[2, 3],[3, 0], [4, 5], [5, 6],[6, 7],[7, 4]],
        [[0, 3], [1, 0],[2, 1],[3, 2], [4, 0], [5, 1],[6, 2],[7, 3]],
        ], dtype=int)
        nc = 8
    acre = self.coords[self.elems][:, iacre]
    vacre = acre[:, :,:,1]-acre[:, :,:,0]
    cvacre = concatenate(vacre, axis=1)

    J = vectorTripleProduct(*cvacre).reshape(ne, nc)
    if not scaled: 
        return J
    else:
        normvol = prod(length(cvacre), axis=0).reshape(ne, nc)#volume of 3 nprmal edges
        Jscaled = J/normvol
        return Jscaled.min(axis=1)


##############################################################################
#
# Initialize
#

def _auto_initialize():
    """Auto-initialize Mesh extensions.

    Calling this function will install some of the mesh functions
    defined in this modules as Mesh methods.
    This function is called when the module is loaded, so the functions
    installed here will always be available as Mesh methods just by
    importing the mesh_ext module.
    """
    Mesh.rings = rings
    Mesh.correctNegativeVolumes = correctNegativeVolumes
    Mesh.scaledJacobian = scaledJacobian
    
_auto_initialize()


# End
