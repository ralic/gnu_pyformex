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

"""Working with variable width tables.

Mesh type geometries use tables of integer data to store the connectivity
between different geometric entities. The basic connectivity table in a
Mesh with elements of the same type is a table of constant width: the
number of nodes connected to each element is constant.
However, the inverse table (the elements connected to each node) does not
have a constant width.

Tables of constant width are usually stored as a 2D array, allowing fast
indexing by row and/or column number. A variable width table can be stored
(using arrays) in two ways:

- as a 2D array, with a width equal to the maximal row length.
  Unused positions in the row are then filled with an invalid value (-1).
- as a 1D array, storing a simple concatenation of the rows.
  An additional array then stores the position in that array of the first
  element of each row.

In pyFormex, variable width tables were initially stored as 2D arrays:
a remnant of the author's past FORTRAN experience. With a growing
professional use of pyFormex involving ever larger models, it became clear
that there was a large memory and speed penalty related to the use of
2D arrays. This is illustrated in the following table, obtained on the
inversion of a connectivity table of 10000 rows and 25 columns.
The table shows the memory size of the inverse table, the time needed to
compute it, and the time to compute both tables. The latter involves an
extra conversion of the stored array to the other data type.

====================  ===============  ==============  ===============
Stored as:             2D (ndarray)     1D (Varray)     1D (Varray)
Rows are sorted:       yes              yes             no
====================  ===============  ==============  ===============
Memory size                450000         250000        250000
Time to create table       128 ms         49 ms         25ms
Time to create both        169 ms         82 ms         57ms
====================  ===============  ==============  ===============

The memory and speed gains of using the Varray are important.
The 2D array can even be faster generated by first creating the
1D array, and then converting that to 2D.
Not sorting the entries in the Varray provides a further gain.
The Varray class defined below therefore does not sort the rows
by default, but provides the methods to sort them when needed.
"""

from pyformex.arraytools import *
import sys

class Varray(object):
    """A variable width 2D integer array

    This class provides an efficient way to store tables of
    nonnegative integers when the rows of the table may have
    different length.

    For large tables this may allow a serious memory saving
    compared to the full array as returned by
    :func:`arraytools.inverseIndex`. Data in the Varray are stored as
    a single 1D array, containing the concatenation of all rows.
    An index is kept with the start position of each row in the 1D array.

    Parameters:

    - `data`: can be one of the following:

      - another Varray instance: a shallow copy of the Varray is created.

      - a list of lists of integers. Each item in the list contains
        one row of the table.

      - a 2D ndarray of integer type. The nonnegative numbers on each row
        constitute the data for that row.

      - a 1D array or list of integers, containing the concatenation of
        the rows. The second argument `ind` specifies the indices of the
        first element of each row.

      - a 1D array or list of integers, containing the concatenation of
        the rows obtained by prepending each row with the row length.
        The caller should make sure the these 1D data are consistent.

    - `ind`: only used when `data` is the pure concatenation of all rows.
      It is a 1D integer array or list specifying the position in `data` of
      the first element of each row. Its length should be equal to the
      number of rows (`nrows`) or `nrows+1`.
      It should be a non-decreasing series of integer values, starting with 0,
      and ending with the total number of elements in `data` in the position
      `nrows+1`. This last value may be omitted, and will then be added
      automatically. Note that two subsequent elements may be equal,
      corresponding with an empty row.

    Attributes:

    - `nrows`: the number of rows in the table
    - `width`: the maximum row length
    - `size`: the total number of entries in the table

    A Varray is by default printed in user-friendly format:

    >>> Va = Varray([[0],[1,2],[0,2,4],[0,2]])
    >>> print(Va)
    Varray (4,3)
      [0]
      [1 2]
      [0 2 4]
      [0 2]
    <BLANKLINE>

    Other initialization methods resulting in the same Varray:

    >>> Vb = Varray(Va)
    >>> print(str(Vb) == str(Va))
    True
    >>> Vb = Varray(array([[-1,-1,0],[-1,1,2],[0,2,4],[-1,0,2]]))
    >>> print(str(Vb) == str(Va))
    True
    >>> Vc = Varray([0,1,2,0,2,4,0,2],cumsum([0,1,2,3,2]))
    >>> print(str(Vc) == str(Va))
    True
    >>> Vd = Varray([1,0, 2,1,2, 3,0,2,4, 2,0,2])
    >>> print(str(Vd) == str(Va))
    True

    Indexing: The data for any row can be obtained by simple indexing:

    >>> print(Va[1])
    [1 2]

    This is equivalent with
    >>> print(Va.row(1))
    [1 2]

    Negative numbers are allowed:
    >>> print(Va.row(-1))
    [0 2]

    Extracted columns are filled with -1 values where needed
    >>> print(Va.col(1))
    [-1  2  2  2]

    Indexing with an iterable of integers returns a new Varray:

    >>> print(Va[[1,3]])
    Varray (2,2)
      [1 2]
      [0 2]
    <BLANKLINE>

    Select takes row numbers or bool:

    >>> print(Va.select([1,3]))
    Varray (2,2)
      [1 2]
      [0 2]
    <BLANKLINE>
    >>> print(Va.select(Va.lengths==2))
    Varray (2,2)
      [1 2]
      [0 2]
    <BLANKLINE>

    Iterator: A Varray provides its own iterator:

    >>> for row in Va:
    ...     print(row)
    [0]
    [1 2]
    [0 2 4]
    [0 2]


    >>> print(Varray())
    Varray (0,0)
    <BLANKLINE>

    >>> L,R = Va.sameLength()
    >>> print(L)
    [1 2 3]
    >>> print(R)
    [array([0]), array([1, 3]), array([2])]
    >>> for a in Va.split():
    ...     print(a)
    [[0]]
    [[1 2]
     [0 2]]
    [[0 2 4]]


    """
    def __init__(self,data=[],ind=None):
        """Initialize the Varray. See the class docstring."""

        # If data is a Varray, just use its data
        if isinstance(data, Varray):
            self.replace_data(data)
            return

        # Allow for empty Varray
        if len(data) <= 0:
            data = array([],dtype=Int)

        # If data is an array, convert to list of lists
        try:
            data = checkArray(data, kind='i', ndim=2)
            data = [ row[row>=0] for row in data ]
        except:
            pass

        # If data is a list of lists, concatenate and create index
        try:
            # construct row length array
            rowlen = [ len(row) for row in data ]
            ind = cumsum([0]+rowlen)
            data = concatenate(data).astype(Int)
        except:
            pass

        # data should now be 1D array
        # ind is also 1D array, unless initialized from inlined length data
        try:
            data = checkArray(data, kind='i', ndim=1)
            if ind is None:
                # extract row lengths from data
                i = 0
                size = len(data)
                rowlen = []
                while i < size:
                    rowlen.append(data[i])
                    i += data[i]+1
                # create indices and remove row lengths from data
                ind = cumsum([0]+rowlen)
                data = delete(data,ind[:-1]+arange(len(rowlen)))

            ind = checkArray(ind, kind='i', ndim=1)
            ind.sort()
            if ind[0] != 0 or ind[-1] > len(data):
                raise ValueError
            if ind[-1] != len(data):
                ind = concatenate([ind, [len(data)]])
        except:
            raise ValueError("Invalid input data for Varray")

        # Store the data
        self.data = data
        self.ind = ind
        # We also store the width because it is often needed and
        # may be expensive to compute
        self.width = max(self.lengths) if len(self.lengths) > 0 else 0
        # And the current row, for use in iterators
        self._row = 0


    def replace_data(self, va):
        """Replace the current data with data from another Varray"""
        if not isinstance(va, Varray):
            raise ValueError("Expected a Varray as argument")
        self.data = va.data
        self.ind = va.ind
        self.width = va.width


    # Attributes computed ad hoc, because cheap(er)

    @property
    def lengths(self):
        """Return the length of all rows of the Varray"""
        return self.ind[1:]-self.ind[:-1]

    @property
    def nrows(self):
        """Return the number of rows in the Varray"""
        return len(self.ind) - 1

    @property
    def size(self):
        """Return the total number of elements in the Varray"""
        return self.ind[-1]

    @property
    def shape(self):
        """Return a tuple with the number of rows and maximum row length"""
        return (self.nrows,self.width)


    ## Do we need this? Yes, if we do not store lengths
    def length(self, i):
        """Return the length of row i"""
        return self.ind[i+1]-self.ind[i]


    def row(self,i):
        """Return the data for row i"""
        if i < 0:
            i += self.nrows
        return self.data[self.ind[i]:self.ind[i+1]]


    def col(self,i):
        """Return the data for column i

        This always returns a list of length nrows.
        For rows where the column index i is missing, a value -1 is returned.
        """
        return array([ r[i] if i in range(-len(r),len(r)) else -1 for r in self ])


    def __getitem__(self, i):
        """Return the data for the row or rows i.

        Parameters:

        - `i`: the index of the requested row(s).

        Returns:

        - if `i` is a single integer: a 1D integer array with the values of
          row i,
        - if `i` is an iterable of integers: a Varray only containing the rows
          whose index occurs in `i`.
        """
        if isInt(i):
            return self.row(i)
        else:
            return Varray([ self.row(j) for j in i ])
        # Shall we also add a tuple as index?
        # to allow self[i,j] instead of i[i][j]


    # BV: Shall we add this to __getitem__ ?
    #     Or remove multiple values from __getitem__ ?

    def select(self, sel):
        """Select some rows from the Varray.

        Parameters:

        - `sel`: specifies the requested row(s). It can be one of:

          - an iterable of ints, specifying the requested row numbers;
          - an iterable of bools, flagging the requested rows.

        Returns a Varray containing the requested rows.
        """
        if len(sel) > 0 and not isInt(sel[0]):
            sel = where(sel)[0]
        return Varray([ self[j] for j in sel ])


    def __iter__(self):
        """Return an iterator for the Varray"""
        self._row = 0
        return self


    def __next__(self):
        """_Return the next row of the Varray"""
        if self._row >= self.nrows:
            raise StopIteration
        row = self[self._row]
        self._row += 1
        return row

    if (sys.hexversion) < 0x03000000:
        # In Python2 the next method is used instead of __next__
        next = __next__


    def index(self, sel):
        """Convert a selector to an index

        sel is either a list of element numbers or a bool array with
        length self.size

        Returns an index array with the selected numbers.
        """
        try:
            sel = checkArray(sel, shape=(self.size,), kind='b')
            sel = where(sel)[0]
        except:
            sel = checkArray(sel, kind='i')
        return sel


    def rowindex(self, sel):
        """Return the rowindex for the elements flagged by selector sel.

        sel is either a list of element numbers or a bool array with
        length self.size
        """
        sel = self.index(sel)
        return self.ind.searchsorted(sel, side='right')-1


    def colindex(self, sel):
        """Return the column index for the elements flagged by selector sel.

        sel is either a list of element numbers or a bool array with
        length self.size
        """
        sel = self.index(sel)
        ri = self.rowindex(sel)
        return sel - self.ind[ri]


    def where(self, sel):
        """Return row and column index of the selected elements

        sel is either a list of element numbers or a bool array with
        length self.size

        Returns a 2D array where the first column is the row index
        and the second column the corresponding column index of an
        element selected by sel
        """
        return column_stack([self.rowindex(sel), self.colindex(sel)])


    def index1d(self, i, j):
        """Return the sequential index for the element with 2D index i,j"""
        if j >= 0 and j < self.length(i):
            return self.ind[i]+j
        else:
            raise IndexError("Index out of bounds")


    def sorted(self):
        """Returns a sorted Varray.

        Returns a Varray with the same entries but where each
        row is sorted.

        This returns a copy of the data, and leaves the original
        unchanged.

        See also :meth:`sort` for sorting the rows inplace.
        """
        return Varray([sorted(row) for row in self])


    def sort(self):
        """Sort the Varray inplace.

        Sorting a Varray sorts all the elements row by row.
        The sorting is done inplace.

        See also :meth:`sorted` for sorting the rows without
        changing the original.
        """
        [ row.sort() for row in self ]


    def toArray(self):
        """Convert the Varray to a 2D array.

        Returns a 2D array with shape (self.nrows,self.width), containing
        the row data of the Varray.
        Rows which are shorter than width are padded at the start with
        values -1.
        """
        a = -ones((self.nrows, self.width), dtype=Int)
        for i, r in enumerate(self):
            if len(r) > 0:
                a[i, -len(r):] = r
        return a


    def sameLength(self):
        """Groups the rows according to their length.

        Returns a tuple of two lists (lengths,rows):

        - lengths: the sorted unique row lengths,
        - rows: the indidces of the rows having the corresponding length.
        """
        lens = self.lengths
        ulens = unique(lens)
        return ulens,[ where(lens==l)[0] for l in ulens]


    def split(self):
        """Split the Varray into 2D arrays.

        Returns a list of 2D arrays with the same number
        of columns and the indices in the original Varray.
        """
        return [ self.select(ind).toArray() for ind in self.sameLength()[1] ]


    def toList(self):
        """Convert the Varray to a nested list.

        Returns a list of lists of integers.
        """
        return [ r.tolist() for r in self ]


    def inverse(self):
        """Return the inverse of a Varray.

        The inverse of a Varray is again a Varray. Values k on a row i will
        become values i on row k. The number of data in both Varrays is thus
        the same.

        The inverse of the inverse is equal to the original. Two Varrays are
        equal if they have the same number of rows and all rows contain the
        same numbers, independent of their order.

        Example:

        >>> a = Varray([[0,1],[2,0],[1,2],[4]])
        >>> b = a.inverse()
        >>> c = b.inverse()
        >>> print(a,b,c)
        Varray (4,2)
          [0 1]
          [2 0]
          [1 2]
          [4]
         Varray (5,2)
          [0 1]
          [0 2]
          [1 2]
          []
          [3]
         Varray (4,2)
          [0 1]
          [0 2]
          [1 2]
          [4]
        <BLANKLINE>
        """
        return inverseIndex(self)


    def __str__(self):
        """Nicely print the Varray"""
        s = "%s (%s,%s)\n" % (self.__class__.__name__, self.nrows, self.width)
        for row in self:
            s += '  ' + row.__str__() + '\n'
        return s


def inverseIndex(a,sort=False,expand=False):
    """Create the inverse of a 2D index array.

    Parameters:

    - `a`: a Varray or a 2D index array. A 2D index array is a 2D integer
      array where only nonnegative values are significant and negative
      values are silently ignored.
      While in most cases all values in a row are unique, this is not a
      requirement. Degenerate elements may have the same node number
      appearing multiple times in the same row.

    -

    Returns the inverse index, as a Varray (default) or as an ndarray (if
    expand is True). If sort is True, rows are sorted.

    Example:

      >>> a = inverseIndex([[0,1],[0,2],[1,2],[0,3]])
      >>> print(a)
      Varray (4,3)
        [0 1 3]
        [0 2]
        [1 2]
        [3]
      <BLANKLINE>
    """
    if isinstance(a, Varray):
        a = a.toArray()
    a = checkArray(a, ndim=2, kind='i')
    b = resize(arange(a.shape[0]), a.shape[::-1])
    c = stack([a, b.transpose()]).reshape(2, -1)
    s = c[0].argsort()
    t = c[0][s]
    u = c[1][s]
    v = t.searchsorted(arange(t.max()+1))
    if v[0] > 0:
        # There were negative numbers: remove them
        u = u[v[0]:]
        v -= v[0]
    Va = Varray(u, v)
    if sort:
        Va.sort()
    if expand:
        return Va.toArray()
    return Va


# End
