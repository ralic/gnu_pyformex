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
"""Formex algebra in Python

This module defines the :class:`Formex` class, which is the major class for
representing geometry in pyFormex. The Formex class implements most
functionality of Formex algebra in a consistent and easy to understand
syntax.
"""
from __future__ import absolute_import, division, print_function
from pyformex import zip

from pyformex.coords import *
from pyformex.geometry import Geometry
import re


###########################################################################
##
##   Formex class
##
#########################
#

class Formex(Geometry):
    """A structured collection of points in 3D space.

    A Formex is a collection of points in the 3D space, that are structured
    into a set of elements all having the same number of points (e.g. a
    collection of line segments or a collection of triangles.)

    The Formex basically contains (in its `coords` attribute) a :class:`Coords`
    object, which is a Float type array with 3 axes (numbered 0,1,2).
    A scalar element of this array represents a coordinate.

    A row along the last axis (2) is a set of coordinates and represents
    a point (aka. node, vertex).
    For simplicity's sake, the current implementation only deals with points
    in a 3-dimensional space. This means that the length of axis 2 is always 3.
    The user can create Formices (plural of Formex) in a 2-D space, but
    internally these will be stored with 3 coordinates, by adding a third
    value 0. All operations work with 3-D coordinate sets. However, a method
    exists to extract only a limited set of coordinates from the results,
    permitting to return to a 2-D environment

    A plane along the axes 2 and 1 is a set of points or element. This can be
    thought of as a geometrical shape (2 points form a line segment, 3 points
    make a triangle, ...) or as an element in Finite Element terms.
    But it really is up to the user as to how this set of points is to be
    interpreted.

    Finally, the whole Formex represents a collection of such elements.

    Additionally, a Formex may have a property set, which is an 1-D array of
    integers. The length of the array is equal to the length of axis 0 of the
    Formex data (i.e. the number of elements in the Formex). Thus, a single
    integer value may be attributed to each element. It is up to the user to
    define the use of this integer (e.g. it could be an index in a table of
    element property records).
    If a property set is defined, it will be copied together with the Formex
    data whenever copies of the Formex (or parts thereof) are made.
    Properties can be specified at creation time, and they can be set,
    modified or deleted at any time. Of course, the properties that are
    copied in an operation are those that exist at the time of performing
    the operation.

    The Formex data can be initialized by another Formex,
    by a 2D or 3D coordinate list, or by a string to be used in one of the
    pattern functions to create a coordinate list.
    If 2D coordinates are given, a 3-rd coordinate 0.0 is added.
    Internally, Formices always work with 3D coordinates.
    Thus::

      F = Formex([[[1,0],[0,1]],[[0,1],[1,2]]])

    creates a Formex with two elements, each having 2 points in the global
    z-plane. The innermost level of brackets group the coordinates of a
    point, the next level groups the points in an element, and the outermost
    brackets group all the elements of the Formex.
    Because the coordinates are stored in an array with 3 axes,
    all the elements in a Formex must contain the same number of points.
    This number is called the plexitude of the Formex.

    A Formex may be initialized with a string instead of the numerical
    coordinate data. The string has the format `#:data` where `#` is a
    leader specifying the plexitude of the elements to be created.
    The `data` part of the string is passed to the :func:`coords.pattern`
    function to generate a list of points on a regular grid of unit distances.
    Then the generated points are grouped in elements. If `#` is a number
    it just specifies the plexitude::

      F = Formex('3:012034')

    This creates six points, grouped by 3, thus leading to two elements
    (triangles). The leader can als be the character `l`. In that case
    each generated point is turned into a 2-point (line) element, by
    connecting it to the previous point. The following are two equivalent
    definitions of (the circumference of) a triangle::

      F = Formex('2:010207')
      G = Formex('l:127')

    The Formex constructor takes two optional arguments: prop and eltype.
    If a prop argument is specified, the setProp() function will be
    called to assign the specified properties. eltype can be used to
    specify a non-default element type. The default element type is
    derived from the plexitude as follows: 1 = point, 2 = line segment,
    3 = triangle, 4 or more is a polygon. Specifying ``eltype = 'tet4'``
    will e.g. interprete 4 point elements as a tetraeder.

    Because the :class:`Formex` class is derived from :class:`Geometry`,
    the following :class:`Formex` methods exist and return the value of the
    same method applied on the :attr:`coords` attribute:
    `x`,
    `y`,
    `z`,
    `bbox`,
    `center`,
    `centroid`,
    `sizes`,
    `dsize`,
    `bsphere`,
    `distanceFromPlane`,
    `distanceFromLine`,
    `distanceFromPoint`,
    `directionalSize`,
    `directionalWidth`,
    `directionalExtremes`,
    `__str__`.
    Refer to the correponding :class:`Coords` method for their usage.

    Also, the following :class:`Coords` transformation methods can be
    directly applied to a :class:`Formex` object or a derived class object.
    The return value is a new object identical to the original,
    except for the coordinates,
    which will have been transformed by the specified method.
    Refer to the correponding :class:`Coords` method for the usage of these
    methods:
    `scale`,
    `translate`,
    `rotate`,
    `shear`,
    `reflect`,
    `affine`,
    `cylindrical`,
    `hyperCylindrical`,
    `toCylindrical`,
    `spherical`,
    `superSpherical`,
    `toSpherical`,
    `bump`,
    `bump1`,
    `bump2`,
    `flare`,
    `map`,
    `map1`,
    `mapd`,
    `newmap`,
    `replace`,
    `swapAxes`,
    `rollAxes`,
    `projectOnSphere`,
    `projectOnCylinder`,
    `rot`,
    `trl`.

    Example:

    >>> print(Formex([[0,1],[2,3]]))
    {[0.0,1.0,0.0], [2.0,3.0,0.0]}
    >>> print(Formex('1:0123'))
    {[0.0,0.0,0.0], [1.0,0.0,0.0], [1.0,1.0,0.0], [0.0,1.0,0.0]}
    >>> print(Formex('4:0123'))
    {[0.0,0.0,0.0; 1.0,0.0,0.0; 1.0,1.0,0.0; 0.0,1.0,0.0]}
    >>> print(Formex('2:0123'))
    {[0.0,0.0,0.0; 1.0,0.0,0.0], [1.0,1.0,0.0; 0.0,1.0,0.0]}
    >>> print(Formex('l:1234'))
    {[0.0,0.0,0.0; 1.0,0.0,0.0], [1.0,0.0,0.0; 1.0,1.0,0.0], [1.0,1.0,0.0; 0.0,1.0,0.0], [0.0,1.0,0.0; 0.0,0.0,0.0]}
    """


###########################################################################
#
#   Create a new Formex
#

    def __init__(self,data=[],prop=None,eltype=None):
        """Create a new Formex."""
        Geometry.__init__(self)
        if isinstance(data, Formex):
            if prop is None:
                prop = data.prop
            if eltype is None:
                eltype = data.eltype
            data = data.coords
        else:
            if isinstance(data, str):
                d = re.compile("(((?P<base>[^:]*):)?(?P<data>.*))").match(data).groupdict()
                base, data = d['base'], d['data']
                if base is None or base == 'l':
                    data = Coords.concatenate([origin(), pattern(data)])
                    data = stack([data[:-1],data[1:]],axis=1)
                ## removed in 0.9.1
                ## elif base == 'm':
                ##     data = mpattern(data)
                else:
                    try:
                        nplex = int(base)
                        data = xpattern(data, nplex)
                    except:
                        raise ValueError("Invalid string data for Formex")

            data = asarray(data).astype(Float)

            if data.size == 0:   ### MAYBE THIS SHOULD BE CHANGED ?????
                if len(data.shape) == 3:
                    nplex = data.shape[1]
                elif len(data.shape) == 2:
                    nplex = 1
                else:
                    nplex = 0
                data = data.reshape(0, nplex, 3) # An empty Formex
            else:
                # check dimensions of data
                if not len(data.shape) in [1, 2, 3]:
                    raise RuntimeError("Formex init: needs a 1-, 2- or 3-dim. data array, got shape %s" % str(data.shape))
                if len(data.shape) == 1:
                    data = data.reshape(1, 1, data.shape[0])
                elif len(data.shape) == 2:
                    data = data.reshape(data.shape[0], 1, data.shape[1])
                if not data.shape[-1] in [1, 2, 3]:
                    raise RuntimeError("Formex init: last axis dimension of data array should be 1, 2 or 3, got shape %s" % str(data.shape))
                # add 3-rd dimension if data are 1-d or 2-d
                # this will be done by Coords
                pass
                if data.shape[-1] == 2:
                    z = zeros((data.shape[0], data.shape[1], 1), dtype=Float)
                    data = concatenate([data, z], axis=-1)

        # data should be OK now
        self.coords = Coords(data)    # make sure coordinates are a Coords object
        self.setProp(prop)

        try:
            self.eltype = eltype.lower()
        except:
            if eltype is not None:
                utils.warn("warn_formex_eltype")
            self.eltype = None


    def _set_coords(self, coords):
        """Replace the current coords with new ones.

        """
        coords = Coords(coords)
        if coords.shape == self.coords.shape:
            F = Formex(coords, self.prop, self.eltype)
            F.attrib(**self.attrib)
            return F
        else:
            raise ValueError("Invalid reinitialization of Formex coords")


    def __getitem__(self, i):
        """Return element i of the Formex.

        This allows addressing element i of Formex F as F[i].
        """
        return self.coords[i]

    def __setitem__(self, i, val):
        """Change element i of the Formex.

        This allows writing expressions as F[i] = [[1,2,3]].
        """
        self.coords[i] = val


    def __setstate__(self, state):
        """Set the object from serialized state.

        This allows to read back old pyFormex Project files where the Formex
        class had 'f' and 'p' attributes.
        """
        if "p" in state:
            state['prop'] = state['p']
            del state['p']
        if 'f'  in state:
            state['coords'] = state['f']
            del state['f']
        self.__dict__.update(state)

    def element(self, i):
        """Return element i of the Formex"""
        return self.coords[i]

    def point(self, i, j):
        """Return point j of element i"""
        return self.coords[i, j]

    def coord(self, i, j, k):
        """Return coord k of point j of element i"""
        return self.coords[i, j, k]

###########################################################################
#
#   Return information about a Formex
#
    def nelems(self):
        """Return the number of elements in the formex."""
        return self.coords.shape[0]


    __len__ = nelems  # implements len(Formex)


    def nplex(self):
        """Return the number of points per element.

        Examples:

        1. unconnected points,
        2. straight line elements,
        3. triangles or quadratic line elements,
        4. tetraeders or quadrilaterals or cubic line elements.
        """
        return self.coords.shape[1]

    def ndim(self):
        """Return the number of dimensions.

        This is the number of coordinates for each point. In the
        current implementation this is always 3, though you can
        define 2D Formices by given only two coordinates: the third
        will automatically be set to zero.
        """
        return self.coords.shape[2]

    def npoints(self):
        """Return the number of points in the formex.

        This is the product of the number of elements in the formex
        with the number of nodes per element.
        """
        return self.coords.shape[0]*self.coords.shape[1]


    ncoords = npoints


    # Making this a property so it can be used as (constant) attribute
    @property
    def shape(self):
        """Return the shape of the Formex.

        The shape of a Formex is the shape of its coords array,
        i.e. a tuple (nelems, nplex, ndim).
        """
        return self.coords.shape


    def elType(self):
        """Return the element type, or None"""
        from pyformex.elements import elementType
        if self.eltype is not None:
            return elementType(self.eltype)
        else:
            return None


    def elName(self):
        """Return the element type name, or None"""
        et = self.elType()
        if et:
            return et.name()
        else:
            return None


    def level(self):
        """Return the level (dimensionality) of the Formex.

        The level or dimensionality of a geometrical object is the minimum
        number of parametric directions required to describe the object.
        Thus we have the following values:

        0: points
        1: lines
        2: surfaces
        3: volumes

        Because the geometrical meaning of a Formex is not always defined,
        the level may be unknown. In that case, -1 is returned.

        If the Formex has an 'eltype' set, the value is determined from
        the Element database. Else, the value is equal to the plexitude minus
        one for plexitudes up to 3, an equal to 2 for any higher plexitude
        (since the default is to interprete a higher plexitude as a polygon).
        """
        et = self.elType()
        if et:
            return et.ndim
        else:
            if self.nplex() > 2:
                return 2
            else:
                return self.nplex()-1


    # Coordinates
    def view(self):
        """Return the Formex coordinates as a numpy array (ndarray).

        Since the ndarray object has a method view() returning a view on
        the ndarray, this method allows writing code that works with both
        Formex and ndarray instances. The results is always an ndarray.
        """
        return self.coords.view()


    # Properties
    def getProp(self,index=None):
        """Return the property numbers of the element in index"""
        if index is None or self.prop is None:
            return self.prop
        else:
            return self.prop[index]

    def maxProp(self):
        """Return the highest property value used, or None"""
        if self.prop is None:
            return None
        else:
            return self.prop.max()

    def propSet(self):
        """Return a list with unique property values on this Formex."""
        if self.prop is None:
            return None
        else:
            return unique(self.prop)


    def centroids(self):
        """Return the centroids of all elements of the Formex.

        The centroid of an element is the point whose coordinates
        are the mean values of all points of the element.
        The return value is a Coords object with nelems points.
        """
        return self.coords.mean(axis=1)


    # Data conversion

    def fuse(self,repeat=True,ppb=1,rtol=1.e-5,atol=None):
        """Return a tuple of nodal coordinates and element connectivity.

        A tuple of two arrays is returned. The first is float array with
        the coordinates of the unique nodes of the Formex. The second is
        an integer array with the node numbers connected by each element.
        The elements come in the same order as they are in the Formex, but
        the order of the nodes is unspecified.
        By the way, the reverse operation of ``coords,elems=fuse(F)``
        is accomplished by ``F=Formex(coords[elems])``

        There is a (very small) probability that two very close nodes are
        not equivalenced  by this procedure. Use it multiple times with
        different parameters to check.
        You can also set the rtol/atol parameters to influence the
        equivalence checking of two points.
        The default settting for atol is rtol * self.dsize()
        """
        if atol is None:
            atol = rtol * self.dsize()
        coords = reshape(self.coords, (self.nnodes(), 3))
        coords, index = coords.fuse(ppb, 0.5, rtol=rtol, atol=atol, repeat=repeat)
        index = index.reshape(self.coords.shape[:2])
        return coords, index


    def toMesh(self,*args,**kargs):
        """Convert a Formex to a Mesh.

        Converts a geometry in Formex model to the equivalent Mesh model.
        In the Mesh model, all points with nearly identical coordinates
        are fused into a single point, and elements are defined by a
        connectivity table with integers pointing to the corresponding vertex.
        """
        from pyformex.mesh import Mesh
        x, e = self.fuse(*args,**kargs)
        return Mesh(x, e, prop=self.prop, eltype=self.eltype)


    def toSurface(self):
        """Convert a Formex to a Surface.

        Tries to convert the Formex to a TriSurface.
        First the Formex is converted to a Mesh, and then the resulting Mesh
        is converted to a TriSurface.

        The conversion will only work if the Formex represents a surface and
        its elements are triangles or quadrilaterals.

        Returns a TriSurface if the conversion succeeds, else an error is
        raised.
        If the plexitude of the Formex is 3, the returned TriSurface is
        equivalent with the Formex.
        """
        return self.toMesh().toSurface()


    def info(self):
        """Return formatted information about a Formex."""
        bb = self.bbox()
        return """shape    = %s
bbox[lo] = %s
bbox[hi] = %s
center   = %s
maxprop  = %s
""" % (self.shape, bb[0], bb[1], self.center(), self.maxProp())

##############################################################################
# Create string representations of a Formex
#

    @classmethod
    def point2str(clas, point):
        """Return a string representation of a point"""
        s = ""
        if len(point)>0:
            s += str(point[0])
            if len(point) > 1:
                for i in point[1:]:
                    s += "," + str(i)
        return s

    @classmethod
    def element2str(clas, elem):
        """Return a string representation of an element"""
        s = "["
        if len(elem) > 0:
            s += clas.point2str(elem[0])
            if len(elem) > 1:
                for i in elem[1:]:
                    s += "; " + clas.point2str(i)
        return s+"]"

    def asFormex(self):
        """Return string representation of a Formex as in Formian.

        Coordinates are separated by commas, points are separated
        by semicolons and grouped between brackets, elements are
        separated by commas and grouped between braces::

           >>> F = Formex([[[1,0],[0,1]],[[0,1],[1,2]]])
           >>> print(F)
           {[1.0,0.0,0.0; 0.0,1.0,0.0], [0.0,1.0,0.0; 1.0,2.0,0.0]}
        """
        s = "{"
        if len(self.coords) > 0:
            s += self.element2str(self.coords[0])
            if len(self.coords) > 1:
                for i in self.coords[1:]:
                    s += ", " + self.element2str(i)
        return s+"}"

    def asFormexWithProp(self):
        """Return string representation as Formex with properties.

        The string representation as done by asFormex() is followed by
        the words "with prop" and a list of the properties.
        """
        s = self.asFormex()
        if isinstance(self.prop, ndarray):
            s += " with prop " + self.prop.__str__()
        else:
            s += " no prop "
        return s

    def asArray(self):
        """Return string representation as a numpy array."""
        return self.coords.__str__()

    #default print function
    __str__ = asFormex

    @classmethod
    def setPrintFunction (clas, func):
        """Choose the default formatting for printing formices.

        This sets how formices will be formatted by a print statement.
        Currently there are two available functions: asFormex, asArray.
        The user may create its own formatting method.
        This is a class method. It should be used asfollows:
        Formex.setPrintFunction(Formex.asArray).
        """
        clas.__str__ = func


    def fprint(self,*args,**kargs):
        self.coords.fprint(*args,**kargs)


##############################################################################
#
#  These are the methods that change a Formex !
#
##############################################################################


    def append(self, F):
        """Append the members of Formex F to this one.

        This function changes (and returns) the original object!
        Use __add__ if what you want is a copy with the sum.

        >>> F = Formex([[[1.0,1.0,1.0]]])
        >>> G = F.append(F)
        >>> print(F)
        {[1.0,1.0,1.0], [1.0,1.0,1.0]}
        """
        if F.coords.size == 0:
            return self
        if self.coords.size == 0:
            self.coords = F.coords
            self.prop = F.prop
            return self

        self.coords = Coords(concatenate((self.coords, F.coords)))
        ## What to do if one of the formices has properties, the other one not?
        ## The current policy is to use zero property values for the Formex
        ## without props
        if self.prop is not None or F.prop is not None:
            if self.prop is None:
                self.prop = zeros(shape=self.coords.shape[:1], dtype=Int)
            if F.prop is None:
                p = zeros(shape=F.coords.shape[:1], dtype=Int)
            else:
                p = F.prop
            self.prop = concatenate((self.prop, p))
        return self


##############################################################################
##
## All the following functions leave the original Formex unchanged and return
## a new Formex instead.
## This is a design decision intended so that the user can write statements as
##   G = F.op1().op2().op3()
## without having an impact on F. If the user wishes, he can always change an
## existing Formex by a statement such as
##   F = F.op()
## While this may seem to create a lot of intermediate array data, Python and
## numpy are clever enough to release the memory that is no longer used.
##
##############################################################################
#
# Create copies, concatenations, subtractions, connections, ...
#

    def __add__(self, other):
        """Return the sum of two formices.

        This returns a Formex with all elements of self and other.
        It allows us to write simple expressions as F+G to concatenate
        the Formices F and G.
        """
        return self.copy().append(other)
    # BV: would Formex.concatenate([self,other]) be better?
    #

    @classmethod
    def concatenate(clas, Flist):
        """Concatenate all Formices in Flist.

        All the Formices in the list should have the same plexitude,
        If any of the Formices has property numbers, the resulting Formex will
        inherit the properties. In that case, any Formices without properties
        will be assigned property 0.
        If all Formices are without properties, so will be the result.
        The eltype of the resulting Formex will be that of the first Formex in
        the list.

        This is a class method, not an instance method!

        >>> F = Formex([[[1,2,3]]],1)
        >>> print(Formex.concatenate([F,F,F]))
        {[1.0,2.0,3.0], [1.0,2.0,3.0], [1.0,2.0,3.0]}

        Formex.concatenate([F,G,H]) is functionally equivalent with F+G+H.
        The latter is simpler to write for a list with a few elements.
        If the list becomes large, or the number of items in the list
        is not fixed, the concatenate method is easier (and faster).
        We made it a class method and not a global function, because that
        would interfere with NumPy's own concatenate function.
        """
        def _force_prop(m):
            if m.prop is None:
                return zeros(m.nelems(), dtype=Int)
            else:
                return m.prop

        f = concatenate([ F.coords for F in Flist ])

        # Keep the available props
        prop = [F.prop for F in Flist if F.prop is not None]
        if len(prop) == 0:
            prop = None
        elif len(prop) < len(Flist):
            prop = concatenate([_force_prop(F) for F in Flist])
        else:
            prop = concatenate(prop)

        return Formex(f, prop, Flist[0].eltype)


    def _select(self,selected,**kargs):
        """_Return a Formex only holding the selected elements.

        This is the low level select method. The normal user interface
        is via the Geometry.select method.
        """
        selected = checkArray1D(selected)
        if self.prop is None:
            return Formex(self.coords[selected], eltype=self.eltype)
        else:
            return Formex(self.coords[selected], self.prop[selected], self.eltype)


    def selectNodes(self, idx):
        """Return a Formex which holds only some nodes of the parent.

        idx is a list of node numbers to select.
        Thus, if F is a plex 3 Formex representing triangles, the sides of
        the triangles are given by
        F.selectNodes([0,1]) + F.selectNodes([1,2]) + F.selectNodes([2,0])
        The returned Formex inherits the property of its parent.
        """
        return Formex(self.coords[:, idx,:], self.prop, self.eltype)


    def asPoints(self):
        """Return a Formex containing only the points.

        This is obviously a Formex with plexitude 1. It holds the same data
        as the original Formex, but in another shape: the number of points
        per element is 1, and the number of elements is equal to the total
        number of points.
        The properties are not copied over, since they will usually not make
        any sense.

        The points() method returns the same data, but as a Coords object
        with a simple list of points.
        """
        return Formex(self.coords.reshape((-1, 1, 3)))


    # REMOVED 1.0.0
    ## # retained for compatibility, deprecated
    ## @deprecated('depr_vertices')
    ## def vertices(self):
    ##     return self.points()


    def remove(self, F):
        """Return a Formex where the elements in F have been removed.

        This is also the subtraction of the current Formex with F.
        Elements are only removed if they have the same nodes in the same
        order. This is a slow operation: for large structures, you should
        avoid it where possible.
        """
        flag = ones((self.coords.shape[0],))
        for i in range(self.coords.shape[0]):
            for j in range(F.coords.shape[0]):
                if allclose(self.coords[i], F.coords[j]):
                    # element i is same as element j of F
                    flag[i] = 0
                    break
        if self.prop is None:
            p = None
        else:
            p = self.prop[flag>0]
        return Formex(self.coords[flag>0], p, self.eltype)


    @utils.deprecated_by('Formex.withProp','Formex.selectProp')
    def withProp(self, val):
        return self.selectProp(val)


    @utils.deprecated_by('Formex.elbbox','Formex.bboxes')
    def elbbox(self):
        return Formex(self.bboxes())


    def removeDuplicate(self,permutations=True,rtol=1.e-4,atol=1.e-6):
        """Return a Formex which holds only the unique elements.

        Two elements are considered equal when all its points are (nearly)
        coincident. By default any permutation of point order is also allowed.

        Two coordinate value are considered equal if they are both small
        compared to atol or if their difference divided by the second value
        is small compared to rtol.

        If permutations is set False, two elements are not considered equal
        if one's points are a permutation of the other's.
        """
        M = self.toMesh(rtol=rtol, atol=atol)
        ind, ok = M.elems.testDuplicate()
        return self.select(ind[ok])

    # REMOVED IN 1.0.0
    ## unique = removeDuplicate


#############################
# Test and clipping functions

    def test(self,nodes='all',dir=0,min=None,max=None,atol=0.):
        """Flag elements having nodal coordinates between min and max.

        This function is very convenient in clipping a Formex in a specified
        direction. It returns a 1D integer array flagging (with a value 1 or
        True) the elements having nodal coordinates in the required range.
        Use where(result) to get a list of element numbers passing the test.
        Or directly use clip() or cclip() to create the clipped Formex.

        The test plane can be defined in two ways, depending on the value of dir.
        If dir==0, 1 or 2, it specifies a global axis and min and max are
        the minimum and maximum values for the coordinates along that axis.
        Default is the 0 (or x) direction.

        Else, dir should be compaitble with a (3,) shaped array and specifies
        the direction of the normal on the planes. In this case, min and max
        are points and should also evaluate to (3,) shaped arrays.

        nodes specifies which nodes are taken into account in the comparisons.
        It should be one of the following:
        - a single (integer) point number (< the number of points in the Formex)
        - a list of point numbers
        - one of the special strings: 'all', 'any', 'none'
        The default ('all') will flag all the elements that have all their
        nodes between the planes x=min and x=max, i.e. the elements that
        fall completely between these planes. One of the two clipping planes
        may be left unspecified.
        """
        if min is None and max is None:
            raise ValueError("At least one of min or max have to be specified.")

        if isinstance(nodes, str):
            nod = arange(self.nplex())
        else:
            nod = nodes

        # Perform the test on the selected nodes
        X = self.coords[:, nod]
        T = X.test(dir=dir, min=min, max=max, atol=atol)

        if len(T.shape) > 1:
            # We have results for more than 1 node per element
            if nodes == 'any':
                T = T.any(axis=1)
            elif nodes == 'none':
                T = ~T.any(axis=1)
            else:
                T = T.all(axis=1)

        return asarray(T)


##############################################################################
#
#   Transformations that preserve the topology (but change coordinates)
#


    def circulize(self, angle):
        """Transform a linear sector into a circular one.

        A sector of the (0,1) plane with given angle, starting from the 0 axis,
        is transformed as follows: points on the sector borders remain in
        place. Points inside the sector are projected from the center on the
        circle through the intersection points of the sector border axes and
        the line through the point and perpendicular to the bisector of the
        angle. See Diamatic example."""
        e = tand(0.5*angle)
        errh = seterr(divide='ignore', invalid='ignore') # ignore division errors
        res = self.map(lambda x, y, z:[where(y==0, x, (x*x+x*y*e)/sqrt(x*x+y*y)), where(x==0, y, (x*y+y*y*e)/sqrt(x*x+y*y)), 0])
        seterr(**errh) # reactivate division errors
        return res


    def circulize1(self):
        """Transforms the first octant of the 0-1 plane into 1/6 of a circle.

        Points on the 0-axis keep their position. Lines parallel to the 1-axis
        are transformed into circular arcs. The bisector of the first quadrant
        is transformed in a straight line at an angle Pi/6.
        This function is especially suited to create circular domains where
        all bars have nearly same length. See the Diamatic example.
        """
        errh = seterr(divide='ignore', invalid='ignore') # ignore division errors
        res =self.map(lambda x, y, z:[where(x>0, x-y*y/(x+x), 0), where(x>0, y*sqrt(4*x*x-y*y)/(x+x), y), 0])
        seterr(**errh) # reactivate division errors
        return res


    def shrink(self, factor):
        """Shrinks each element with respect to its own center.

        Each element is scaled with the given factor in a local coordinate
        system with origin at the element center. The element center is the
        mean of all its nodes.
        The shrink operation is typically used (with a factor around 0.9) in
        wireframe draw mode to show all elements disconnected. A factor above
        1.0 will grow the elements.
        """
        c = self.coords.mean(1).reshape((self.coords.shape[0], 1, self.coords.shape[2]))
        return Formex(factor*(self.coords-c)+c, self.prop, self.eltype)


##############################################################################
#
#   Transformations that change the topology
#

    def reverse(self):
        """Return a Formex where all elements have been reversed.

        Reversing an element means reversing the order of its points.
        This is equivalent to::

          self.selectNodes(arange(self.nplex()-1,-1,-1))
        """
        return Formex(self.coords[:, ::-1], self.prop, self.eltype)


    def mirror(self,dir=2,pos=0,keep_orig=True):
        """Reflect a Formex in one of the coordinate directions

        This method behaves like reflect(), but adds the reflected
        part to the original. Setting keep_orig=False makes it behave just
        like reflect().
        """
        if keep_orig:
            return self+self.reflect(dir, pos)
        else:
            return self.reflect(dir, pos)


    def replicate(self,n,dir=0,step=1.0):
        """Replicate a Formex n times with fixed step in any direction.

        Returns a Formex which is the concatenation of n copies, where each
        copy is equal to the previous one translated over `(dir,step)`, where
        `dir` and `step` are interpreted just like in the :meth:`translate`
        method. The first of the copies is equal to the original.
        """
        f = self.coords.replicate(n, dir, step=step)
        f.shape = (f.shape[0]*f.shape[1], f.shape[2], f.shape[3])
        ## the replication of the properties is automatic!
        return Formex(f, self.prop, self.eltype)


    def rep(self,n,dir=None,step=None):
        """Like replicate, but allow repeated replication

        n, dir and step are lists. Default values for dir are [0,1,2]
        and [1.0,1.0,1.0], cutoff at the length of the specified n.
        """
        F = self
        if dir is None:
            dir = list(range(len(n)))
        if step is None:
            step = [1.]*len(n)
        for ni, diri, stepi in zip(n, dir, step):
            F = F.replicate(ni, diri, stepi)
        return F


    def replic(self,n,step=1.0,dir=0):
        """Return a Formex with n replications in direction dir with step.

        The original Formex is the first of the n replicas.
        """
        n = int(n)
        f = array( [ self.coords for i in range(n) ] )
        for i in range(1, n):
            f[i,:,:, dir] += i*step
        f.shape = (f.shape[0]*f.shape[1], f.shape[2], f.shape[3])
        ## the replication of the properties is automatic!
        return Formex(f, self.prop, self.eltype)


    def replic2(self,n1,n2,t1=1.0,t2=1.0,d1=0,d2=1,bias=0,taper=0):
        """Replicate in two directions.

        n1,n2 number of replications with steps t1,t2 in directions d1,d2
        bias, taper : extra step and extra number of generations in direction
        d1 for each generation in direction d2
        """
        P = [ self.translatem((d1, i*bias), (d2, i*t2)).replic(n1+i*taper, t1, d1)
              for i in range(n2) ]
        ## We should replace the Formex concatenation here by
        ## separate data and prop concatenations, because we are
        ## guaranteed that either none or all formices in P have props.
        return Formex.concatenate(P)


    def replicm(self,n,t=(1.0,1.0,1.0),d=(0,1,2)):
        """Replicate repeatedly in many directions.

        n: tuple: number of replications in subsequent directions
        t: tuple: steps in subsequent directions
        d: tuple: subsequent directions

        The three tuples shouls have the same length.
        """
        P = self
        for ni,ti,di in zip(n,t,d):
            P = P.replic(ni,ti,di)
        return P


    def rosette(self,n,angle,axis=2,point=[0., 0., 0.]):
        """Return a Formex with n rotational replications with angular
        step angle around an axis parallel with one of the coordinate axes
        going through the given point. axis is the number of the axis (0,1,2).
        point must be given as a list (or array) of three coordinates.
        The original Formex is the first of the n replicas.
        """
        f = self.coords - point
        f = array( [ f for i in range(n) ] )
        for i in range(1, n):
            m = array(rotationMatrix(i*angle, axis))
            f[i] = dot(f[i], m)
        f.shape = (f.shape[0]*f.shape[1], f.shape[2], f.shape[3])
        return Formex(f + point, self.prop, self.eltype)

    ros = rosette

    def translatem(self,*args,**kargs):
        """Multiple subsequent translations in axis directions.

        The argument list is a sequence of tuples (axis, step).
        Thus translatem((0,x),(2,z),(1,y)) is equivalent to
        translate([x,y,z]). This function is especially conveniant
        to translate in calculated directions.
        """
        tr = [0., 0., 0.]
        for d, t in args:
            tr[d] += t
        return self.translate(tr)


##############################################################################
#
#   Transformations that change the plexitude
#

    def extrude(self,div,dir=0,length=1.):
        """Extrude a Formex along a straight line.

        The Formex is extruded over a given length in the given direction.

        Parameters:

        - `div`: a value accepted as input by the :func:`mesh.smartSeed`
          function.
          It specifies how the extruded direction will be subdivided in
          elements.
        - `dir`: the direction of the extrusion: either a global axis
          number or a direction vector.
        - `length`: the length of the extrusion, measured along the direction
          `dir`.

        Returns the Formex obtained by extruding the input Formex over the
        given `length` in direction `dir`, subdividing this length according
        to the seeds specified by `dir`. The plexitude of the result will be
        double that of the input.

        This method works by converting the Formex to a :class:`Mesh`,
        using the :func:`Mesh.extrude` and then converting the result
        back to a Formex.

        See the :func:`connect` function for a more general tool to create
        new Formices out of existing ones.
        """
        return self.toMesh().extrude(div, dir, length).toFormex()


##############################################################################
#
#   Transformations that work only for some plexitudes
#
# !! It is not clear if they really belong here, or should go to a subclass


    def divide(self, div):
        """Divide a plex-2 Formex at the values in div.

        Replaces each member of the Formex by a sequence of members obtained
        by dividing the Formex at the relative values specified in div.
        The values should normally range from 0.0 to 1.0.

        As a convenience, if an integer is specified for div, it is taken as a
        number of divisions for the interval [0..1].

        This function only works on plex-2 Formices (line segments).
        """
        if self.nplex() != 2:
            raise RuntimeError("Can only divide plex-2 Formices")
        div = unitDivisor(div)
        A = interpolate(self.selectNodes([0]), self.selectNodes([1]), div[:-1], swap=True)
        B = interpolate(self.selectNodes([0]), self.selectNodes([1]), div[1:], swap=True)
        return connect([A, B])


    # TODO: returned Formex could inherit properties of parent
    def intersectionWithPlane(self,p,n,atol=0):
        """Return the intersection of a Formex with the plane (p,n) within tolerance atol.

        Currently this only works for plex-2 and plex-3 Formices.

        The intersection of the Formex with a plane specified by a point p
        and normal n is returned. For a plex-2 Formex (lines), the returned
        Formex will be of plexitude 1 (points). For a plex-3 Formex
        (triangles) the returned Formex has plexitude 2 (lines).
        """
        if self.nplex() == 2:
            from pyformex.geomtools import intersectionSWP
            return Formex(intersectionSWP(self.coords, p, n, mode='pair', atol=atol)[1])
        elif self.nplex() == 3:
            m = self.toSurface().intersectionWithPlane(p, n, atol=atol)
            if m.nelems() > 0:
                return m.toFormex()
            else:
                return Formex(array([], dtype=Float).reshape(0, 2, 3))
            #return Formex(intersectionLinesWithPlane(self,p,n))
        else:
            # OTHER PLEXITUDES NEED TO BE IMPLEMENTED
            raise ValueError("Formex should be plex-2 or plex-3")


    def cutWithPlane(self,p,n,side='',atol=None,newprops=None):
        """Cut a Formex with the plane(s) (p,n).

        .. warning:: This method currently only works for plexitude 2 or 3!

        Parameters:

        - `p`, `n`: a point and normal vector defining the cutting plane.
          In case of a Formex of plexitude 2, both `p` and `n` have shape (3,).
          In case of plexitude 3, `p` and/or `n` can be sequences of
          points, resp. vectors, allowing cutting with multiple planes.
          Both `p` and `n` can have shape (3) or (nplanes,3).
        - `side`: either an empty string, or one of '+' or '-'. In the latter
          cases, only the part at the positive, resp. negative side of the
          plane (as defined by its normal) is returned. The (default) empty
          string makes both parts being returned as a tuple (pos,neg).


        Returns:

          The default return value is a tuple of two Formices of the same
          plexitude as the input: (Fpos,Fneg), where Fpos is the part of the
          Formex at the positive side of the plane (as defined by the normal
          vector), and Fneg is the part at the negative side.
          Elements of the input Formex that are lying completely on one side
          of the plane will return unaltered. Elements that are crossing the
          plane will be cut and split up into multiple parts.

          When side = '+' or '-' (or 'positive'or 'negative'), only one
          of the sides is returned.

        """
        if atol is None:
            atol = 1.e-5*self.dsize()
        if self.nplex() == 2:
            return cut2AtPlane(self, p, n, side, atol, newprops)
        elif self.nplex() == 3:
            return cut3AtPlane(self, p, n, side, atol, newprops)
        else:
            # OTHER PLEXITUDES NEED TO BE IMPLEMENTED
            raise ValueError("Formex should be plex-2 or plex-3")


#################### Misc Operations #########################################

    def split(self,n=1):
        """Split a Formex in subFormices containing n elements.

        The number of elements in the Formex should be a multiple of n.
        Returns a list of Formices each comprising n elements.
        """
        if self.nelems() % n != 0:
            raise RuntimeError("Number of elements should be integer multiple of n")
        m = self.nelems()//n
        if self.prop is None:
            return [ Formex(self.coords[n*i:n*(i+1)], self.eltype) for i in range(m) ]
        else:
            return [ Formex(self.coords[n*i:n*(i+1)], self.prop[n*i:n*(i+1)], self.eltype) for i in range(m) ]


    def lengths(self):
        """Compute the length of all elements of a 2-plex Formex.

        The length of an element is the distance between its two points.
        """
        if self.nplex() != 2:
            raise ValueError("Expected a 2-plex Formex, got %s" % self.nplex())
        from pyformex.geomtools import levelVolumes
        return levelVolumes(self.coords)


    def areas(self):
        """Compute the areas of all elements of a 3-plex Formex.

        The area of an element is the aread of the triangle formed by its
        three points.
        """
        if self.nplex() != 3:
            raise ValueError("Expected a 3-plex Formex, got %s" % self.nplex())
        from pyformex.geomtools import levelVolumes
        return levelVolumes(self.coords)


    def volumes(self):
        """Compute the volume of all elements of a 4-plex Formex.

        The volume of an element is the volume of the tetraeder formed
        by its points.
        """
        if self.nplex() != 4:
            raise ValueError("Expected a 4-plex Formex, got %s" % self.nplex())
        from pyformex.geomtools import levelVolumes
        return levelVolumes(self.coords)


#################### Read from string/file ##################################

    #
    # See also Geometry.read and Geometry.write
    #


    @classmethod
    def fromstring(clas,fil,sep=' ',nplex=1,ndim=3,count=-1):
        """Create a :class:`Formex` from coodinates in a string.

        This uses the :meth:`Coords.fromstring` method to read coordinates
        from a string and restructures them into a Formex of the specified
        plexitude.

        Parameters:

        - `fil`: a string containing a single sequence of float numbers separated
          by whitespace and a possible separator string.
        - `sep`: the separator used between the coordinates. If not a space,
          all extra whitespace is ignored.
        - `ndim`: number of coordinates per point. Should be 1, 2 or 3 (default).
          If 1, resp. 2, the coordinate string only holds x, resp. x,y values.
        - `count`: total number of coordinates to read. This should be a multiple
          of 3. The default is to read all the coordinates in the string.
          ``count`` can be used to force an error condition if the string
          does not contain the expected number of values.

        The return value is a :class:`Coords` object.
        """
        x = Coords.fromstring(fil, sep=sep, ndim=ndim, count=count)
        if x.shape[0] % nplex != 0:
            raise RuntimeError("Number of points read: %s, expected a multiple of %s!" % (x.shape[0], nplex))
        return Formex(x.reshape(-1, nplex, 3))


    @classmethod
    def fromfile(clas,fil,sep=' ',nplex=1):
        """Read the coordinates of a Formex from a file"""
        x = Coords.fromfile(fil, sep=sep)
        if x.shape[0] % nplex != 0:
            raise RuntimeError("Number of points read: %s, should be multiple of %s!" % (x.shape[0], nplex))
        return Formex(x.reshape(-1, nplex, 3))


    def actor(self,**kargs):
        from pyformex.opengl.drawable import GeomActor

        if self.nelems() == 0:
            return None

        return GeomActor(self,**kargs)


#########################################################################
    #
    # Obsolete and deprecated functions
    #

    nnodes = npoints


##############################################################################
#
#    Functions which are not Formex class methods
#

def connect(Flist,nodid=None,bias=None,loop=False,eltype=None):
    """Return a Formex which connects the Formices in list.

    Flist is a list of formices, nodid is an optional list of nod ids and
    bias is an optional list of element bias values. All lists should have
    the same length.
    The returned Formex has a plexitude equal to the number of
    formices in list. Each element of the Formex consist of a node from
    the corresponding element of each of the formices in list. By default
    this will be the first node of that element, but a nodid list may be
    given to specify the node id to be used for each of the formices.
    Finally, a list of bias values may be given to specify an offset in
    element number for the subsequent formices.
    If loop==False, the order of the Formex will be the minimum order of
    the formices in Flist, each minus its respective bias. By setting
    loop=True however, each Formex will loop around if its end is
    encountered, and the order of the result is the maximum order in Flist.
    """
    try:
        m = len(Flist)
        for i in range(m):
            if isinstance(Flist[i], Formex):
                pass
            elif isinstance(Flist[i], ndarray):
                Flist[i] = Formex(Flist[i])
            else:
                raise TypeError
    except TypeError:
        raise TypeError('connect(): first argument should be a list of formices')

    if not nodid:
        nodid = [ 0 for i in range(m) ]
    if not bias:
        bias = [ 0 for i in range(m) ]
    if loop:
        n = max([ Flist[i].nelems() for i in range(m) ])
    else:
        n = min([ Flist[i].nelems() - bias[i] for i in range(m) ])
    f = zeros((n, m, 3), dtype=Float)
    for i, j, k in zip(range(m), nodid, bias):
        v = Flist[i].coords[k:k+n, j,:]
        if loop and k > 0:
            v = concatenate([v, Flist[i].coords[:k, j,:]])
        f[:, i,:] = resize(v, (n, 3))
    return Formex(f,eltype=eltype)


def interpolate(F,G,div,swap=False,concat=True):
    """Create interpolations between two formices.

    F and G are two Formices with the same shape.
    div is a list of floating point values.
    The result is the concatenation of the interpolations of F and G at all
    the values in div.
    An interpolation of F and G at value v is a Formex H where each coordinate
    Hijk is obtained from:  Hijk = Fijk + v * (Gijk-Fijk).
    Thus, a Formex interpolate(F,G,[0.,0.5,1.0]) will contain all elements
    of F and G and all elements with mean coordinates between those of F and G.

    As a convenience, if an integer is specified for div, it is taken as a
    number of divisions for the interval [0..1].
    Thus, interpolate(F,G,n) is equivalent with
    interpolate(F,G,arange(0,n+1)/float(n))

    The swap argument sets the order of the elements in the resulting Formex.
    By default, if n interpolations are created of an m-element Formex, the
    element order is in-Formex first (n sequences of m elements).
    If swap==True, the order is swapped and you get m sequences of n
    interpolations.
    """
    r = F.coords.interpolate(G.coords, div)
    # r is a 4-dim array
    if swap:
        r = r.swapaxes(0, 1)
    return Formex(r.reshape((-1,) + r.shape[-2:]))


def pointsAt(F, t):
    """Return the points of a plex-2 Formex at times t.

    F is a plex 2 Formex and t is an array with F.nelems() float values which
    are interpreted as local parameters along the edges of the Formex, such
    that the first node has value 0.0 and the last has value 1.0.
    The return value is a :class:`coords.Coords` array with the points at values t.
    """
    f = F.coords
    t = t[:, newaxis]
    return Coords((1.-t) * f[:, 0,:] + t * f[:, 1,:])


def intersectionLinesWithPlane(F,p,n,atol=1.e-4):
    """Return the intersection lines of a plex-3 Formex with plane (p,n).

    F is a Formex of plexitude 3.
    p is a point specified by 3 coordinates.
    n is the normal vector to a plane, specified by 3 components.
    atol is a tolerance factor defining whether an edge is intersected by the plane.
    """
    n = asarray(n)
    p = asarray(p)
    F = F.cclip(F.test('all', n, p)) # remove elements at the negative side
    if F.nelems() == 0:
        return Formex(empty((0, 2, 3,), dtype=float))
    F = F.cclip(F.test('all', -n, p)) # select elements that will be cut by plane
    if F.nelems() == 0:
        return Formex(empty((0, 2, 3,), dtype=float))
    F1 = F21 = F22 = F31 = F32 = F41 = F42= F43 = Formex(empty((0, 2, 3,), dtype=float))
    # Create a Formex with the edges
    C = Formex.concatenate([ F.selectNodes(e) for e in [[0, 1], [1, 2], [2, 0]] ])
    t = C.intersectionWithPlane(p, n)
    P = pointsAt(C, t)
    t = t.reshape(3, -1).transpose()
    Pb = P.reshape(3, -1, 3).swapaxes(0, 1)
    Pf = F.coords
    Ps = roll(F.coords, -1, axis=1)
    t1 = t >= 0.+atol
    t2 = t <= 1.-atol
    t3 = t >= 0.-atol
    t4 = t <= 1.+atol
    Tb = t1 * t2
    Tf = (1-t1).astype(bool)*t3
    Ts = (1-t2).astype(bool)*t4
    Nb = Tb.sum(axis=-1)
    Nf = Tf.sum(axis=-1)
    Ns = Ts.sum(axis=-1)
    # Get the triangles with 2 edge intersections
    w1 = where(Nb==2)[0]
    if w1.size > 0:
        P = Pb[w1][Tb[w1]].reshape(-1, 2, 3)
        F1 = Formex(P)
    # Get the triangles with 1 edge intersection and 1 vertex intersection
    w21 = where( (Nb==1) * (Nf==1) * (Ns==0) )[0]
    if w21.size > 0:
        P1 = Pb[w21][Tb[w21]].reshape(-1, 1, 3)
        P2 = Pf[w21][Tf[w21]].reshape(-1, 1, 3)
        P = column_stack([P1, P2])
        F21 = Formex(P)
    w22 = where( (Nb==1) * (Nf==0) * (Ns==1) )[0]
    if w22.size > 0:
        P1 = Pb[w22][Tb[w22]].reshape(-1, 1, 3)
        P2 = Ps[w22][Ts[w22]].reshape(-1, 1, 3)
        P = column_stack([P1, P2])
        F22 = Formex(P)
    # Get the triangles with 1 edge intersection and 2 vertex intersections
    w3 = where( (Nb==1) * (Nf==1) * (Ns==1) )[0]
    if w3.size > 0:
        Tb3 = Tb[w3]
        Tf3 = Tf[w3]
        Ts3 = Ts[w3]
        Pb3 = Pb[w3]
        Pf3 = Pf[w3]
        Ps3 = Ps[w3]
        i = where(Ts3)[1] - where(Tf3)[1]
        w31 = where((i == 1)+(i==-2))[0] # different vertices
        if w31.size > 0:
            P1 = Pf3[w31][Tf3[w31]].reshape(-1, 1, 3)
            P2 = Ps3[w31][Ts3[w31]].reshape(-1, 1, 3)
            P = column_stack([P1, P2])
            F32 = Formex(P)
        w32 = where((i == -1)+(i==2))[0] # equal vertices
        if w32.size > 0:
            P1 = Pb3[w32][Tb3[w32]].reshape(-1, 1, 3)
            P2 = Pf3[w32][Tf3[w32]].reshape(-1, 1, 3)
            P = column_stack([P1, P2])
            F31 = Formex(P)
    # Get the triangles with 0 edge intersections and 2 or 3 vertex intersections
    w41 = where( (Nb==0) * (Nf==2) )[0]
    if w41.size > 0:
        P = Pf[w41][Tf[w41]].reshape(-1, 2, 3)
        F41 = Formex(P)
    w42 = where( (Nb==0) * (Ns==2) )[0]
    if w42.size > 0:
        P = Ps[w42][Ts[w42]].reshape(-1, 2, 3)
        F42 = Formex(P)
    w43 = where( (Nb==0) * (Nf==1) * (Ns==1) )[0]
    if w43.size > 0:
        Tf43 = Tf[w43]
        Ts43= Ts[w43]
        Pf43 = Pf[w43]
        Ps43 = Ps[w43]
        i = where(Ts43)[1] - where(Tf43)[1]
        w43 = where((i == 1)+(i==-2))[0] # different vertices
        if w43.size > 0:
            P1 = Pf43[w43][Tf43[w43]].reshape(-1, 1, 3)
            P2 = Ps43[w43][Ts43[w43]].reshape(-1, 1, 3)
            P = column_stack([P1, P2])
            F43 = Formex(P)
    # join all the pieces
    Ft = F1 + F21 + F22 + F31 + F32 + F41 + F42+ F43
    return Ft


def _sane_side(side):
    """_Allow some old variants of arguments_"""
    if isinstance(side, str):
        if side.startswith('pos'):
            side = '+'
        if side.startswith('neg'):
            side = '-'
    if not (side == '+' or side == '-'):
        side = ''
    return side

def _select_side(side, alist):
    """_Return selected parts dependent on side_"""
    if side == '+':
        return alist[0]
    elif side == '-':
        return alist[1]
    else:
        return alist


def cut2AtPlane(F,p,n,side='',atol=None,newprops=None):
    """Returns all elements of the Formex cut at plane.

    F is a Formex of plexitude 2.
    p is a point specified by 3 coordinates.
    n is the normal vector to a plane, specified by 3 components.

    The return value is:

    - with side = '+' or '-' or 'positive'or 'negative' :
      a Formex of the same plexitude with all elements
      located completely at the positive/negative side of the plane(s) (p,n)
      retained, all elements lying completely at the negative/positive side
      removed and the elements intersecting the plane(s) replaced by new
      elements filling up the parts at the positive/negative side.
    - with side = '': two Formices of the same plexitude, one representing
      the positive side and one representing the negative side.

    To avoid roundoff errors and creation of very small elements,
    a tolerance can be specified. Points lying within the tolerance
    distance will be considered lying in the plane, and no cutting near
    these points.
    """
    side = _sane_side(side)
    dist = F.distanceFromPlane(p, n)
    if atol is None:
        atol = 1.e-5*dist.max()
    above = sum(dist>atol, -1)
    below = sum(dist<-atol, -1)
    A = F.clip(below==0)
    B = F.clip(above==0)
    cutting = (above>0)*(below>0)
    if newprops:
       A.setProp(newprops[0])
       B.setProp(newprops[1])
    ## print("Elements in F: %s" % F.nelems())
    ## print("Elements in A: %s" % A.nelems())
    ## print("Elements in B: %s" % B.nelems())

    if cutting.any():
        G = F.clip(cutting)
        H = G.copy()

        g = G.intersectionWithPlane(p, n)
        dist = dist[cutting]
        i0 = dist[:, 0] < 0.
        i1 = dist[:, 1] < 0.
        G[i0, 0,:] = H[i0, 1,:] = g[i0].reshape(-1, 3)
        G[i1, 1,:] = H[i1, 0,:] = g[i1].reshape(-1, 3)
        if newprops:
           G.setProp(newprops[2])
           H.setProp(newprops[3])
        A += G
        B += H

        ## print("Elements in G: %s" % G.nelems())
        ## print("Elements in A: %s" % A.nelems())
        ## print("Elements in B: %s" % B.nelems())
    return _select_side(side, [ A, B ])


def cut3AtPlane(F,p,n,side='',atol=None,newprops=None):
    """Returns all elements of the Formex cut at plane(s).

    F is a Formex of plexitude 3.
    p is a point or a list of points.
    n is the normal vector to a plane or a list of normal vectors.
    Both p and n have shape (3) or (npoints,3).

    The return value is:

    - with side='+' or '-' or 'positive'or 'negative' :
      a Formex of the same plexitude with all elements
      located completely at the positive/negative side of the plane(s) (p,n)
      retained, all elements lying completely at the negative/positive side
      removed and the elements intersecting the plane(s) replaced by new
      elements filling up the parts at the positive/negative side.
    - with side='': two Formices of the same plexitude, one representing
      the positive side and one representing the negative side.

    Let :math:`dist` be the signed distance of the vertices to a plane.
    The elements located completely at the positive or negative side of
    a plane have three vertices for which :math:`|dist|>atol`.
    The elements intersecting a plane can have one or more vertices for which
    :math:`|dist|<atol`.
    These vertices are projected on the plane so that their distance is zero.

    If the Formex has a property set, the new elements will get the property
    numbers defined in newprops. This is a list of 7 property numbers flagging
    elements with following properties:

    0) no vertices with :math:`|dist|<atol`, triangle after cut
    1) no vertices with :math:`|dist|<atol`, triangle 1 from quad after cut
    2) no vertices with :math:`|dist|<atol`, triangle 2 from quad after cut
    3) one vertex with :math:`|dist|<atol`, two vertices at pos. or neg. side
    4) one vertex with :math:`|dist|<atol`, one vertex at pos. side, one at neg.
    5) two vertices with :math:`|dist|<atol`, one vertex at pos. or neg. side
    6) three vertices with :math:`|dist|<atol`
    """
    if atol is None:
        atol = 1.e-5*F.dsize()
    # make sure we have sane newprops
    if newprops is None:
        newprops = [None,]*7
    else:
        try:
            newprops = newprops[:7]
            for prop in newprops:
                if not (prop is None or isinstance(prop, int)):
                    raise
        except:
            newprops = arange(7)
    side = _sane_side(side)

    p = asarray(p).reshape(-1, 3)
    n = asarray(n).reshape(-1, 3)
    nplanes = len(p)
    test = stack([F.test('any', n[i], p[i], atol=atol) for i in range(nplanes)]).all(axis=0) # elements having part at positive side of all planes
    F_pos = F.clip(test) # save elements having part at positive side of all planes
    if side in '-': # Dirty trick: this also includes side='' !
        F_neg = F.cclip(test) # save elements completely at negative side of one of the planes
    else:
        F_neg = None
    if F_pos.nelems() != 0:
        test = stack([F_pos.test('all', n[i], p[i], atol=-atol) for i in range(nplanes)]).all(axis=0) # elements completely at positive side of all planes
        F_cut = F_pos.cclip(test) # save elements that will be cut by one of the planes
        F_pos = F_pos.clip(test)  # save elements completely at positive side of all planes
        if F_cut.nelems() != 0:
            if nplanes == 1:
                if side == '+':
                    F_pos += cutElements3AtPlane(F_cut, p[i], n[i], newprops, side, atol)
                elif side == '-':
                    F_neg += cutElements3AtPlane(F_cut, p[i], n[i], newprops, side, atol)
                elif side == '':
                    cut_pos, cut_neg = cutElements3AtPlane(F_cut, p[i], n[i], newprops, side, atol)
                    F_pos += cut_pos
                    F_neg += cut_neg
            elif nplanes > 1:
                S = F_cut
                for i in range(nplanes):
                    if i > 0:
                        # due to the projection of vertices with |distance| < atol on plane i-1, some elements can be completely at negative side of plane i instead of cut by plane i
                        t = S.test('any', n[i], p[i], atol=atol)
                        if side in '-':
                            F_neg += S.cclip(t) # save elements completely at negative side of plane i
                        S = S.clip(t) # save elements at positive side of plane i
                    t = S.test('all', n[i], p[i], atol=-atol)
                    R = S.clip(t) # save elements completely at positive side of plane i
                    S = S.cclip(t) # save elements that will be cut by plane i
                    if side == '+':
                        cut_pos = cutElements3AtPlane(S, p[i], n[i], newprops, '+', atol)
                    elif side in '-':
                        cut_pos, cut_neg = cutElements3AtPlane(S, p[i], n[i], newprops, '', atol)
                        F_neg += cut_neg
                    S = R + cut_pos
                F_pos += S

    return _select_side(side, [ F_pos, F_neg ])


def cutElements3AtPlane(F,p,n,newprops=None,side='',atol=0.):
    """This function needs documentation.

    Should it be called by the user? or only via cut3AtPlane?
    For now, lets suppose the last, so no need to check arguments here.

    newprops should be a list of 7 values: each an integer or None
    side is either '+', '-' or ''
    """
    if atol is None:
        atol = 1.e-5*F.dsize()

    def get_new_prop(p, ind, newp):
        """Determines the value of the new props for a subset.

        p are the original props (possibly None)
        ind is the list of elements to treat
        newp is the new property value.

        The return value is determined as follows:

        - If p is None: return None (no property set)
        - If p is set, but newp is None: return p[ind] : keep original
        - if p is set, and newp is set: return newp (single value)
        """
        if p is None:
            return None
        elif newp is None:
            return p[ind]
        else:
            return newp

    from pyformex.geomtools import intersectionSWP
    C = [connect([F, F], nodid=ax) for ax in [[0, 1], [1, 2], [2, 0]]]
    errh = seterr(divide='ignore', invalid='ignore')
    res = [intersectionSWP(Ci.coords, p, n, mode='pair', return_all=True, atol=atol) for Ci in C]
    seterr(**errh)
    t = column_stack([r[0] for r in res])
    P = stack([r[1] for r in res], axis=1)
    del res
    T = (t >= 0.)*(t <= 1.)
    d = F.coords.distanceFromPlane(p, n)
    U = abs(d) < atol
    V = U.sum(axis=-1) # number of vertices with |distance| < atol
    F1_pos = F2_pos = F3_pos = F4_pos = F5_pos = F6_pos = F7_pos = F1_neg = F2_neg = F3_neg = F4_neg = F5_neg = F6_neg = F7_neg = Formex()
    # No vertices with |distance| < atol => triangles with 2 intersections
    w1 = where(V==0)[0]
    if w1.size > 0:
        T1 = T[w1]
        P1 = P[w1][T1].reshape(-1, 2, 3)
        F1 = F[w1]
        d1 = d[w1]
        if F.prop is None:
            p1 = None
        else:
            p1 = F.prop[w1]
        # split problem in two cases
        w11 = where(d1[:, 0]*d1[:, 1]*d1[:, 2] > 0.)[0] # case 1: triangle at positive side after cut
        w12 = where(d1[:, 0]*d1[:, 1]*d1[:, 2] < 0.)[0] # case 2: quadrilateral at positive side after cut
        # case 1: triangle at positive side after cut
        if w11.size > 0:
            T11 = T1[w11]
            P11 = P1[w11]
            F11 = F1[w11]
            if side in '+':
                v1 = where(T11[:, 0]*T11[:, 2] == 1, 0, where(T11[:, 0]*T11[:, 1] == 1, 1, 2))
                K1 = asarray([F11[j, v1[j]] for j in range(shape(F11)[0])]).reshape(-1, 1, 3)
                E1_pos = column_stack([P11, K1])
                F1_pos = Formex(E1_pos, get_new_prop(p1, w11, newprops[0]))
            if side in '-': #quadrilateral at negative side after cut
                v2 = where(T11[:, 0]*T11[:, 2] == 1, 2, where(T11[:, 0]*T11[:, 1] == 1, 2, 0))
                v3 = where(T11[:, 0]*T11[:, 2] == 1, 1, where(T11[:, 0]*T11[:, 1] == 1, 0, 1))
                K2 = asarray([F11[j, v2[j]] for j in range(shape(F11)[0])]).reshape(-1, 1, 3)
                K3 = asarray([F11[j, v3[j]] for j in range(shape(F11)[0])]).reshape(-1, 1, 3)
                E2_neg = column_stack([P11, K2])
                F2_neg = Formex(E2_neg, get_new_prop(p1, w11, newprops[1]))
                E3_neg = column_stack([P11[:, 0].reshape(-1, 1, 3), K2, K3])
                F3_neg = Formex(E3_neg, get_new_prop(p1, w11, newprops[2]))
        # case 2: quadrilateral at positive side after cut
        if w12.size > 0:
            T12 = T1[w12]
            P12 = P1[w12]
            F12 = F1[w12]
            if side in '+':
                v2 = where(T12[:, 0]*T12[:, 2] == 1, 2, where(T12[:, 0]*T12[:, 1] == 1, 2, 0))
                v3 = where(T12[:, 0]*T12[:, 2] == 1, 1, where(T12[:, 0]*T12[:, 1] == 1, 0, 1))
                K2 = asarray([F12[j, v2[j]] for j in range(shape(F12)[0])]).reshape(-1, 1, 3)
                K3 = asarray([F12[j, v3[j]] for j in range(shape(F12)[0])]).reshape(-1, 1, 3)
                E2_pos = column_stack([P12, K2])
                F2_pos = Formex(E2_pos, get_new_prop(p1, w12, newprops[1]))
                E3_pos = column_stack([P12[:, 0].reshape(-1, 1, 3), K2, K3])
                F3_pos = Formex(E3_pos, get_new_prop(p1, w12, newprops[2]))
            if side in '-': # triangle at negative side after cut
                v1 = where(T12[:, 0]*T12[:, 2] == 1, 0, where(T12[:, 0]*T12[:, 1] == 1, 1, 2))
                K1 = asarray([F12[j, v1[j]] for j in range(shape(F12)[0])]).reshape(-1, 1, 3)
                E1_neg = column_stack([P12, K1])
                F1_neg = Formex(E1_neg, get_new_prop(p1, w12, newprops[0]))
    # One vertex with |distance| < atol
    w2 = where(V==1)[0]
    if w2.size > 0:
        F2 = F[w2]
        d2 = d[w2]
        U2 = U[w2]
        if F.prop is None:
            p2 = None
        else:
            p2 = F.prop[w2]
        # split problem in three cases
        W = (d2 > atol).sum(axis=-1)
        w21 = where(W == 2)[0] # case 1: two vertices at positive side
        w22 = where(W == 1)[0] # case 2: one vertex at positive side
        w23 = where(W == 0)[0] # case 3: no vertices at positive side
        # case 1: two vertices at positive side
        if w21.size > 0 and side in '+':
            F21 = F2[w21]
            U21 = U2[w21]
            K1 = F21[U21] # vertices with |distance| < atol
            n = normalize(n)
            K1 = (K1 - n*d2[w21][U21].reshape(-1, 1)).reshape(-1, 1, 3) # project vertices on plane (p,n)
            K2 = F21[d2[w21]>atol].reshape(-1, 2, 3) # vertices with distance > atol
            E4_pos = column_stack([K1, K2])
            F4_pos = Formex(E4_pos, get_new_prop(p2, w21, newprops[3]))
        # case 2: one vertex at positive side
        if w22.size > 0:
            F22 = F2[w22]
            U22 = U2[w22]
            K1 = F22[U22] # vertices with |distance| < atol
            K1 = (K1 - n*d2[w22][U22].reshape(-1, 1)).reshape(-1, 1, 3) # project vertices on plane (p,n)
            P22 = P[w2][w22][roll(U22, 1, axis=-1)].reshape(-1, 1, 3) # intersection points
            if side in '+':
                K2 = F22[d2[w22]>atol].reshape(-1, 1, 3) # vertices with distance > atol
                E5_pos = column_stack([P22, K1, K2])
                F5_pos = Formex(E5_pos, get_new_prop(p2, w22, newprops[4]))
            if side in '-':
                K3 = F22[d2[w22]<-atol].reshape(-1, 1, 3) # vertices with distance < - atol
                E5_neg = column_stack([P22, K1, K3])
                F5_neg = Formex(E5_neg, get_new_prop(p2, w22, newprops[4]))
        # case 3: no vertices at positive side
        if w23.size > 0 and side in '-':
            F23 = F2[w23]
            U23 = U2[w23]
            K1 = F23[U23] # vertices with |distance| < atol
            K1 = (K1 - n*d2[w23][U23].reshape(-1, 1)).reshape(-1, 1, 3) # project vertices on plane (p,n)
            K2 = F23[d2[w23]<-atol].reshape(-1, 2, 3) # vertices with distance < - atol
            E4_neg = column_stack([K1, K2])
            F4_neg = Formex(E4_neg, get_new_prop(p2, w23, newprops[3]))
    # Two vertices with |distance| < atol
    w3 = where(V==2)[0]
    if w3.size > 0:
        F3 = F[w3]
        d3 = d[w3]
        U3 = U[w3]
        # split problem in two cases
        W = (d3 > atol).sum(axis=-1)
        w31 = where(W == 1)[0] # case 1: one vertex at positive side
        w32 = where(W == 0)[0] # case 2: no vertices at positive side
        # case 1: one vertex at positive side
        if w31.size > 0 and side in '+':
            F31 = F3[w31]
            U31 = U3[w31]
            K1 = F31[U31] # vertices with |distance| < atol
            K1 = (K1 - n*d3[w31][U31].reshape(-1, 1)).reshape(-1, 2, 3) # project vertices on plane (p,n)
            K2 = F31[d3[w31]>atol].reshape(-1, 1, 3) # vertices with distance > atol
            E6_pos = column_stack([K1, K2])
            F6_pos = Formex(E6_pos, get_new_prop(F.prop, w31, newprops[5]))
        # case 2: no vertices at positive side
        if w32.size > 0 and side in '-':
            F32 = F3[w32]
            U32 = U3[w32]
            K1 = F32[U32] # vertices with |distance| < atol
            K1 = (K1 - n*d3[w32][U32].reshape(-1, 1)).reshape(-1, 2, 3) # project vertices on plane (p,n)
            K2 = F32[d3[w32]<-atol].reshape(-1, 1, 3) # vertices with distance < - atol
            E6_neg = column_stack([K1, K2])
            F6_neg = Formex(E6_neg, get_new_prop(F.prop, w32, newprops[5]))
    # Three vertices with |distance| < atol
    w4 = where(V==3)[0]
    if w4.size > 0:
        F4 = F[w4]
        d4 = d[w4]
        U4 = U[w4]
        if side in '+':
            K1 = F4[U4] # vertices with |distance| < atol
            K1 = (K1 - n*d4[U4].reshape(-1, 1)).reshape(-1, 3, 3) # project vertices on plane (p,n)
            E7_pos = K1
            F7_pos = Formex(E7_pos, get_new_prop(F.prop, w4, newprops[6]))
        if side in '-':
            E7_neg = K1
            F7_neg = Formex(E7_neg, get_new_prop(F.prop, w4, newprops[6]))
    # join all the pieces
    if side in '+':
        cut_pos = F1_pos+F2_pos+F3_pos+F4_pos+F5_pos+F6_pos+F7_pos
    if side in '-':
        cut_neg = F1_neg+F2_neg+F3_neg+F4_neg+F5_neg+F6_neg+F7_neg

    if side == '+':
        return cut_pos
    elif side == '-':
        return cut_neg
    else:
        return [ cut_pos, cut_neg ]


# End
