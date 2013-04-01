# $Id$
"""opengl/renderer.py

Python OpenGL framework for pyFormex

This OpenGL framework is intended to replace (in due time)
the current OpenGL framework in pyFormex.

(C) 2013 Benedict Verhegghe and the pyFormex project.

"""

import os
import pyformex as pf
from coords import bbox
import numpy as np
from OpenGL import GL
from shader import Shader
from OpenGL.arrays.vbo import VBO


class Renderer(object):

    def __init__(self,canvas=None):
        self.canvas = canvas
        self.camera = canvas.camera
        self.canvas.makeCurrent()

        self.shader = Shader()
        self._objects = []
        self._vbo = {}
        self._bbox = bbox([0.,0.,0.])


    def clear(self):
        self._objects = []
        self._vbo = {}


    def add(self,obj):
        #if not isinstance
        #obj = obj.toFormex()
        if obj.nplex() != 3:
            raise ValueError,"Can only add plex-3 objects"
        self._objects.append(obj)
        oid = id(obj)
        self._vbo[oid] = VBO(obj.coords)
        self._bbox = bbox([self._bbox,obj])
        self.canvas.camera.focus = self._bbox.center()
        print(self._bbox)


    def renderObject(self,obj):
        oid = id(obj)
        vbo = self._vbo[oid]
        vbo.bind()
        try:
            GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
            GL.glVertexPointerf(vbo)
            GL.glDrawArrays(GL.GL_TRIANGLES,0,vbo.size)
        finally:
            vbo.unbind()
            GL.glDisableClientState(GL.GL_VERTEX_ARRAY)


    def render(self):
        """Render the geometry for the scene."""
        self.shader.bind()

        # Get the current modelview*projection matrix
        print("MODELVIEW",self.camera.modelview)
        print("PROJECTION",self.camera.modelview)
        pvmat = self.camera.modelview * self.camera.projection
        print("PVM",pvmat)
        # Propagate the matrices to the uniforms of the shader
        loc = self.shader.uniform['perspective']
        GL.glUniformMatrix4fv(loc,1,True,pvmat.gl())

        try:
            for obj in self._objects:
                if hasattr(obj,'objectColor'):
                    # Propagate the color to the uniforms of the shader
                    loc = self.shader.uniform['objectColor']
                    GL.glUniformMatrix3x1fv(loc,1,False,obj.objectColor)

                self.renderObject(obj)
        finally:
            self.shader.unbind()


# End
