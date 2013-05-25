# $Id$
##
##  This file is part of pyFormex 0.9.0  (Mon Mar 25 13:52:29 CET 2013)
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
"""Operations on triangulated surfaces using VMTK functions.

This module provides access to VMTK functionality from inside pyFormex.
Documentation for VMTK can be found on http://www.vmtk.org/Main/Tutorials/
and http://www.vmtk.org/VmtkScripts/vmtkscripts/
"""
from __future__ import print_function

import pyformex as pf
from coords import *
from mesh import Mesh
from plugins.trisurface import TriSurface
import utils
import os


def readVmtkCenterlineDat(fn):
   """Read a .dat file containing the centerlines generated with vmtk.

   The first line may contain a header.
   All other lines ('nlines') contain  'nf' floats.
   All data are seperated by blanks.
   
   The return value is a tuple of
   
   - a float array (nlines,nf) with the data
   - a list with the identifiers from the first line
   """
   fil = file(fn,'r')
   line = fil.readline()
   s = line.strip('\n').split()
   data = fromfile(fil,sep=' ',dtype=float32)
   data = data.reshape(-1,len(s))
   return data, s


def centerline(self,seedselector='pickpoint',sourcepoints=[],
               targetpoints=[],endpoints=False,return_data=False,groupcl=False):
    """Compute the centerline of a surface.

    The centerline is computed using VMTK. This is very well suited for
    computing the centerlines in vascular models.

    Parameters:
    
    - `seedselector`: str: seed point selection method, one of
      [`pickpoint`,`openprofiles`,`carotidprofiles`,`pointlist`,`idlist`]
    - `sourcepoints`: list: flattened source point coordinates for `pointlist` method
      or a list of point ids for `idlist` method
    - `targetpoints`: list: flattened target point coordinates for `pointlist` method
      or a list of point ids for `idlist` method
    - `endpoints`: boolean: append source- and targetpoints to centerlines
    - `groupcl`: boolean: if True the points of the centerlines are merged and
      grouped to avoid repeated points and separate different branches
    - `return_data`: boolean: if True returns a tuple containing a list of the 
      additional information per each point (such as maximum inscribed sphere 
      used for the centerline computation, local coordinate system
      and various integers values to group the centerline points according to 
      the branching) and the array cointaing all these values (check the vmtk 
      website for specific informations).
          
      Note that when seedselector is `idlist`, the surface must be clenead converting
      it to a vtkPolyData using the function convert2VPD with flag clean=True and then
      converted back using convertFromVPD implemented in the vtk_itf plugin to avoid
      wrong point selection of the vmtk function.
.
    Returns a Coords with the points defining the centerline

    If return_data is True tuple cointaing the list of the names of the additional infomations
    per each point and an array cointaing all these values .
    """

    tmp = utils.tempFile(suffix='.stl').name
    tmp1 = utils.tempFile(suffix='.vtp').name
    tmp2 = utils.tempFile(suffix='.dat').name
    pf.message("Writing temp file %s" % tmp)
    self.write(tmp,'stl')
    pf.message("Computing centerline using VMTK")
    cmds=[]
    cmd = 'vmtk vmtkcenterlines -seedselector %s -ifile %s -ofile %s'%(seedselector,tmp,tmp1)
    if seedselector in ['pointlist','idlist']:
        if not(len(sourcepoints)) or not(len(targetpoints)):
            raise ValueError,'sourcepoints and targetpoints cannot be an empty list when using seedselector= \'%s\''%seedselector
        if seedselector=='pointlist':
            fmt=' %f'
        if seedselector=='idlist':
            fmt=' %i'
    
        cmd += ' -source%ss'%seedselector[:-4]
        cmd += fmt*len(sourcepoints)%tuple(sourcepoints)
        cmd += ' -target%ss'%seedselector[:-4]
        cmd += fmt*len(targetpoints)%tuple(targetpoints)
    
    cmd += ' -endpoints %i'%endpoints
    
    cmds.append(cmd)
    if groupcl:
        cmds.append('vmtk vmtkcenterlineattributes -ifile %s --pipe vmtkbranchextractor -radiusarray@ MaximumInscribedSphereRadius \
        --pipe vmtkbifurcationreferencesystems --pipe vmtkcenterlineoffsetattributes -referencegroupid 0 -ofile %s\n'%(tmp1,tmp1))
        cmds.append('vmtk vmtkcenterlinemerge -ifile %s -ofile %s -radiusarray MaximumInscribedSphereRadius -groupidsarray GroupIds -centerlineidsarray CenterlineIds -tractidsarray TractIds -blankingarray Blanking -mergeblanked 1'%(tmp1,tmp1))
    cmds.append('vmtk vmtksurfacecelldatatopointdata -ifile %s -ofile %s'%(tmp1,tmp2))
    
    for c in cmds:
        sta,out = utils.runCommand(c)
        if sta:
            pf.message("An error occurred during the centerline computing")
            pf.message(out)
            return None
    data, header = readVmtkCenterlineDat(tmp2)
    cl = Coords(data[:,:3])
    if return_data:
        print('Returning Array data with values:')
        print(' %s'*len(header[3:])%tuple(header[3:]))
        return cl,(header[3:],data[:,3:])
    else:
        return cl


def remesh(self,elementsizemode='edgelength',edgelength=None,
           area=None,aspectratio=None):
    """Remesh a TriSurface.

    Parameters:

    - `elementsizemode`: str: metric that is used for remeshing,
      `edgelength` and `area` allow to specify a global target triangle
      edgelength and area respectively.
    - `edgelength`: float: global target triangle edgelength
    - `area`: float: global target triangle area
    - `aspectratio`: float: upper threshold for aspect ratio (default=1.2).
    
    Returns the remeshed TriSurface.
    """
    tmp = utils.tempFile(suffix='.stl').name
    tmp1 = utils.tempFile(suffix='.stl').name
    pf.message("Writing temp file %s" % tmp)
    self.write(tmp,'stl')
    cmd = 'vmtk vmtksurfaceremeshing -ifile %s -ofile %s'  % (tmp,tmp1)
    if elementsizemode == 'edgelength':
        if  edgelength is None:
           self.getElemEdges()
           E = Mesh(self.coords,self.edges,eltype='line2')
           edgelength =  E.lengths().mean()
        cmd += ' -elementsizemode edgelength -edgelength %f' % edgelength
    elif elementsizemode == 'area':
        if  area is None:
            self.areaNormals()
            area = self.areas.mean()
        cmd += ' -elementsizemode area -area %f' % area
    if aspectratio is not None:
        cmd += ' -aspectratio %f' % aspectratio
    pf.message("Remeshing with command\n %s" % cmd)
    sta,out = utils.runCommand(cmd)
    os.remove(tmp)
    if sta:
        pf.message("An error occurred during the remeshing.")
        pf.message(out)
        return None
    S = TriSurface.read(tmp1)
    os.remove(tmp1)
    return S


def install_trisurface_methods():
    """Install extra TriSurface methods

    """
    #from plugins.trisurface import TriSurface
    TriSurface.centerline = centerline
    TriSurface.remesh = remesh

install_trisurface_methods()

# End













