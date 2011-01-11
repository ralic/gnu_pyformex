# $Id$
"""geometry_menu.py

This is a pyFormex plugin menu. It is not intended to be executed as a script,
but to be loaded into pyFormex using the plugin facility.
"""

import pyformex as pf
import utils
from odict import ODict

from geometry import Geometry
from geomfile import GeometryFile
from formex import Formex
from mesh import Mesh
from trisurface import TriSurface

from gui import actors
from gui import menu
from gui.draw import *

from plugins import objects,trisurface,inertia,partition,sectionize

import commands, os, timer


##################### select, read and write ##########################

selection = objects.DrawableObjects(clas=Geometry)
drawable = pf.GUI.drawable


setSelection = selection.set
drawSelection = selection.draw
drawAll = drawable.draw

autoName = dict([(clas,utils.NameSequence(clas)) for clas in [ 'Formex', 'Mesh', 'TriSurface' ]])


def autoName(clas):
    """Return the next autoenerated name for objects of type clas."""
    if type(clas) is not str:
        clas = clas.__class__.__name__
    print "CLASS %s" % clas
    return autoName[clas].next()
    

def readGeometry(filename,filetype=None):
    """Read geometry from a stored file.

    This is a wrapper function over several other functions specialized
    for some file type. Some file types require the existence of more
    than one file, may need to write intermediate files, or may call
    external programs.
    
    The return value is a dictionary with named geometry objects read from
    the file.

    If no filetype is given, it is derived from the filename extension.
    Currently the following file types can be handled. 

    'pgf': pyFormex Geometry File. This is the native pyFormex geometry
        file format. It can store multiple parts of different type, together
        with their name.
    'surface': a global filetype for any of the following surface formats:
        'stl', 'gts', 'off',
    'stl': 
    """
    res = {}
    if filetype is None:
        filetype = utils.fileTypeFromExt(filename)
        
    print "Reading file of type %s" % filetype

    if filetype == 'pgf':
        res = GeometryFile(filename).read()

    #elif filetype == 'pyf':

    elif filetype in ['surface','stl','off','gts','smesh','neu']:
        surf = TriSurface.read(filename)
        res = {autoName(TriSurface):surf}

    else:
        error("Can not import from file %s of type %s" % (filename,filetype))
        
    return res


def importGeometry(select=True,draw=True,clas=Geometry):
    """Read geometry from file.
    
    If select is True (default), the imported geometry becomes the current
    selection.
    If select and draw are True (default), the selection is drawn.
    """
    types = utils.fileDescription(['pgf','pyf','surface','off','stl','gts','smesh','neu','all'])
    cur = pf.cfg['workdir']
    fn = askFilename(cur=cur,filter=types)
    if fn:
        message("Reading geometry file %s" % fn)
        res = readGeometry(fn)
        export(res)
        #selection.readFromFile(fn)
        print res.keys()
        if select:
            selection.set(res.keys())
            if draw:
                selection.draw()
                zoomAll()


def writeGeometry(obj,filename,filetype=None,shortlines=False):
    """Write the geometry items in objdict to the specified file.

    """
    if filetype is None:
        filetype = utils.fileTypeFromExt(filename)
        
    print "Writing file of type %s" % filetype

    if filetype in [ 'pgf', 'pyf' ]:
        # Can write anything
        if filetype == 'pgf':
            res = writeGeomFile(filename,obj,shortlines=shortlines)

    else:
        error("Don't know how to export in '%s' format" % filetype)
        
    return res


def exportGeometry(types=['pgf','all'],shortlines=False):
    """Write geometry to file."""
    drawable.ask()
    if not drawable.check():
        return
    
    filter = utils.fileDescription(types)
    cur = pf.cfg['workdir']
    fn = askNewFilename(cur=cur,filter=filter)
    if fn:
        message("Writing geometry file %s" % fn)
        res = writeGeometry(drawable.odict(),fn,shortlines=shortlines)
        pf.message("Contents: %s" % res)

def exportPgf():
    exportGeometry(['pgf'])
def exportPgfShortlines():
    exportGeometry(['pgf'],shortlines=True)
def exportOff():
    exportGeometry(['off'])
 

################### menu #################
 
_menu = 'Geometry'
   
def create_menu():
    """Create the plugin menu."""
    MenuData = [
        ("&Import Geometry",importGeometry),
        ("&Export",
         [("pyFormex Geometry File (.pgf)",exportPgf),
          ("pyFormex Geometry File with short lines",exportPgfShortlines),
          ("Object File Format (.off)",exportOff),
          ]),
        ## ("&Select",selection.ask),
        ## ("&Draw Selection",selection.draw),
        ## ("&Forget Selection",selection.forget),
        ## ("---",None),
        ## ("Print &Information",
        ##  [('&Data Size',printSize),
        ##   ('&Bounding Box',selection.printbbox),
        ##   ]),
        ## ("&Set Property",selection.setProperty),
        ## ("&Shrink",shrink),
        ## ("Toggle &Annotations",
        ##  [("&Names",selection.toggleNames,dict(checkable=True)),
        ##   ("&Numbers",selection.toggleNumbers,dict(checkable=True)),
        ##   ('&Toggle Bbox',selection.toggleBbox,dict(checkable=True)),
        ##   ]),
        ## ("---",None),
        ## ("&Bbox",
        ##  [('&Show Bbox Planes',showBbox),
        ##   ('&Remove Bbox Planes',removeBbox),
        ##   ]),
        ## ("&Transform",
        ##  [("&Scale Selection",scaleSelection),
        ##   ("&Scale non-uniformly",scale3Selection),
        ##   ("&Translate",translateSelection),
        ##   ("&Center",centerSelection),
        ##   ("&Rotate",rotateSelection),
        ##   ("&Rotate Around",rotateAround),
        ##   ("&Roll Axes",rollAxes),
        ##   ]),
        ## ("&Clip/Cut",
        ##  [("&Clip",clipSelection),
        ##   ("&Cut With Plane",cutSelection),
        ##   ]),
        ## ("&Undo Last Changes",selection.undoChanges),
        ## ("---",None),
        ## ("Show &Principal Axes",showPrincipal),
        ## ("Rotate to &Principal Axes",rotatePrincipal),
        ## ("Transform to &Principal Axes",transformPrincipal),
        ## ("---",None),
        ## ("&Concatenate Selection",concatenateSelection),
        ## ("&Partition Selection",partitionSelection),
        ## ("&Create Parts",createParts),
        ## ("&Sectionize Selection",sectionizeSelection),
        ## ("---",None),
        ## ("&Fly",fly),
        ("---",None),
        ("&Reload menu",reload_menu),
        ("&Close",close_menu),
        ]
    return menu.Menu(_menu,items=MenuData,parent=pf.GUI.menu,before='help')

    
def show_menu():
    """Show the Tools menu."""
    if not pf.GUI.menu.item(_menu):
        create_menu()


def close_menu():
    """Close the Tools menu."""
    m = pf.GUI.menu.item(_menu)
    if m :
        m.remove()
      

def reload_menu():
    """Reload the Postproc menu."""
    from plugins import refresh
    close_menu()
    refresh('geometry_menu')
    show_menu()


####################################################################
######### What to do when the script is executed ###################

if __name__ == "draw":

    reload_menu()


# End
