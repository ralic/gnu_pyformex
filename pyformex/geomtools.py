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
"""Basic geometrical operations.

This module defines some basic operations on simple geometrical entities
such as points, lines, planes, vectors, segments, triangles, circles.

The operations include intersection, projection, distance computing.

Many of the functions in this module are exported as methods on the
Coords and Geometry classes and subclasses.


Renamed functions::

    intersectionPointsLWL    -> intersectLineWithLine
    intersectionTimesLWL     -> intersectLineWithLine
    intersectionPointsLWP    -> intersectLineWithPlane
    intersectionTimesLWP     -> intersectLineWithPlane


Planned renaming of functions::

    areaNormals
    degenerate
    levelVolumes
    smallestDirection
    distance                 -> distance
    closest
    closestPair
    projectedArea
    polygonNormals
    averageNormals
    triangleInCircle
    triangleCircumCircle
    triangleBoundingCircle
    triangleObtuse
    lineIntersection         -> to be removed (or intersect2DLineWithLine)
    displaceLines
    segmentOrientation
    rotationAngle
    anyPerpendicularVector
    perpendicularVector
    projectionVOV            -> projectVectorOnVector
    projectionVOP            -> projectVectorOnPlane


    pointsAtLines            -> pointOnLine
    pointsAtSegments         -> pointOnSegment
    intersectionTimesSWP     -> remove or intersectLineWithLineTimes2
    intersectionSWP          -> intersectSegmentWithPlaneTimes
    intersectionPointsSWP    -> intersectSegmentWithPlane
    intersectionTimesLWT     -> intersectLineWithTriangleTimes
    intersectionPointsLWT    -> intersectLineWithTriangle
    intersectionTimesSWT     -> intersectSegmentWithTriangleTimes
    intersectionPointsSWT    -> intersectSegmentWithTriangle
    intersectionPointsPWP    -> intersectThreePlanes
    intersectionLinesPWP     -> intersectTwoPlanes (or intersectPlaneWithPlane)
    intersectionSphereSphere -> intersectTwoSpheres (or intersectSphereWithSphere)

    faceDistance             ->
    edgeDistance             ->
    vertexDistance           ->
    baryCoords
    insideSimplex
    insideTriangle

"""
from __future__ import absolute_import, division, print_function


from pyformex import utils
from pyformex import multi
from pyformex.formex import *


#
#  TODO : these functions need doctests!
#

class Line(object):
    def __init__(self, P, n=None):
        if n is None:
            if isinstance(P,Line):
                self.data = P.data
                return
            elif not isinstance(P,tuple):
                P = checkArray(P,shape=(-1,2,3))
                P[:,1,:] -= P[:,0,:]
                self.data = P
                return
            elif isinstance(P,tuple):
                P, n = P
        P = checkArray(P,shape=(-1,3))
        n = checkArray(n,shape=(P.shape[0],3))
        self.data = stack([P,n],axis=1)


    @property
    def p(self):
        return self.data[:,0,:]

    @property
    def n(self):
        return self.data[:,1,:]

    def toFormex(self):
        P = self.data.copy()
        P[:,1,:] += P[:,0,:]
        return Formex(P)


class Plane(object):
    def __init__(self, P, n):
        self.coords = Coords.concatenate([P, normalize(n)])


def pointsAtLines(q, m, t):
    """Return the points of lines (q,m) at parameter values t.

    Parameters:

    - `q`,`m`: (...,3) shaped arrays of points and vectors, defining
      a single line or a set of lines. The vectors do not need to
      have unit length.
    - `t`: array of parameter values, broadcast compatible with `q` and `m`.
      Parametric value 0 is at point q, parametric value 1 ia at q+m.

    Returns a Coords array with the points at parameter values t.
    """
    t = t[..., newaxis]
    return Coords(q+t*m)


def pointsAtSegments(S, t):
    """Return the points of line segments S at parameter values t.

    Parameters:

    - `S`: (...,2,3) shaped array, defining a single line segment or
      a set of line segments.
    - `t`: array of parameter values, broadcast compatible with `S`.

    Returns an array with the points at parameter values t.
    """
    q0 = S[..., 0,:]
    q1 = S[..., 1,:]
    return pointsAtLines(q0, q1-q0, t)



################## intersection #######################
#


def intersectLineWithLine(q1,m1,q2,m2,mode='all',times=False):
    """Find the common perpendicular of lines (q1,m1) and lines (q2,m2)

    Return the intersection points of lines (q1,m1) and lines (q2,m2)
    with the perpendiculars between them. For intersecting lines, the
    corresponding points will coincide.

    Parameters:

    - `qi`,`mi` (i=1,2): (nqi,3) shaped arrays of points and vectors defining
      nqi lines.
    - `mode`: 'all' or 'pair:

      - if 'all', the interesection of all lines q1,m1 with all lines q2,m2
        is computed; `nq1` and `nq2` can be different.
      - if 'pair': `nq1` and `nq2` should be equal (or 1) and the intersection
        of pairs of lines are computed (using broadcasting for
        length 1 data).
    - `times`: bool: if True, returns the parameter values of the
      intersection points instead of the intersection points themselves.

    Returns two Coords arrays with the intersection points on lines (q1,m1)
    and (q2,m2) respectively (or, if `times` is True, two float arrays
    with the parameter values of these points).
    The size of the Coords arrays is (nq1,nq2,3) for mode 'all' and (nq1,3)
    for mode 'pair'. With `times` True, the size of the returned parameter
    arrays is (nq1,nq2,3) for mode 'all' and size (nq1,3) for mode 'pair'.

    Note: taking the intersection of two parallel lines will result in
    nan values. These are not removed from the result. The user can do
    it if he so wishes.

    Example:

    >>> q,m = [[0,0,0],[0,0,1],[0,0,3]], [[1,0,0],[1,1,0],[0,1,0]]
    >>> p,n = [[2.,0.,0.],[0.,0.,0.]], [[0.,1.,0.],[0.,0.,1.]]

    >>> x1,x2 = intersectLineWithLine(q,m,p,n)
    >>> print(x1)
    [[[  2.   0.   0.]
      [  0.   0.   0.]]
    <BLANKLINE>
     [[  2.   2.   1.]
      [  0.   0.   1.]]
    <BLANKLINE>
     [[ nan  nan  nan]
      [  0.   0.   3.]]]
    >>> print(x2)
    [[[  2.   0.   0.]
      [  0.   0.   0.]]
    <BLANKLINE>
     [[  2.   2.   0.]
      [  0.   0.   1.]]
    <BLANKLINE>
     [[ nan  nan  nan]
      [  0.   0.   3.]]]

    >>> x1,x2 = intersectLineWithLine(q[:2],m[:2],p,n,mode='pair')
    >>> print(x1)
    [[ 2.  0.  0.]
     [ 0.  0.  1.]]
    >>> print(x2)
    [[ 2.  0.  0.]
     [ 0.  0.  1.]]

    >>> t1,t2 = intersectLineWithLine(q,m,p,n,times=True)
    >>> print(t1)
    [[  2.  -0.]
     [  2.  -0.]
     [ nan  -0.]]
    >>> print(t2)
    [[ -0.  -0.]
     [  2.   1.]
     [ nan   3.]]

    >>> t1,t2 = intersectLineWithLine(q[:2],m[:2],p,n,mode='pair',times=True)
    >>> print(t1)
    [ 2. -0.]
    >>> print(t2)
    [-0.  1.]

    """
    if mode == 'all':
        q1 = asarray(q1).reshape(-1, 1, 3)
        m1 = asarray(m1).reshape(-1, 1, 3)
        q2 = asarray(q2).reshape(1, -1, 3)
        m2 = asarray(m2).reshape(1, -1, 3)
    else:
        q1 = asarray(q1).reshape(-1, 3)
        m1 = asarray(m1).reshape(-1, 3)
        q2 = asarray(q2).reshape(-1, 3)
        m2 = asarray(m2).reshape(-1, 3)

    dot11 = dotpr(m1, m1)
    dot22 = dotpr(m2, m2)
    dot12 = dotpr(m1, m2)
    denom = (dot12**2-dot11*dot22)
    q12 = q2-q1
    dot11 = dot11[..., newaxis]
    dot22 = dot22[..., newaxis]
    dot12 = dot12[..., newaxis]
    errh = seterr(divide='ignore', invalid='ignore')
    t1 = dotpr(q12, m2*dot12-m1*dot22) / denom
    t2 = dotpr(q12, m2*dot11-m1*dot12) / denom
    seterr(**errh)
    if times:
        return t1, t2
    else:
        return pointsAtLines(q1, m1, t1), pointsAtLines(q2, m2, t2)


def intersectLineWithPlane(q,m,p,n,mode='all',times=False):
    """Find the intersection of lines (q,m) and planes (p,n)

    Return the intersection points of lines (q,m) and planes (p,n).

    Parameters:

    - `q`,`m`: (nq,3) shaped arrays of points and vectors (`mode=all`)
      or broadcast compatible arrays (`mode=pair`), defining a single line
      or a set of lines.
    - `p`,`n`: (np,3) shaped arrays of points and normals (`mode=all`)
      or broadcast compatible arrays (`mode=pair`), defining a single plane
      or a set of planes.
    - `mode`: `all` to calculate the intersection of each line (q,m) with
      all planes (p,n) or `pair` for pairwise intersections.

    Returns a (nq,np) shaped (`mode=all`) array of parameter values t,
    such that the intersection points are given by q+t*m.

    Notice that the result will contain an INF value for lines that are
    parallel to the plane.

    Example:

    >>> q,m = [[0,0,0],[0,1,0],[0,0,3]], [[1,0,0],[0,1,0],[0,0,1]]
    >>> p,n = [[1.,1.,1.],[1.,1.,1.]], [[1.,1.,0.],[1.,1.,1.]]

    >>> t = intersectLineWithPlane(q,m,p,n,times=True)
    >>> print(t)
    [[  2.   3.]
     [  1.   2.]
     [ inf   0.]]
    >>> x = intersectLineWithPlane(q,m,p,n)
    >>> print(x)
    [[[  2.   0.   0.]
      [  3.   0.   0.]]
    <BLANKLINE>
     [[  0.   2.   0.]
      [  0.   3.   0.]]
    <BLANKLINE>
     [[ nan  nan  inf]
      [  0.   0.   3.]]]
    >>> x = intersectLineWithPlane(q[:2],m[:2],p,n,mode='pair')
    >>> print(x)
    [[ 2.  0.  0.]
     [ 0.  3.  0.]]
    """
    q = checkArray(q,(-1,3),'f','i')
    m = checkArray(m,(-1,3),'f','i')
    p = checkArray(p,(-1,3),'f','i')
    n = checkArray(n,(-1,3),'f','i')

    errh = seterr(divide='ignore', invalid='ignore')
    if mode == 'all':
        t = (dotpr(p, n) - inner(q, n)) / inner(m, n)
    elif mode == 'pair':
        t = dotpr(n, p-q) / dotpr(m, n)
    seterr(**errh)

    if times:
        return t
    else:
        if mode == 'all':
            q = q[:, newaxis]
            m = m[:, newaxis]
        return pointsAtLines(q, m, t)


def intersectionTimesLWP(q,m,p,n,mode='all'):
    return intersectLineWithPlane(q,m,p,n,mode,times=True)


def intersectionPointsLWP(q,m,p,n,mode='all'):
    return intersectLineWithPlane(q,m,p,n,mode)


def intersectionTimesSWP(S,p,n,mode='all'):
    """Return the intersection of line segments S with planes (p,n).

    This is like intersectionTimesLWP, but the lines are defined by two points
    instead of by a point and a vector.
    Parameters:

    - `S`: (nS,2,3) shaped array (`mode=all`) or broadcast compatible array
      (`mode=pair`), defining one or more line segments.
    - `p`,`n`: (np,3) shaped arrays of points and normals (`mode=all`)
      or broadcast compatible arrays (`mode=pair`), defining a single plane
      or a set of planes.
    - `mode`: `all` to calculate the intersection of each line segment S with
      all planes (p,n) or `pair` for pairwise intersections.

    Returns a (nS,np) shaped (`mode=all`) array of parameter values t,
    such that the intersection points are given by
    `(1-t)*S[...,0,:] + t*S[...,1,:]`.
    """
    q0 = S[..., 0,:]
    q1 = S[..., 1,:]
    return intersectionTimesLWP(q0, q1-q0, p, n, mode)


def intersectionSWP(S,p,n,mode='all',return_all=False,atol=0.):
    """Return the intersection points of line segments S with planes (p,n).

    Parameters:

    - `S`: (nS,2,3) shaped array, defining a single line segment or a set of
      line segments.
    - `p`,`n`: (np,3) shaped arrays of points and normals, defining a single
      plane or a set of planes.
    - `mode`: `all` to calculate the intersection of each line segment S with
      all planes (p,n) or `pair` for pairwise intersections.
    - `return_all`: if True, all intersection points of the lines along the
      segments are returned. Default is to return only the points that lie
      on the segments.
    - `atol`: float tolerance of the points inside the line segments.


    Return values if `return_all==True`:

    - `t`: (nS,NP) parametric values of the intersection points along the line
      segments.
    - `x`: the intersection points themselves (nS,nP,3).

    Return values if `return_all==False`:

    - `t`: (n,) parametric values of the intersection points along the line
      segments (n <= nS*nP)
    - `x`: the intersection points themselves (n,3).
    - `wl`: (n,) line indices corresponding with the returned intersections.
    - `wp`: (n,) plane indices corresponding with the returned intersections
    """
    S = asanyarray(S).reshape(-1, 2, 3)
    p = asanyarray(p).reshape(-1, 3)
    n = asanyarray(n).reshape(-1, 3)
    # Find intersection parameters
    t = intersectionTimesSWP(S, p, n, mode)

    if not return_all:
        # Find points inside segments
        ok = (t >= 0.0-atol) * (t <= 1.0+atol)
        t = t[ok]
        if mode == 'all':
            wl, wt = where(ok)
        elif mode == 'pair':
            S = S[ok]
            wl = wt = where(ok)[0]

    if len(t) > 0:
        if mode == 'all':
            S = S[:, newaxis]
        x = pointsAtSegments(S, t)
        if x.ndim == 1:
            x = x.reshape(1, 3)
        if mode == 'all' and not return_all:
            x = x[ok]
    else:
        # No intersection: return empty Coords
        x = Coords()

    if return_all:
        return t, x
    else:
        return t, x, wl, wt


def intersectionPointsSWP(S,p,n,mode='all',return_all=False,atol=0.):
    """Return the intersection points of line segments S with planes (p,n) within tolerance atol.

    This is like :func:`intersectionSWP` but does not return the parameter
    values. It is equivalent to::

      intersectionSWP(S,p,n,mode,return_all)[1:]
    """
    res = intersectionSWP(S, p, n, mode, return_all, atol)
    if return_all:
        return res[1]
    else:
        return res[1:]


def intersectionTimesLWT(q,m,F,mode='all'):
    """Return the intersection of lines (q,m) with triangles F.

    Parameters:

    - `q`,`m`: (nq,3) shaped arrays of points and vectors (`mode=all`)
      or broadcast compatible arrays (`mode=pair`), defining a single line
      or a set of lines.
    - `F`: (nF,3,3) shaped array (`mode=all`) or broadcast compatible array
      (`mode=pair`), defining a single triangle or a set of triangles.
    - `mode`: `all` to calculate the intersection of each line (q,m) with
      all triangles F or `pair` for pairwise intersections.

    Returns a (nq,nF) shaped (`mode=all`) array of parameter values t,
      such that the intersection points are given q+tm.
    """
    Fn = cross(F[..., 1,:]-F[..., 0,:], F[..., 2,:]-F[..., 1,:])
    return intersectionTimesLWP(q, m, F[..., 0,:], Fn, mode)


def intersectionPointsLWT(q,m,F,mode='all',return_all=False):
    """Return the intersection points of lines (q,m) with triangles F.

    Parameters:

    - `q`,`m`: (nq,3) shaped arrays of points and vectors, defining a single
      line or a set of lines.
    - `F`: (nF,3,3) shaped array, defining a single triangle or a set of
      triangles.
    - `mode`: `all` to calculate the intersection points of each line (q,m) with
      all triangles F or `pair` for pairwise intersections.
    - `return_all`: if True, all intersection points are returned. Default is
      to return only the points that lie inside the triangles.

    Returns:

      If `return_all==True`, a (nq,nF,3) shaped (`mode=all`) array of
      intersection points, else, a tuple of intersection points with shape (n,3)
      and line and plane indices with shape (n), where n <= nq*nF.
    """
    q = asanyarray(q).reshape(-1, 3)
    m = asanyarray(m).reshape(-1, 3)
    F = asanyarray(F).reshape(-1, 3, 3)
    if not return_all:
        # Find lines passing through the bounding spheres of the triangles
        r, c, n = triangleBoundingCircle(F)
        if mode == 'all':
            mode = 'pair'

            #
            # TODO: check if/why this is slower
            # If so, we should move this into distanceFromLine
            #
##            d = distanceFromLine(c,(q,m),mode).transpose() # this is much slower for large arrays
            d = row_stack([ distanceFromLine(c, ([q[i]],[m[i]]), mode) for i in range(q.shape[0]) ])
            wl, wt = where(d<=r)
        elif mode == 'pair':
            d = distanceFromLine(c, (q,m), mode)
            wl = wt = where(d<=r)[0]
        if wl.size == 0:
            return empty((0, 3,), dtype=float), wl, wt
        q, m, F = q[wl], m[wl], F[wt]
    t = intersectionTimesLWT(q, m, F, mode)
    if mode == 'all':
        #
        # TODO:
        ## !!!!! CAN WE EVER GET HERE? only if return_all??
        #
        q = q[:, newaxis]
        m = m[:, newaxis]
    x = pointsAtLines(q, m, t)
    if not return_all:
        # Find points inside the faces
        ok = insideTriangle(F, x[newaxis]).reshape(-1)
        return x[ok], wl[ok], wt[ok]
    else:
        return x


def intersectionTimesSWT(S,F,mode='all'):
    """Return the intersection of lines segments S with triangles F.

    Parameters:

    - `S`: (nS,2,3) shaped array (`mode=all`) or broadcast compatible array
      (`mode=pair`), defining a single line segment or a set of line segments.
    - `F`: (nF,3,3) shaped array (`mode=all`) or broadcast compatible array
      (`mode=pair`), defining a single triangle or a set of triangles.
    - `mode`: `all` to calculate the intersection of each line segment S with
      all triangles F or `pair` for pairwise intersections.

    Returns a (nS,nF) shaped (`mode=all`) array of parameter values t,
    such that the intersection points are given by
    `(1-t)*S[...,0,:] + t*S[...,1,:]`.
    """
    Fn = cross(F[..., 1,:]-F[..., 0,:], F[..., 2,:]-F[..., 1,:])
    return intersectionTimesSWP(S, F[..., 0,:], Fn, mode)


def intersectionPointsSWT(S,F,mode='all',return_all=False):
    """Return the intersection points of lines segments S with triangles F.

    Parameters:

    - `S`: (nS,2,3) shaped array, defining a single line segment or a set of
      line segments.
    - `F`: (nF,3,3) shaped array, defining a single triangle or a set of
      triangles.
    - `mode`: `all` to calculate the intersection points of each line segment S
      with all triangles F or `pair` for pairwise intersections.
    - `return_all`: if True, all intersection points are returned. Default is
      to return only the points that lie on the segments and inside the
      triangles.

    Returns:

      If `return_all==True`, a (nS,nF,3) shaped (`mode=all`) array of
      intersection points, else, a tuple of intersection points with shape (n,3)
      and line and plane indices with shape (n), where n <= nS*nF.
    """

    S = asanyarray(S).reshape(-1, 2, 3)
    F = asanyarray(F).reshape(-1, 3, 3)
    if not return_all:
        # Find lines passing through the bounding spheres of the triangles
        r, c, n = triangleBoundingCircle(F)
        if mode == 'all':
            #
            # TODO: check why, if so move into distanceFromLine
            #
##            d = distanceFromLine(c,S,mode).transpose() # this is much slower for large arrays
            mode = 'pair'
            d = row_stack([ distanceFromLine(c, S[i], mode) for i in range(S.shape[0]) ])
            wl, wt = where(d<=r)
        elif mode == 'pair':
            d = distanceFromLine(c, S, mode)
            wl = wt = where(d<=r)[0]
        if wl.size == 0:
            return empty((0, 3,), dtype=float), wl, wt
        S, F = S[wl], F[wt]
    t = intersectionTimesSWT(S, F, mode)
    if mode == 'all':
        S = S[:, newaxis]
    x = pointsAtSegments(S, t)
    if not return_all:
        # Find points inside the segments and faces
        ok = (t >= 0.0) * (t <= 1.0) * insideTriangle(F, x[newaxis]).reshape(-1)
        return x[ok], wl[ok], wt[ok]
    else:
        return x


def intersectionPointsPWP(p1,n1,p2,n2,p3,n3,mode='all'):
    """Return the intersection points of planes (p1,n1), (p2,n2) and (p3,n3).

    Parameters:

    - `pi`,`ni` (i=1...3): (npi,3) shaped arrays of points and normals
      (`mode=all`)
      or broadcast compatible arrays (`mode=pair`), defining a single plane
      or a set of planes.
    - `mode`: `all` to calculate the intersection of each plane (p1,n1) with
      all planes (p2,n2) and (p3,n3) or `pair` for pairwise intersections.

    Returns a (np1,np2,np3,3) shaped (`mode=all`) array of intersection points.
    """
    if mode == 'all':
        p1 = asanyarray(p1).reshape(-1, 1, 1, 3)
        n1 = asanyarray(n1).reshape(-1, 1, 1, 3)
        p2 = asanyarray(p2).reshape(1, -1, 1, 3)
        n2 = asanyarray(n2).reshape(1, -1, 1, 3)
        p3 = asanyarray(p3).reshape(1, 1, -1, 3)
        n3 = asanyarray(n3).reshape(1, 1, -1, 3)
    dot1 = dotpr(p1, n1)[..., newaxis]
    dot2 = dotpr(p2, n2)[..., newaxis]
    dot3 = dotpr(p3, n3)[..., newaxis]
    cross23 = cross(n2, n3)
    cross31 = cross(n3, n1)
    cross12 = cross(n1, n2)
    denom = dotpr(n1, cross23)[..., newaxis]
    return (dot1*cross23+dot2*cross31+dot3*cross12)/denom


def intersectionLinesPWP(p1,n1,p2,n2,mode='all'):
    """Return the intersection lines of planes (p1,n1) and (p2,n2).

    Parameters:

    - `pi`,`ni` (i=1...2): (npi,3) shaped arrays of points and normals (`mode=all`)
      or broadcast compatible arrays (`mode=pair`), defining a single plane
      or a set of planes.
    - `mode`: `all` to calculate the intersection of each plane (p1,n1) with
      all planes (p2,n2) or `pair` for pairwise intersections.

    Returns a tuple of (np1,np2,3) shaped (`mode=all`) arrays of intersection
    points q and vectors m, such that the intersection lines are given by
    ``q+t*m``.
    """
    if mode == 'all':
        p1 = asanyarray(p1).reshape(-1, 1, 3)
        n1 = asanyarray(n1).reshape(-1, 1, 3)
        p2 = asanyarray(p2).reshape(1, -1, 3)
        n2 = asanyarray(n2).reshape(1, -1, 3)
    m =  cross(n1, n2)
    q = intersectionPointsPWP(p1, n1, p2, n2, p1, m, mode='pair')
    return q, m


def intersectionSphereSphere(R, r, d):
    """Intersection of two spheres (or two circles in the x,y plane).

    Computes the intersection of two spheres with radii R, resp. r, having
    their centres at distance d <= R+r. The intersection is a circle with
    its center on the segment connecting the two sphere centers at a distance
    x from the first sphere, and having a radius y. The return value is a
    tuple x,y.
    """
    if d > R+r:
        raise ValueError("d (%s) should not be larger than R+r (%s)" % (d, R+r))
    dd = R**2-r**2+d**2
    d2 = 2*d
    x = dd/d2
    y = sqrt(d2**2*R**2 - dd**2) / d2
    return x, y


########## projection #############################################

    ## intersectionTimesPOP     -> projectPointOnPlaneTimes
    ## intersectionPointsPOP    -> projectPointOnPlane
    ## intersectionTimesPOL     -> projectPointOnLineTimes
    ## intersectionPointsPOL    -> projectPointOnLine


def projectPointOnPlane(X,p,n,mode='all'):
    """Return the projection of points X on planes (p,n).

    Parameters:

    - `X`: a (nx,3) shaped array of points.
    - `p`, `n`: (np,3) shaped arrays of points and normals defining `np` planes.
    - `mode`: 'all' or 'pair:

      - if 'all', the projection of all points on all planes is computed;
        `nx` and `np` can be different.
      - if 'pair': `nx` and `np` should be equal (or 1) and the projection
        of pairs of point and plane are computed (using broadcasting for
        length 1 data).

    Returns a float array of size (nx,np,3) for mode 'all', or size (nx,3)
    for mode 'pair'.

    Example:

    >>> X = Coords([[0.,1.,0.],[3.,0.,0.],[4.,3.,0.]])
    >>> p,n = [[2.,0.,0.],[0.,1.,0.]], [[1.,0.,0.],[0.,1.,0.]]
    >>> print(projectPointOnPlane(X,p,n))
    [[[ 2.  1.  0.]
      [ 0.  1.  0.]]
    <BLANKLINE>
     [[ 2.  0.  0.]
      [ 3.  1.  0.]]
    <BLANKLINE>
     [[ 2.  3.  0.]
      [ 4.  1.  0.]]]
    >>> print(projectPointOnPlane(X[:2],p,n,mode='pair'))
    [[ 2.  1.  0.]
     [ 3.  1.  0.]]

    """
    X = asarray(X).reshape(-1, 3)
    p = asarray(p).reshape(-1, 3)
    n = asarray(n).reshape(-1, 3)
    t =  projectPointOnPlaneTimes(X, p, n, mode)
    if mode == 'all':
        X = X[:, newaxis]
    return pointsAtLines(X, n, t)


def projectPointOnPlaneTimes(X,p,n,mode='all'):
    """Return the projection of points X on planes (p,n).

    This is like :meth:`projectPointOnPlane` but instead of returning
    the projected points, returns the parametric values t along the
    lines (X,n), such that the projection points can be computed from
    X+t*n.

    Parameters: see :meth:`projectPointOnPlane`.

    Returns a float array of size (nx,np) for mode 'all', or size (nx,)
    for mode 'pair'.

    Example:

    >>> X = Coords([[0.,1.,0.],[3.,0.,0.],[4.,3.,0.]])
    >>> p,n = [[2.,0.,0.],[0.,1.,0.]], [[1.,0.,0.],[0.,1.,0.]]
    >>> print(projectPointOnPlaneTimes(X,p,n))
    [[ 2.  0.]
     [-1.  1.]
     [-2. -2.]]
    >>> print(projectPointOnPlaneTimes(X[:2],p,n,mode='pair'))
    [ 2.  1.]

    """
    if mode == 'all':
        return (dotpr(p, n) - inner(X, n)) / dotpr(n, n)
    elif mode == 'pair':
        return (dotpr(p, n) - dotpr(X, n)) / dotpr(n, n)


def projectPointOnLine(X,p,n,mode='all'):
    """Return the projection of points X on lines (p,n).

    Parameters:

    - `X`: a (nx,3) shaped array of points.
    - `p`, `n`: (np,3) shaped arrays of points and vectors defining `np` lines.
    - `mode`: 'all' or 'pair:

      - if 'all', the projection of all points on all lines is computed;
        `nx` and `np` can be different.
      - if 'pair': `nx` and `np` should be equal (or 1) and the projection
        of pairs of point and line are computed (using broadcasting for
        length 1 data).

    Returns a float array of size (nx,np,3) for mode 'all', or size (nx,3)
    for mode 'pair'.

    Example:

    >>> X = Coords([[0.,1.,0.],[3.,0.,0.],[4.,3.,0.]])
    >>> p,n = [[2.,0.,0.],[0.,1.,0.]], [[0.,2.,0.],[1.,0.,0.]]
    >>> print(projectPointOnLine(X,p,n))
    [[[ 2.  1.  0.]
      [ 0.  1.  0.]]
    <BLANKLINE>
     [[ 2.  0.  0.]
      [ 3.  1.  0.]]
    <BLANKLINE>
     [[ 2.  3.  0.]
      [ 4.  1.  0.]]]
    >>> print(projectPointOnLine(X[:2],p,n,mode='pair'))
    [[ 2.  1.  0.]
     [ 3.  1.  0.]]

    """
    X = asarray(X).reshape(-1, 3)
    p = asarray(p).reshape(-1, 3)
    n = asarray(n).reshape(-1, 3)
    t = projectPointOnLineTimes(X, p, n, mode)
    return pointsAtLines(p, n, t)


def projectPointOnLineTimes(X,p,n,mode='all'):
    """Return the projection of points X on lines (p,n).

    This is like :meth:`projectPointOnLine` but instead of returning
    the projected points, returns the parametric values t along the
    lines (X,n), such that the projection points can be computed from
    p+t*n.

    Parameters: see :meth:`projectPointOnLine`.

    Returns a float array of size (nx,np) for mode 'all', or size (nx,)
    for mode 'pair'.

    Example:

    >>> X = Coords([[0.,1.,0.],[3.,0.,0.],[4.,3.,0.]])
    >>> p,n = [[2.,0.,0.],[0.,1.,0.]], [[0.,1.,0.],[1.,0.,0.]]
    >>> print(projectPointOnLineTimes(X,p,n))
    [[ 1.  0.]
     [ 0.  3.]
     [ 3.  4.]]
    >>> print(projectPointOnLineTimes(X[:2],p,n,mode='pair'))
    [ 1.  3.]

    """
    if mode == 'all':
        return (inner(X, n) - dotpr(p, n)) / dotpr(n, n)
    elif mode == 'pair':
        return (dotpr(X, n) - dotpr(p, n)) / dotpr(n, n)


#################### distance ##############################

 #   distancesPFL             -> distanceFromLine
 #   distancesPFS             -> distanceFromLine

# TODO: we should extend the method of Coords.distanceFromLine

def distanceFromLine(X,lines,mode='all'):
    """Return the distance of points X from lines (p,n).

    Parameters:

    - `X`: a (nx,3) shaped array of points.
    - `lines`: one of the following definitions of the line(s):

      - a tuple (p,n), where both p and n are (np,3) shaped arrays of
        respectively points and vectors defining `np` lines;
      - an (np,2,3) shaped array containing two points of each line.

    - `mode`: 'all' or 'pair:

      - if 'all', the distance of all points to all lines is computed;
        `nx` and `np` can be different.
      - if 'pair': `nx` and `np` should be equal (or 1) and the distance
        of pairs of point and line are computed (using broadcasting for
        length 1 data).

    Returns a float array of size (nx,np) for mode 'all', or size (nx)
    for mode 'pair'.

    Example:

    >>> X = Coords([[0.,1.,0.],[3.,0.,0.],[4.,3.,0.]])
    >>> L = Line([[2.,0.,0.],[0.,1.,0.]], [[0.,3.,0.],[1.,0.,0.]])
    >>> print(distanceFromLine(X,L))
    [[ 2.  0.]
     [ 1.  1.]
     [ 2.  2.]]
    >>> print(distanceFromLine(X[:2],L,mode='pair'))
    [ 2.  1.]
    >>> L = Line([[[2.,0.,0.],[2.,2.,0.]], [[0.,1.,0.],[1.,1.,0.]]])
    >>> print(distanceFromLine(X,L))
    [[ 2.  0.]
     [ 1.  1.]
     [ 2.  2.]]
    >>> print(distanceFromLine(X[:2],L,mode='pair'))
    [ 2.  1.]
    """
    lines = Line(lines)
    if mode == 'all':
        return column_stack(X.distanceFromLine(p,n) for p,n in zip(lines.p,lines.n))
    else:
        Y = projectPointOnLine(X, lines.p, lines.n, mode)
        return length(Y-X)


def pointNearLine(X,p,n,atol,nproc=1):
    """Find the points from X that are near to lines (p,n).

    Finds the points from X that are closer than atol to any of the lines (p,n).

    Parameters:

    - `X`: a (nx,3) shaped array of points.
    - `p`, `n`: (np,3) shaped arrays of points and vectors defining `np` lines.
    - `atol`: float or (nx,) shaped float array of pointwise tolerances

    Returns a list of arrays with sorted point indices for each of the lines.

    Example:

    >>> X = Coords([[0.,1.,0.],[3.,0.,0.],[4.,3.,0.]])
    >>> p,n = [[2.,0.,0.],[0.,1.,0.]], [[0.,3.,0.],[1.,0.,0.]]
    >>> print(pointNearLine(X,p,n,1.5))
    [array([1]), array([0, 1])]
    >>> print(pointNearLine(X,p,n,1.5,2))
    [array([1]), array([0, 1])]
    """
    if isFloat(atol):
         atol = [atol]*len(X)
    atol = checkArray1D(atol,kind=None,allow=None,size=len(X))
    if nproc == 1:
        ip = [ where(X.distanceFromLine(pi,ni) < atol)[0] for pi,ni in zip(p,n) ]
        return ip
    args = multi.splitArgs((X,p,n,atol),mask=(0,1,1,0),nproc=nproc)
    tasks = [(pointNearLine, a) for a in args]
    res = multi.multitask(tasks, nproc)
    from pyformex import olist
    return olist.concatenate(res)


def faceDistance(X,Fp,return_points=False):
    """Compute the closest perpendicular distance to a set of triangles.

    X is a (nX,3) shaped array of points.
    Fp is a (nF,3,3) shaped array of triangles.

    Note that some points may not have a normal with footpoint inside any
    of the facets.

    The return value is a tuple OKpid,OKdist,OKpoints where:

    - OKpid is an array with the point numbers having a normal distance;
    - OKdist is an array with the shortest distances for these points;
    - OKpoints is an array with the closest footpoints for these points
      and is only returned if return_points = True.
    """
    if not Fp.shape[1] == 3:
        raise ValueError("Currently this function only works for triangular faces.")
    # Compute normals on the faces
    Fn = cross(Fp[:, 1]-Fp[:, 0], Fp[:, 2]-Fp[:, 1])
    # Compute projection of points X on facets F
    Y = projectPointOnPlane(X, Fp[:, 0,:], Fn)
    # Find intersection points Y inside the facets
    inside = insideTriangle(Fp, Y)
    pid = where(inside)[0]
    if pid.size == 0:
        if return_points:
            return [], [], []
        else:
            return [], []

    # Compute the distances
    X = X[pid]
    Y = Y[inside]
    dist = length(X-Y)
    # Get the shortest distances
    OKpid, OKpos = groupArgmin(dist, pid)
    OKdist = dist[OKpos]
    if return_points:
        # Get the closest footpoints matching OKpid
        OKpoints = Y[OKpos]
        return OKpid, OKdist, OKpoints
    return OKpid, OKdist


def edgeDistance(X,Ep,return_points=False):
    """Compute the closest perpendicular distance of points X to a set of edges.

    X is a (nX,3) shaped array of points.
    Ep is a (nE,2,3) shaped array of edge vertices.

    Note that some points may not have a normal with footpoint inside any
    of the edges.

    The return value is a tuple OKpid,OKdist,OKpoints where:

    - OKpid is an array with the point numbers having a normal distance;
    - OKdist is an array with the shortest distances for these points;
    - OKpoints is an array with the closest footpoints for these points
      and is only returned if return_points = True.
    """
    # Compute vectors along the edges
    En = Ep[:, 1] - Ep[:, 0]
    # Compute intersection points of perpendiculars from X on edges E
    t = projectPointOnLineTimes(X, Ep[:, 0], En)
    Y = pointsAtLines(Ep[:, 0], En, t)
    # Find intersection points Y inside the edges
    inside = (t >= 0.) * (t <= 1.)
    pid = where(inside)[0]
    if pid.size == 0:
        if return_points:
            return [], [], []
        else:
            return [], []

    # Compute the distances
    X = X[pid]
    Y = Y[inside]
    dist = length(X-Y)
    # Get the shortest distances
    OKpid, OKpos = groupArgmin(dist, pid)
    OKdist = dist[OKpos]
    if return_points:
        # Get the closest footpoints matching OKpid
        OKpoints = Y[OKpos]
        return OKpid, OKdist, OKpoints
    return OKpid, OKdist


def vertexDistance(X,Vp,return_points=False):
    """Compute the closest distance of points X to a set of vertices.

    X is a (nX,3) shaped array of points.
    Vp is a (nV,3) shaped array of vertices.

    The return value is a tuple OKdist,OKpoints where:

    - OKdist is an array with the shortest distances for the points;
    - OKpoints is an array with the closest vertices for the points
      and is only returned if return_points = True.
    """
    # Compute the distances
    dist = length(X[:, newaxis]-Vp)
    # Get the shortest distances
    OKdist = dist.min(-1)
    if return_points:
        # Get the closest points matching X
        minid = dist.argmin(-1)
        OKpoints = Vp[minid]
        return OKdist, OKpoints
    return OKdist,



################ other functions #################################

def areaNormals(x):
    """Compute the area and normal vectors of a collection of triangles.

    x is an (ntri,3,3) array with the coordinates of the vertices of ntri
    triangles.

    Returns a tuple (areas,normals) with the areas and the normals of the
    triangles. The area is always positive. The normal vectors are normalized.
    """
    x = x.reshape(-1, 3, 3)
    area, normals = vectorPairAreaNormals(x[:, 1]-x[:, 0], x[:, 2]-x[:, 1])
    area *= 0.5
    return area, normals


def degenerate(area, normals):
    """Return a list of the degenerate faces according to area and normals.

    area,normals are equal sized arrays with the areas and normals of a
    list of faces, such as the output of the :func:`areaNormals` function.

    A face is degenerate if its area is less or equal to zero or the
    normal has a nan (not-a-number) value.

    Returns a list of the degenerate element numbers as a sorted array.
    """
    return unique(concatenate([where(area<=0)[0], where(isnan(normals))[0]]))


def hexVolume(x):
    """Compute the volume of hexahedrons.

    Parameters:

    - `x`: float array (nelems,8,3)

    Returns a float array (nelems) withe the approximate volume of the
    hexahedrons formed by each 8-tuple of vertices. The volume is obained
    by dividing the hexahedron in 24 tetrahedrons and using the formulas
    from http://www.osti.gov/scitech/servlets/purl/632793

    Example:

    >>> from pyformex.elements import Hex8
    >>> X = Coords(Hex8.vertices).reshape(-1,8,3)
    >>> print(hexVolume(X))
    [ 1.]

    """
    x = checkArray(x,shape=(-1,8,3),kind='f')
    x71 = x[...,6,:] - x[...,1,:]
    x60 = x[...,7,:] - x[...,0,:]
    x72 = x[...,6,:] - x[...,3,:]
    x30 = x[...,2,:] - x[...,0,:]
    x50 = x[...,5,:] - x[...,0,:]
    x74 = x[...,6,:] - x[...,4,:]
    return (vectorTripleProduct(x71+x60,x72,x30) + vectorTripleProduct(x60,x72+x50,x74) + vectorTripleProduct(x71,x50,x74+x30)) / 12


def levelVolumes(x):
    """Compute the level volumes of a collection of elements.

    x is an (nelems,nplex,3) array with the coordinates of the nplex vertices
    of nelems elements, with nplex equal to 2, 3 or 4.

    If nplex == 2, returns the lengths of the straight line segments.
    If nplex == 3, returns the areas of the triangle elements.
    If nplex == 4, returns the signed volumes of the tetraeder elements.
    Positive values result if vertex 3 is at the positive side of the plane
    defined by the vertices (0,1,2). Negative volumes are reported for
    tetraeders having reversed vertex order.

    For any other value of nplex, raises an error.
    If succesful, returns an (nelems,) shaped float array.
    """
    nplex = x.shape[1]
    if nplex == 2:
        return length(x[:, 1]-x[:, 0])
    elif nplex == 3:
        return vectorPairArea(x[:, 1]-x[:, 0], x[:, 2]-x[:, 1]) / 2
    elif nplex == 4:
        return vectorTripleProduct(x[:, 1]-x[:, 0], x[:, 2]-x[:, 1], x[:, 3]-x[:, 0]) / 6
    else:
        raise ValueError("Plexitude should be one of 2, 3 or 4; got %s" % nplex)

# TODO: move to Coords, rename to principalSizes(order=False)
def inertialDirections(x):
    """Return the directions and dimension of a Coords based of inertia.

    - `x`: a Coords-like array

    Returns a tuple of the principal direction vectors and the sizes along
    these directions, ordered from the smallest to the largest direction.

    """
    I = x.inertia()
    Iprin, Iaxes = I.principal()
    C = I.ctr
    X = x.trl(-C).rot(Iaxes)
    sizes = X.sizes()
    i = argsort(sizes)
    return Iaxes[i], sizes[i]


def smallestDirection(x,method='inertia',return_size=False):
    """Return the direction of the smallest dimension of a Coords

    - `x`: a Coords-like array
    - `method`: one of 'inertia' or 'random'
    - return_size: if True and `method` is 'inertia', a tuple of a direction
      vector and the size  along that direction and the cross directions;
      else, only return the direction vector.
    """
    x = x.reshape(-1, 3)
    if method == 'inertia':
        # The idea is to take the smallest dimension in a coordinate
        # system aligned with the global axes.
        N,sizes=inertialDirections(x)
        if return_size:
            return N[0], sizes[0]
        else:
            return N[0]
    elif method == 'random':
        # Take the mean of the normals on randomly created triangles
        from pyformex.trisurface import TriSurface
        n = x.shape[0]
        m = 3 * (n // 3)
        e = arange(m)
        random.shuffle(e)
        if n > m:
            e = concatenate([e, [0, 1, n-1]])
        #el = e[-3:]
        S = TriSurface(x, e.reshape(-1, 3))
        A, N = S.areaNormals()
        ok = where(isnan(N).sum(axis=1) == 0)[0]
        N = N[ok]
        N = N*N
        N = N.mean(axis=0)
        N = sqrt(N)
        N = normalize(N)
        return N


def largestDirection(x,return_size=False):
    """Return the direction of the largest dimension of a Coords.

    - `x`: a Coords-like array
    - return_size: if True and `method` is 'inertia', a tuple of a direction
      vector and the size  along that direction and the cross directions;
      else, only return the direction vector.
    """
    x = x.reshape(-1, 3)
    N,sizes = inertialDirections(x)
    if return_size:
        return N[2], sizes[2]
    else:
        return N[2]


# todo: add parameter mode = 'all' or 'pair'
def distance(X, Y):
    """Returns the distance of all points of X to those of Y.

    Parameters:

    - `X`: (nX,3) shaped array of points.
    - `Y`: (nY,3) shaped array of points.

    Returns an (nX,nT) shaped array with the distances between all points of
    X and Y.
    """
    X = asarray(X).reshape(-1,3)
    Y = asarray(Y).reshape(-1,3)
    return length(X[:, newaxis]-Y)


def closest(X,Y=None,return_dist=False):
    """Find the point of Y closest to each of the points of X.

    Parameters:

    - `X`: (nX,3) shaped array of points
    - `Y`: (nY,3) shaped array of points. If None, Y is taken equal to X,
      allowing to search for the closest point in a single set. In the latter
      case, the point itself is excluded from the search (as otherwise
      that would obviously be the closest one).
    - `return_dist`: bool. If True, also returns the distances of the closest
      points.

    Returns:

    - `ind`: (nX,) int array with the index of the closest point in Y to the
      points of X
    - `dist`: (nX,) float array with the distance of the closest point. This
      is equal to length(X-Y[ind]). It is only returned if return_dist is True.
    """
    if Y is None:
        dist = distance(X, X)   # Compute all distances
        ar = arange(X.shape[0])
        dist[ar,ar] = dist.max()+1.
    else:
        dist = distance(X, Y)   # Compute all distances
    ind = dist.argmin(-1)       # Locate the smallest distances
    if return_dist:
        return ind, dist[arange(dist.shape[0]), ind]
    else:
        return ind


def closestPair(X, Y):
    """Find the closest pair of points from X and Y.

    Parameters:

    - `X`: (nX,3) shaped array of points
    - `Y`: (nY,3) shaped array of points

    Returns a tuple (i,j,d) where i,j are the indices in X,Y identifying
    the closest points, and d is the distance between them.
    """
    dist = distance(X, Y)   # Compute all distances
    ind = dist.argmin()     # Locate the smallest distances
    i, j = divmod(ind, Y.shape[0])
    return i, j, dist[i, j]


def projectedArea(x, dir):
    """Compute projected area inside a polygon.

    Parameters:

    - `x`: (npoints,3) Coords with the ordered vertices of a
      (possibly nonplanar) polygonal contour.
    - `dir`: either a global axis number (0, 1 or 2) or a direction vector
      consisting of 3 floats, specifying the projection direction.

    Returns a single float value with the area inside the polygon projected
    in the specified direction.

    Note that if the polygon is planar and the specified direction is that
    of the normal on its plane, the returned area is that of the planar
    figure inside the polygon. If the polygon is nonplanar however, the area
    inside the polygon is not defined. The projected area in a specified
    direction is, since the projected polygon is a planar one.
    """
    if x.shape[0] < 3:
        return 0.0
    if isinstance(dir, int):
        dir = unitVector(dir)
    else:
        dir = normalize(dir)
    x1 = roll(x, -1, axis=0)
    area = vectorTripleProduct(Coords(dir), x, x1)
    return 0.5 * area.sum()


def polygonNormals(x):
    """Compute normals in all points of polygons in x.

    x is an (nel,nplex,3) coordinate array representing nel (possibly nonplanar)
    polygons.

    The return value is an (nel,nplex,3) array with the unit normals on the
    two edges ending in each point.
    """
    if x.shape[1] < 3:
        #raise ValueError("Cannot compute normals for plex-2 elements"
        n = zeros_like(x)
        n[:,:, 2] = -1.
        return n

    ni = arange(x.shape[1])
    nj = roll(ni, 1)
    nk = roll(ni, -1)
    v1 = x-x[:, nj]
    v2 = x[:, nk]-x
    n = vectorPairNormals(v1.reshape(-1, 3), v2.reshape(-1, 3)).reshape(x.shape)
    return n


def averageNormals(coords,elems,atNodes=False,treshold=None):
    """Compute average normals at all points of elems.

    coords is a (ncoords,3) array of nodal coordinates.
    elems is an (nel,nplex) array of element connectivity.

    The default return value is an (nel,nplex,3) array with the averaged
    unit normals in all points of all elements.
    If atNodes == True, a more compact array with the unique averages
    at the nodes is returned.
    """
    if treshold is not None:
        print("AVERAGE NORMALS THRESHOLD IS NOT IMPLEMENTED!")
    normals = polygonNormals(coords[elems])
    normals,cnt = nodalSum(normals, elems, coords.shape[0])
    # No need to take average, since we are going to normalize anyway
    normals = normalize(normals)
    if not atNodes:
        normals = normals[elems]
    return normals


def triangleInCircle(x):
    """Compute the incircles of the triangles x

    The incircle of a triangle is the largest circle that can be inscribed
    in the triangle.

    x is a Coords array with shape (ntri,3,3) representing ntri triangles.

    Returns a tuple r,C,n with the radii, Center and unit normals of the
    incircles.

    Example:

    >>> X = Formex(Coords([1.,0.,0.])).rosette(3,120.)
    >>> print(X)
    {[1.0,0.0,0.0], [-0.5,0.866025,0.0], [-0.5,-0.866025,0.0]}
    >>> radius, center, normal = triangleInCircle(X.coords.reshape(-1,3,3))
    >>> print(radius)
    [ 0.5]
    >>> print(center)
    [[ 0.  0.  0.]]
    """
    checkArray(x, shape=(-1, 3, 3))
    # Edge vectors
    v = roll(x, -1, axis=1) - x
    v = normalize(v)
    # create bisecting lines in x0 and x1
    b0 = v[:, 0]-v[:, 2]
    b1 = v[:, 1]-v[:, 0]
    # find intersection => center point of incircle
    center = intersectLineWithLine(x[:, 0], b0, x[:, 1], b1, mode='pair')[0]
    # find distance to any side => radius
    radius = distanceFromLine(center,(x[:,0], v[:,0]),mode='pair')
    # normals
    normal = cross(v[:, 0], v[:, 1])
    normal /= length(normal).reshape(-1, 1)
    return radius, center, normal


def triangleCircumCircle(x,bounding=False):
    """Compute the circumcircles of the triangles x

    x is a Coords array with shape (ntri,3,3) representing ntri triangles.

    Returns a tuple r,C,n with the radii, Center and unit normals of the
    circles going through the vertices of each triangle.

    If bounding=True, this returns the triangle bounding circle.
    """
    checkArray(x, shape=(-1, 3, 3))
    # Edge vectors
    v = x - roll(x, -1, axis=1)
    vv = dotpr(v, v)
    # Edge lengths
    lv = sqrt(vv)
    n = cross(v[:, 0], v[:, 1])
    nn = dotpr(n, n)
    # Radius
    N = sqrt(nn)
    r = asarray(lv.prod(axis=-1) / N / 2)
    # Center
    w = -dotpr(roll(v, 1, axis=1), roll(v, 2, axis=1))
    a = w * vv
    C = a.reshape(-1, 3, 1) * roll(x, 1, axis=1)
    C = C.sum(axis=1) / nn.reshape(-1, 1) / 2
    # Unit normals
    n = n / N.reshape(-1, 1)
    # Bounding circle
    if bounding:
        # Modify for obtuse triangles
        for i, j, k in [[0, 1, 2], [1, 2, 0], [2, 0, 1]]:
            obt = vv[:, i] >= vv[:, j]+vv[:, k]
            r[obt] = 0.5 * lv[obt, i]
            C[obt] = 0.5 * (x[obt, i] + x[obt, j])

    return r, C, n


def triangleBoundingCircle(x):
    """Compute the bounding circles of the triangles x

    The bounding circle is the smallest circle in the plane of the triangle
    such that all vertices of the triangle are on or inside the circle.
    If the triangle is acute, this is equivalent to the triangle's
    circumcircle. It the triangle is obtuse, the longest edge is the
    diameter of the bounding circle.

    x is a Coords array with shape (ntri,3,3) representing ntri triangles.

    Returns a tuple r,C,n with the radii, Center and unit normals of the
    bounding circles.
    """
    return triangleCircumCircle(x, bounding=True)


def triangleObtuse(x):
    """Checks for obtuse triangles

    x is a Coords array with shape (ntri,3,3) representing ntri triangles.

    Returns an (ntri) array of True/False values indicating whether the
    triangles are obtuse.
    """
    checkArray(x, shape=(-1, 3, 3))
    # Edge vectors
    v = x - roll(x, -1, axis=1)
    vv = dotpr(v, v)
    return (vv[:, 0] > vv[:, 1]+vv[:, 2]) + (vv[:, 1] > vv[:, 2]+vv[:, 0]) + (vv[:, 2] > vv[:, 0]+vv[:, 1])


@utils.deprecated_by('geomtools.lineIntersection','geomtools.intersectLineWithLine')
def lineIntersection(P0, N0, P1, N1):
    """Finds the intersection of 2 (sets of) lines.

    This relies on the lines being pairwise coplanar.
    """
    Y0,Y1 = intersectLineWithLine(P0,N0,P1,N1,mode='pair')
    return Y0


def displaceLines(A, N, C, d):
    """Move all lines (A,N) over a distance a in the direction of point C.

    A,N are arrays with points and directions defining the lines.
    C is a point.
    d is a scalar or a list of scalars.
    All line elements of F are translated in the plane (line,C)
    over a distance d in the direction of the point C.
    Returns a new set of lines (A,N).
    """
    l, v = vectorNormalize(N)
    w = C - A
    vw = (v*w).sum(axis=-1).reshape((-1, 1))
    Y = A + vw*v
    l, v = vectorNormalize(C-Y)
    return A + d*v, N


def segmentOrientation(vertices,vertices2=None,point=None):
    """Determine the orientation of a set of line segments.

    vertices and vertices2 are matching sets of points.
    point is a single point.
    All arguments are Coords objects.

    Line segments run between corresponding points of vertices and vertices2.
    If vertices2 is None, it is obtained by rolling the vertices one position
    foreward, thus corresponding to a closed polygon through the vertices).
    If point is None, it is taken as the center of vertices.

    The orientation algorithm checks whether the line segments turn
    positively around the point.

    Returns an array with +1/-1 for positive/negative oriented segments.
    """
    if vertices2 is None:
        vertices2 = roll(vertices, -1, axis=0)
    if point is None:
        point = vertices.center()

    w = cross(vertices, vertices2)
    orient = sign(dotpr(point, w)).astype(Int)
    return orient


def rotationAngle(A,B,m=None,angle_spec=DEG):
    """Return rotation angles and vectors for rotations of A to B.

    A and B are (n,3) shaped arrays where each line represents a vector.
    This function computes the rotation from each vector of A to the
    corresponding vector of B.
    If m is None, the return value is a tuple of an (n,) shaped array with
    rotation angles (by default in degrees) and an (n,3) shaped array with
    unit vectors along the rotation axis.
    If m is a (n,3) shaped array with vectors along the rotation axis, the
    return value is a (n,) shaped array with rotation angles.
    Specify angle_spec=RAD to get the angles in radians.
    """
    A = asarray(A).reshape(-1, 3)
    B = asarray(B).reshape(-1, 3)
    if m is None:
        A = normalize(A)
        B = normalize(B)
        n = cross(A, B) # vectors perpendicular to A and B
        t = length(n) == 0.
        if t.any(): # some vectors A and B are parallel
            if A.shape[0] >=  B.shape[0]:
                temp = A[t]
            else:
                temp = B[t]
            n[t] = anyPerpendicularVector(temp)
        n = normalize(n)
        c = dotpr(A, B)
        angle = arccosd(c.clip(min=-1., max=1.), angle_spec)
        return angle, n
    else:
        m = asarray(m).reshape(-1, 3)
        # project vectors on plane
        A = projectionVOP(A, m)
        B = projectionVOP(B, m)
        angle, n = rotationAngle(A, B, angle_spec=angle_spec)
        # check sign of the angles
        m = normalize(m)
        inv = isClose(dotpr(n, m), [-1.])
        angle[inv] *= -1.
        return angle


def anyPerpendicularVector(A):
    """Return arbitrary vectors perpendicular to vectors of A.

    A is a (n,3) shaped array of vectors.
    The return value is a (n,3) shaped array of perpendicular vectors.

    The returned vector is always a vector in the x,y plane. If the original
    is the z-axis, the result is the x-axis.
    """
    A = asarray(A).reshape(-1, 3)
    x, y, z = hsplit(A, [1, 2])
    n = zeros(x.shape, dtype=Float)
    i = ones(x.shape, dtype=Float)
    t = (x==0.)*(y==0.)
    B = where(t, column_stack([i, n, n]), column_stack([-y, x, n]))
    # B = where(t,column_stack([-z,n,x]),column_stack([-y,x,n]))
    return B


def perpendicularVector(A, B):
    """Return vectors perpendicular on both A and B."""
    return cross(A, B)


def projectionVOV(A, B):
    """Return the projection of vector of A on vector of B."""
    L = projection(A, B)
    B = normalize(B)
    shape = list(L.shape)
    shape.append(1)
    return L.reshape(shape)*B


def projectionVOP(A, n):
    """Return the projection of vector of A on plane of B."""
    Aperp = projectionVOV(A, n)
    return A-Aperp


#################### barycentric coordinates ###############


def baryCoords(S, P):
    """Compute the barycentric coordinates of points  P wrt. simplexes S.

    S is a (nel,nplex,3) shaped array of n-simplexes (n=nplex-1):
    - 1-simplex: line segment
    - 2-simplex: triangle
    - 3-simplex: tetrahedron
    P is a (npts,3), (npts,nel,3) or (npts,1,3) shaped array of points.

    The return value is a (nplex,npts,nel) shaped array of barycentric coordinates.
    """
    if S.ndim != 3:
        raise ValueError("S should be a 3-dim array, got shape %s" % str(S.shape))
    if P.ndim == 2:
        P = P.reshape(-1, 1, 3)
    elif P.shape[1] != S.shape[0] and P.shape[1] != 1:
        raise ValueError("Second dimension of P should be first dimension of S or 1.")
    S = S.transpose(1, 0, 2) # (nplex,nel,3)
    vp = P - S[0]
    vs = S[1:] - S[:1]
    A = dotpr(vs[:, newaxis], vs[newaxis]) # (nplex-1,nplex-1,nel)
    b = dotpr(vp[newaxis], vs[:, newaxis]) # (nplex-1,npts,nel)
    #import timer
    #T = timer.Timer()
    t = solveMany(A, b)
    #print "DIRECT SOLVER: %s" % T.seconds()
    #T.reset()
    #tt = solveMany(A,b,False)
    #print "GENERAL SOLVER: %s" % T.seconds()
    #print "RESULTS MATCH: %s" % (tt-t).sum()

    t0 = (1.-t.sum(0))
    t0 = addAxis(t0, 0)
    t = row_stack([t0, t])
    return t


def insideSimplex(BC,bound=True):
    """Check if points are in simplexes.

    BC is an array of barycentric coordinates (along the first axis),
    which sum up to one.
    If bound = True, a point lying on the boundary is considered to
    be inside the simplex.
    """
    if bound:
        return (BC >= 0.).all(0)
    else:
        return (BC > 0.).all(0)



def insideTriangle(x,P,method='bary'):
    """Checks whether the points P are inside triangles x.

    x is a Coords array with shape (ntri,3,3) representing ntri triangles.
    P is a Coords array with shape (npts,ntri,3) representing npts points
    in each of the ntri planes of the triangles.
    This function checks whether the points of P fall inside the corresponding
    triangles.

    Returns an array with (npts,ntri) bool values.
    """
    if method == 'bary':
        return insideSimplex(baryCoords(x, P))
    else:
        # Older, slower algorithm
        # TODO: This can be removed?
        xP = x[newaxis, ...] - P[:,:, newaxis,:]
        xx = [ cross(xP[:,:, i], xP[:,:, j]) for (i, j) in ((0, 1), (1, 2), (2, 0)) ]
        xy = (xx[0]*xx[1]).sum(axis=-1)
        yz = (xx[1]*xx[2]).sum(axis=-1)
        d = dstack([xy, yz])
        return (d > 0).all(axis=-1)


############# things that need fixing or be removed ##############


# End
