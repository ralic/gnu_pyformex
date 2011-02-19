# $Id$
##
##  This file is part of pyFormex 0.8.3 Release Sun Dec  5 18:01:17 2010
##  pyFormex is a tool for generating, manipulating and transforming 3D
##  geometrical models by sequences of mathematical operations.
##  Homepage: http://pyformex.org   (http://pyformex.berlios.de)
##  Copyright (C) Benedict Verhegghe (benedict.verhegghe@ugent.be) 
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

"""Error and Warning Messages

"""

import pyformex as pf


def getMessage(msg):
    """Return the real message corresponding with the specified mnemonic.

    If no matching message was defined, the original is returned.
    """
    msg = str(msg) # allows for msg being a Warning
    return globals().get(msg,msg)



warn_drawaxes_changed = "The syntax of drawAxes has changed. The use of the 'pos' argument is deprecated. Use an appropriate CoordinateSystem instead."

warn_viewport_switching = """.. warn_viewport_switching

Viewport switching
------------------
The viewport switching functions have changed: interactive changes through the
GUI are now decoupled from changes by the script.
This may result in unwanted effects if your script relied on the old (coupled)
functionality.
"""

warn_viewport_linking = "Linking viewports is an experimental feature and is not fully functional yet."

warn_avoid_sleep = "The sleep function is not yet fully functional and its use should currently be avoided. Use the delay and pause functions, or the drawwait setting instead!"

warn_old_table_dialog = "The use of OldTableDialog is deprecated. Please use a combination of the Dialog, Tabs and Table widgets."

warn_trisurface_getfaces = "TriSurface.getFaces now returns the faces' node numbers. Use TriSurface.getElemEdges() to get the faces' edge numbers."

warn_mesh_select_default_compacted = "Mesh.select now by default compacts the Mesh. Use the `compact=False` argument if you do not want the compaction."

warn_widgets_updatedialogitems = "gui.widgets.updateDialogItems now expects data in the new InputItem format. Use gui.widgets.updateOldDialogItems for use with old data format."

warn_deprecated_inputitem = "Using a list or tuple as InputItem data is deprecated. Please use the new dict format."

# End
