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
"""OpenGL rendering objects for the new OpenGL2 engine.

"""
from __future__ import print_function

import pyformex as pf
from gui.drawable import *
from gui import colors
from OpenGL import GL
from OpenGL.arrays.vbo import VBO
from shader import Shader
from attributes import Attributes
from formex import Formex
from mesh import Mesh
from elements import elementType,_default_eltype
import geomtools as gt
import arraytools as at
import numpy as np
import utils


### Drawable Objects ###############################################




def glObjType(nplex):
    if nplex <= 3:
        return [GL.GL_POINTS,GL.GL_LINES,GL.GL_TRIANGLES][nplex-1]
    else:
        # everything higher is a polygon
        #
        #  THIS IS BAD: CAN ONLY DRAW A SINGLE POLYGON, NOT MULTIPLE!!!
        #
        #return GL.GL_TRIANGLE_FAN

        raise ValueError,"Can only draw plexitude <= 3!"


class Drawable(Attributes):
    """Proposal for drawn objects

    __init__:  store all static values: attributes, geometry, vbo's
    prepare: creates sanitized and derived attributes/data
    render: push values to shader and render the object

    __init__ is only dependent on input attributes and geometry

    prepare may depend on current canvas settings:
      mode, transparent, avgnormals

    render depends on canvas and renderer

    This is the basic drawable object. It can not have extras nor
    children. The geometry is initialized by a coords,elems
    tuple. This class is normally not added directly to renderer,
    but through one of the *Actor classes.
    The passed parameters should at least contain vbo.
    """

    # A list of acceptable attributes in the drawable
    ## attributes = Shader.uniforms + [
    ##     'glmode', 'frontface', 'backface', 'vbo', 'ibo', 'nbo', 'cbo',
    ##     'color',
    ##     ]
    attributes = [
        'frontface', 'backface', 'subelems', 'color',
        'vbo', 'nbo'
        ]

    def __init__(self,parent,**kargs):
        """Create a new drawable."""

        kargs = utils.selectDict(kargs,Drawable.attributes)
        Attributes.__init__(self,kargs,default=parent)
        #print("ATTRIBUTES STORED IN DRAWABLE",self)
        #print("ATTRIBUTES STORED IN PARENT",parent)

        # The final plexitude of the drawn objects
        if self.subelems is not None:
            self.nplex = self.subelems.shape[-1]
        else:
            self.nplex = self._fcoords.shape[-2]
        self.glmode = glObjType(self.nplex)

        self.prepareColor()
        #self.prepareNormals()  # The normals are currently always vertex
        self.prepareSubelems()


    def prepareColor(self):
        """Prepare the colors for the shader."""
        #print("PREPARECOLOR")
        # Set derived uniforms for shader
        # colormode:
        # 0 = None
        # 1 = object
        # 2 = element
        # 3 = vertex
        if self.color is None:
            self.colormode = 0
        else:
            self.colormode = self.color.ndim

        if self.colormode == 1:
            self.objectColor = self.color
        elif self.colormode == 2:
            self.vertexColor = at.multiplex(self.color,self.object.nplex())
            print ("Multiplexing colors: %s -> %s " % (self.color.shape,self.vertexColor.shape))
            self.colormode = 3
        elif self.colormode == 3:
            self.vertexColor = self.color

        if self.vertexColor is not None:
            self.cbo = VBO(self.vertexColor.astype(float32))
        #print("SELF.COLORMODE = %s" % (self.colormode))


    def prepareSubelems(self):
        """Create an index buffer to draw subelements

        This is always used for nplex > 3, but also to draw the edges
        for nplex=3.
        """
        if self.subelems is not None:
            self.ibo = VBO(self.subelems.astype(int32),target=GL.GL_ELEMENT_ARRAY_BUFFER)


    def render(self,renderer):
        """Render the geometry of this object"""

        def render_geom():
            if self.ibo:
                GL.glDrawElementsui(self.glmode,self.ibo)
            else:
                GL.glDrawArrays(self.glmode,0,asarray(self.vbo.shape[:-1]).prod())

        self.builtin = renderer.shader.builtin
        renderer.shader.loadUniforms(self)

        self.vbo.bind()
        if self.builtin:
            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
            GL.glVertexPointerf(self.vbo)
        else:
            GL.glEnableVertexAttribArray(renderer.shader.attribute['vertexPosition'])
            GL.glVertexAttribPointer(renderer.shader.attribute['vertexPosition'],3, GL.GL_FLOAT,False,0,self.vbo)

        if self.ibo:
            self.ibo.bind()

        if self.nbo:
            self.nbo.bind()
            if self.builtin:
                GL.glEnableClientState(GL.GL_NORMAL_ARRAY)
                GL.glNormalPointerf(self.nbo)
            else:
                GL.glEnableVertexAttribArray(renderer.shader.attribute['vertexNormal'])
                GL.glVertexAttribPointer(renderer.shader.attribute['vertexNormal'],3, GL.GL_FLOAT,False,0,self.nbo)

        if self.cbo:
            self.cbo.bind()
            if self.builtin:
                GL.glEnableClientState(GL.GL_COLOR_ARRAY)
                GL.glColorPointerf(self.cbo)
            else:
                GL.glEnableVertexAttribArray(renderer.shader.attribute['vertexColor'])
                GL.glVertexAttribPointer(renderer.shader.attribute['vertexColor'],3, GL.GL_FLOAT,False,0,self.cbo)


        if self.frontface:
            # Draw front faces
            GL.glEnable(GL.GL_CULL_FACE)
            GL.glCullFace(GL.GL_BACK)
        elif self.backface:
            # Draw back faces
            GL.glEnable(GL.GL_CULL_FACE)
            GL.glCullFace(GL.GL_FRONT)
        else:
            GL.glDisable(GL.GL_CULL_FACE)

        render_geom()

        GL.glDisable(GL.GL_CULL_FACE)

        if self.ibo:
            self.ibo.unbind()
        if self.cbo:
            self.cbo.unbind()
            if self.builtin:
                GL.glDisableClientState(GL.GL_COLOR_ARRAY)
            else:
                GL.glDisableVertexAttribArray(renderer.shader.attribute['vertexColor'])
        if self.nbo:
            self.nbo.unbind()
            if self.builtin:
                GL.glDisableClientState(GL.GL_NORMAL_ARRAY)
            else:
                GL.glDisableVertexAttribArray(renderer.shader.attribute['vertexNormal'])
        self.vbo.unbind()
        if self.builtin:
            GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        else:
            GL.glDisableVertexAttribArray(renderer.shader.attribute['vertexPosition'])


def polygonFaceIndex(n):
    i0 = (n-1) * ones(n-1)
    i1 = arange(n-1)
    i2 = i1+1
    return column_stack([i0,i1,i2])


def polygonEdgeIndex(n):
    i1 = arange(n)
    i2 = roll(i1,i)
    return column_stack([i0,i1])


class GeomActor(Attributes):
    """Proposal for drawn objects

    __init__:  store all static values: attributes, geometry, vbo's
    prepare: creates sanitized and derived attributes/data
    render: push values to shader and render the object

    __init__ is only dependent on input attributes and geometry

    prepare may depend on current canvas settings:
      mode, transparent, avgnormals

    render depends on canvas and renderer

    If the actor does not have a name, it will be given a
    default one.

    The actor has the following attributes, initialized or computed on demand

    """

    # default names for the actors
    defaultname = utils.NameSequence('object-0')


    def __init__(self,obj,**kargs):

        if 'name' not in kargs:
            kargs['name'] = GeomActor.defaultname.next()

        Attributes.__init__(self)

        # Check it is something we can draw
        if not isinstance(obj,Mesh) and not isinstance(obj,Formex):
            raise ValueError,"Object is of type %s.\nCan only render Mesh, Formex and objects that can be converted to Formex" % type(obj)
        self.object = obj

        if isinstance(obj,Mesh): # should we store coords, elems and eltype?
            coords = obj.coords.astype(float32)
            elems = obj.elems.astype(int32)
            eltype = obj.elName()

        elif isinstance(obj,Formex):
            coords = obj.coords.astype(float32)
            elems = None
            eltype = obj.eltype
            #
            # We always want an eltype for drawing
            #
            if eltype is None and obj.nplex() <= 4:
                # Set default eltype
                eltype = _default_eltype[obj.nplex()]

        self.eltype = elementType(eltype)
        #print("ELTYPE %s" % self.eltype)

        self.children = []

        # Acknowledge all object attributes and passed parameters
        self.update(obj.attrib)
        self.update(kargs)

        # Store minimal data
        coords = coords.astype(float32)
        if elems is None:
            self._fcoords = coords
        else:
            self._coords = coords.reshape(-1,3)
            self._elems = elems.astype(int32)

        # Currently do everything in Formex model
        # And we always need this one
        self.vbo = VBO(self.fcoords)


    @property
    def coords(self):
        """Return the fused coordinates of the object"""
        if self._coords is None:
            if self._fcoords is None:
                raise ValueError,"Object has neither _coords nor _fcoords"
            self._coords,self._elems = self._fcoords.fuse()
        return self._coords


    @property
    def elems(self):
        """Return the original elems of the object"""
        if self._elems is None:
            if self._fcoords is None:
                raise ValueError,"Object has neither _coords nor _fcoords"
            self._coords,self._elems = self._fcoords.fuse()
        return self._elems


    @property
    def fcoords(self):
        """Return the full coordinate set of the object"""
        if self._fcoords is None:
            if self._coords is None or self._elems is None:
                raise ValueError,"Object has neither _coords nor _fcoords"
            self._fcoords = self._coords[self._elems]
        return self._fcoords


    @property
    def faces(self):
        """Return the elems of the object as they will be drawn

        This returns a 2D index in a single element. All elements
        should have compatible node numberings.
        """
        if self._faces is None:
            if self.eltype is not None:
                self._faces = self.eltype.getDrawFaces()[0]
            else:
                if self.object.nplex() > 3:
                    # It is a polygon. We should create polygon elementtype!!
                    self._faces = polygonFaceIndex(self.object.nplex())
        return self._faces


    @property
    def edges(self):
        """Return the edges of the object as they will be drawn

        This returns a 2D index in a single element. All elements
        should have compatible node numberings.
        """
        if self._edges is None:
            if self.eltype is not None:
                self._edges = self.eltype.getDrawEdges()[0]
            else:
                if self.object.nplex() > 3:
                    # It is a polygon. We should create polygon elementtype!!
                    self._edges = polygonEdgeIndex(self.object.nplex())
        return self._edges


    @property
    def b_normals(self):
        """Return individual normals at all vertices of all elements"""
        if self._normals is None:
            self._normals = gt.polygonNormals(self.fcoords.astype(float32))
            print("COMPUTED NORMALS: %s" % str(self._normals.shape))
        return self._normals


    @property
    def b_avgnormals(self):
        """Return averaged normals at the vertices"""
        if self._avgnormals is None:
            tol = pf.cfg['render/avgnormaltreshold']
            self._avgnormals = gt.averageNormals(self.coords,self.elems,False,tol).astype(float32)
            print("COMPUTE AVGNORMALS: %s" % str(self._avgnormals.shape))
        return self._avgnormals


    def prepare(self,renderer):
        """Prepare the attributes for the renderer.

        This sanitizes and completes the attributes for the renderer.
        Since the attributes may be dependent on the rendering mode,
        this method is called on each mode change.
        """
        #print("PREPARE ACTOR")

        self.setColor(self.color,self.colormap)
        self.setBkColor(self.bkcolor,self.bkcolormap)
        self.setAlpha(self.alpha,self.bkalpha)
        self.setLineWidth(self.linewidth)
        self.setLineStipple(self.linestipple)

        self.changeMode(renderer)

        #### CHILDREN ####
        for child in self.children:
            child.prepare(renderer)


    def changeMode(self,renderer):
        """Modify the actor according to the specified mode"""
        #print("GEOMACTOR.changeMode")
        self.drawable = []
        self._prepareNormals(renderer)
        # Draw the colored faces/edges
        if renderer.mode == 'wireframe' and self.object.nplex() >= 3:
            self._addEdges(renderer)
        else:
            self._addFaces(renderer)
        # Overlay the black edges (or not)
        self._addWires(renderer)


    def _prepareNormals(self,renderer):
        """Prepare the normals buffer object for the actor.

        The normals buffer object depends on the renderer settings:
        lighting, avgnormals
        """
        if renderer.canvas.settings.lighting:
            if renderer.canvas.settings.avgnormals:
                normals = self.b_avgnormals
            else:
                normals = self.b_normals
            # Normals are always full fcoords size
            print("SIZE OF NORMALS: %s; COORDS: %s" % (normals.size,self.fcoords.size))
            self.nbo = VBO(normals)



    def fullElems(self):
        """Return an elems index for the full coords set"""
        nelems,nplex = self.fcoords.shape[:2]
        return arange(nelems*nplex).reshape(nelems,nplex)


    def subElems(self,selector):
        """Create an index for the drawable subelems

        This index always refers to the full coords (fcoords).
        The selector is 2D (nsubelems, nsubplex)
        If selector is None, returns None
        """
        if selector is None:
            return None
        else:
            # The elems index defining the original elements
            # based on the full fcoords
            elems = self.fullElems()
            #print("FULL ELEMS",elems.shape,elems)
            return elems[:,selector].reshape(-1,selector.shape[-1])


    def _addFaces(self,renderer):
        """Draw the elems"""
        #print("ADDFACES %s" % self.faces)
        elems = self.subElems(self.faces)
        #if elems is not None:
            #print("ADDFACES SIZE %s" % (elems.shape,))
        if ( self.bkcolor is not None or
             self.bkalpha is not None or
             renderer.canvas.settings.alphablend ):
            # Draw both sides separately
            # First, front sides
            self.drawable.append(Drawable(self,subelems=elems,frontface=True))
            # Then back sides
            extra = Attributes()
            if self.bkalpha is not None:
                extra.alpha = self.alpha
            if self.bkcolor is not None:
                extra.color = self.bkcolor
            # !! What about colormap?
            self.drawable.append(Drawable(self,subelems=elems,backface=True,**extra))
        else:
            # Just draw both sides at once
            self.drawable.append(Drawable(self,subelems=elems))


    def _addEdges(self,renderer):
        """Draw the edges"""
        #print("ADDEDGES %s" % self.edges)
        if self.edges is not None:
            elems = self.subElems(self.edges)
            #if elems is not None:
                #print("ADDEDGES SIZE %s" % (elems.shape,))
            self.drawable.append(Drawable(self,subelems=elems))


    def _addWires(self,renderer):
        """Add or remove the edges depending on rendering mode"""
        wiremode = renderer.canvas.settings.wiremode
        elems = None
        if wiremode > 0 and self.edges is not None:
            if wiremode == 1:
                # all edges:
                #print("ADDWIRES %s" % self.edges)
                elems = self.subElems(self.edges)
            elif wiremode == 2:
                # border edges
                #print("SELF.ELEMS",self.elems)
                inv = at.inverseIndex(self.elems.reshape(-1,1))[:,-1]
                #print("INVERSE",inv)
                M = Mesh(self.coords,self.elems)
                elems = M.getFreeEntities(level=1)
                elems = inv[elems]
                #print("ELEMS",elems)
            elif wiremode == 3:
                # feature edges
                print("FEATURE EDGES NOT YET IMPLEMENTED")


        if elems is not None and elems.size > 0:
            #print("ADDWIRES SIZE %s" % (elems.shape,))
            self.drawable.append(Drawable(self,subelems=elems,lighting=False,color = array(black),opak=True))


    def setColor(self,color,colormap=None):
        """Set the color of the Actor."""
        if type(color) is str:
            if color == 'prop' and hasattr(self.object,'prop'):
                color = self.object.prop
            elif color == 'random':
                # create random colors
                color = np.random.rand(F.nelems(),3)

        color,colormap = saneColorSet(color,colormap,self.fcoords.shape)

        if color is not None:
            if color.dtype.kind == 'i':
                # We have a color index
                if colormap is None:
                    colormap = array(colors.palette)
                print("PALETTE:%s"%colormap)
                color = colormap[color]

            print("VERTEX SHAPE = %s" % (self.fcoords.shape,))
            print("COLOR SHAPE = %s" % (color.shape,))

        self.color = color


    def setBkColor(self,color,colormap=None):
        """Set the backside color of the Actor."""
        self.bkcolor,self.bkcolormap = saneColorSet(color,colormap,self.fcoords.shape)


    def setAlpha(self,alpha,bkalpha=None):
        """Set the Actors alpha value."""
        try:
            self.alpha = float(alpha)
        except:
            del self.alpha
        try:
            self.bkalpha = float(bkalpha)
        except:
            del self.bkalpha
        self.opak = (self.alpha == 1.0) or (self.bkalpha == 1.0 )


    def setLineWidth(self,linewidth):
        """Set the linewidth of the Drawable."""
        self.linewidth = saneLineWidth(linewidth)

    def setLineStipple(self,linestipple):
        """Set the linewidth of the Drawable."""
        self.linestipple = saneLineStipple(linestipple)


    def render(self,renderer):
        """Render the geometry of this object"""

        if self.modified:
            #print("GeomActor.render: %s" % self.alpha)
            renderer.shader.loadUniforms(self)
            self.modified = False

        for obj in self.drawable:
            obj.render(renderer)

        for obj in self.children:
            obj.render(renderer)


### End