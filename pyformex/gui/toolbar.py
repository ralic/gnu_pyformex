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
"""Toolbars for the pyFormex GUI.

This module defines the functions for creating the pyFormex window toolbars.
"""
from __future__ import absolute_import, division, print_function

import pyformex as pf
from pyformex import utils
from pyformex.gui import QtGui, widgets


################### General Button Functions ###########

def addButton(toolbar,tooltip,icon,func,repeat=False,toggle=False,checked=False,icon0=None,enabled=True):
    """Add a button to a toolbar.

    - `toolbar`: the toolbar where the button will be added
    - `tooltip`: the text to appear as tooltip
    - `icon`: name of the icon to be displayed on the button,
    - `func`: function to be called when the button is pressed,
    - `repeat`: if True, the `func` will repeatedly be called if button is
      held down.
    - `toggle`: if True, the button is a toggle and stays in depressed state
      until pressed again.
    - `checked`: initial state for a toggle buton.
    - `icon1`: for a toggle button, icon to display when button is not checked.
    """
    iconset = QtGui.QIcon()
    icon_on = QtGui.QPixmap(utils.findIcon(icon))
    iconset.addPixmap(icon_on, QtGui.QIcon.Normal, QtGui.QIcon.On)
    if toggle and icon0:
        icon_off = QtGui.QPixmap(utils.findIcon(icon0))
        iconset.addPixmap(icon_off, QtGui.QIcon.Normal, QtGui.QIcon.Off)

    a = toolbar.addAction(iconset, tooltip, func)
    a.setEnabled(enabled)

    b = toolbar.widgetForAction(a)

    if repeat:
        b.setAutoRepeat(True)
        b.setAutoRepeatDelay(500)
        b.clicked.connect(a.trigger)

    if toggle:
        b.setCheckable(True)
        b.clicked.connect(b.toggle)
        b.setChecked(checked)

    b.setToolTip(tooltip)

    return b


def removeButton(toolbar, button):
    """Remove a button from a toolbar."""
    toolbar.removeAction(button)


################### Script action toolbar ###########


def addActionButtons(toolbar):
    """Add the script action buttons to the toolbar."""
    from pyformex.gui import draw
    from pyformex.gui import fileMenu
    action = {}
    avail_buttons = [
        ( "Play", "next", draw.play, False ),
        ( "ReRun", "rerun", draw.replay, False ),
        ## ( "Step", "nextstop", draw.step, False ),
        ( "Continue", "ff", draw.fforward, False ),
        ( "Stop", "stop", draw.raiseExit, False ),
        ( "Edit", "pencil", fileMenu.editApp, False ),
        ( "Info", "info", draw.showDoc, False ),
        ]
    # Filter configured buttons
    show_buttons = pf.cfg['gui/actionbuttons']
    show_buttons = [ b for b in avail_buttons if b[0].lower() in show_buttons ]
    for name, icon, func, enabled in show_buttons:
        action[name] = addButton(toolbar, '', icon, func, enabled=enabled)
    return action


################# Camera action toolbar ###############


def addCameraButtons(toolbar):
    """Add the camera buttons to a toolbar."""
    # The buttons have the following fields:
    #  0 : tooltip
    #  1 : icon
    #  2 : function
    # optional:
    #  3 : REPEAT  (default True)
    from pyformex.gui import cameraMenu
    buttons = [ [ "Rotate left", "rotleft", cameraMenu.rotLeft ],
                [ "Rotate right", "rotright", cameraMenu.rotRight ],
                [ "Rotate up", "rotup", cameraMenu.rotUp ],
                [ "Rotate down", "rotdown", cameraMenu.rotDown ],
                [ "Twist left", "twistleft", cameraMenu.twistLeft ],
                [ "Twist right", "twistright", cameraMenu.twistRight ],
                [ "Translate left", "left", cameraMenu.panLeft ],
                [ "Translate right", "right", cameraMenu.panRight ],
                [ "Translate down", "down", cameraMenu.panDown ],
                [ "Translate up", "up", cameraMenu.panUp ],
                [ "Zoom Out", "zoomout", cameraMenu.dollyOut ],
                [ "Zoom In", "zoomin", cameraMenu.dollyIn ],
                [ "Zoom Rectangle", "zoomrect", cameraMenu.zoomRectangle, False ],
                [ "Zoom All", "zoomall", cameraMenu.zoomAll, False ],
                ]
    for but in buttons:
        icon = widgets.pyformexIcon(but[1])
        a = toolbar.addAction(icon, but[0], but[2])
        b = toolbar.children()[-1] # Get the QToolButton for the last action
        if len(but) < 4 or but[3]:
            b.setAutoRepeat(True)
            b.setAutoRepeatDelay(500)
            b.released.connect(a.trigger)
        if len(but) >= 5:
            b.setCheckable(but[4])
            b.released.connect(a.toggle)

        b.setToolTip(but[0])


#######################################################################
# Viewport Toggle buttons #
###########################


class Toggle(object):
    def __init__(self,state=False):
        self.state = state
    def toggle(self,onoff=None):
        if onoff is None:
            onoff = not self.state
        self.state = onoff



class ViewportToggleButton(object):
    def __init__(self,toolbar,tooltip,icon,func,attr,checked=False,icon0=None):
        self.button = addButton(toolbar, tooltip, icon, func, toggle=True, icon0=icon0)
        self.attr = attr

    def updateButton(self):
        """Update the button to current viewport state."""
        #print "UPDATE TOGGLE %s" % attr
        vp = pf.GUI.viewports.current
        if vp == pf.canvas:
            self.setChecked(vp.settings[self.attr])
        pf.GUI.processEvents()

    def toggle(self,attr,state=None):
        """Update the corresponding viewport attribute.

        This does not update the button state.
        """
        vp = pf.GUI.viewports.current
        vp.setToggle(attr, state)
        vp.update()
        pf.GUI.processEvents()


def toggleButton(attr,state=None):
    """Update the corresponding viewport attribute.

    This does not update the button state.
    """
    vp = pf.GUI.viewports.current
    vp.setToggle(attr, state)
    vp.update()
    pf.GUI.processEvents()

def updateButton(button, attr):
    """Update the button to correct state."""
    if button:
        vp = pf.GUI.viewports.current
        button.setChecked(vp.settings[attr])
        pf.GUI.processEvents()


def updateViewportButtons(vp):
    ## if vp != pf.GUI.viewports.current:
    ##     print "viewport %s is not current" % pf.GUI.viewports.viewIndex(vp)
    if vp.focus:
        #print "viewport %s has focus" % pf.GUI.viewports.viewIndex(vp)
        updateWireButton()
        updateTransparencyButton()
        updateLightButton()
        updateNormalsButton()


#
# BEWARE: The toggle functions are currently not passed the state!
#         It should be got from
#

################# Wire Button ###############

wire_button = None # the toggle wire button

def addWireButton(toolbar):
    global wire_button
    wire_button = addButton(toolbar, 'Toggle Wire Mode',
                            'wireall', toggleWire, icon0='wirenone',
                            toggle=True)

def toggleWire(state=None):
    vp = pf.GUI.viewports.current
    state = wire_button.isChecked()
    # TODO:
    # WELL, it looks like we get here BEFORE the button is updated,
    # so we need to change the state.
    # WE should really connect this to a signal that is raised
    # AFTER the button state is update
    state = not state
    vp.setWireMode(state)
    vp.update()
    pf.GUI.processEvents()


def updateWireButton():
    """Update the wire button to correct state."""
    if wire_button:
        vp = pf.GUI.viewports.current
        wire_button.setChecked(vp.settings['wiremode'] > 0)
        pf.GUI.processEvents()


################# Transparency Button ###############

transparency_button = None # the toggle transparency button

def addTransparencyButton(toolbar):
    global transparency_button
    transparency_button = addButton(toolbar, 'Toggle Transparent Mode',
                                    'transparent', toggleTransparency,
                                    toggle=True)

def toggleTransparency(state=None):
    toggleButton('alphablend', state)

def updateTransparencyButton():
    """Update the transparency button to correct state."""
    updateButton(transparency_button, 'alphablend')


################# Lights Button ###############

light_button = None

def addLightButton(toolbar):
    global light_button
    light_button = addButton(toolbar, 'Toggle Lights',
                             'lamp-on', toggleLight, icon0='lamp',
                             toggle=True, checked=True)

def toggleLight(state=None):
    toggleButton('lighting', state)

def updateLightButton():
    """Update the light button to correct state."""
    updateButton(light_button, 'lighting')


################# Normals Button ###############

normals_button = None

def addNormalsButton(toolbar):
    global normals_button
    normals_button = addButton(toolbar, 'Toggle Normals',
                               'normals-avg', toggleNormals, icon0='normals-ind',
                               toggle=True, checked=False)

def toggleNormals(state=None):
    toggleButton('avgnormals', state)

def updateNormalsButton(state=True):
    """Update the normals button to correct state."""
    updateButton(normals_button, 'avgnormals')


################# Perspective Button ###############

perspective_button = None # the toggle perspective button

def togglePerspective(mode=None): # Called by the button, not by user
    vp = pf.GUI.viewports.current
    if mode is None:
        mode = not vp.camera.perspective
    vp.camera.setPerspective(mode)
    vp.display()
    vp.update()
    pf.GUI.processEvents()

def addPerspectiveButton(toolbar):
    global perspective_button
    perspective_button = addButton(toolbar, 'Toggle Perspective/Projective Mode',
                                   'perspect', togglePerspective,
                                   toggle=True, icon0='project', checked=True)

def updatePerspectiveButton():
    """Update the normals button to correct state."""
    #updateButton(perspective_button,'avgnormals')
    vp = pf.GUI.viewports.current
    if vp == pf.canvas:
        perspective_button.setChecked(vp.camera.perspective)
    pf.GUI.processEvents()

def setPerspective():
    togglePerspective(True)
    updatePerspectiveButton()

def setProjection():
    togglePerspective(False)
    updatePerspectiveButton()

################# Shrink Button ###############

#
# The shrink button currently does not redraw, it only sets the default
# shrink factor and clears the viewport
#
shrink_button = None # the toggle shrink button

def toggleShrink(): # Called by the button
    from pyformex.gui import draw
    mode = draw.DrawOptions.get('shrink', None)
    if mode is None:
        mode = 0.8
    else:
        mode = None
    draw.shrink(mode)

def addShrinkButton(toolbar):
    global shrink_button
    shrink_button = addButton(toolbar, 'Toggle Shrink Mode',
                              'shrink', toggleShrink,
                              toggle=True)

def setShrink(mode):
    from pyformex.gui import draw
    draw.shrink(mode)
    if shrink_button:
        shrink_button.setChecked(mode != None)

################# Timeout Button ###############

timeout_button = None # the timeout toggle button

def toggleTimeout(onoff=None):
    if onoff is None:
        onoff = widgets.input_timeout < 0
    if onoff:
        timeout = pf.cfg.get('gui/timeoutvalue', -1)
    else:
        timeout = -1

    widgets.setInputTimeout(timeout)
    onoff = widgets.input_timeout > 0
    if onoff:
        # THIS SUSPENDS ALL WAITING! WE SHOULD IMPLEMENT A TIMEOUT!
        # BY FORCING ALL INDEFINITE PAUSES TO A WAIT TIME EQUAL TO
        # WIDGET INPUT TIMEOUT
        pf.debug("FREEING the draw lock")
        pf.GUI.drawlock.free()
    else:
        pf.debug("ALLOWING the draw lock")
        pf.GUI.drawlock.allow()
    return onoff


def addTimeoutButton(toolbar):
    """Add or remove the timeout button,depending on cfg."""
    global timeout_button
    if pf.cfg['gui/timeoutbutton']:
        if timeout_button is None:
            timeout_button = addButton(toolbar, 'Toggle Timeout', 'clock', toggleTimeout, toggle=True, checked=False)
    else:
        if timeout_button is not None:
            removeButton(toolbar, timeout_button)
            timeout_button = None


def timeout(onoff=None):
    """Programmatically toggle the timeout button"""
    if timeout_button is not None:
        timeout_button.setChecked(toggleTimeout(onoff))



# End
