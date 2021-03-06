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
"""This implements an OpenGL drawing widget for painting 3D scenes.

"""
from __future__ import absolute_import, division, print_function

import pyformex as pf

from pyformex import utils, coords
from pyformex import arraytools as at

from pyformex.mydict import Dict
from pyformex.odict import OrderedDict
from pyformex.collection import Collection
from pyformex.simple import cuboid2d
from pyformex.opengl import decors
from pyformex.opengl import colors
from .sanitize import saneColor
from .drawable import Actor
from .camera import Camera
from .renderer import Renderer
from .scene import Scene, ItemList

import numpy as np

from OpenGL import GL, GLU


def glVersion(mode='all'):
    return OrderedDict([
        ('vendor', str(GL.glGetString(GL.GL_VENDOR))),
        ('renderer', str(GL.glGetString(GL.GL_RENDERER))),
        ('version', str(GL.glGetString(GL.GL_VERSION))),
        ('glsl_version', str(GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION))),
        ])


libGL = None

def loadLibGL():
    # TODO
    # BV: UGLY! WE SHOULD GET RID OF THIS
    global libGL
    if libGL is None and pf.X11:
        from ctypes import cdll
        libGL = cdll.LoadLibrary("libGL.so.1")


def gl_pickbuffer():
    "Return a list of the 2nd numbers in the openGL pick buffer."
    buf = GL.glRenderMode(GL.GL_RENDER)
    return np.asarray([ r[2] for r in buf ])

# Used in CanvasSettings.glOverride !
from OpenGL.GL import glLineWidth as glLinewidth, glPointSize as glPointsize

fill_modes = [ GL.GL_FRONT_AND_BACK, GL.GL_FRONT, GL.GL_BACK ]
fill_mode = GL.GL_FRONT_AND_BACK

def glFillMode(mode):
    global fill_mode
    if mode in fill_modes:
        fill_mode = mode
def glFrontFill():
    glFillMode(GL.GL_FRONT)
def glBackFill():
    glFillMode(GL.GL_BACK)
def glBothFill():
    glFillMode(GL.GL_FRONT_AND_BACK)

def glFill(fill=True):
    if fill:
        GL.glPolygonMode(fill_mode, GL.GL_FILL)
    else:
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)

def glLineSmooth(onoff):
    if onoff is True:
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    elif onoff is False:
        GL.glDisable(GL.GL_LINE_SMOOTH)


def glLineStipple(factor, pattern):
    """Set the line stipple pattern.

    When drawing lines, OpenGl can use a stipple pattern. The stipple
    is defined by two values: a pattern (on/off) of maximum 16 bits,
    used on the pixel level, and a multiplier factor for each bit.

    If factor <= 0, the stippling is disabled.
    """
    print("Line stipple is currently not supported with gl2 engine")
    ## if factor > 0:
    ##     GL.glLineStipple(factor, pattern)
    ##     GL.glEnable(GL.GL_LINE_STIPPLE)
    ## else:
    ##     GL.glDisable(GL.GL_LINE_STIPPLE)

def glSmooth(smooth=True):
    """Enable smooth shading"""
    if smooth:
        GL.glShadeModel(GL.GL_SMOOTH)
    else:
        GL.glShadeModel(GL.GL_FLAT)

def glFlat():
    """Disable smooth shading"""
    glSmooth(False)


def onOff(onoff):
    """Convert On/Off strings to a boolean"""
    if isinstance(onoff, str):
        return (onoff.lower() == 'on')
    else:
        if onoff:
            return True
        else:
            return False


def glEnable(facility, onoff):
    """Enable/Disable an OpenGL facility, depending on onoff value

    facility is an OpenGL facility.
    onoff can be True or False to enable, resp. disable the facility, or
    None to leave it unchanged.
    """
    #pf.debug("%s: %s" % (facility,onoff),pf.DEBUG.DRAW)
    if onOff(onoff):
        #pf.debug("ENABLE",pf.DEBUG.DRAW)
        GL.glEnable(facility)
    else:
        #pf.debug("DISABLE",pf.DEBUG.DRAW)
        GL.glDisable(facility)


def glCulling(onoff=True):
    glEnable(GL.GL_CULL_FACE, onoff)
def glNoCulling():
    glCulling(False)


def glPolygonFillMode(mode):
    if isinstance(mode, str):
        mode = mode.lower()
        if mode == 'Front and Back':
            glBothFill()
        elif mode == 'Front':
            glFrontFill()
        elif mode == 'Back':
            glBackFill()


def glPolygonMode(mode):
    if isinstance(mode, str):
        mode = mode.lower()
        glFill(mode == 'fill')


def glShadeModel(model):
    if isinstance(model, str):
        model = model.lower()
        if model == 'smooth':
            glSmooth()
        elif model == 'flat':
            glFlat()


def glPolygonOffset(value):
    if value <= 0.0:
        GL.glDisable(GL.GL_POLYGON_OFFSET_FILL)
    else:
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glPolygonOffset(value, value)



############### OpenGL Lighting #################################

class Material(object):
    def __init__(self,name,ambient=0.2,diffuse=0.2,specular=0.9,emission=0.1,shininess=2.0):
        self.name = str(name)
        self.ambient = float(ambient)
        self.diffuse = float(diffuse)
        self.specular = float(specular)
        self.emission = float(emission)
        self.shininess = float(shininess)


    def setValues(self,**kargs):
        #print "setValues",kargs
        for k in kargs:
            #print k,kargs[k]
            if hasattr(self, k):
                #print getattr(self,k)
                setattr(self, k, float(kargs[k]))
                #print getattr(self,k)


    def dict(self):
        """Return the material light parameters as a dict"""
        return dict([(k, getattr(self, k)) for k in ['ambient', 'diffuse', 'specular', 'emission', 'shininess']])


    def __str__(self):
        return """MATERIAL: %s
    ambient:  %s
    diffuse:  %s
    specular: %s
    emission: %s
    shininess: %s
""" % (self.name, self.ambient, self.diffuse, self.specular, self.emission, self.shininess)


def getMaterials():
    mats = pf.refcfg['material']
    mats.update(pf.prefcfg['material'])
    mats.update(pf.cfg['material'])
    return mats


def createMaterials():
    mats = getMaterials()
    matdb = {}
    for m in mats:
        matdb[m] = Material(m,**mats[m])
    return matdb


class Light(object):
    """A class representing an OpenGL light.

    The light can emit 3 types of light: ambient, diffuse and specular,
    which can have different color and are all off by default.


    """

    def __init__(self,ambient=0.0,diffuse=0.0,specular=0.0,position=[0., 0., 1.],enabled=True):
        self.setValues(ambient, diffuse, specular, position)
        self.enable(enabled)

    def setValues(self,ambient=None,diffuse=None,specular=None,position=None):
        if ambient is not None:
            self.ambient = colors.GLcolor(ambient)
        if diffuse is not None:
            self.diffuse = colors.GLcolor(diffuse)
        if specular is not None:
            self.specular = colors.GLcolor(specular)
        if position is not None:
            self.position = at.checkArray(position, (3,), 'f')

    def enable(self,onoff=True):
        self.enabled = bool(onoff)

    def disable(self):
        self.enable(False)


    def __str__(self,name=''):
        return """LIGHT%s (enabled: %s):
    ambient color:  %s
    diffuse color:  %s
    specular color: %s
    position: %s
""" % (name, self.enabled, self.ambient, self.diffuse, self.specular, self.position)


class LightProfile(object):
    """A lightprofile contains all the lighting parameters.

    Currently this consists off:
    - `ambient`: the global ambient lighting (currently a float)
    - `lights`: a list of 1 to 4 Lights
    """

    def __init__(self, ambient, lights):
        self.ambient = ambient
        self.lights = lights


    def __str__(self):
        s = """LIGHTPROFILE:
    global ambient:  %s
    """ % self.ambient
        for i, l in enumerate(self.lights):
            s += '  ' + l.__str__(i)
        return s


##################################################################
#
#  The Canvas Settings
#


class CanvasSettings(Dict):
    """A collection of settings for an OpenGL Canvas.

    The canvas settings are a collection of settings and default values
    affecting the rendering in an individual viewport. There are two type of
    settings:

    - mode settings are set during the initialization of the canvas and
      can/should not be changed during the drawing of actors and decorations;
    - default settings can be used as default values but may be changed during
      the drawing of actors/decorations: they are reset before each individual
      draw instruction.

    Currently the following mode settings are defined:

    - bgmode: the viewport background color mode
    - bgcolor: the viewport background color: a single color or a list of
      colors (max. 4 are used).
    - bgimage: background image filename
    - slcolor: the highlight color
    - alphablend: boolean (transparency on/off)

    The list of default settings includes:

    - fgcolor: the default drawing color
    - bkcolor: the default backface color
    - colormap: the default color map to be used if color is an index
    - bklormap: the default color map to be used if bkcolor is an index
    - smooth: boolean (smooth/flat shading)
    - lighting: boolean (lights on/off)
    - culling: boolean
    - transparency: float (0.0..1.0)
    - avgnormals: boolean
    - wiremode: integer -3..3
    - pointsize: the default size for drawing points
    - marksize: the default size for drawing markers
    - linewidth: the default width for drawing lines

    Any of these values can be set in the constructor using a keyword argument.
    All items that are not set, will get their value from the configuration
    file(s).
    """

    # A collection of default rendering profiles.
    # These contain the values different from the overall defaults
    RenderProfiles = {
        'wireframe': Dict({
            'smooth': False,
            'fill': False,
            'lighting': False,
            'alphablend': False,
            'transparency': 1.0,
            'wiremode': -1,
            'avgnormals': False,
            }),
        'smooth': Dict({
            'smooth': True,
            'fill': True,
            'lighting': True,
            'alphablend': False,
            'transparency': 0.5,
            'wiremode': -1,
            'avgnormals': False,
            }),
        'smooth_avg': Dict({
            'smooth': True,
            'fill': True,
            'lighting': True,
            'alphablend': False,
            'transparency': 0.5,
            'wiremode': -1,
            'avgnormals': True,
            }),
        'smoothwire': Dict({
            'smooth': True,
            'fill': True,
            'lighting': True,
            'alphablend': False,
            'transparency': 0.5,
            'wiremode': 1,
            'avgnormals': False,
            }),
        'flat': Dict({
            'smooth': False,
            'fill': True,
            'lighting': False,
            'alphablend': False,
            'transparency': 0.5,
            'wiremode': -1,
            'avgnormals': False,
            }),
        'flatwire': Dict({
            'smooth': False,
            'fill': True,
            'lighting': False,
            'alphablend': False,
            'transparency': 0.5,
            'wiremode': 1,
            'avgnormals': False,
            }),
        }
    bgcolor_modes = [ 'solid', 'vertical', 'horizontal', 'full' ]
    edge_modes = [ 'none', 'feature', 'all' ]

    def __init__(self,**kargs):
        """Create a new set of CanvasSettings."""
        Dict.__init__(self)
        self.reset(kargs)

    def reset(self,d={}):
        """Reset the CanvasSettings to its defaults.

        The default values are taken from the configuration files.
        An optional dictionary may be specified to override (some of) these defaults.
        """
        self.update(pf.refcfg['canvas'])
        self.update(self.RenderProfiles[pf.prefcfg['draw/rendermode']])
        self.update(pf.prefcfg['canvas'])
        self.update(pf.cfg['canvas'])
        if d:
            self.update(d)

    def update(self,d,strict=True):
        """Update current values with the specified settings

        Returns the sanitized update values.
        """
        ok = self.checkDict(d, strict)
        Dict.update(self, ok)

    @classmethod
    def checkDict(clas,dict,strict=True):
        """Transform a dict to acceptable settings."""
        ok = {}
        for k, v in dict.items():
            try:
                if k in [ 'bgcolor', 'fgcolor', 'bkcolor', 'slcolor',
                          'colormap', 'bkcolormap' ]:
                    if v is not None:
                        v = saneColor(v)
                elif k in ['bgimage']:
                    v = str(v)
                elif k in ['smooth', 'fill', 'lighting', 'culling',
                           'alphablend', 'avgnormals',]:
                    v = bool(v)
                elif k in ['linewidth', 'pointsize', 'marksize']:
                    v = float(v)
                elif k in ['wiremode']:
                    v = int(v)
                elif k == 'linestipple':
                    v = [int(vi) for vi in v]
                elif k == 'transparency':
                    v = max(min(float(v), 1.0), 0.0)
                elif k == 'bgmode':
                    v = str(v).lower()
                    if not v in clas.bgcolor_modes:
                        raise
                elif k == 'marktype':
                    pass
                else:
                    raise
                ok[k] = v
            except:
                if strict:
                    raise ValueError("Invalid key/value for CanvasSettings: %s = %s" % (k, v))
        return ok

    def __str__(self):
        return utils.formatDict(self)


    ## def setMode(self):
    ##     """Activate the mode canvas settings in the GL machine."""
    ##     GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    ##     if self.bgcolor.ndim > 1:
    ##         color = self.bgcolor[0]
    ##     else:
    ##         color = self.bgcolor
    ##     GL.glClearColor(*colors.RGBA(color))


    def activate(self):
        """Activate the default canvas settings in the GL machine."""
        self.glOverride(self, self)


    @staticmethod
    def glOverride(settings, default):
        for k in settings:
            if k in ['smooth', 'fill', 'linewidth', 'pointsize']:
                func = globals()['gl'+k.capitalize()]
                func(settings[k])


### OLD: to be rmoved (still used in viewport)
def glSettings(settings):
    pf.debug("GL SETTINGS: %s" % settings, pf.DEBUG.DRAW)
    glShadeModel(settings.get('Shading', None))
    glCulling(settings.get('Culling', None))
    #glLighting(settings.get('Lighting', None))
    glLineSmooth(onOff(settings.get('Line Smoothing', None)))
    glPolygonFillMode(settings.get('Polygon Fill', None))
    glPolygonMode(settings.get('Polygon Mode', None))
    pf.canvas.update()


def extractCanvasSettings(d):
    """Split a dict in canvas settings and other items.

    Returns a tuple of two dicts: the first one contains the items
    that are canvas settings, the second one the rest.
    """
    return utils.select(d, pf.refcfg['canvas']), utils.remove(d, pf.refcfg['canvas'])

#############################################################################
#############################################################################
#
#  The Canvas
#
#############################################################################
#############################################################################

def print_camera(self):
    print(self.report())


def print_lighting(s):
    try:
        settings = pf.GUI.viewports.current.settings
        print("%s: LIGTHING %s (%s)" %(s, settings.lighting, id(settings)))
    except:
        print("No settings yet")


class Canvas(object):
    """A canvas for OpenGL rendering.

    The Canvas is a class holding all global data of an OpenGL scene rendering.
    This includes colors, line types, rendering mode.
    It also keeps lists of the actors and decorations in the scene.
    The canvas has a Camera object holding important viewing parameters.
    Finally, it stores the lighting information.

    It does not however contain the viewport size and position.
    """

    def __init__(self,settings={}):
        """Initialize an empty canvas with default settings."""
        #print("NEW CANVAS %s" % id(self))
        from pyformex.gui import views
        loadLibGL()
        self.scene = Scene(self)
        self.highlights = ItemList(self)
        self.camera = None
        self.triade = None
        self.settings = CanvasSettings(**settings)
        self.mode2D = False
        self.rendermode = None
        self.setRenderMode(pf.cfg['draw/rendermode'])
        self.resetLighting()
        #print("INIT: %s, %s" %(self.rendermode,self.settings.fill))
        self.view_angles = views.ViewAngles()
        self.cursor = None
        self.focus = False
        pf.debug("Canvas Setting:\n%s"% self.settings, pf.DEBUG.DRAW)
        self.makeCurrent()  # we need correct OpenGL context
        #print("CANVAS",glVersion())


    @property
    def actors(self):
        return self.scene.actors

    @property
    def bbox(self):
        return self.scene.bbox

    def sceneBbox(self):
        """Return the bbox of all actors in the scene"""
        from pyformex.coords import bbox
        return bbox(self.scene.actors)


    ## def enable_lighting(self, state):
    ##     """Toggle OpenGL lighting on/off."""
    ##     glLighting(state)


    def resetDefaults(self,dict={}):
        """Return all the settings to their default values."""
        self.settings.reset(dict)
        self.resetLighting()
        ## self.resetLights()

    def setAmbient(self, ambient):
        """Set the global ambient lighting for the canvas"""
        self.lightprof.ambient = float(ambient)

    def setMaterial(self, matname):
        """Set the default material light properties for the canvas"""
        self.material = pf.GUI.materials[matname]


    def resetLighting(self):
        """Change the light parameters"""
        self.lightmodel = pf.cfg['render/lightmodel']
        self.setMaterial(pf.cfg['render/material'])
        self.lightset = pf.cfg['render/lights']
        lights = [ Light(**pf.cfg['light/%s' % light]) for light in self.lightset ]
        self.lightprof = LightProfile(pf.cfg['render/ambient'], lights)


    def resetOptions(self):
        """Reset the Drawing options to some defaults"""
        self.drawoptions = dict(
            view = None,        # Keep the current camera angles
            bbox = 'auto',      # Automatically zoom on the drawed object
            clear_ = False,     # Clear on each drawing action
            shrink = False,
            shrink_factor = 0.8,
#            marksize = 5.0,
#            color = 'prop',
            wait = True,
            silent = True
            )

    def setOptions(self, d):
        """Set the Drawing options to some values"""

        ## # BEWARE
        ## # We rename the 'clear' to 'clear_', because we use a Dict
        ## # to store these (in __init__.draw) and Dict does not allow
        ## # a 'clear' key.

        if 'clear' in d and isinstance(d['clear'],bool):
            d['clear_'] = d['clear']
            del d['clear']
        self.drawoptions.update(d)


    def setRenderMode(self,mode,lighting=None):
        """Set the rendering mode.

        This sets or changes the rendermode and lighting attributes.
        If lighting is not specified, it is set depending on the rendermode.

        If the canvas has not been initialized, this merely sets the
        attributes self.rendermode and self.settings.lighting.
        If the canvas was already initialized (it has a camera), and one of
        the specified settings is different from the existing, the new mode
        is set, the canvas is re-initialized according to the newly set mode,
        and everything is redrawn with the new mode.
        """
        if mode not in CanvasSettings.RenderProfiles:
            raise ValueError("Invalid render mode %s" % mode)

        self.settings.update(CanvasSettings.RenderProfiles[mode])
        if lighting is None:
            lighting = self.settings.lighting

        if self.camera:
            if mode != self.rendermode or lighting != self.settings.lighting:
                self.rendermode = mode
                self.scene.changeMode(self, mode)

            self.settings.lighting = lighting
            self.reset()

        else:
            pf.debug("NO camera, but setting rendermode anyways",pf.DEBUG.OPENGL)
            self.rendermode = mode


    def setWireMode(self,state,mode=None):
        """Set the wire mode.

        This toggles the drawing of edges on top of 2D and 3D geometry.
        State is either True or False, mode is 1, 2 or 3 to switch:

        1: all edges
        2: feature edges
        3: border edges

        If no mode is specified, the current wiremode is used. A negative
        value inverses the state.
        """
        #print("CANVAS.setWireMode %s %s" % (state, mode))
        oldstate = self.settings.wiremode
        if mode is None:
            mode = abs(oldstate)
        if state is False:
            state = -mode
        else:
            state = mode
        self.settings.wiremode = state
        self.do_wiremode(state, oldstate)


    def setToggle(self, attr, state):
        """Set or toggle a boolean settings attribute

        Furthermore, if a Canvas method do_ATTR is defined, it will be called
        with the old and new toggle state as a parameter.
        """
        #print("CANVAS.setTogggle %s = %s"%(attr,state))
        oldstate = self.settings[attr]
        if state not in [True, False]:
            state = not oldstate
        self.settings[attr] = state
        try:
            func = getattr(self, 'do_'+attr)
            func(state, oldstate)
        except:
            pass


    def setLighting(self, onoff):
        self.setToggle('lighting', onoff)


    def do_wiremode(self, state, oldstate):
        """Change the wiremode"""
        #print("CANVAS.do_wiremode: %s -> %s"%(oldstate, state))
        if state != oldstate and (state>0 or oldstate>0):
            # switching between two <= modes does not change anything
            #print("Changemode %s" % self.settings.wiremode)
            self.scene.changeMode(self)
            self.display()


    def do_alphablend(self, state, oldstate):
        """Toggle alphablend on/off."""
        #print("CANVAS.do_alphablend: %s -> %s"%(state,oldstate))
        if state != oldstate:
            #self.renderer.changeMode(self)
            self.scene.changeMode(self)
            self.display()


    def do_lighting(self, state, oldstate):
        """Toggle lights on/off."""
        #print("CANVAS.do_lighting: %s -> %s"%(state,oldstate))
        if state != oldstate:
            self.enable_lighting(state)
            self.scene.changeMode(self)
            self.display()


    def do_avgnormals(self, state, oldstate):
        #print("CANVAS.do_avgnormals: %s -> %s" % (state, oldstate))
        if state!=oldstate and self.settings.lighting:
            self.scene.changeMode(self)
            self.display()


    def setLineWidth(self, lw):
        """Set the linewidth for line rendering."""
        self.settings.linewidth = float(lw)


    def setLineStipple(self, repeat, pattern):
        """Set the linestipple for line rendering."""
        self.settings.update({'linestipple':(repeat, pattern)})


    def setPointSize(self, sz):
        """Set the size for point drawing."""
        self.settings.pointsize = float(sz)


    def setBackground(self,color=None,image=None):
        """Set the color(s) and image.

        Change the background settings according to the specified parameters
        and set the canvas background accordingly. Only (and all) the specified
        parameters get a new value.

        Parameters:

        - `color`: either a single color, a list of two colors or a list of
          four colors.
        - `image`: an image to be set.
        """
        self.scene.backgrounds.clear()
        if color is not None:
            self.settings.update(dict(bgcolor=color))
        if image is not None:
            self.settings.update(dict(bgimage=image))
        color = self.settings.bgcolor
        if color.ndim == 1 and not self.settings.bgimage:
            pf.debug("Clearing fancy background", pf.DEBUG.DRAW)
        else:
            self.createBackground()


    def createBackground(self):
        """Create the background object."""
        F = cuboid2d(xmin=[-1.,-1.],xmax=[1.,1.])
        # TODO: Currently need a Mesh for texture
        F = F.toMesh()
        image = None
        if self.settings.bgimage:
            from pyformex.plugins.imagearray import qimage2numpy
            try:
                image = qimage2numpy(self.settings.bgimage, indexed=False)
            except:
                pass
        actor = Actor(F,name='background',rendermode='smooth',color=[self.settings.bgcolor],texture=image,rendertype=3,opak=True,lighting=False,view='front')
        #print("SCENE %s" % id(self.scene))
        self.scene.addAny(actor)
        #print(self.scene.backgrounds[0])
        self.update()



    def setFgColor(self, color):
        """Set the default foreground color."""
        self.settings.fgcolor = colors.GLcolor(color)


    def setSlColor(self, color):
        """Set the highlight color."""
        self.settings.slcolor = colors.GLcolor(color)


    def setTriade(self,pos='lb',siz=100,triade=None):
        """Set the Triade for this canvas.

        Display the Triade on the current viewport.
        The Triade is a reserved Actor displaying the orientation of
        the global axes. It has special methods to show/hide it.
        See also: :meth:`removeTriade`, :meth:`hasTriade`

        Parameters:

        - `pos`: string of two characters. The characters define the horizontal
          (one of 'l', 'c', or 'r') and vertical (one of 't', 'c', 'b') position
          on the camera's viewport. Default is left-bottom.
        - `siz`: float: intended size (in pixels) of the triade.
        - `triade`: None or Geometry: defines the Geometry to be used for
          representing the global axes.

          If None, use the previously set triade, or set a default if no
          previous.

          If Geometry, use this to represent the axes. To be useful and properly
          displayed, the Geometry's bbox should be around [(-1,-1,-1),(1,1,1)].
          Drawing attributes may be set on the Geometry to influence
          the appearence. This allows to fully customize the Triade.

        """
        if self.triade:
            self.removeTriade()
        if triade:
            from pyformex.opengl.draw import draw
            self.triade = None
            x, y, w, h = GL.glGetIntegerv(GL.GL_VIEWPORT)
            if pos[0] == 'l':
                x0 = x + siz
            elif pos[0] =='r':
                x0 = x + w - siz
            else:
                x0 = x + w // 2
            if pos[1] == 'b':
                y0 = y + siz
            elif pos[1] == 't':
                y0 = y + h - siz
            else:
                y0 = y + h // 2
            A = draw(triade.scale(siz),rendertype=-2,single=True,size=siz,x=x0,y=y0)
            self.triade = A
        elif self.triade:
            self.addAny(self.triade)


    def removeTriade(self):
        """Remove the Triade from the canvas.

        Remove the Triade from the current viewport.
        The Triade is a reserved Actor displaying the orientation of
        the global axes. It has special methods to draw/undraw it.
        See also: :meth:`setTriade`, :meth:`hasTriade`

        """
        if self.hasTriade():
            self.removeAny(self.triade)


    def hasTriade(self):
        """Check if the canvas has a Triade displayed.

        Return True if the Triade is currently displayed.
        The Triade is a reserved Actor displaying the orientation of
        the global axes.
        See also: :meth:`setTriade`, :meth:`removeTriade`

        """
        return self.triade is not None and self.triade in self.scene.decorations


    def initCamera(self):
        self.makeCurrent()  # we need correct OpenGL context for camera
        self.camera = Camera()
        ## if pf.options.testcamera:
        ##     self.camera.modelview_callback = print_camera
        ##     self.camera.projection_callback = print_camera
        self.renderer = Renderer(self)


    def clearCanvas(self):
        """Clear the canvas to the background color."""
        color = self.settings.bgcolor
        if color.ndim > 1:
            color = color[0]
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glClearColor(*colors.RGBA(color))
        self.setDefaults()


    def setSize (self, w, h):
        if h == 0:	# prevent divide by zero
            h = 1
        GL.glViewport(0, 0, w, h)
        self.aspect = float(w)/h
        self.camera.setLens(aspect=self.aspect)
        ## if self.scene.background:
        ##     # recreate the background to match the current size
        ##     self.createBackground()
        self.display()


    def drawit(self, a):
        """_Perform the drawing of a single item"""
        self.setDefaults()
        a.draw(self)


    def setDefaults(self):
        """Activate the canvas settings in the GL machine."""
        self.settings.activate()
        #self.enable_lighting(self.settings.lighting)
        GL.glDepthFunc(GL.GL_LESS)


    def overrideMode(self, mode):
        """Override some settings"""
        settings = CanvasSettings.RenderProfiles[mode]
        CanvasSettings.glOverride(settings, self.settings)


    def reset(self):
        """Reset the rendering engine.

        The rendering machine is initialized according to self.settings:
        - self.rendermode: one of
        - self.lighting
        """
        self.setDefaults()
        self.setBackground(self.settings.bgcolor, self.settings.bgimage)
        self.clearCanvas()
        GL.glClearDepth(1.0)	       # Enables Clearing Of The Depth Buffer
        GL.glEnable(GL.GL_DEPTH_TEST)	       # Enables Depth Testing
        #GL.glEnable(GL.GL_CULL_FACE)
        if self.rendermode == 'wireframe':
            glPolygonOffset(0.0)
        else:
            glPolygonOffset(1.0)


    def glinit(self):
        """Initialize the rendering engine.

        """
        self.reset()


    def glupdate(self):
        """Flush all OpenGL commands, making sure the display is updated."""
        GL.glFlush()


    # TODO: this is here for compatibility reasons
    # should be removed after complete transition to shaders
    def draw_sorted_objects(self, objects, alphablend):
        """Draw a list of sorted objects through the fixed pipeline.

        If alphablend is True, objects are separated in opaque
        and transparent ones, and the opaque are drawn first.
        Inside each group, ordering is preserved.
        Else, the objects are drawn in the order submitted.
        """
        if alphablend:
            opaque = [ a for a in objects if a.opak ]
            transp = [ a for a in objects if not a.opak ]
            for obj in opaque:
                self.setDefaults()
                obj.draw(canvas=self)
            GL.glEnable (GL.GL_BLEND)
            GL.glDepthMask (GL.GL_FALSE)
            if pf.cfg['draw/disable_depth_test']:
                GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glBlendFunc (GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
            for obj in transp:
                self.setDefaults()
                obj.draw(canvas=self)
            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glDepthMask (GL.GL_TRUE)
            GL.glDisable (GL.GL_BLEND)
        else:
            for obj in objects:
                self.setDefaults()
                obj.draw(canvas=self)


    def display(self):
        """(Re)display all the actors in the scene.

        This should e.g. be used when actors are added to the scene,
        or after changing  camera position/orientation or lens.
        """
        #pf.debugt("UPDATING CURRENT OPENGL CANVAS",pf.DEBUG.DRAW)
        self.makeCurrent()

        self.clearCanvas()
        glSmooth()
        glFill()

        # draw the focus rectangle if more than one viewport
        if len(pf.GUI.viewports.all) > 1 and pf.cfg['gui/showfocus']:
            if self.hasFocus(): # QT focus
                self.draw_focus_rectangle(0, color=colors.blue)
            if self.focus:      # pyFormex DRAW focus
                self.draw_focus_rectangle(2, color=colors.red)

        # draw the highlighted actors
        pf.debug("draw highlights", pf.DEBUG.DRAW)
        if self.highlights:
            for actor in self.highlights:
                self.setDefaults()
                actor.draw(canvas=self)

        # Draw the opengl2 actors
        pf.debug("opengl2 shader rendering", pf.DEBUG.DRAW)
        self.renderer.render(self.scene)

        # make sure canvas is updated
        GL.glFlush()


    def zoom_2D(self,zoom=None):
        if zoom is None:
            zoom = (0, self.width(), 0, self.height())
        GLU.gluOrtho2D(*zoom)


    def begin_2D_drawing(self):
        """Set up the canvas for 2D drawing on top of 3D canvas.

        The 2D drawing operation should be ended by calling end_2D_drawing.
        It is assumed that you will not try to change/refresh the normal
        3D drawing cycle during this operation.
        """
        #pf.debug("Start 2D drawing",pf.DEBUG.DRAW)
        if self.mode2D:
            #pf.debug("WARNING: ALREADY IN 2D MODE",pf.DEBUG.DRAW)
            return
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        self.zoom_2D()
        GL.glDisable(GL.GL_DEPTH_TEST)
        #self.enable_lighting(False)
        self.mode2D = True


    def end_2D_drawing(self):
        """Cancel the 2D drawing mode initiated by begin_2D_drawing."""
        #pf.debug("End 2D drawing",pf.DEBUG.DRAW)
        if self.mode2D:
            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glPopMatrix()
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glPopMatrix()
            #self.enable_lighting(self.settings.lighting)
            self.mode2D = False



#    def addHighlight(self, itemlist):
#        """Add a highlight or a list thereof to the 3D scene."""
#        self.highlights.add(itemlist)
#
#    def removeHighlight(self,itemlist=None):
#        """Remove a highlight or a list thereof from the 3D scene.
#
#        Without argument, removes all highlights from the scene.
#        """
#        if itemlist is None:
#            itemlist = self.highlights[:]
#        self.highlights.delete(itemlist)


    def addAny(self, itemlist):
        self.scene.addAny(itemlist)


    addActor = addAnnotation = addDecoration = addAny

    def removeAny(self, itemlist):
        self.scene.removeAny(itemlist)

    removeActor = removeAnnotation = removeDecoration = removeAny


    def removeAll(self,sticky=False):
        self.scene.clear(sticky)
        self.highlights.clear()


    def dummy(self):
        pass

    redrawAll = dummy


    def setBbox(self, bbox):
        #print("SETBBOX %s" % bbox)
        self.scene.bbox = bbox


    def setCamera(self,bbox=None,angles=None):
        """Sets the camera looking under angles at bbox.

        This function sets the camera parameters to view the specified
        bbox volume from the specified viewing direction.

        Parameters:

        - `bbox`: the bbox of the volume looked at
        - `angles`: the camera angles specifying the viewing direction.
          It can also be a string, the key of one of the predefined
          camera directions

        If no angles are specified, the viewing direction remains constant.
        The scene center (camera focus point), camera distance, fovy and
        clipping planes are adjusted to make the whole bbox viewed from the
        specified direction fit into the screen.

        If no bbox is specified, the following remain constant:
        the center of the scene, the camera distance, the lens opening
        and aspect ratio, the clipping planes. In other words the camera
        is moving on a spherical surface and keeps focusing on the same
        point.

        If both are specified, then first the scene center is set,
        then the camera angles, and finally the camera distance.

        In the current implementation, the lens fovy and aspect are not
        changed by this function. Zoom adjusting is performed solely by
        changing the camera distance.
        """
        #
        # TODO: we should add the rectangle (digital) zooming to
        #       the docstring

        self.makeCurrent()

        # set scene center
        if bbox is not None:
            pf.debug("SETTING BBOX: %s" % bbox, pf.DEBUG.DRAW)
            self.setBbox(bbox)

            X0, X1 = self.scene.bbox
            self.camera.focus = 0.5*(X0+X1)

        # set camera angles
        if isinstance(angles, str):
            angles = self.view_angles.get(angles)
        if angles is not None:
            try:
                self.camera.setAngles(angles)
            except:
                raise ValueError('Invalid view angles specified')

        # set camera distance and clipping planes
        if bbox is not None:
            #print("SET CAMERA %s" % bbox)
            # Currently, we keep the default fovy/aspect
            # and change the camera distance to focus
            fovy = self.camera.fovy
            #pf.debug("FOVY: %s" % fovy,pf.DEBUG.DRAW)
            self.camera.setLens(fovy, self.aspect)
            # Default correction is sqrt(3)
            correction = float(pf.cfg.get('gui/autozoomfactor', 1.732))
            tf = coords.tand(fovy/2.)

            from pyformex import simple
            bbix = simple.regularGrid(X0, X1, [1, 1, 1],swapaxes=True)
            bbix = np.dot(bbix, self.camera.rot[:3, :3])
            bbox = coords.Coords(bbix).bbox()
            dx, dy, dz = bbox[1] - bbox[0]
            vsize = max(dx/self.aspect, dy)
            dsize = bbox.dsize()
            offset = dz
            dist = (vsize/tf + offset) / correction

            if dist == np.nan or dist == np.inf:
                pf.debug("DIST: %s" % dist, pf.DEBUG.DRAW)
                return
            if dist <= 0.0:
                dist = 1.0
            self.camera.dist = dist

            ## print "vsize,dist = %s, %s" % (vsize,dist)
            ## near,far = 0.01*dist,100.*dist
            ## print "near,far = %s, %s" % (near,far)
            #near,far = dist-1.2*offset/correction,dist+1.2*offset/correction
            near, far = dist-1.0*dsize, dist+1.0*dsize
            # print "near,far = %s, %s" % (near,far)
            #print (0.0001*vsize,0.01*dist,near)
            # make sure near is positive
            near = max(near, 0.0001*vsize, 0.01*dist, np.finfo(coords.Float).tiny)
            # make sure far > near
            if far <= near:
                far += np.finfo(coords.Float).eps
            #print "near,far = %s, %s" % (near,far)
            self.camera.setClip(near, far)
            self.camera.resetArea()


    def project(self,x,y,z,locked=False):
        "Map the object coordinates (x,y,z) to window coordinates."""
        ## locked=False
        ## if locked:
        ##     model, proj, view = self.projection_matrices
        ## else:
        ##     self.makeCurrent()
        ##     self.camera.loadProjection()
        ##     model = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)
        ##     proj = GL.glGetDoublev(GL.GL_PROJECTION_MATRIX)
        ##     view = GL.glGetIntegerv(GL.GL_VIEWPORT)
        ## winx, winy, winz = GLU.gluProject(x, y, z, model, proj, view)
        ## return winx, winy, winz
        X = self.camera.project([[x, y, z]])
        #print(X,X.size)
        return X[0]


    def unproject(self,x,y,z,locked=False):
        "Map the window coordinates (x,y,z) to object coordinates."""
        ## locked=False
        ## if locked:
        ##     model, proj, view = self.projection_matrices
        ## else:
        ##     self.makeCurrent()
        ##     self.camera.loadProjection()
        ##     model = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)
        ##     proj = GL.glGetDoublev(GL.GL_PROJECTION_MATRIX)
        ##     view = GL.glGetIntegerv(GL.GL_VIEWPORT)
        ## objx, objy, objz = GLU.gluUnProject(x, y, z, model, proj, view)
        ## return (objx, objy, objz)
        X = self.camera.unproject([[x,y,z]])
        #print(X)
        return X


    def zoom(self,f,dolly=True):
        """Dolly zooming.

        Zooms in with a factor `f` by moving the camera closer
        to the scene. This does noet change the camera's FOV setting.
        It will change the perspective view though.
        """
        if dolly:
            self.camera.dolly(f)


    def zoomRectangle(self, x0, y0, x1, y1):
        """Rectangle zooming.

        Zooms in/out by changing the area and position of the visible
        part of the lens.
        Unlike zoom(), this does not change the perspective view.

        `x0,y0,x1,y1` are pixel coordinates of the lower left and upper right
        corners of the area of the lens that will be mapped on the
        canvas viewport.
        Specifying values that lead to smaller width/height will zoom in.
        """
        w, h = float(self.width()), float(self.height())
        self.camera.setArea(x0/w, y0/h, x1/w, y1/h)


    def zoomCentered(self,w,h,x=None,y=None):
        """Rectangle zooming with specified center.

        This is like zoomRectangle, but the zoom rectangle is specified
        by its center and size, which may be more appropriate when using
        off-center zooming.
        """
        self.zoomRectangle(x-w/2, y-h/2, x+w/2, y+w/2)


    def zoomAll(self):
        """Rectangle zoom to make full scene visible.

        """
        self.camera.resetArea()


    def saveBuffer(self):
        """Save the current OpenGL buffer"""
        self.save_buffer = GL.glGetIntegerv(GL.GL_DRAW_BUFFER)

    def showBuffer(self):
        """Show the saved buffer"""
        pass


    def draw_focus_rectangle(self,ofs=0,color=colors.pyformex_pink):
        """Draw the focus rectangle.

        """
        from . import decors
        #w, h = self.width(), self.height()
        self._focus = decors.Grid2D(-1.,-1.,1.,1., color=color, linewidth=2, rendertype=3)
        self.addAny(self._focus)


    def draw_cursor(self, x, y):
        """draw the cursor"""
        from . import decors
        if self.cursor:
            self.removeAny(self.cursor)
        w, h = pf.cfg.get('draw/picksize', (20, 20))
        col = pf.cfg.get('pick/color', 'yellow')
        self.cursor = decors.Grid2D(x-w/2, y-h/2, x+w/2, y+h/2, color=col, linewidth=1)
        self.addAny(self.cursor)


    def draw_rectangle(self, x, y):
        if self.cursor:
            self.removeAny(self.cursor)
        col = pf.cfg.get('pick/color', 'yellow')
        self.cursor = decors.Grid2D(self.statex, self.statey, x, y, color=col, linewidth=1)
        self.addAny(self.cursor)


    def pick_actors(self):
        """Set the list of actors inside the pick_window."""
        stackdepth = 1
        npickable = len(self.actors)
        selbuf = GL.glSelectBuffer(npickable*(3+stackdepth))
        GL.glRenderMode(GL.GL_SELECT)
        GL.glInitNames()
        self.renderer.render(self.scene, pick=self.pick_window)
        # Store pick window for debugging
        pf.PF['pick_window'] = self.pick_window
        libGL.glRenderMode(GL.GL_RENDER)
        # Read the selection buffer
        store_closest = self.selection_filter == 'single' or \
                        self.selection_filter == 'closest'
        self.picked = []
        if selbuf[0] > 0:
            buf = np.asarray(selbuf).reshape(-1, 3+selbuf[0])
            buf = buf[buf[:, 0] > 0]
            self.picked = buf[:, 3]
            if store_closest:
                w = buf[:, 1].argmin()
                self.closest_pick = (self.picked[w], buf[w, 1])


    def pick_parts(self,obj_type,store_closest=False):
        """Set the list of actor parts inside the pick_window.

        obj_type can be 'element', 'face', 'edge' or 'point'.
        'face' and 'edge' are only available for Mesh type geometry.

        The picked object numbers are stored in self.picked.
        If store_closest==True, the closest picked object is stored in as a
        tuple ( [actor,object] ,distance) in self.picked_closest

        A list of actors from which can be picked may be given.
        If so, the resulting keys are indices in this list.
        By default, the full actor list is used.
        """
        pf.debug('PICK_PARTS %s %s' % (obj_type, store_closest), pf.DEBUG.DRAW)

        # This allows us to set a list of pickable actors different
        # from the default (the pickable actors)
        # This is e.g. used in the draw2d plugin
        # It should however not be set by the user
        if self.pickable is None:
            pickable = [ a for a in self.actors if a.pickable ]
        else:
            pickable = self.pickable

        self.picked = Collection(self.pick_mode)
        self.closest_pick = None

        # Make sure we always return Actor index from self.actors
        for i, a in enumerate(self.actors):
            if a in pickable:
                picked = a.inside(self.camera, rect=self.pick_window[:4], mode=self.pick_mode, sel=self.pick_mode_subsel, return_depth=store_closest)
                #print("PICK_PARTS %s" % self.pick_mode)
                #print(picked)
                if store_closest:
                    picked,zdepth = picked
                self.picked.add(picked, key=i)

                if store_closest and len(picked) > 0:
                    w = zdepth.argmin()
                    #print("PICK_PARTS CLOSEST: %s" % w)
                    if self.closest_pick is None or zdepth[w] < self.closest_pick[1]:
                        self.closest_pick = ([i,picked[w]],zdepth[w])
                    #print("CLOSEST_PICK: " + str(self.closest_pick))


    # TODO: pick actors based on pick_parts
    # this would however make pick actors only work if points are picked
    ## def pick_actors(self):
    ##     """Set the list of actors inside the pick_window."""
    ##     self.pick_parts('actor', store_closest=\
    ##                     self.selection_filter == 'single' or\
    ##                     self.selection_filter == 'closest',
    ##                     )


    def pick_elements(self):
        """Set the list of actor elements inside the pick_window."""
        self.pick_parts('element', store_closest=\
                        self.selection_filter == 'single' or\
                        self.selection_filter == 'closest' or\
                        self.selection_filter == 'connected'
                        )


    def pick_points(self):
        """Set the list of actor points inside the pick_window."""
        self.pick_parts('point', store_closest=\
                        self.selection_filter == 'single' or\
                        self.selection_filter == 'closest',
                        )


    def pick_edges(self):
        """Set the list of actor edges inside the pick_window."""
        self.pick_parts('edge', store_closest=\
                        self.selection_filter == 'single' or\
                        self.selection_filter == 'closest',
                        )


    def pick_faces(self):
        """Set the list of actor faces inside the pick_window."""
        self.pick_parts('face', store_closest=\
                        self.selection_filter == 'single' or\
                        self.selection_filter == 'closest',
                        )


    def pick_numbers(self):
        """Return the numbers inside the pick_window."""
        self.camera.loadProjection(pick=self.pick_window)
        self.camera.loadModelView()
        self.picked = [0, 1, 2, 3]
        if self.numbers:
            self.picked = self.numbers.drawpick()


    def highlightActors(self, K):
        """Highlight a selection of actors on the canvas.

        K is Collection of actors as returned by the pick() method.
        colormap is a list of two colors, for the actors not in, resp. in
        the Collection K.
        """
        #print("HIGHLIGHT_ACTORS", K)
        self.scene.removeHighlight()
        for i in K.get(-1, []):
            self.scene.actors[i].addHighlight()


    def highlightElements(self, K):
        #print("HIGHLIGHT_ELEMENTS", K)
        self.scene.removeHighlight()
        for i in K.keys():
            pf.debug("Actor %s: Selection %s" % (i, K[i]), pf.DEBUG.DRAW)
            self.actors[i].addHighlightElements(K[i])


    def highlightPoints(self, K):
        #print("HIGHLIGHT_POINTS", K)
        self.scene.removeHighlight()
        for i in K.keys():
            pf.debug("Actor %s: Selection %s" % (i, K[i]), pf.DEBUG.DRAW)
            self.actors[i].addHighlightPoints(K[i])


    def highlightEdges(self, K):
        pass

    def removeHighlight(self):
        """Remove a highlight or a list thereof from the 3D scene.

        Without argument, removes all highlights from the scene.
        """
        self.scene.removeHighlight()


    highlight_funcs = { 'actor': highlightActors,
                        'element': highlightElements,
                        'point': highlightPoints,
                        'edge': highlightEdges,
                        }


### End
