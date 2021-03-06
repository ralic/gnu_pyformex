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

"""Using NURBS in pyFormex.

The :mod:`nurbs` module defines functions and classes to manipulate
NURBS curves and surface in pyFormex.
"""
from __future__ import absolute_import, division, print_function


from pyformex import arraytools as at
from pyformex import geomtools as gt
from pyformex.coords import Coords
from pyformex.attributes import Attributes
from pyformex.lib import nurbs
from pyformex.plugins import curve
from pyformex import utils

import numpy as np


###########################################################################
##
##   class Coords4
##
#########################
#
class Coords4(np.ndarray):
    """A collection of points represented by their homogeneous coordinates.

    While most of the pyFormex implementation is based on the 3D Cartesian
    coordinates class :class:`Coords`, some applications may benefit from using
    homogeneous coordinates. The class :class:`Coords4` provides some basic
    functions and conversion to and from cartesian coordinates.
    Through the conversion, all other pyFormex functions, such as
    transformations, are available.

    :class:`Coords4` is implemented as a float type :class:`numpy.ndarray`
    whose last axis has a length equal to 4.
    Each set of 4 values (x,y,z,w) along the last axis represents a
    single point in 3D space. The cartesian coordinates of the point
    are obtained by dividing the first three values by the fourth:
    (x/w, y/w, z/w). A zero w-value represents a point at infinity.
    Converting such points to :class:`Coords` will result in Inf or NaN
    values in the resulting object.

    The float datatype is only checked at creation time. It is the
    responsibility of the user to keep this consistent throughout the
    lifetime of the object.

    Just like :class:`Coords`, the class :class:`Coords4` is derived from
    :class:`numpy.ndarray`.

    Parameters:

    `data`: array_like
      If specified, data should evaluate to an array of floats, with the
      length of its last axis not larger than 4. When equal to four, each
      tuple along the last axis represents a ingle point in homogeneous
      coordinates.
      If smaller than four, the last axis will be expanded to four by adding
      values zero in the second and third position and values 1 in the last
      position.
      If no data are given, a single point (0.,0.,0.) will be created.

    `w`: array_like
      If specified, the w values are used to denormalize the homogeneous
      data such that the last component becomes w.

    `dtyp`: data-type
      The datatype to be used. It not specified, the datatype of `data`
      is used, or the default :data:`Float` (which is equivalent to
      :data:`numpy.float32`).

    `copy`: boolean
      If ``True``, the data are copied. By default, the original data are
      used if possible, e.g. if a correctly shaped and typed
      :class:`numpy.ndarray` is specified.
    """

    def __new__(cls, data=None, w=None, normalize=True, dtyp=at.Float, copy=False):
        """Create a new instance of :class:`Coords4`."""
        if data is None:
            # create an empty array
            ar = np.ndarray((0, 4), dtype=dtyp)
        else:
            # turn the data into an array, and copy if requested
            ar = np.array(data, dtype=dtyp, copy=copy)

        if ar.shape[-1] in [3, 4]:
            pass
        elif ar.shape[-1] in [1, 2]:
            # make last axis length 3, adding 0 values
            ar = at.growAxis(ar, 3-ar.shape[-1], -1)
        elif ar.shape[-1] == 0:
            # allow empty coords objects
            ar = ar.reshape(0, 3)
        else:
            raise ValueError("Expected a length 1,2,3 or 4 for last array axis")

        # Make sure dtype is a float type
        if ar.dtype.kind != 'f':
            ar = ar.astype(at.Float)

        # We should now have a float array with last axis 3 or 4
        if ar.shape[-1] == 3:
            # Expand last axis to length 4, adding values 1
            ar = at.growAxis(ar, 1, -1, 1.0)

        if w is not None:
            if normalize:
                ar[...,:3] /= w
            else:
                # Insert weight
                ar[...,3] = w

        # Transform 'subarr' from an ndarray to our new subclass.
        ar = ar.view(cls)

        return ar


    def normalize(self):
        """Normalize the homogeneous coordinates.

        Two sets of homogeneous coordinates that differ only by a
        multiplicative constant refer to the same points in cartesian space.
        Normalization of the coordinates is a way to make the representation
        of a single point unique. Normalization is done so that the last
        component (w) is equal to 1.

        The normalization of the coordinates is done in place.

        .. warning:: Normalizing points at infinity will result in Inf or
           NaN values.
        """
        self /= self[..., 3:]


    def deNormalize(self, w):
        """Denormalizes the homogeneous coordinates.

        This multiplies the homogeneous coordinates with the values w.
        w normally is a constant or an array with shape
        self.shape[:-1] + (1,).
        It then multiplies all 4 coordinates of a point with the same
        value, thus resulting in a denormalization while keeping the
        position of the point unchanged.

        The denormalization of the coordinates is done in place.
        If the Coords4 object was normalized, it will have precisely w as
        its 4-th coordinate value after the call.
        """
        self *= w


    def toCoords(self):
        """Convert homogeneous coordinates to cartesian coordinates.

        Returns:

        A :class:`Coords` object with the cartesian coordinates
        of the points. Points at infinity (w=0) will result in
        Inf or NaN value. If there are no points at infinity, the
        resulting :class:`Coords` point set is equivalent to the
        :class:`Coords4` one.
        """
        return Coords(self[..., :3] / self[..., 3:])


    def npoints(self):
        """Return the total number of points."""
        return np.asarray(self.shape[:-1]).prod()


    ncoords = npoints


    def x(self):
        """Return the x-plane"""
        return self[..., 0]
    def y(self):
        """Return the y-plane"""
        return self[..., 1]
    def z(self):
        """Return the z-plane"""
        return self[..., 2]
    def w(self):
        """Return the w-plane"""
        return self[..., 3]


    def bbox(self):
        """Return the bounding box of a set of points.

        Returns the bounding box of the cartesian coordinates of
        the object.
        """
        return self.toCoords().bbox()


    def actor(self,**kargs):
        """Graphical representation"""
        return self.toCoords().actor()


class Geometry4(object):
    """This is a preliminary class intended to provide some transforms in 4D

    """

    def __init__(self):
        """Initialize a Geometry4"""
        self.attrib = Attributes()

    def scale(self,*args,**kargs):
        self.coords[..., :3] = Coords(self.coords[..., :3]).scale(*args,**kargs)
        return self


class KnotVector(object):

    """A knot vector

    A knot vector is sequence of float values sorted in ascending order.
    Values can occur multiple times. In they typical use case for this
    class (Nurbs) most values do indeed occur multiple times, and the
    multiplicity of the values is an important quantity.
    Therefore, the knot vector is stored in two arrays of the same length:

    - `v`: the unique float values, a strictly ascending sequence
    - `m`: the multiplicity of each of the values

    Example:

    >>> K = KnotVector([0.,0.,0.,0.5,0.5,1.,1.,1.])
    >>> print(K.val)
    [ 0.   0.5  1. ]
    >>> print(K.mul)
    [3 2 3]
    >>> print(K)
    KnotVector: 0.0(3), 0.5(2), 1.0(3)
    >>> print(K.knots())
    [(0.0, 3), (0.5, 2), (1.0, 3)]
    >>> print(K.values())
    [ 0.   0.   0.   0.5  0.5  1.   1.   1. ]
    >>> K.index(0.5)
    1
    >>> K.span(1.0)
    5
    >>> K.mult(0.5)
    2
    >>> K.mult(0.7)
    0
    >>> K[4],K[-1]
    (0.5, 1.0)
    >>> K[4:6]
    array([ 0.5,  1. ], dtype=float32)

    """

    def __init__(self,data=None,val=None,mul=None):
        """Initialize a KnotVector"""
        if data is not None:
            data = at.checkArray(data,(-1,),'f','i')
            val,inv = np.unique(data,return_inverse=True)
            mul,bins = at.multiplicity(inv)
        else:
            val = at.checkArray(val,(-1,),'f','i')
            mul = at.checkArray(mul,val.shape,'i')
        self.val = val
        self.mul = mul
        self.csum = self.mul.cumsum() - 1


    def nknots(self):
        """Return the total number of knots"""
        return self.mul.sum()


    def knots(self):
        """Return the knots as a list of tuples (value,multiplicity)"""
        return zip(self.val,self.mul)


    def values(self):
        """Return the full list of knot values"""
        return np.concatenate([ [v]*m for v,m in self.knots()])


    def __str__(self):
        """Format the knot vector as a string."""
        return "KnotVector: " + ", ".join(["%s(%s)" % (v,m) for v,m in self.knots()])


    def index(self,u):
        """Find the index of knot value u.

        If the value does not exist, a ValueError is raised.
        """
        w = np.where(np.isclose(self.val,u))[0]
        if len(w) <= 0:
            raise ValueError("The value %s does not appear in the KnotVector" % u)
        return w[0]


    def mult(self,u):
        """Return the multiplicity of knot value u.

        Returns an int with the multiplicity of the knot value u, or 0 if
        the value is not in the KNotVector.
        """
        try:
            i = self.index(u)
            return self.mul[i]
        except:
            return 0


    def span(self,u):
        """Find the (first) index of knot value u in the full knot values vector.

        If the value does not exist, a ValueError is raised.
        """
        i = self.index(u)
        return self.mul[:i].sum()

#    def value(self,i):
#        """Return knot i.
#
#        Returns the knot with the index i, taking into account
#        the multiplicity of the knots.
#        """
#        ind = self.csum.searchsorted(i)
#        return self.val[ind]
#

    def __getitem__(self,i):
        """Return knot i.

        Returns the knot with the index i, taking into account
        the multiplicity of the knots.
        """
        if isinstance(i,slice):
            i = np.arange(i.start,i.stop,i.step)
        i %= self.nknots()
        ind = self.csum.searchsorted(i)
        return self.val[ind]


    def copy(self):
        """Return a copy of the KnotVector.

        Changing the copy will not change the original.
        """
        return KnotVector(val=self.val,mul=self.mul)


    def reverse(self):
        """Return the reverse knot vector.

        Example:

        >>> print(KnotVector([0,0,0,1,3,6,6,8,8,8]).reverse().values())
        [ 0.  0.  0.  2.  2.  5.  7.  8.  8.  8.]

        """
        val = self.val.min() + self.val.max() - self.val
        return KnotVector(val=val[::-1],mul=self.mul[::-1])


def genKnotVector(nctrl,degree,blended=True,closed=False):
    """Compute sensible knot vector for a Nurbs curve.

    A knot vector is a sequence of non-decreasing parametric values. These
    values define the `knots`, i.e. the points where the analytical expression
    of the Nurbs curve may change. The knot values are only meaningful upon a
    multiplicative constant, and they are usually normalized to the range
    [0.0..1.0].

    A Nurbs curve with ``nctrl`` points and of given ``degree`` needs a knot
    vector with ``nknots = nctrl+degree+1`` values. A ``degree`` curve needs
    at least ``nctrl = degree+1`` control points, and thus at least
    ``nknots = 2*(degree+1)`` knot values.

    To make an open curve start and end in its end points, it needs knots with
    multiplicity ``degree+1`` at its ends. Thus, for an open blended curve, the
    default policy is to set the knot values at the ends to 0.0, resp. 1.0,
    both with multiplicity ``degree+1``, and to spread the remaining
    ``nctrl - degree - 1`` values equally over the interval.

    For a closed (blended) curve, the knots are equally spread over the
    interval, all having a multiplicity 1 for maximum continuity of the curve.

    For an open unblended curve, all internal knots get multiplicity ``degree``.
    This results in a curve that is only one time continuously derivable at
    the knots, thus the curve is smooth, but the curvature may be discontinuous.
    There is an extra requirement in this case: ``nctrl`` should be a multiple
    of ``degree`` plus 1.

    Returns a KnotVector instance.

    Example:

    >>> print(genKnotVector(7,3))
    KnotVector: 0.0(4), 0.25(1), 0.5(1), 0.75(1), 1.0(4)
    >>> print(genKnotVector(7,3,blended=False))
    KnotVector: 0.0(4), 1.0(3), 2.0(4)
    >>> print(genKnotVector(3,2,closed=True))
    KnotVector: 0.0(1), 0.2(1), 0.4(1), 0.6(1), 0.8(1), 1.0(1)
    """
    nknots = nctrl+degree+1
    if closed or blended:
        nval = nknots
        if not closed:
            nval -= 2*degree
        val = at.uniformParamValues(nval-1) # Returns nval values!
        mul = np.ones(nval,dtype=at.Int)
        if not closed:
            mul[0] = mul[-1] = degree+1
    else:
        nparts = (nctrl-1) // degree
        if nparts*degree+1 != nctrl:
            raise ValueError("Discrete knot vectors can only be used if the number of control points is a multiple of the degree, plus one.")
        val = np.arange(nparts+1).astype(at.Float)
        mul = np.ones(nparts+1,dtype=at.Int) * degree
        mul[0] = mul[-1] = degree+1

    return KnotVector(val=val,mul=mul)


class NurbsCurve(Geometry4):

    """A NURBS curve

    The Nurbs curve is defined by nctrl control points, a degree (>= 1) and
    a knot vector with nknots = nctrl+degree+1 parameter values.

    Parameters:

    - `control`: Coords-like (nctrl,3): the vertices of the control polygon.
    - `degree`: int: the degree of the Nurbs curve. If not specified, it is
      derived from the length of the knot vector (`knots`).
    - `wts`: float array (nctrl): weights to be attributed to the control
      points. Default is to attribute a weight 1.0 to all points. Using
      different weights allows for more versatile modeling (like perfect
      circles and arcs.)
    - `knots`: KnotVector or an ascending list of nknots float values.
      The values are only defined upon a multiplicative constant and will
      be normalized to set the last value to 1.
      If `degree` is specified, default values are constructed automatically
      by calling :func:`genKnotVector`.
      If no knots are given and no degree is specified, the degree is set to
      the nctrl-1 if the curve is blended. If not blended, the degree is not
      set larger than 3.
    - `closed`: bool: determines whether the curve is closed. Default
      False. The use of closed NurbsCurves is currently very limited.
    - `blended`: bool: determines that the curve is blended. Default is True.
      Set blended==False to define a nonblended curve.
      A nonblended curve is a chain of independent curves, Bezier curves if the
      weights are all ones. See also :meth:`decompose`.
      The number of control points should be a multiple of the degree, plus one.      This parameter is only used if no knots are specified.

    """

    N_approx = 100
#
#    order (2,3,4,...) = degree+1 = min. number of control points
#    ncontrol >= order
#    nknots = order + ncontrol >= 2*order
#
#    convenient solutions:
#    OPEN:
#      nparts = (ncontrol-1) // degree
#      nintern =
#
    def __init__(self,control,degree=None,wts=None,knots=None,closed=False,blended=True):
        Geometry4.__init__(self)
        self.closed = closed
        nctrl = len(control)
        if knots is not None:
            if not isinstance(knots,KnotVector):
                knots = KnotVector(knots)
            nknots = knots.nknots()

        if degree is None:
            if knots is None:
                degree = nctrl-1
                if not blended:
                    degree = min(degree, 3)
            else:
                degree = nknots - nctrl -1
                if degree <= 0:
                    raise ValueError("Length of knot vector (%s) must be at least number of control points (%s) plus 2" % (nknots, nctrl))

        order = degree+1
        control = Coords4(control)
        if wts is not None:
            control.deNormalize(wts.reshape(wts.shape[-1], 1))

        if closed:
            # We need to wrap nwrap control points
            if knots is None:
                nwrap = degree
            else:
                nwrap = nknots - nctrl - order
#            # We split them over the start and end
#            nextra1 = (nwrap+1) // 2
#            nextra2 = nwrap-nextra1
#            print("extra %s = %s + %s" % (nwrap, nextra1, nextra2))
#            control = Coords4(concatenate([control[-nextra1:], control, control[:nextra2]], axis=0))
            # !! Changed: wrap at the end
            control = Coords4(np.concatenate([control, control[:nwrap]], axis=0))

        nctrl = control.shape[0]

        if nctrl < order:
            raise ValueError("Number of control points (%s) must not be smaller than order (%s)" % (nctrl, order))

        if knots is None:
            knots = genKnotVector(nctrl, degree, blended=blended, closed=closed)
            nknots = knots.nknots()

        if nknots != nctrl+order:
            raise ValueError("Length of knot vector (%s) must be equal to number of control points (%s) plus order (%s)" % (nknots, nctrl, order))


        self.coords = control
        self.knotu = knots
        self.degree = degree
        self.closed = closed


    @property
    def knots(self):
        """Return the full list of knot values"""
        return self.knotu.values()

    # This is commented out because there is only 1 place where we set
    # the knots: __init__
#    @knots.setter
#    def knots(self,value):
#        """Set the knot values"""
#        self.knotu = KnotVector(knots)


    def nctrl(self):
        """Return the number of control points"""
        return self.coords.shape[0]

    def nknots(self):
        """Return the number of knots"""
        return self.knotu.nknots()

    def order(self):
        """Return the order of the Nurbs curve"""
        return self.nknots()-self.nctrl()

    def urange(self):
        """Return the parameter range on which the curve is defined.

        Returns a (2,) float array with the minimum and maximum parameter
        value for which the curve is defined.
        """
        p = self.degree
        return [self.knotu[p],self.knotu[-1-p]]


    def isClamped(self):
        """Return True if the NurbsCurve uses a clamped knot vector.

        A clamped knot vector has a multiplicity p+1 for the first and
        last knot. All our generated knot vectors are clamped.
        """
        return self.knotu.mul[0] == self.knotu.mul[-1] == (self.degree + 1)


    def isUniform(self):
        """Return True if the NurbsCurve has a uniform knot vector.

        A uniform knot vector has a constant spacing between the knot values.
        """
        d = self.knotu.val[1:] - self.knotu.val[:-1]
        return np.isclose(d[1:],d[0]).all()


    def isRational(self):
        """Return True if the NurbsCurve is rational.

        The curve is rational if the weights are not constant.
        The curve is polygonal if the weights are constant.

        Returns True for a rational curve, False for a polygonal curve.
        """
        w = self.coords[:,3]
        return not np.isclose(w[1:],w[0]).all()


    def isBlended(self):
        """Return True if the NurbsCurve is blended.

        An clamped NurbsCurve is unblended (or decomposed) if it consists
        of a chain of independent Bezier curves.
        Such a curve has multiplicity p for all internal knots and p+1
        for the end knots of an open curve.
        Any other NurbsCurve is blended.

        Returns True for a blended curve, False for an unblended one.

        Note: for testing whether an unclamped curve is blended or not,
        first clamp it.
        """
        return self.isClamped() and (self.knotu.mul[1:-1] == self.degree).all()


    def bbox(self):
        """Return the bounding box of the NURBS curve.

        """
        return self.coords.toCoords().bbox()


    def __str__(self):
        return """NURBS Curve, degree = %s, nctrl = %s, nknots = %s
  closed: %s; clamped: %s; uniform: %s; rational: %s
  Control points:
%s,
  %s
  urange = %s
"""  % ( self.degree, len(self.coords), self.nknots(), self.closed, self.isClamped(), self.isUniform(), self.isRational(), self.coords, self.knotu, self.urange())



    def copy(self):
        """Return a (deep) copy of self.

        Changing the copy will not change the original.
        """
        return NurbsCurve(control=self.coords.copy(),degree=self.degree,knots=self.knotu.copy(),closed=self.closed)


    def pointsAt(self, u):
        """Return the points on the Nurbs curve at given parametric values.

        Parameters:

        - `u`: (nu,) shaped float array, parametric values at which a point
          is to be placed. Note that valid points are only obtained for
          parameter values in the range self.range().

        Returns (nu,3) shaped Coords with nu points at the specified
        parametric values.

        """
        ctrl = self.coords.astype(np.double)
        knots = self.knotu.values().astype(np.double)
        u = np.atleast_1d(u).astype(np.double)

        try:
            pts = nurbs.curvePoints(ctrl, knots, u)
            if np.isnan(pts).any():
                print("We got a NaN")
                raise RuntimeError
        except:
            raise RuntimeError("Some error occurred during the evaluation of the Nurbs curve")

        if pts.shape[-1] == 4:
            pts = Coords4(pts).toCoords()
        else:
            pts = Coords(pts)
        return pts


    def derivs(self,u,d=1):
        """Returns the points and derivatives up to d at parameter values u

        Parameters:

        - `u`: either of:

          - int: number of points (npts) at which to evaluate the points
            and derivatives. The points will be equally spaced in parameter
            space.

          - float array (npts): parameter values at which to compute points
            and derivatives.

        - `d`: int: highest derivative to compute.

        Returns a float array of shape (d+1,npts,3).
        """
        if isinstance(u, int):
            u = at.uniformParamValues(u, self.knotu.val[0], self.knotu.val[-1])
        else:
            u = at.checkArray(u, (-1,), 'f', 'i')

        # sanitize arguments for library call
        ctrl = self.coords.astype(np.double)
        knots = self.knotu.values().astype(np.double)
        u = np.atleast_1d(u).astype(np.double)
        d = int(d)

        try:
            pts = nurbs.curveDerivs(ctrl, knots, u, d)
            if np.isnan(pts).any():
                print("We got a NaN")
                print(pts)
                raise RuntimeError
        except:
            raise RuntimeError("Some error occurred during the evaluation of the Nurbs curve")

        if pts.shape[-1] == 4:
            pts = Coords4(pts)
            # When using no weights, ctrl points are Coords4 normalized points,
            # and the derivatives all have w=0: the points represent directions
            # We just strip off the w=0.
            # HOWEVER, if there are weights, not sure what to do.
            # Points themselves could be just normalized and returned.
            pts[0].normalize()
            pts = Coords(pts[..., :3])
        else:
            pts = Coords(pts)
        return pts


    def frenet(self,u):
        """Compute Frenet vectors, curvature and torsion at parameter values u

        Parameters:

        - `u`: either of:

          - int: number of points (npts) at which to evaluate the points
            and derivatives. The points will be equally spaced in parameter
            space.

          - float array (npts): parameter values at which to compute points
            and derivatives.

        Returns a float array of shape (d+1,npts,3).

        Returns a tuple of arrays at nu parameter values u:

        - `T`: normalized tangent vector (nu,3)
        - `N`: normalized normal vector (nu,3)
        - `B`: normalized binormal vector (nu,3)
        - `k`: curvature of the curve (nu)
        - `t`: torsion of the curve (nu)

        """
        derivs = self.derivs(u,3)
        return frenet(derivs[1],derivs[2],derivs[3])


    def curvature(self,u,torsion=False):
        """Compute Frenet vectors, curvature and torsion at parameter values u

        Parameters:

        - `u`: either of:

          - int: number of points (npts) at which to evaluate the points
            and derivatives. The points will be equally spaced in parameter
            space.

          - float array (npts): parameter values at which to compute points
            and derivatives.

        - `torsion`: bool. If True, also returns the torsion in the curve.

        If `torsion` is False (default), returns a float array with the
        curvature at parameter values `u`.
        If `torsion` is True, also returns a float array with the
        torsion at parameter values `u`.

        """
        T,N,B,k,t = self.frenet(u)
        if torsion:
            return k,t
        else:
            return k


    def knotPoints(self,multiple=False):
        """Returns the points at the knot values.

        If multiple is True, points are returned with their multiplicity.
        The default is to return all points just once.
        """
        if multiple:
            val = self.knotu.knots
        else:
            val = self.knotu.val
        return self.pointsAt(val)


    def insertKnots(self, u):
        """Insert a set of knots in the Nurbs curve.

        u is a vector with knot parameter values to be inserted into the
        curve. The control points are adapted to keep the curve unchanged.

        Returns:

        A Nurbs curve equivalent with the original but with the
        specified knot values inserted in the knot vector, and the control
        points adapted.
        """
        if self.closed:
            raise ValueError("insertKnots currently does not work on closed curves")
        # sanitize arguments for library call
        ctrl = self.coords.astype(np.double)
        knots = self.knotu.values().astype(np.double)
        u = np.asarray(u).astype(np.double)
        newP, newU = nurbs.curveKnotRefine(ctrl, knots, u)
        return NurbsCurve(newP, degree=self.degree, knots=newU, closed=self.closed)


    def requireKnots(self, val, mul):
        """Insert knots until the required multiplicity reached.

        Inserts knot values only if they are currently not there or their
        multiplicity is lower than the required one.

        Parameters:

        - `val`: list of float (nval): knot values required in the knot vector.
        - `mul`: list of int (nval): multiplicities required for the knot values `u`.

        Returns:

        A Nurbs curve equivalent with the original but where the knot vector
        is guaranteed to contain the values in `u` with at least the
        corresponding multiplicity in `m`. If all requirements were already
        fulfilled at the beginning, returns self.

        """
        # get actual multiplicities
        m = np.array([ self.knotu.mult(ui) for ui in val ])
        # compute missing multiplicities
        mul = mul - m
        if (mul > 0).any():
            # list of knots to insert
            u = [ [ui]*mi for ui,mi in zip(val,mul) if mi > 0 ]
            return self.insertKnots(np.concatenate(u))
        else:
            return self


    def subCurve(self,u1,u2):
        """Extract the subcurve between parameter values u1 and u2

        Parameters:

        - `u1`, `u2`: two parameter values (u1 < u2), delimiting the part of the
          curve to extract. These values do not have to be knot values.

        Returns a NurbsCurve containing only the part between u1 and u2.
        """
        p = self.degree
        # Make sure we have the knots
        N = self.requireKnots([u1,u2],[p+1,p+1])
        j1 = N.knotu.index(u1)
        j2 = N.knotu.index(u2)
        knots = KnotVector(val=N.knotu.val[j1:j2+1],mul=N.knotu.mul[j1:j2+1])
        k1 = N.knotu.span(u1)
        nctrl = knots.nknots() - p - 1
        ctrl = N.coords[k1:k1+nctrl]
        return NurbsCurve(control=ctrl,degree=p,knots=knots,closed=self.closed)


    def clamp(self):
        """Clamp the knot vector of the curve.

        A clamped knot vector starts and ends with multiplicities p-1.
        See also :meth:`isClamped`.

        Returns self if the curve is already clamped, else returns an
        equivalent curve with clamped knot vector.

        Note: The use of unclamped knot vectors is deprecated.
        This method is provided only as a convenient method to import
        curves from legacy systems using unclamped knot vectors.

        """
        if self.isClamped():
            return self

        else:
            p = self.degree
            u1, u2 = self.knotu.val[[p,-1-p]]
            return self.subCurve(u1,u2)


    def unclamp(self):
        """Unclamp the knot vector of the curve.

        An unclamped knot vector starts and ends with multiplicities p-1.
        See also :meth:`isClamped`.

        Returns self if the curve is already clamped, else returns an
        equivalent curve with clamped knot vector.

        Note: The use of unclamped knot vectors is deprecated.
        This method is provided as a convenient method to export
        curves to legacy systems that only handle unclamped knot vectors.

        """
        if self.isClamped():
            from pyformex.lib.nurbs_e import curveUnclamp
            P,U = curveUnclamp(self.coords,self.knotu.values())
            return NurbsCurve(control=P,degree=self.degree,knots=U,closed=self.closed)

        else:
            return self


    def unblend(self):
        """Decomposes a curve in subsequent Bezier curves.

        Returns an equivalent unblended Nurbs.

        See also :meth:`toBezier`
        """
        # sanitize arguments for library call
        ctrl = self.coords
        knots = self.knotu.values().astype(np.double)
        X = nurbs.curveDecompose(ctrl, knots)
        return NurbsCurve(X, degree=self.degree, blended=False)


    # For compatibility
    decompose = unblend


    def toCurve(self,force_Bezier=False):
        """Convert a (nonrational) NurbsCurve to a BezierSpline or PolyLine.

        This decomposes the curve in a chain of Bezier curves and converts
        the chain to a BezierSpline or PolyLine.

        This only works for nonrational NurbsCurves, as the
        BezierSpline and PolyLine classes do not allow homogeneous
        coordinates required for rational curves.

        Returns a BezierSpline or PolyLine (if degree is 1) that is equivalent
        with the NurbsCurve.

        See also :meth:`unblend` which decomposes both rational and
        nonrational NurbsCurves.

        """
        if self.isRational():
            raise ValueError("Can not convert a rational NURBS ro Bezier")

        ctrl = self.coords
        knots = self.knotu.values()
        X = nurbs.curveDecompose(ctrl, knots)
        X = Coords4(X).toCoords()
        if self.degree > 1 or force_Bezier:
            return curve.BezierSpline(control=X,degree=self.degree,closed=self.closed)
        else:
            return curve.PolyLine(X,closed=self.closed)


    def toBezier(self):
        """Convert a (nonrational) NurbsCurve to a BezierSpline.

        This is equivalent with toCurve(force_Bezier=True) and returns
        a BezierSpline in all cases.
        """
        return self.toCurve(force_Bezier=True)


    def removeKnot(self, u, m, tol=1.e-5):
        """Remove a knot from the knot vector of the Nurbs curve.

        u: knot value to remove
        m: how many times to remove (if negative, remove maximally)

        Returns:

        A Nurbs curve equivalent with the original but with a knot vector
        where the specified value has been removed m times, if possible,
        or else as many times as possible. The control points are adapted
        accordingly.

        """
        if self.closed:
            raise ValueError("removeKnots currently does not work on closed curves")

        i = self.knotu.index(u)

        if m < 0:
            m = self.knotu.mul[i]

        P = self.coords.astype(np.double)
        Uv = self.knotu.val.astype(np.double)
        Um = self.knotu.mul.astype(at.Int)
        t,newP,newU = nurbs.curveKnotRemove(P,Uv,Um,i,m,tol)

        if t > 0:
            print("Removed the knot value %s %s times" % (u,t))
            return NurbsCurve(newP, degree=self.degree, knots=newU, closed=self.closed)
        else:
            print("Can not remove the knot value %s" % u)
            return self


    def removeAllKnots(self,tol=1.e-5):
        """Remove all removable knots

        Parameters:

        - `tol`: float: acceptable error (distance between old and new curve).

        Returns an equivalent (if tol is small) NurbsCurve with all
        extraneous knots removed.

        """
        N = self
        print(N)
        while True:
            print(N)
            for u in N.knotu.val:
                print("Removing %s" % u)
                NN = N.removeKnot(u,m=-1,tol=tol)
                if NN is N:
                    print("Can not remove")
                    continue
                else:
                    break
            if NN is N:
                print("Done")
                break
            else:
                print("Cycle")
                N = NN
        return N


    blend = removeAllKnots


    def elevateDegree(self, t=1):
        """Elevate the degree of the Nurbs curve.

        t: how much to elevate the degree

        Returns:

        A Nurbs curve equivalent with the original but of a higher degree.

        """
        if self.closed:
            raise ValueError("elevateDegree currently does not work on closed curves")

        P = self.coords.astype(np.double)
        U = self.knotu.values()

        newP,newU,nh,mh = nurbs.curveDegreeElevate(P, U, t)

        return NurbsCurve(newP, degree=self.degree+t, knots=newU, closed=self.closed)


    def reduceDegree(self, t=1):
        """Reduce the degree of the Nurbs curve.

        t: how much to reduce the degree (max. = degree-1)

        Returns:

        A Nurbs curve approximating the original but of a lower degree.

        """
        from pyformex.lib.nurbs_e import curveDegreeReduce
#        from nurbs import curveDegreeReduce
        if self.closed:
            raise ValueError("reduceDegree currently does not work on closed curves")

        if t >= self.degree:
            raise ValueError("Can maximally reduce degree %s times" % self.degree-1)

        N = self
        while t > 0:
            newP,newU,nh,mh,maxerr = curveDegreeReduce(N.coords, N.knots)
            #newP,newU,nh,mh = nurbs.curveDegreeReduce(N.coords, N.knots)
            N = NurbsCurve(newP, degree=self.degree-1, knots=newU, closed=self.closed)
            print("Reduced to degree %s with maxerr = %s" % (N.degree,maxerr))
            t -= 1

        return N


    # TODO: This might be implemented in C for efficiency
    def projectPoint(self, P, eps1=1.e-5, eps2=1.e-5, maxit=20, nseed=20):
        """Project a given point on the Nurbs curve.

        This can also be used to determine the parameter value of a point
        lying on the curve.

        Parameters:

        - `P`: Coords-like (npts,3): one or more points is space.

        Returns a tuple (u,X):

        - `u`: float: parameter value of the base point X of the projection
          of P on the NurbsCurve.
        - `X`: Coords (3,): the base point of the projection of P
          on the NurbsCurve.

        The algorithm is based on the from The Nurbs Book.

        """
        P = at.checkArray(P,(3,),'f','i')

        # Determine start value from best match of nseed+1 points
        umin,umax = self.knotu.val[[0,-1]]
        u = at.uniformParamValues(nseed+1,umin,umax)
        pts = self.pointsAt(u)
        i = pts.distanceFromPoint(P).argmin()
        u0,P0 = u[i],pts[i]
        #print("Start at point %s : %s" % (u0,P0))

        # Apply Newton's method to minimize distance
        i = 0
        ui = u0
        while i < maxit:
            i += 1
            C = self.derivs([ui],2)
            C0,C1,C2 = C[:,0]
            CP = (C0-P)
            CPxCP = np.dot(CP,CP)
            C1xCP = np.dot(C1,CP)
            C1xC1 = np.dot(C1,C1)
            eps1sq = eps1*eps1
            eps2sq = eps2*eps2
            # Check convergence
            chk1 = CPxCP <= eps1sq
            chk2 = C1xCP / C1xC1 / CPxCP <= eps2sq

            uj = ui - np.dot(C1,CP) / ( np.dot(C2,CP) + np.dot(C1,C1) )
            # ensure that parameter stays in range
            if self.closed:
                while uj < umin:
                    uj += umax - umin
                while uj > umax:
                    uj -= umax - umin
            else:
                if uj < umin:
                    uj = umin
                if uj > umax:
                    uj = umax

            # Check convergence
            chk4 = (uj-ui)**2 * C1xC1 <= eps1sq
            P0 = self.pointsAt([uj])[0]
            #print("u[%s] = %s (P=%s) conv=%s" % (i,uj,P0,(chk1,chk2,chk4)))

            if (chk1 or chk2) and chk4:
                # Converged!
                break
            else:
                # Prepare for next it
                ui = uj

        if i == maxit:
            print("Convergence not reached after %s iterations" % maxit)

        return u0,P0


    def approx(self,ndiv=None,nseg=None,**kargs):
        """Return a PolyLine approximation of the Nurbs curve

        If no `nseg` is given, the curve is approximated by a PolyLine
        through equidistant `ndiv+1` point in parameter space. These points
        may be far from equidistant in Cartesian space.

        If `nseg` is given, a second approximation is computed with `nseg`
        straight segments of nearly equal length. The lengths are computed
        based on the first approximation with `ndiv` segments.
        """
        from pyformex.plugins.curve import PolyLine
        if ndiv is None:
            ndiv = self.N_approx
        umin,umax = self.urange()
        u = at.uniformParamValues(ndiv,umin,umax)
        PL = PolyLine(self.pointsAt(u))
        if nseg is not None:
            u = PL.atLength(nseg)
            PL = PolyLine(PL.pointsAt(u))
        return PL


    def actor(self,**kargs):
        """Graphical representation"""
        from pyformex.opengl.actors import Actor
        G = self.approx(ndiv=100).toFormex()
        G.attrib(**self.attrib)
        return Actor(G,**kargs)


    def reverse(self):
        """Return the reversed Nurbs curve.

        The reversed curve is geometrically identical, but start and en point
        are interchanged and parameter values increase in the opposite direction.
        """
        return NurbsCurve(control=self.coords[::-1], knots=self.knotu.reverse(), degree=self.degree, closed=self.closed)




#######################################################
## NURBS Surface ##


class NurbsSurface(Geometry4):

    """A NURBS surface

    The Nurbs surface is defined as a tensor product of NURBS curves in two
    parametrical directions u and v. The control points form a grid of
    (nctrlu,nctrlv) points. The other data are like those for a NURBS curve,
    but need to be specified as a tuple for the (u,v) directions.

    The knot values are only defined upon a multiplicative constant, equal to
    the largest value. Sensible default values are constructed automatically
    by a call to the :func:`genKnotVector` function.

    If no knots are given and no degree is specified, the degree is set to
    the number of control points - 1 if the curve is blended. If not blended,
    the degree is not set larger than 3.

    .. warning:: This is a class under development!

    """

    def __init__(self,control,degree=(None, None),wts=None,knots=(None, None),closed=(False, False),blended=(True, True)):
        """Initialize the NurbsSurface.

        """

        Geometry4.__init__(self)
        self.closed = closed

        control = Coords4(control)
        if wts is not None:
            control.deNormalize(wts.reshape(wts.shape[-1], 1))

        for d in range(2):
            nctrl = control.shape[1-d] # BEWARE! the order of the nodes
            deg = degree[d]
            kn = knots[d]
            bl = blended[d]
            cl = closed[d]

            if deg is None:
                if kn is None:
                    deg = nctrl-1
                    if not bl:
                        deg = min(deg, 3)
                else:
                    deg = len(kn) - nctrl -1
                    if deg <= 0:
                        raise ValueError("Length of knot vector (%s) must be at least number of control points (%s) plus 2" % (len(knots), nctrl))
                # make degree changeable
                degree = list(degree)
                degree[d] = deg

            order = deg+1

            if nctrl < order:
                raise ValueError("Number of control points (%s) must not be smaller than order (%s)" % (nctrl, order))

            if kn is None:
                kn = genKnotVector(nctrl, deg, blended=bl, closed=cl).values()
            else:
                kn = np.asarray(kn).ravel()

            nknots = kn.shape[0]

            if nknots != nctrl+order:
                raise ValueError("Length of knot vector (%s) must be equal to number of control points (%s) plus order (%s)" % (nknots, nctrl, order))

            if d == 0:
                self.knotu = kn
            else:
                self.knotv = kn

        self.coords = control
        self.degree = degree
        self.closed = closed


    def order(self):
        return (self.knotu.shape[0]-self.coords.shape[1],
                self.knotv.shape[0]-self.coords.shape[0])


    def urange(self):
        """Return the u-parameter range on which the curve is defined.

        Returns a (2,) float array with the minimum and maximum parameter
        value u for which the curve is defined.
        """
        p = self.degree[0]
        return [self.knotu[p],self.knotu[-1-p]]


    def vrange(self):
        """Return the v-parameter range on which the curve is defined.

        Returns a (2,) float array with the minimum and maximum parameter
        value v for which the curve is defined.
        """
        p = self.degree[1]
        return [self.knotv[p],self.knotv[-1-p]]


    def bbox(self):
        """Return the bounding box of the NURBS surface.

        """
        return self.coords.toCoords().bbox()


    def pointsAt(self, u):
        """Return the points on the Nurbs surface at given parametric values.

        Parameters:

        - `u`: (nu,2) shaped float array: `nu` parametric values (u,v) at which
          a point is to be placed.

        Returns (nu,3) shaped Coords with `nu` points at the specified
        parametric values.

        """
        ctrl = self.coords.astype(np.double)
        U = self.knotv.astype(np.double)
        V = self.knotu.astype(np.double)
        u = np.asarray(u).astype(np.double)

        try:
            pts = nurbs.surfacePoints(ctrl, U, V, u)
            if np.isnan(pts).any():
                print("We got a NaN")
                raise RuntimeError
        except:
            raise RuntimeError("Some error occurred during the evaluation of the Nurbs surface.\nPerhaps you are not using the compiled library?")

        if pts.shape[-1] == 4:
            pts = Coords4(pts).toCoords()
        else:
            pts = Coords(pts)
        return pts


    def derivs(self, u, m):
        """Return points and derivatives at given parametric values.

        Parameters:

        - `u`: (nu,2) shaped float array: `nu` parametric values (u,v) at which
          the points and derivatives are evaluated.
        - `m`: tuple of two int values (mu,mv). The points and derivatives up
          to order mu in u direction and mv in v direction are returned.

        Returns:

        (nu+1,nv+1,nu,3) shaped Coords with `nu` points at the
        specified parametric values. The slice (0,0,:,:) contains the
        points.

        """
        # sanitize arguments for library call
        ctrl = self.coords.astype(np.double)
        U = self.knotv.astype(np.double)
        V = self.knotu.astype(np.double)
        u = np.asarray(u).astype(np.double)
        mu, mv = m
        mu = int(mu)
        mv = int(mv)

        try:
            pts = nurbs.surfaceDerivs(ctrl, U, V, u, mu, mv)
            if np.isnan(pts).any():
                print("We got a NaN")
                raise RuntimeError
        except:
            raise RuntimeError("Some error occurred during the evaluation of the Nurbs surface")

        if pts.shape[-1] == 4:
            pts = Coords4(pts)
            pts[0][0].normalize()
            pts = Coords(pts[..., :3])
        else:
            pts = Coords(pts)
        return pts


    def approx(self,ndiv=None,**kargs):
        """Return a Quad4 Mesh approximation of the Nurbs surface

        Parameters:

        - `ndiv`: number of divisions of the parametric space
        If no `nseg` is given, the curve is approximated by a PolyLine
        through equidistant `ndiv+1` point in parameter space. These points
        may be far from equidistant in Cartesian space.

        If `nseg` is given, a second approximation is computed with `nseg`
        straight segments of nearly equal length. The lengths are computed
        based on the first approximation with `ndiv` segments.
        """
        from pyformex.mesh import Mesh, quad4_els
        if ndiv is None:
            ndiv = self.N_approx
        if at.isInt(ndiv):
            ndiv = (ndiv,ndiv)
        udiv,vdiv = ndiv
        umin,umax = self.urange()
        vmin,vmax = self.vrange()
        u = at.uniformParamValues(udiv,umin,umax)
        v = at.uniformParamValues(udiv,umin,umax)
        uv = np.ones((udiv+1,vdiv+1,2))
        uv[:,:,0] *= u
        uv[:,:,1] *= v.reshape(-1,1)
        coords = self.pointsAt(uv.reshape(-1,2))
        elems = quad4_els(udiv,vdiv)
        return Mesh(coords,elems,eltype='quad4')


    def actor(self,**kargs):
        """Graphical representation"""
        from pyformex.opengl.actors import Actor
        G = self.approx(ndiv=100)
        G.attrib(**self.attrib)
        return Actor(G,**kargs)


################################################################


def globalInterpolationCurve(Q,degree=3,strategy=0.5):
    """Create a global interpolation NurbsCurve.

    Given an ordered set of points Q, the globalInterpolationCurve
    is a NURBS curve of the given degree, passing through all the
    points.

    Returns:

    A NurbsCurve through the given point set. The number of
    control points is the same as the number of input points.

    .. warning:: Currently there is the limitation that two consecutive
      points should not coincide. If they do, a warning is shown and
      the double points will be removed.

    The procedure works by computing the control points that will
    produce a NurbsCurve with the given points occurring at predefined
    parameter values. The strategy to set this values uses a parameter
    as exponent. Different values produce (slighly) different curves.
    Typical values are:

    0.0: equally spaced (not recommended)
    0.5: centripetal (default, recommended)
    1.0: chord length (often used)
    """
    from pyformex.plugins.curve import PolyLine
    # set the knot values at the points
    #nc = Q.shape[0]
    #n = nc-1

    # chord length
    d = PolyLine(Q).lengths()
    if (d==0.0).any():
        utils.warn("warn_nurbs_gic")
        Q = np.concatenate([Q[d!=0.0], Q[-1:]], axis=0)
        d = PolyLine(Q).lengths()
        if (d==0.0).any():
            raise ValueError("Double points in the data set are not allowed")
    # apply strategy
    d = d ** strategy
    d = d.cumsum()
    d /= d[-1]
    u = np.concatenate([[0.], d])
    #print "u = ",u
    U, A = nurbs.curveGlobalInterpolationMatrix(Q, u, degree)
    #print "U = ",U
    #print "A = ",A
    P = np.linalg.solve(A, Q)
    #print "P = ",P
    return NurbsCurve(P, knots=U, degree=degree)


def NurbsCircle(O=[0.,0.,0.],r=1.0,X=[1.,0.,0.],Y=[0.,1.,0.],ths=0.,the=360.):
    """Create a NurbsCurve representing a perfect circle or arc.

    Parameters:

    - `O`: float (3,): center of the circle
    - `r`: float: radius
    - `X`: unit vector in the plane of the circle
    - 'Y': unit vector in the plane of the circle and perpendicular to `X`
    - `ths`: start angle, measured from the X axis, coungerclockwise in X-Y plane
    - `the`: end angle, measured from the X axis

    Returns a NurbsCurve that is a perfect circle or arc.
    """
    if the < ths:
        the += 360.
    theta = (the-ths)
    # Get the number of arcs
    narcs = int(np.ceil(theta/90.))
    n = 2*narcs   # n+1 control points
    O,X,Y = ( at.checkArray(x,(3,),'f','i') for x in (O,X,Y) )
    dths = ths*at.DEG
    dtheta = theta*at.DEG/narcs
    w1 = np.cos(dtheta/2.) # base angle
    # Initialize start values
    P0 = O + r*np.cos(dths)*X + r*np.sin(dths)*Y
    T0 = -np.sin(ths)*X + np.cos(ths)*Y
    Pw = np.zeros((n+1,4),dtype=at.Float)
    Pw[0] = Coords4(P0)
    index = 0
    angle = ths*at.DEG
    # create narcs segments
    for i in range(1,narcs+1):
        angle += dtheta
        P2 = O + r*np.cos(angle)*X + r*np.sin(angle)*Y
        Pw[index+2] = Coords4(P2)
        T2 = -np.sin(angle)*X + np.cos(angle)*Y
        P1,P1b = gt.intersectLineWithLine(P0,T0,P2,T2)
        Pw[index+1] = Coords4(P1) * w1
        Pw[index+1,3] = w1
        index += 2
        if i < narcs:
            P0,T0 = P2,T2
    # Load the knot vector
    j= 2*narcs+1
    U = np.zeros((j+3,),dtype=at.Float)
    for i in range(3):
        U[i] = 0.
        U[i+j] = 1.
    if narcs == 2:
        U[3] = U[4] = 0.5
    elif narcs == 3:
        U[3] = U[4] = 1./3.
        U[5] = U[6] = 2./3.
    elif narcs == 4:
        U[3] = U[4] = 0.25
        U[5] = U[6] = 0.5
        U[7] = U[8] = 0.75

    return NurbsCurve(control=Pw,degree=2,knots=U)


def toCoords4(x):
    """Convert cartesian coordinates to homogeneous

    `x`: :class:`Coords`
      Array with cartesian coordinates.

    Returns a Coords4 object corresponding to the input cartesian coordinates.
    """
    return Coords4(x)

Coords.toCoords4 = toCoords4


def pointsOnBezierCurve(P, u):
    """Compute points on a Bezier curve

    Parameters:

    P is an array with n+1 points defining a Bezier curve of degree n.
    u is a vector with nu parameter values between 0 and 1.

    Returns:

    An array with the nu points of the Bezier curve corresponding with the
    specified parametric values.
    ERROR: currently u is a single paramtric value!

    See also:
    examples BezierCurve, Casteljau
    """
    u = np.asarray(u).ravel()
    n = P.shape[0]-1
    return Coords.concatenate([
        (nurbs.allBernstein(n, ui).reshape(1, -1, 1) * P).sum(axis=1)
        for ui in u ], axis=0)


def deCasteljau(P, u):
    """Compute points on a Bezier curve using deCasteljau algorithm

    Parameters:

    P is an array with n+1 points defining a Bezier curve of degree n.
    u is a single parameter value between 0 and 1.

    Returns:

    A list with point sets obtained in the subsequent deCasteljau
    approximations. The first one is the set of control points, the last one
    is the point on the Bezier curve.

    This function works with Coords as well as Coords4 points.
    """
    n = P.shape[0]-1
    C = [P]
    for k in range(n):
        Q = C[-1]
        Q = (1.-u) * Q[:-1] + u * Q[1:]
        C.append(Q)
    return C


def splitBezierCurve(P, u):
    """Split a Bezier curve at parametric values

    Parameters:

    P is an array with n+1 points defining a Bezier curve of degree n.
    u is a single parameter value between 0 and 1.

    Returns two arrays of n+1 points, defining the Bezier curves of degree n
    obtained by splitting the input curve at parametric value u. These results
    can be used with the control argument of BezierSpline to create the
    corresponding curve.

    """
    C = deCasteljau(P, u)
    L = np.stack([x[0] for x in C])
    R = np.stack([x[-1] for x in C[::-1]])
    return L,R


def frenet(d1,d2,d3=None):
    """Compute Frenet vectors, curvature and torsion.

    Parameters:

    - `d1`: first derivative at `npts` points of a nurbs curve
    - `d2`: second derivative at `npts` points of a nurbs curve
    - `d3`: (optional) third derivative at `npts` points of a nurbs curve

    The derivatives of the nurbs curve are normally obtained from
    :func:`NurbsCurve.deriv`.

    Returns:

    - `T`: normalized tangent vector to the curve at `npts` points
    - `N`: normalized normal vector to the curve at `npts` points
    - `B`: normalized binormal vector to the curve at `npts` points
    - `k`: curvature of the curve at `npts` points
    - `t`: (only if `d3` was specified) torsion of the curve at `npts` points

    Curvature is found from  `| d1 x d2 | / |d1|**3`

    """
    l = at.length(d1)
    # What to do when l is 0? same as with k?
    if l.min() == 0.0:
        print("l is zero at %s" % np.where(l==0.0)[0])
    e1 = d1 / l.reshape(-1, 1)
    e2 = d2 - at.dotpr(d2, e1).reshape(-1, 1)*e1
    k = at.length(e2)
    if k.min() == 0.0:
        w = np.where(k==0.0)[0]
        print("k is zero at %s" % w)
    # where k = 0: set e2 to mean of previous and following
    e2 /= k.reshape(-1, 1)
    #e3 = normalize(ddd - dotpr(ddd,e1)*e1 - dotpr(ddd,e2)*e2)
    e3 = np.cross(e1, e2)
    #m = at.dotpr(np.cross(d1, d2), e3)
    #print "m",m
    m = np.cross(d1,d2)
    k = at.length(m) / l**3
    if d3 is None:
        return e1, e2, e3, k
    # compute torsion
    t = at.dotpr(d1, np.cross(d2, d3)) / at.dotpr(d1, d2)
    return e1, e2, e3, k, t


### End
