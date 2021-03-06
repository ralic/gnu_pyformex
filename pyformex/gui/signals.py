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
"""signals.py: Definition of our own signals used in the GUI communication.

Signals are treated by the normal QT4 machine. They can be emitted from
anywhere, causing attached functions to be executed.
"""
from __future__ import absolute_import, division, print_function


from pyformex.gui import QtCore
from pyformex.gui import Signal

# These have to disappear
SIGNAL = QtCore.SIGNAL

# signals
CANCEL = SIGNAL("Cancel")   # cancel the operation, undoing it
DONE   = SIGNAL("Done")     # accept and finish the operation
TIMEOUT = SIGNAL("Timeout") # terminate what was going on



class Signals(QtCore.QObject):
    """A class with all custom signals in pyFormex.

    Custom signals are instances of the gui.Signal function, and should
    be defined inside a class derived from QtCore.QObject.

    The following signals are currently defined:

    - CANCEL: cancel the operation, undoing it
    - DONE: accept and finish the operation
    - REDRAW: redraw a preview state
    - WAKEUP: wake up from a sleep state
    - TIMEOUT: terminate what was going on
    - SAVE: save current rendering
    - FULLSCREEN: toggle fullscreen mode
    """
    CANCEL = Signal()
    DONE   = Signal()
    REDRAW = Signal()
    WAKEUP = Signal()
    TIMEOUT = Signal()
    SAVE = Signal()
    FULLSCREEN = Signal()



# End
