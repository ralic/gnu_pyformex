# $Id$
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
"""Initialization of the pyFormex opengl module.

The opengl module contains everything related to the new OpenGL2 engine
of pyFormex. The initialization can make changes to the other
pyFormex modules in order to keep them working with the new engine.
"""
from __future__ import absolute_import, division, print_function

#### Set the Formex and Mesh actor method ####

def _set_actors():
    def actor(self,**kargs):

        if self.nelems() == 0:
            return None

        from pyformex.opengl.drawable import Actor

        return Actor(self,**kargs)

    from pyformex import formex
    formex.Formex.actor = actor
    from pyformex import mesh
    mesh.Mesh.actor = actor

#_set_actors()



# End
