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
"""A collection of custom widgets used in the pyFormex GUI

The widgets in this module were primarily created in function of the
pyFormex GUI. The user can apply them to change the GUI or to add
interactive widgets to his scripts. Of course he can also use all the
Qt widgets directly.
"""
from __future__ import absolute_import, division, print_function

import os

import pyformex as pf
from pyformex import mydict, olist
from pyformex import utils
from pyformex import arraytools as at
from pyformex.gui import QtCore, QtGui
from pyformex.opengl import colors
from pyformex import zip
from pyformex.odict import OrderedDict


# timeout value for all widgets providing timeout feature
#  (currently: InputDialog, MessageBox)

input_timeout = -1  # default timeout value : -1 means no timeout

def setInputTimeout(timeout):
    global input_timeout
    input_timeout = timeout


# result values for dialogs
ACCEPTED = QtGui.QDialog.Accepted
REJECTED = QtGui.QDialog.Rejected
TIMEOUT = -1        # the return value if a widget timed out

## # slots
## Accept = QtCore.SLOT("accept()")
## Reject = QtCore.SLOT("reject()")

# QT List selection mode
selection_mode = {
    None: QtGui.QAbstractItemView.NoSelection,
    'single': QtGui.QAbstractItemView.SingleSelection,
    'multi': QtGui.QAbstractItemView.MultiSelection,
    'contiguous': QtGui.QAbstractItemView.ContiguousSelection,
    'extended': QtGui.QAbstractItemView.ExtendedSelection,
    'checked': QtGui.QAbstractItemView.SingleSelection,
    }

# icons
def standardIcon(label):
    try:
        icon = ['noicon', 'info', 'warning', 'error', 'question'].index(label)
        return QtGui.QMessageBox.standardIcon(icon)
    except:
        return label


def pyformexIcon(icon):
    """Create a pyFormex icon.

    Returns a QIcon with an image taken from the pyFormex icons
    directory. `icon` is the basename of the image file (.xpm or .png).
    """
    return QtGui.QIcon(QtGui.QPixmap(utils.findIcon(icon)))


def objSize(object):
    """Return the width and height of an object.

    Returns a tuple w,h for any object that has width and height methods.
    """
    return object.width(), object.height()


def maxWinSize():
    """Return the maximum widget size.

    The maximum widget size is the maximum size for a window on the screen.
    The available size may be smaller than the physical screen size (e.g.
    it may exclude the space for docking panels).
    """
    return objSize(pf.app.desktop().availableGeometry())


def addTimeOut(widget,timeout=None,timeoutfunc=None):
    """Add a timeout to a widget.

    - `timeoutfunc` is a callable. If None it will be set to the widget's
      `timeout` method if one exists.
    - `timeout` is a float value. If None, it will be set to to the global
      `input_timeout`.

    If timeout is positive, a timer will be installed into the widget which
    will call the `timeoutfunc` after `timeout` seconds have elapsed.
    The `timeoutfunc` can be any callable, but usually will emit a signal
    to make the widget accept or reject the input. The timeoutfunc will not
    be called is if the widget is destructed before the timer has finished.
    """
    if timeout is None:
        timeout = input_timeout
    if timeoutfunc is None and hasattr(widget, 'timeout'):
        timeoutfunc = widget.timeout

    try:
        timeout = float(timeout)
        if timeout >= 0.0:
            pf.debug("ADDING TIMEOUT %s,%s" % (timeout, timeoutfunc))
            timer = QtCore.QTimer()
            timer.timeout.connect(timeoutfunc)
            timer.setSingleShot(True)
            timeout = int(1000*timeout)
            timer.start(timeout)
            widget.timer = timer  # make sure this timer stays alive
            pf.debug("TIMER STARTED")
    except:
        raise
        #raise ValueError("Could not start the timeout timer"


def setExpanding(w):
    freePol = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
    w.setSizePolicy(freePol)
    w.adjustSize()

def hspacer():
    spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum )
    return spacer


#####################################################################
########### General Input Dialog ####################################
#####################################################################


class InputItem(QtGui.QWidget):
    """A single input item.

    This is the base class for widgets holding a single input item.
    A single input item is any item that is treated as a unit and
    refered to by a single name.

    This base class is rarely used directly. Most of the components
    of an InputDialog are subclasses of hereof, each specialized in
    some form of input data or representation. There is e.g. an
    InputInteger class to input an integer number and an InputString
    for the input of a string.
    The base class groups the functionality that is common to the
    different input widgets.

    The InputItem widget holds a horizontal layout box (QHBoxLayout)
    to group its its components. In most cases there are just two components:
    a label with the name of the field, and the actual input field.
    Other components, such as buttons or sliders, may be added. This is
    often done in subclasses.

    The constructor has one required argument: `name`. Other
    (optional) positional parameters are passed to the QtGui.QWidget
    constructor. The remaining keyword parameters are options that
    somehow change the default behavior of the InputItem class.

    Parameters:

    - `name`: the name used to identify the item. It should be unique for
      all InputItems in the same InputDialog. It will be used as a key in
      the dictionary that returns all the input values in the dialog. It will
      also be used as the label to display in front of the input field, in
      case no `text` value was specified.
    - `text`: if specified, this text will be displayed in the label in front
      of the input field. This allows for showing descriptive texts for the
      input fields in the dialog, while keeping short and simple names for
      the items in the programming.
      `text` can be set to an empty string to suppress the creation of a label
      in front of the input field. This is useful if the input field
      widget itself already provides a label (see e.g. InputBool).
      `text` can also be a QtGui.QPixmap, allowing for icons to be used
      as labels.
    - `buttons`: a list of (label,function) tuples. For each tuple a button
      will be added after the input field. The button displays the text and
      when pressed, the specified function will be executed. The function
      takes no arguments.
    - `data`: any extra data that you want to be stored into the widget.
      These data are not displayed, but can be useful in the functioning of
      the widget.
    - `enabled`: boolean. If False, the InputItem will not be enabled, meaning
      that the user can not enter any values there. Disabled fields are usually
      displayed in a greyed-out fashion.
    - `readonly`: boolean. If True, the data are read-only and can not be
      changed by the user. Unlike disabled items, they are displayed in a
      normal fashion.
    - `tooltip`: A descriptive text which is only shown when the user pauses
      the cursor for some time on the widget. It can be used to give
      more comprehensive explanation to first time users.
    - `spacer`: string. Only the characters 'l', 'r' and 'c' are relevant.
      If the string contains an 'l', a spacer in inserted before the label.
      If the string contains an 'r', a spacer in inserted after the input field.
      If the string contains a 'c', a spacer in inserted between the label and
      the input filed.

    Subclasses should have an ``__init__()`` method which first constructs
    a proper widget for the input field, and stores it in the attribute
    ``self.input``. Then the baseclass should be properly initialized, passing
    any optional parameters::

      self.input = SomeInputWidget()
      InputItem.__init__(self,name,*args,**kargs)

    Subclasses should also override the following default methods of
    the InputItem base class:

    - text(): if the subclass calls the superclass __init__() method with
      a value ``text=''``. This method should return the value of the
      displayed text.
    - value(): if the value of the input field is not given by
      ``self.input.text()``, i.e. in most cases. This method should
      return the value of the input field.
    - setValue(val): always, unless the field is readonly. This method should
      change the value of the input widget to the specified value.

    Subclasses are allowed to NOT have a ``self.input`` attribute, IFF they
    redefine both the value() and the setValue() methods.

    Subclasses can set validators on the input, like::

      self.input.setValidator(QtGui.QIntValidator(self.input))

    Subclasses can define a show() method e.g. to select the data in the
    input field on display of the dialog.
    """

    def __init__(self,name,*args,**kargs):
        """Create a widget with a horizontal box layout"""
        QtGui.QWidget.__init__(self,*args)
        #addStyle(self,bgcolor='red')
        layout = QtGui.QHBoxLayout()
        #if not pf.options.pyside:
            # PySide does not have this setMargin
        #layout.setMargin(0)
        s = pf.cfg['gui/spacing']
        layout.setContentsMargins(s, s, s, s)
        self.setLayout(layout)
        spacer = kargs.get('spacer', '')
        if 'l' in spacer:
            layout.addStretch()

        self.key = str(name)
        if 'text' in kargs:
            text = kargs['text']
        else:
            text = self.key
        if text:
            self.label = QtGui.QLabel()
            #text = standardIcon(text)
            if isinstance(text, QtGui.QPixmap):
                self.label.setPixmap(text)
            else:
                self.label.setText(text)
            ## if 'b' in kargs.get('stretch',''):
            ##     layout.addStretch()
            layout.addWidget(self.label)
            ## if 'a' in kargs.get('stretch',''):
            ##     print('test')
            ##     layout.addStretch()
            if 'c' in spacer:
                layout.addStretch()


        if 'data' in kargs:
            self.data = kargs['data']

        if 'enabled' in kargs:
            self.setEnabled(kargs['enabled'])

        if 'readonly' in kargs:
            try:
                self.input.setReadOnly(kargs['readonly'])
            except:
                print("Can not set readonly: %s,%s" % (name, kargs))

        if 'width' in kargs:
            try:
                print('SETTING WIDTH', self.input)
                self.input.setMinimumWidth(kargs['width'])
            except:
                pass

        if 'tooltip' in kargs:
            self.setToolTip(kargs['tooltip'])

        ##     if hasattr(self,'label'):
        ##         self.label.setToolTip(kargs['tooltip'])
        ## try:
        ##     self.input.setToolTip(kargs['tooltip'])
        ## except:
        ##     pass

        if 'buttons' in kargs and kargs['buttons']:
            self.buttons = ButtonBox(actions=kargs['buttons'], parent=self)
            layout.addWidget(self.buttons)

        if 'r' in spacer:
            layout.addStretch()


    def name(self):
        """Return the name of the InputItem."""
        return self.key

    def text(self):
        """Return the displayed text of the InputItem."""
        if hasattr(self, 'label'):
            return str(self.label.text())
        else:
            return self.key

    def value(self):
        """Return the widget's value."""
        return str(self.input.text())

    def setValue(self, val):
        """Change the widget's value."""
        self.input.setText(str(val))


class InputInfo(InputItem):
    """An unchangeable input field with a label in front.

    It is just like an InputString, but the text can not be edited.
    The value should be a simple string without newlines.

    There are no specific options.
    """
    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        self.input = QtGui.QLineEdit(str(value))
        self.input.setReadOnly(True)
        InputItem.__init__(self,name,*args,**kargs)
        self._value_ = value
        if self._value_ is not None:
            self.layout().insertWidget(1, self.input)

    def value(self):
        """Return the widget's value."""
        return self._value_


class InputLabel(InputItem):
    """An unchangeable information field.

    The value is displayed as a string, but may contain more complex texts.

    By default, the text format will be guessed to be either plain text,
    ReStructuredText ot html. Specify plain=True to display in plain text.
    """
    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        self._plain = kargs.get('plain', False)
        self.input =  QtGui.QLabel()
        #maxw,maxh = self.maxSize()
        #self.input.setMaximumSize(0.6*maxw,0.6*maxh)
        #self.input.setMinimumSize(0.2*maxw,0.2*maxh)
        setExpanding(self.input)
        InputItem.__init__(self,name,*args,**kargs)
        self.setValue(value)
        self.layout().insertWidget(1, self.input)
 #       self.setSize()

    def setValue(self, val):
        """Change the widget's value."""
        val = str(val)
        if self._plain:
            self.input.setText(val)
            self.input.setWordWrap(False)
        else:
            updateText(self.input, val)
            self.input.setWordWrap(True)


##     def layoutMinimumWidth(self):
## #        self.input.activate()
##         return self.totalMinimumSize().width()


##     def setSize(self):
##         maxw,maxh = maxSize()
##         maxw -= 40

##         self.input.setWordWrap(False) # makes the label return min size
##         width = self.layoutMinimumWidth()
##         #print "min size: %s" % width
##         self.input.setWordWrap(True)


class InputString(InputItem):
    """A string input field with a label in front.

    If the type of value is not a string, the input string
    will be eval'ed before returning.

    Options:

    - `max`: the maximum number of characters in the string.
    """
    def __init__(self,name,value,max=None,*args,**kargs):
        """Initialize the input item."""
        self.input = QtGui.QLineEdit(str(value))
        InputItem.__init__(self,name,*args,**kargs)
        if isinstance(max, int) and max > 0:
            self.input.setMaxLength(max)
        self._is_string_ = isinstance(value, str)
        self.layout().insertWidget(1, self.input)

    def show(self, *args):
        """Select all text on first display."""
        InputItem.show(self, *args)
        self.input.selectAll()

    def value(self):
        """Return the widget's value."""
        s = str(self.input.text())
        if self._is_string_:
            return s
        else:
            return eval(s)


class InputText(InputItem):
    """A scrollable text input field with a label in front.

    By default, the text format will be guessed to be either plain text,
    ReStructuredText ot html.

    Specify plain=True to display in plain text.

    If the type of value is not a string, the input text will be eval'ed
    before returning.
    """
    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        self._is_string_ = isinstance(value, str)
        self._plain = kargs.get('plain', False)
        self.input =  QtGui.QTextEdit()
#        maxw,maxh = maxSize()
#        self.input.setMaximumSize(0.6*maxw,0.6*maxh)
#        self.input.setMinimumSize(0.2*maxw,0.2*maxh)
        setExpanding(self.input)
        InputItem.__init__(self,name,*args,**kargs)
        self.setValue(value)
        self.layout().insertWidget(1, self.input)
        if 'font' in kargs:
            try:
                self.setFont(QtGui.QFont(kargs['font']))
            except:
                pass
        if 'size' in kargs:
            self._size = kargs['size']


    def sizeHint(self):
        if hasattr(self, '_size'):
            width, height = self._size
            docsize = self.input.document().size().toSize()
            #print "docsize = %s" % docsize
            font = self.input.font()
            if width < 0:
                #print "Pixelsize = %s" % font.pixelSize()
                #print "Pointsize = %s" % font.pointSize()
                width = max(80 * font.pixelSize(), 50* font.pointSize())
                #width = docsize.width() + (self.input.width() - self.input.viewport().width())
            if height < 0:
                height = docsize.height() + (self.input.height() - self.input.viewport().height())
                height = max(height, 0.75*width)
            size = QtCore.QSize(width, height)
            #print "newsize = %s" % size
        else:
            size = QtGui.QTextEdit.sizeHint(self.input)

        return size


    def show(self,*args):
        """Select all text on first display."""
        InputItem.show(self,*args)
        self.input.selectAll()

    def value(self):
        """Return the widget's value."""
        s = str(self.input.toPlainText())
        if self._is_string_:
            return s
        else:
            return eval(s)

    def setValue(self, val):
        """Change the widget's value."""
        val = str(val)
        if self._plain:
            self.input.setPlainText(val)
            ## self.input.setLineWrapMode(QtGui.QTextEdit.FixedColumnWidth)
            ## self.input.setLineWrapColumnOrWidth(200)
        else:
            updateText(self.input, val)
            ## self.input.setLineWrapMode(QtGui.QTextEdit.FixedPixelWidth)
            ## self.input.setLineWrapColumnOrWidth(600)
        self.input.adjustSize()


class InputBool(InputItem):
    """A boolean input item.

    Creates a new checkbox for the input of a boolean value.

    Displays the name next to a checkbox, which will initially be set
    if value evaluates to True. (Does not use the label)
    The value is either True or False,depending on the setting
    of the checkbox.

    Options:

    - `func`: an optional function to be called whenever the value is
      changed. The function receives the input field as argument. With
      this argument, the fields attributes like name, value, text, can
      be retrieved.
    """

    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        if 'text' in kargs:
            text = kargs['text']
        else:
            text = str(name)
        kargs['text'] = '' # Force no label
        self.input = QtGui.QCheckBox(text)
        InputItem.__init__(self,name,*args,**kargs)
        self.setValue(value)
        self.layout().insertWidget(1, self.input)
        self.func = kargs.get('func', None)
        if 'func' in kargs:
            self.input.stateChanged.connect(self.on_value_change)

    def text(self):
        """Return the displayed text."""
        return str(self.input.text())

    def value(self):
        """Return the widget's value."""
        return self.input.checkState() == QtCore.Qt.Checked

    def setValue(self, val):
        """Change the widget's value."""
        if val:
            self.input.setCheckState(QtCore.Qt.Checked)
        else:
            self.input.setCheckState(QtCore.Qt.Unchecked)

    def on_value_change(self, val):
        if self.func:
            self.func(self)


class InputList(InputItem):
    """A list selection InputItem.

    A list selection is a widget allowing the selection of zero, one or more
    items from a list.

    choices is a list/tuple of possible values.
    default is the initial/default list of selected items.
    Values in default that are not in the choices list, are ignored.
    If default is None or an empty list, nothing is selected initially.

    By default, the user can select multiple items and the return value is
    a list of all currently selected items.
    If single is True, only a single item can be selected.

    If maxh==-1, the widget gets a fixed height to precisely take the number of
    items in the list. If maxh>=0, the widget will get scrollbars when the
    height is not sufficient to show all items. With maxh>0, the item will
    get the specified height (in pixels), while maxh==0 will try to give the
    widget the required height to show all items

    If check is True, all items have a checkbox and only the checked items
    are returned. This option sets single==False.
    """

    def __init__(self,name,default=[],choices=[],sort=False,single=False,check=False,fast_sel=False,maxh=-1,*args,**kargs):
        """Initialize the input item."""
        if len(choices) == 0:
            raise ValueError("List input expected choices!")
        self._choices_ = [ str(s) for s in choices ]
        self.input = ListWidget(maxh=maxh)

        if fast_sel:
            but = [('Select All', self.setAll), ('Deselect All', self.setNone)]
            if 'buttons' in kargs and kargs['buttons']:
                kargs['buttons'].extend(but)
            else:
                kargs['buttons'] = but
        InputItem.__init__(self,name,*args,**kargs)
        self.input.addItems(self._choices_)
        if sort:
            self.input.sortItems()

        mode = 'extended'
        self._check_ = check
        if check:
            mode = None
            single = False
        if single:
            mode = 'single'

        self.input.setSelectionMode(selection_mode[mode])
        self.setValue(default)

        self.input.setSize()
        if maxh > -1:
            #self.input.updateGeometry()
            self.scroll = QtGui.QScrollArea()
            if maxh > 0:
                self.scroll.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding)
            else:
                self.scroll.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
            self.scroll.setBackgroundRole(QtGui.QPalette.Dark)
            self.scroll.setWidgetResizable(False)
            self.scroll.setWidget(self.input)
            self.layout().insertWidget(1, self.scroll)
        else:
            self.input.updateGeometry()
            self.layout().insertWidget(1, self.input)

        self.updateGeometry()
        #self.input.setSizeHint(QtCore.QSize(self.input.width(),10))

    def setSelected(self,selected,flag=True):
        """Mark the specified items as selected or not."""
        for s in selected:
            for i in self.input.findItems(s, QtCore.Qt.MatchExactly):
                i.setSelected(flag)

    def setChecked(self,selected,flag=True):
        """Mark the specified items as checked or not."""
        if flag:
            qtflag = QtCore.Qt.Checked
        else:
            qtflag = QtCore.Qt.Unchecked

        for s in selected:
            for i in self.input.findItems(s, QtCore.Qt.MatchExactly):
                i.setCheckState(qtflag)

    def getSelected(self):
        return [str(i.text()) for i in self.input.selectedItems()]

    def getChecked(self):
        return [str(i.text()) for i in self.input.allItems() if i.checkState()==QtCore.Qt.Checked ]

    def value(self):
        """Return the widget's value."""
        if self._check_:
            f = self.getChecked
        else:
            f = self.getSelected
        return f()

    def setValue(self, val):
        """Change the widget's value."""
        if self._check_:
            f = self.setChecked
        else:
            f = self.setSelected
        f(val, True)
        f(olist.difference(self._choices_, val), False)

    def setAll(self):
        """Mark all items as selected/checked."""
        self.setValue(self._choices_)

    def setNone(self):
        """Mark all items as not selected/checked."""
        self.setValue([])


class InputCombo(InputItem):
    """A combobox InputItem.

    A combobox is a widget allowing the selection of an item from a drop
    down list.

    choices is a list/tuple of possible values.
    value is the initial/default choice.
    If value is not in the choices list, it is prepended.

    The choices are presented to the user as a combobox, which will
    initially be set to the default value.

    An optional `onselect` function may be specified, which will be called
    whenever the current selection changes. The function is passed the
    selected option string
    """

    def __init__(self,name,value,choices=[],onselect=None,func=None,*args,**kargs):
        """Initialize the input item."""
        if len(choices) == 0:
            raise ValueError("Selection expected choices!")
        if value is None:
            value = choices[0]
        if value not in choices:
            choices[0:0] = [ value ]
        self.input = QtGui.QComboBox()
        InputItem.__init__(self,name,*args,**kargs)
        self._choices_ = []
        self.setChoices(choices)
        if callable(onselect):
            # BEWARE: onselect now returns index of selection instead of string
            self.input.currentIndexChanged['QString'].connect(onselect)
        self.setValue(value)
        self.layout().insertWidget(1, self.input)

    def value(self):
        """Return the widget's value."""
        return str(self.input.currentText())

    def setValue(self, val):
        """Change the widget's current value."""
        val = str(val)
        if val in self._choices_:
            self.input.setCurrentIndex(self._choices_.index(val))

    def setChoices(self, choices):
        """Change the widget's choices.

        This also sets the current value to the first in the list.
        """
        # First remove old choices, if any
        while self.input.count() > 0:
            self.input.removeItem(0)
        # Set new ones
        self._choices_ = [ str(s) for s in choices ]
        self.input.addItems(self._choices_)

    def setIndex(self, i):
        self.input.setCurrentIndex(i)


class InputRadio(InputItem):
    """A radiobuttons InputItem.

    Radio buttons are a set of buttons used to select a value from a list.

    choices is a list/tuple of possible values.
    value is the initial/default choice.
    If value is not in the choices list, it is prepended.
    If value is None, the first item of choices is taken as the default.

    The choices are presented to the user as a hbox with radio buttons,
    of which the default will initially be pressed.
    If direction == 'v', the options are in a vbox.
    """

    def __init__(self,name,value,choices=[],direction='h',*args,**kargs):
        """Initialize the input item."""
        if value is None:
            value = choices[0]
        elif value not in choices:
            choices[0:0] = [ value ]
        self.input = QtGui.QGroupBox()
        InputItem.__init__(self,name,*args,**kargs)
        if direction == 'v':
            self.hbox = QtGui.QVBoxLayout()
            self.hbox.setContentsMargins(0, 10, 0, 10)
        else:
            self.hbox = QtGui.QHBoxLayout()
            self.hbox.setContentsMargins(10, 0, 10, 0)
        self.rb = []
        self.hbox.addStretch(1)

        for v in choices:
            rb = QtGui.QRadioButton(v)
            self.hbox.addWidget(rb)
            self.rb.append(rb)

        self.rb[choices.index(value)].setChecked(True)
        self.input.setLayout(self.hbox)
        self.layout().insertWidget(1, self.input)

    def value(self):
        """Return the widget's value."""
        for rb in self.rb:
            if rb.isChecked():
                return str(rb.text())
        return ''

    def setValue(self, val):
        """Change the widget's value."""
        val = str(val)
        for rb in self.rb:
            if rb.text() == val:
                rb.setChecked(True)
                break


#
# TODO: THIS SHOULD BE MERGED WITH ButtonBox
#
class InputPush(InputItem):
    """A pushbuttons InputItem.

    Creates pushbuttons for the selection of a value from a list.

    choices is a list/tuple of possible values.
    value is the initial/default choice.
    If value is not in the choices list, it is prepended.
    If value is None, the first item of choices is taken as the default.

    The choices are presented to the user as a hbox with push buttons,
    of which the default will initially be selected.
    If direction == 'v', the options are in a vbox.

    Extra parameters:

    - `func`: the function to call when the button is clicked. The function
      receives the input field as argument. From this argument, the fields
      attributes like name, value, text, can be retrieved.
      The function should return the value to be set, or None if it is to be
      unchanged. If no function is specified, the value can not be changed.

    """

    def __init__(self,name,value=None,choices=[],direction='h',count=0,icon=None,iconsonly=False,func=None,*args,**kargs):
        """Initialize the input item."""
        if value is None:
            value = choices[0]
        elif value not in choices:
            choices[0:0] = [ value ]
        self.input = QtGui.QGroupBox()
        self.input.setStyleSheet("QGroupBox { border: 0px;}")
        InputItem.__init__(self,name,*args,**kargs)
        self.input.setFlat(True)
        if direction == 'v' and count <= 0:
            self.hbox = QtGui.QVBoxLayout()
            self.hbox.setContentsMargins(0, 10, 0, 10)
        elif direction == 'h' and count <= 0:
            self.hbox = QtGui.QHBoxLayout()
            self.hbox.setContentsMargins(5, 0, 5, 0)
        else:
            self.hbox = QtGui.QGridLayout()

        self.hbox.setSpacing(0)
        self.func = func

        self.bg = QtGui.QButtonGroup()
        for i, v in enumerate(choices):
            if icon and iconsonly:
                b = QtGui.QToolButton()
                b.setContentsMargins(0, 0, 0, 0)
                b.setStyleSheet("* { margin: 0px; padding: 0px; }")
                b.setText(v)
                b.setIcon(pyformexIcon(icon[i]))
                b.setUsesTextLabel(False)
            else:
                b = QtGui.QPushButton(v)
                if icon:
                    b.setIcon(pyformexIcon(icon[i]))

            if self.func:
                b.clicked.connect(self.doFunc)

            b.setCheckable(True)
            if v == value:
                b.setChecked(True)
            self.bg.addButton(b, i)
            if count <= 0:
                self.hbox.addWidget(b)
            else:
                r,c = divmod(i,count)
                self.hbox.addWidget(b,r,c)

        self.input.setLayout(self.hbox)
        self.layout().insertWidget(1, self.input)

    def setText(self,text,index=0):
        """Change the text on button index."""
        self.bg.button(index).setText(text)

    def setIcon(self,icon,index=0):
        """Change the icon on button index."""
        self.bg.button(index).setIcon(pyformexIcon(icon))

    def value(self):
        """Return the widget's value."""
        return str(self.bg.checkedButton().text())

    def setValue(self, val):
        """Change the widget's value."""
        val = str(val)
        for b in self.bg.buttons():
            b.setChecked(b.text() == val)

    def doFunc(self):
        """Set the value by calling the button's func"""
        self.func(self)


class InputInteger(InputItem):
    """An integer input item.

    Options:

    - `min`, `max`: range of the scale (integer)
    """

    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        self.input = QtGui.QLineEdit(str(value))
        InputItem.__init__(self,name,*args,**kargs)
        self.validator = QtGui.QIntValidator(self)
        if 'min' in kargs:
            self.validator.setBottom(int(kargs['min']))
        if 'max' in kargs:
            self.validator.setTop(int(kargs['max']))
        self.input.setValidator(self.validator)
        self.layout().insertWidget(1, self.input)

    def show(self):
        """Select all text on first display."""
        InputItem.show(self)
        self.input.selectAll()

    def value(self):
        """Return the widget's value."""
        return int(self.input.text())

    def setValue(self, val):
        """Change the widget's value."""
        val = int(val)
        self.input.setText(str(val))


class InputFloat(InputItem):
    """A float input item."""

    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        self.input = QtGui.QLineEdit(str(value))
        InputItem.__init__(self,name,*args,**kargs)
        self.validator = QtGui.QDoubleValidator(self)
        if 'min' in kargs:
            self.validator.setBottom(float(kargs['min']))
        if 'max' in kargs:
            self.validator.setTop(float(kargs['max']))
        if 'dec' in kargs:
            self.validator.setDecimals(int(kargs['dec']))
        self.input.setValidator(self.validator)
        self.layout().insertWidget(1, self.input)

    def show(self):
        """Select all text on first display."""
        InputItem.show(self)
        self.input.selectAll()

    def value(self):
        """Return the widget's value."""
        return float(self.input.text())

    def setValue(self, val):
        """Change the widget's value."""
        val = float(val)
        self.input.setText(str(val))


class InputTable(InputItem):
    """An input item for tabular data.

    - `value`: a 2-D array of items, with `nrow` rows and `ncol` columns.

      If `value` is an numpy array, the Table will use the ArrayModel:
      editing the data will directly change the input data array; all
      items are of the same type; the size of the table can not be changed.

      Else a TableModel is used. Rows and columns can be added to or removed
      from the table. Item type can be set per row or per column or for the
      whole table.
    - `autowidth`:
    - additionally, all keyword parameters of the TableModel or ArrayModel
      may be passed
    """

    def __init__(self,name,value,chead=None,rhead=None,celltype=None,rowtype=None,coltype=None,edit=True,resize=None,autowidth=True,*args,**kargs):
        """Initialize the input item."""
        self.input = Table(value, chead=chead, rhead=rhead, celltype=celltype, rowtype=rowtype, coltype=coltype, edit=edit, resize=resize, autowidth=autowidth)
        InputItem.__init__(self,name,*args,**kargs)
        self.layout().addWidget(self.input)


    def value(self):
        """Return the widget's value."""
        return self.input.value()

    # TODO: need to implement
    ## def setValue(self,val):
    ##     """Change the widget's value."""
    ##     self.input.setText(str(val))



class InputSlider(InputInteger):
    """An integer input item using a slider.

    Options:

    - `min`, `max`: range of the scale (integer)
    - `ticks`: step for the tick marks (default range length / 10)
    - `func`: an optional function to be called whenever the value is
      changed. The function receives the input field as argument. With
      this argument, the fields attributes like name, value, text, can
      be retrieved.
    - `tracking`: bool. If True (default), `func` is called repeatedly
      while the slider is being dragged. If False, `func` is only called
      when the user releases the slider.
    """

    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        InputInteger.__init__(self,name,value,*args,**kargs)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.func = kargs.get('func', None)

        vmin = kargs.get('min', 0)
        vmax = kargs.get('max', 100)
        ticks = kargs.get('ticks', (vmax-vmin)//10)
        tracking = kargs.get('tracking',True)

        self.slider.setTickInterval(ticks)
        self.slider.setMinimum(vmin)
        self.slider.setMaximum(vmax)
        self.slider.setValue(value)
        self.slider.setSingleStep(1)
        self.slider.setTracking(tracking)
        self.slider.valueChanged.connect(self.set_value)
        self.layout().addWidget(self.slider,stretch=2)

    def set_value(self, val):
        val = int(val)
        self.input.setText(str(val))
        if self.func:
            self.func(self)


class InputFSlider(InputFloat):
    """A float input item using a slider.

    Options:

    - `min`, `max`: range of the scale (integer)
    - `scale`: scale factor to compute the float value
    - `ticks`: step for the tick marks (default range length / 10)
    - `func`: an optional function to be called whenever the value is
      changed. The function receives the input field as argument. With
      this argument, the fields attributes like name, value, text, can
      be retrieved.
    - `tracking`: bool. If True (default), `func` is called repeatedly
      while the slider is being dragged. If False, `func` is only called
      when the user releases the slider.
    """

    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        InputFloat.__init__(self,name,value,*args,**kargs)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.scale = kargs.get('scale', 1.0)
        self.func = kargs.get('func', None)

        vmin = kargs.get('min', 0)
        vmax = kargs.get('max', 100)
        ticks = kargs.get('ticks', (vmax-vmin)//10)
        tracking = kargs.get('tracking',True)

        self.slider.setTickInterval(ticks)
        self.slider.setMinimum(vmin)
        self.slider.setMaximum(vmax)
        self.slider.setValue(value/self.scale)
        self.slider.setSingleStep(1)
        self.slider.setTracking(tracking)
        self.slider.valueChanged.connect(self.set_value)
        self.layout().addWidget(self.slider,stretch=2)


    def set_value(self, val):
        val = float(val)
        value = val*self.scale
        #pf.debug("  fslider: %s = %s" % (val, value), pf.DEBUG.GUI)
        self.input.setText(str(value))
        if self.func:
            self.func(self)


class InputPoint(InputItem):
    """A 2D/3D point/vector input item.

    The default gives fields x, y and z. With ndim=2, only x and y.
    """

    def __init__(self,name,value,ndim=3,*args,**kargs):
        """Initialize the input item."""
        self.input = CoordsBox(ndim=ndim)
        InputItem.__init__(self,name,*args,**kargs)
        self.layout().insertWidget(1, self.input)
        self.setValue(value)

    def value(self):
        """Return the widget's value."""
        return self.input.getValues()

    def setValue(self, val):
        """Change the widget's value."""
        self.input.setValues(val)


class InputIVector(InputItem):
    """A vector of int values."""

    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        self.ndim = len(value)
        if 'fields' in kargs:
            fields = kargs['fields']
        else:
            fields = [ str(i) for i in range(self.ndim) ]

        self.input = QtGui.QWidget(*args)
        InputItem.__init__(self,name,*args,**kargs)
        #self.layout().insertWidget(1,self.input)

        #layout = QtGui.QHBoxLayout(self)
        #self.input.setLayout(layout)
        layout = self.layout()
        self.fields = []
        for fld, val in zip(fields, value):
            f = InputInteger(fld, val)
            self.fields.append(f)
            layout.addWidget(f)


    def value(self):
        """Return the widget's value."""
        return [ f.value() for f in self.fields ]

    def setValue(self, val):
        """Change the widget's value."""
        for f, v in zip(self.fields, val):
            f.setValue(v)


class InputButton(InputItem):
    """A button input item.

    The button input field is a button displaying the current value.
    Clicking on the button executes a function responsible for changing
    the value.

    Extra parameters:

    - `func`: the function to call when the button is clicked. The function
      receives the input field as argument. From this argument, the fields
      attributes like name, value, text, can be retrieved.
      The function should return the value to be set, or None if it is to be
      unchanged. If no function is specified, the value can not be changed.

    """

    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        value = str(value)
        self.input = QtGui.QPushButton(value)
        self.func = kargs.get('func', None)
        InputItem.__init__(self,name,*args,**kargs)
        self.setValue(value)
        if self.func:
            self.input.clicked.connect(self.doFunc)
        self.layout().insertWidget(1, self.input)


    def doFunc(self):
        """Set the value by calling the button's func"""
        val = self.func(self)
        if val is not None:
            self.setValue(val)


class InputFilename(InputButton):
    """A filename input item.

    This is a button input field displaying a file name.
    Clicking on the button pops up a file dialog.

    Extra parameters:

    - `filter`: the filter for the filenames to accept.
      See askFilename.
    - `exist`: boolean. Specifies whether the file should exist,
      or a new one can be created (default).
    - `preview`: an :class:`ImageView` widget, or another widget having
      a `showImage` method. This can be used with image files to show a
      preview of the selected file. In most cases the preview widget is
      inserted in a dialog directly below the `InputFilename` field.

    """
    def __init__(self,name,value,filter='*',exist=False,preview=None,**kargs):
        """Initialize the input item."""
        kargs['func'] = InputFilename.changeFilename
        self._filter = filter
        self._exist = exist
        self._preview = preview
        InputButton.__init__(self,name,value,**kargs)


    def changeFilename(self):
        """Pop up a FileDialog to change the filename"""
        from pyformex.gui.draw import askFilename
        fn = askFilename(self.value(), filter=self._filter, exist=self._exist)
        if fn:
            self.setValue(fn)
            if self._preview:
                self._preview.showImage(fn)


class InputColor(InputItem):
    """A color input item.
    Creates a new color input field with a label in front.

    The color input field is a button displaying the current color.
    Clicking on the button opens a color dialog, and the returned
    value is set in the button.

    Options:

    - `func`: an optional function to be called whenever the value is
      changed. The function receives the input field as argument. With
      this argument, the fields attributes like name, value, text, can
      be retrieved.
    """

    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        if value is None:
            value = 'black'
        color = colors.colorName(value)
        self.input = QtGui.QPushButton(color)
        InputItem.__init__(self,name,*args,**kargs)
        self.setValue(color)
        self.input.clicked.connect(self.setColor)
        self.layout().insertWidget(1, self.input)
        self.func = kargs.get('func', None)


    def setColor(self):
        dia = QtGui.QColorDialog(QtGui.QColor(self.input.text()), self)
        dia.currentColorChanged.connect(self.set_value)
        dia.open()


    def set_value(self, val):
        color = colors.colorName(val)
        self.setValue(color)
        if self.func:
            self.func(self)


    def setValue(self, value):
        """Change the widget's value."""
        col = QtGui.QColor(value)
        col = colors.RGBcolor(col)
        lc = colors.luminance(col)
        if lc < 0.40:
            tcol = colors.white
        else:
            tcol = colors.black
        tcol = colors.RGBcolor(tcol)
        self.input.setStyleSheet(
            "* { background-color: rgb(%s,%s,%s); color: rgb(%s,%s,%s) }" %
            (tuple(col)+tuple(tcol)))
        self.input.setText(str(value))


class InputFont(InputItem):
    """An input item to select a font."""
    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        if value is None:
            value = pf.app.font().toString()
        self.input = QtGui.QPushButton(value)
        InputItem.__init__(self,name,*args,**kargs)
        self.setValue(value)
        self.input.clicked.connect(self.setFont)
        self.layout().insertWidget(1, self.input)


    def setFont(self):
        font = selectFont()
        if font:
            self.setValue(font.toString())
            #pf.GUI.setFont(font)


class InputFile(InputItem):
    """An input item to select a file.

    The following arguments are passed to the FileDialog widget:
    value,pattern,exist,multi,dir,compr.
    """
    def __init__(self,name,value,pattern='*',exist=False,multi=False,dir=False,compr=False,*args,**kargs):
        """Initialize the input item."""
        self.input = FileDialog(value, pattern, exist, multi, dir, compr)
        # remove the dialog buttons, since the widget is embedded
        for b in self.input.findChildren(QtGui.QPushButton):
            b.close()

        InputItem.__init__(self,name,*args,**kargs)
        self.layout().insertWidget(1, self.input)


    def value(self):
        """Return the widget's value."""
        #self.input.accept()
        return self.input.value()

    def setValue(self, value):
        self.input.selectFile(value)


class InputWidget(InputItem):
    """An input item containing any other widget.

    The widget should have:

    - a results attribute that is set to a dict with the resulting input
      values when the widget's acceptData() is called.
    - an acceptData() method, that sets the widgets results dict.
    - a setValue(dict) method that sets the widgets values to those
      specified in the dict.

    The return value of this item is an OrderedDict.
    """

    def __init__(self,name,value,*args,**kargs):
        """Initialize the input item."""
        kargs['text'] = '' # Force no label
        self.input = value
        InputItem.__init__(self,name,*args,**kargs)
        self.layout().insertWidget(1, self.input)

    def text(self):
        """Return the displayed text."""
        return ''

    def value(self):
        """Return the widget's value."""
        return self.input.value()

    def setValue(self, val):
        """Change the widget's value."""
        if val:
            self.input.setValue(val)


class InputForm(QtGui.QVBoxLayout):
    """An input form.

    The input form is a layout box in which the items are layed out
    vertically. The layout can also contain any number of tab widgets
    in which items can be layed out using tab pages.
    """

    def __init__(self):
        """Initialize the InputForm."""
        QtGui.QVBoxLayout.__init__(self)
        self.tabs = []      # list of tab widgets in this form
        self.last = None    # last added itemtype


class ScrollForm(QtGui.QScrollArea):
    """An scrolling input form.

    The input form is a layout box in which the items are layed out
    vertically. The layout can also contain any number of tab widgets
    in which items can be layed out using tab pages.
    """

    def __init__(self):
        """Initialize the ScrollForm."""
        QtGui.QScrollArea.__init__(self)
        self.form = InputForm()


class InputGroup(QtGui.QGroupBox):
    """A boxed group of InputItems."""

    def __init__(self,name,*args,**kargs):
        """Initialize the input item."""
        QtGui.QGroupBox.__init__(self,*args)
        self.key = name
        self.input = self
        self.tab = None
        self.form = InputForm()
        self.setLayout(self.form)
        self.setTitle(kargs.get('text', name))
        if 'checked' in kargs:
            self.setCheckable(True)
            self.setChecked(kargs['checked'])
        if 'enabled' in kargs:
            self.setEnabled(kargs['enabled'])

    def name(self):
        return self.key

    def value(self):
        """Return the widget's value."""
        if self.isCheckable():
            return self.isChecked()
        else:
            return None

    def setValue(self, val):
        """Change the widget's value."""
        if self.isCheckable():
            self.setChecked(val)


class InputTab(QtGui.QWidget):
    """A tab page in an input form."""

    def __init__(self,name,tab,*args,**kargs):
        """Initialize the input item."""
        QtGui.QWidget.__init__(self,*args)
        self.key = name
        self.form = InputForm()
        self.setLayout(self.form)
        tab.addTab(self, kargs.get('text', name))

    def name(self):
        return self.key


def defaultItemType(item):
    """Guess the InputItem type from the value"""
    if 'choices' in item:
        itemtype = 'select'
    else:
        itemtype = type(item['value'])
    if itemtype is None:
        itemtype = str
    return itemtype


def simpleInputItem(name,value=None,itemtype=None,**kargs):
    """A convenience function to create an InputItem dictionary"""
    kargs['name'] = name
    if value is not None:
        kargs['value'] = value
    if itemtype is not None:
        kargs['itemtype'] = itemtype
    return kargs

def groupInputItem(name,items=[],**kargs):
    """A convenience function to create an InputItem dictionary"""
    kargs['name'] = name
    kargs['items'] = items
    kargs['itemtype'] = 'group'
    return kargs

def tabInputItem(name,items=[],**kargs):
    """A convenience function to create an InputItem dictionary"""
    kargs['name'] = name
    kargs['items'] = items
    kargs['itemtype'] = 'tab'
    return kargs


def convertInputItem(item):
    """Convert InputItem item to a dict or a widget.

    This function tries to convert some old style or sloppy InputItem item
    to a proper InputItem item dict.

    The conversion does the following:

    - if `item` is a dict, it is considered a proper item and returned as is.
    - if `item` is a QWidget, it is also returned as is.
    - if `item` is a tuple or a list, conversion with simpleInputItem
      is tried, using the item items as arguments.
    - if neither succeeds, an error is raised.
    """
    if isinstance(item, dict):
        return item
    elif isinstance(item, QtGui.QWidget):
        return item
    elif type(item) in [list, tuple]:
        try:
            return simpleInputItem(*item)
        except:
            pass
    raise ValueError("Invalid InputItem item: %s" % str(item))


# define a function to have the same enabling name as for InputItem
def enableItem(self,*args):
    try:
        ok = any([ src.value() == val for src, val in self.enabled_by ])
        self.setEnabled(ok)
    except:
        utils.warn("error_widgets_enableitem")
        pass


InputItem.enableItem = enableItem
QtGui.QGroupBox.enableItem = enableItem
QtGui.QTabWidget.enableItem = enableItem

## def nameGroupBox(self):
##     return self.title()
## QtGui.QGroupBox.name = nameGroupBox
## QtGui.QTabWidget.disable = disableGroup


default_dialog_flags = QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.CustomizeWindowHint

class InputDialog(QtGui.QDialog):
    """A dialog widget to interactively set the value of one or more items.

    Overview

    The pyFormex user has full access to the Qt4 framework on which the
    GUI was built. Therefore he can built input dialogs as complex and
    powerful as he can imagine. However, directly dealing with the
    Qt4 libraries requires some skills and, for simple input widgets,
    more effort than needed.

    The InputDialog class presents a unified system for quick and easy
    creation of common dialog types. The provided dialog can become
    quite sophisticated with tabbed pages, groupboxes and custom widgets.
    Both modal and modeless (non-modal) dialogs can be created.

    Items

    Each basic input item is a dictionary, where the fields have the
    following meaning:

    - name:  the name of the field,
    - value: the initial or default value of the field,
    - itemtype: the type of values the field can accept,
    - options: a dict with options for the field.
    - text: if specified, the text value will be displayed instead of
      the name. The name value will remain the key in the return dict.
      Use this field to display a more descriptive text for the user,
      while using a short name for handling the value in your script.
    - buttons:
    - tooltip:
    - min:
    - max:
    - scale:
    - func:

    For convenience, simple items can also be specified as a tuple.
    A tuple (key,value) will be transformed to a dict
    {'key':key, 'value':value}.

    Other arguments

    - caption: the window title to be shown in the window decoration
    - actions: a list of action buttons to be added at the bottom of the
      input form. By default, a Cancel and Ok button will be added, to either
      reject or accept the input values.
    - default: the default action
    - parent: the parent widget (by default, this is the pyFormex main window)
    - autoprefix: if True, the names of items inside tabs and group boxes will
      get prefixed with the tab and group names, separated with a '/'.
    - flat: if True, the results are returned in a single (flat) dictionary,
      with keys being the specified or autoprefixed ones. If False, the results
      will be structured: the value of a tab or a group is a dictionary with
      the results of its fields. The default value is equal to the value of
      autoprefix.
    - flags:
    - modal:

    - `enablers`: a list of tuples (key,value,key1,...) where the first two
      items indicate the key and value of the enabler, and the next items
      are keys of fields that are enabled when the field key has the specified
      value. Currentley, key should be a field of type boolean, [radio],
      combo or group. Also, any input field should only have one enabler!

    """
    def __init__(self,items,caption=None,parent=None,flags=None,actions=None,default=None,store=None,prefix='',autoprefix=False,flat=None,modal=None,enablers=[],scroll=False,size=None,align_right=False):
        """Create a dialog asking the user for the value of items."""
        if parent is None:
            parent = pf.GUI
        QtGui.QDialog.__init__(self, parent)

        if caption is None:
            caption = 'pyFormex-dialog'
        else:
            caption = str(caption)
        self.setObjectName(caption)
        self.setWindowTitle(caption)
        if modal is not None:
            self.setModal(modal)

        try:
            w, h = size
            if isinstance(w, float):
                w = int(w*pf.maxsize[0])
            if isinstance(h, float):
                h = int(h*pf.maxsize[1])
            self.resize(w, h)
        except:
            pass

        self.fields = []
        self.groups = {}
        self.results = OrderedDict()
        self._pos = None
        self.store = store
        self.autoname = utils.NameSequence('input')
        self.prefix = prefix
        self.autoprefix = autoprefix
        if flat is None:
            self.flat = self.autoprefix
        else:
            self.flat = flat

        # create the form with the input fields
        self.tab = None  # tabwidget for all the tabs in this form
        if scroll:
            self.scroll = ScrollForm()
            self.form = self.scroll.form
        else:
            self.form = InputForm()

        # add the items to the input form
        # converting first allows for sloppy input
        items = [ convertInputItem(i) for i in items ]
        self.add_items(items, self.form, self.prefix)

        # add the action buttons
        but = ButtonBox(actions=actions, default=default, parent=self, stretch=[0, 1])
        self.form.addWidget(but)

        self.setLayout(self.form)
        self.accepted.connect(self.acceptData)

        # add the enablers
        init_signals = []
        for en in enablers:
            #print "Enabler %s " % str(en)
            src = self[en[0]]
            if src:
                val = en[1]
                for t in en[2:]:
                    tgt = self[t]
                    #print "%s" % (tgt)
                    if tgt:
                        try:
                            tgt.enabled_by.append((src, val))
                        except:
                            tgt.enabled_by = [(src, val)]
                        signal = None
                        if isinstance(src, InputBool):
                            signal = src.input.stateChanged[int]
                        elif isinstance(src, InputRadio):
                            utils.warn('radio_enabler')
                            # BV: this does not work
                            #signal = src.input.buttonClicked[int]
                        elif isinstance(src, InputCombo):
                            signal = src.input.currentIndexChanged[int]
                        elif isinstance(src, InputGroup):
                            signal = src.input.clicked[bool]
                        else:
                            raise ValueError("Can not enable from a %s input field" % type(src.input))


                        if signal:
                            init_signals.append(signal)
                            signal.connect(tgt.enableItem)

        # emit the signal to adjust initial state
        for signal in init_signals:
            signal.emit(0)


    def add_items(self,items,form,prefix=''):
        """Add input items to form.

        items is a list of input item data
        layout is the widget layout where the input widgets will be added
        """
        for item in items:

            if isinstance(item, dict):

                itemtype = item.get('itemtype', None)

                if itemtype == 'tab':
                    self.add_tab(form,prefix=prefix,**item)

                elif itemtype == 'group':
                    self.add_group(form,prefix=prefix,**item)

                else:
                    self.add_input(form,prefix=prefix,**item)

                form.last = itemtype

            elif isinstance(item, QtGui.QWidget):
                # this allows including widgets which are not
                # input fields
                form.addWidget(item)
                form.last = None

            else:
                raise ValueError("Invalid input item (type %s). Expected a dict or a QWidget." % type(item))


    def add_tab(self,form,prefix,name,items,**extra):
        """Add a Tab page of input items."""
        if form.last == 'tab':
            # Add to previous tab widget
            tab = form.tabs[-1]
        else:
            # Create a new tab widget
            tab = QtGui.QTabWidget()
            form.addWidget(tab)
            form.tabs.append(tab)

        w = InputTab(prefix+name,tab,**extra)
        if self.autoprefix:
            prefix += name+'/'
        self.add_items(items, w.form, prefix=prefix)
        w.form.addStretch() # makes items in tab align to top


    def add_group(self,form,prefix,name,items,**extra):
        """Add a group of input items."""
        w = InputGroup(prefix+name,**extra)
        form.addWidget(w)
        if w.isCheckable:
            self.fields.append(w)

        if self.autoprefix:
            prefix += name+'/'
        self.add_items(items, w.form, prefix=prefix)


    def add_input(self,form,prefix,**item):
        """Add a single input item to the form."""
        #print item
        item['name'] = prefix + item.get('name', self.autoname.next())
        if not 'value' in item:
            # no value: try to find one
            if 'choices' in item:
                item['value'] = item['choices'][0]
            # DO NOT USE A TEST  if self.store:  HERE
            # THAT DOES NOT SEEM TO WORK: ALWAYS RETURNS FALSE
            try:
                item['value'] = self.store[item['name']]
            except:
                pass

        # we should have a value now, or we can't continue!
        if not 'value' in item:
            raise ValueError("No value specified for item '%s'" % item['name'])

        if not 'itemtype' in item or item['itemtype'] is None:
            item['itemtype'] = defaultItemType(item)

        itemtype = item['itemtype']

        if isinstance(itemtype, str):
            if itemtype.endswith('radio') or itemtype.endswith('push'):
                if itemtype[0] in 'hv':
                    item['direction'] = itemtype[0]
                    item['itemtype'] = itemtype[1:]
                else:
                    # default horizontal
                    item['direction'] = 'h'


            if itemtype == 'slider':
                value = item['value']
                if at.isInt(value):
                    pass
                elif isinstance(value, float):
                    item['itemtype'] = 'fslider'
                else:
                    raise ValueError("Invalid value type for slider: %s" % value)

        item['parent'] = self

        field = inputAny(**item)
        self.fields.append(field)
        form.addWidget(field)


    def __getitem__(self, name):
        """Return the input item with specified name."""
        items = [ f for f in self.fields if f.name() == name ]
        if len(items) > 0:
            return items[0]
        else:
            raise ValueError("No input field named: %s" % name)
            #return self.groups.get(name,None)


    def timeout(self):
        """Hide the dialog and set the result code to TIMEOUT"""
        pf.debug("TIMEOUT")
        self.acceptData(TIMEOUT)


    def timedOut(self):
        """Returns True if the result code was set to TIMEOUT"""
        return self.result() == TIMEOUT


    def show(self,timeout=None,timeoutfunc=None,modal=False):
        """Show the dialog.

        For a non-modal dialog, the user has to call this function to
        display the dialog.
        For a modal dialog, this is implicitely executed by getResults().

        If a timeout is given, start the timeout timer.
        """
        # Set the keyboard focus to the first input field
        #self.fields[0].input.setFocus()
        self.status = None

        self.setModal(modal)
        if not modal:
            #print "DELETE ON CLOSE"
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        #self.adjustSize()
        self.setMaximumHeight(1000)
        #print self.maximumHeight()
        QtGui.QDialog.show(self)

        addTimeOut(self, timeout, timeoutfunc)


    ## def close(self):
    ##     """Close and delete the dialog.

    ##     """
    ##     QtGui.QDialog.close(self)
    ##     print self.parent()
    ##     print self.parent().children()
    ##     self.parent().removeChild(self)


    def acceptData(self,result=ACCEPTED):
        """Update the dialog's return value from the field values.

        This function is connected to the 'accepted()' signal.
        Modal dialogs should normally not need to call it.
        In non-modal dialogs however, you can call it to update the
        results without having to raise the accepted() signal (which
        would close the dialog).
        """
        self.results = OrderedDict()
        self.results.update([ (fld.name(), fld.value()) for fld in self.fields ])
        #print(self.results)
        ## if self.report_pos:
        ##     self.results.update({'__pos__':self.pos()})
        if result == TIMEOUT:
            self.done(result)
        else:
            self.setResult(result)


    def updateData(self, d):
        """Update a dialog from the data in given dictionary.

        d is a dictionary where the keys are field names in the dialog.
        The values will be set in the corresponding input items.
        """
        for f in self.fields:
            n = f.name()
            if n in d:
                f.setValue(d[n])


    def getResults(self,timeout=None):
        """ Get the results from the input dialog.

        This fuction is used to present a modal dialog to the user (i.e. a
        dialog that must be ended before the user can continue with the
        program. The dialog is shown and user interaction is processed.
        The user ends the interaction either by accepting the data (e.g. by
        pressing the OK button or the ENTER key) or by rejecting them (CANCEL
        button or ESC key).
        On accept, a dictionary with all the fields and their values is
        returned. On reject, an empty dictionary is returned.

        If a timeout (in seconds) is given, a timer will be started and if no
        user input is detected during this period, the input dialog returns
        with the default values set.
        A value 0 will timeout immediately, a negative value will never timeout.
        The default is to use the global variable input_timeout.

        The result() method can be used to find out how the dialog was ended.
        Its value will be one of ACCEPTED, REJECTED ot TIMEOUT.
        """
        self.results = OrderedDict()
        self.setResult(0)
        if self._pos is not None:
            self.restoreGeometry(self._pos)

        self.show(timeout, modal=True)
        self.exec_()
        #self.activateWindow()
        #self.raise_()
        pf.app.processEvents()
        self._pos = self.saveGeometry()
        return self.results



class ScrollDialog(InputDialog):
    def __init__(self,*args,**kargs):
        # This is experimental !!!
        InputDialog.__init__(self,*args,**kargs)
        self.scroll = QtGui.QScrollArea()
        self.scroll.setWidget(self)
        #self.viewport().setBackgroundRole(QtGui.QPalette.Dark)
        self.scroll.viewport().setAutoFillBackground(True)
        #self.scroll.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Maximum)
        #self.scroll.resize(pf.GUI.width()/2,pf.GUI.height())
        #self.scroll.setWidgetResizable(True)

    def show(self):
        self.scroll.show()

    def close(self):
        self.scroll.close()


# Create a dict with itemtype <-> InputItem mapping

def getInputItemDict(base=InputItem):
    sub = base.__subclasses__()
    if not sub:
        return {}

    d = dict([ (k.__name__[5:].lower(), k) for k in sub ])
    for k in sub:
        d.update(getInputItemDict(k))
    return d

InputItems = getInputItemDict()

# some itemtypes are not strings but Python type objects.
# also add some name mismatches
InputItems.update({
    None: InputItem,
    bool: InputBool,
    int: InputInteger,
    float: InputFloat,
    str: InputString,
    'select': InputCombo,
})

#
# TODO: all itemtypes should become strings. Sorting mixed types
#       will not work in Python3
#
#keys = sorted(InputItems)
## DO WE USE THIS ANYWHERE?


def inputAny(name,value,itemtype,**options):
    """Create an InputItem of any type, depending on the arguments.

    Arguments: only name, value and itemtype are required

    - name: name of the item, also the key for the return value
    - value: initial value,
    - itemtype: one of the available itemtypes
    """
    try:
        f = InputItems[itemtype]
    except:
        f = InputString # default convert to string
    return f(name,value,**options)


def updateDialogItems(data, newdata):
    """Update the input data fields with new data values

    - data: a list of dialog items, as required by an InputDialog.
    - newdata: a dictionary with new values for (some of) the items.

    The data items with a name occurring as a key in newdata will have
    their value replaced with the corresponding value in newdata, unless
    this value is None.

    The user should make sure to set only values of the proper type!
    """
    if newdata:
        # check for old format
        if isinstance(data, dict):
            return updateOldDialogItems(data, newdata)
        for d in data:
            if not isinstance(d, dict):
                return updateOldDialogItems(data, newdata)
        # new format
        for d in data:
            if d.get('itemtype', None) in [ 'group', 'tab' ]:
                updateDialogItems(d['items'], newdata)
            else:
                newval = newdata.get(d['name'], None)
                if newval is not None:
                    d['value'] = newval


def updateOldDialogItems(data, newdata):
    """_Update the input data fields with new data values."""
    utils.warn("warn_widgets_updatedialogitems")
    if newdata:
        if isinstance(data, dict):
            for d in data:
                updateOldDialogItems(data[d], newdata)
        else:
            for d in data:
                v = newdata.get(d[0], None)
                if v is not None:
                    d[1] = v



####################################################################
########### Specialized Widgets #####################################
#####################################################################


class ListWidget(QtGui.QListWidget):
    """A customized QListWidget with ability to compute its required size.

    """
    def __init__(self,maxh=0):
        """Initialize the ListWidget"""
        QtGui.QListWidget.__init__(self)
        self.maxh = maxh
        self._size = QtGui.QListWidget.sizeHint(self)

    def allItems(self):
        return [ self.item(i) for i in range(self.count()) ]

    def reqSize(self):
        w = 0
        h = 10 # margin
        for i in self.allItems():
            r = self.visualItemRect(i)
            h += r.height()
            w = max(w, r.width())
        return w, h

    def setSize(self):
        w, h = self.reqSize()
        pf.debug("Required list size is %s,%s" % (w, h), pf.DEBUG.WIDGET)
        if self.maxh > -1:
            self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            if self.maxh > 0:
                h = min(h, self.maxh)
            w, hs = objSize(QtGui.QListWidget.sizeHint(self))
            pf.debug("QListWidget hints size %s,%s" % (w, hs), pf.DEBUG.WIDGET)

        if self.maxh < 0:
            self.setFixedSize(w, h)

        pf.debug("Setting list size to %s,%s" % (w, h), pf.DEBUG.WIDGET)
        self._size = QtCore.QSize(w, h)

    def sizeHint(self):
        if self.maxh > 0:
            w, h = objSize(QtGui.QListWidget.sizeHint(self))
            print(w)
            print(h)
            print("QListWidget hints size %s,%s" % (w, h), pf.DEBUG.WIDGET)
            h = max(h, self.maxh)
            return QtCore.QSize(w, h)
        else:
            return self._size


########################### Table widgets ###########################

_EDITROLE = QtCore.Qt.EditRole


class TableModel(QtCore.QAbstractTableModel):
    """A model representing a two-dimensional array of items.

    - `data`: any tabular data organized in a fixed number of rows and colums.
      This means that an item at row i and column j can be addressed as
      data[i][j]. Thus it can be a list of lists, or a list of tuples or
      a 2D numpy array. The data will always be returned as a list of lists
      though.
      Unless otherwise specified by the use of a `celltype`, `coltype` or
      `rowtype` argument, all items are converted to strings and will be
      returned as strings.
      Item storage order is row by row.
    - `chead`: optional list of (ncols) column headers
    - `rhead`: optional list of (nrows) row headers
    - `celltype`: callable: if specified, it is used to map all items.
      This is only used if neither `rowtype` nor `coltype` are specified.
      If unspecified, it will be set to 'str', unless `data` is a numpy array,
      in which case it will be set to the datatype of the array.
    - `rowtype`: list of nrows callables: if specified, the items of each row
      are mapped by the corresponding callable.
      This overrides `celltype` and is only used if `coltype` ais not specified.
    - `coltype`: list of ncols callables: if specified, the items of each
      column are mapped by the corresponding callable.
      This overrides `celltype` and `rowtype`.
    - `edit`: bool: if True (default), the table is editable. Set to False
      to make the data readonly.
    - `resize`: bool: if True, the table can be resized: rows and columns can be
      added or removed. If False, the size of the table can not be changed.
      The default value is equal to the value of `edit`.
      If `coltype` is specified, the number of columns can not be changed.
      If `rowtype` is specified, the number of rows can not be changed.
    """

    def __init__(self,data,chead=None,rhead=None,celltype=None,rowtype=None,coltype=None,edit=True,resize=None):
        """Initialize the TableModel"""
        import numpy as np
        QtCore.QAbstractTableModel.__init__(self)
        self.celltype = self.rowtype = self.coltype = None
        if coltype is not None:
            self.coltype = coltype
        elif rowtype is not None:
            self.rowtype = rowtype
        elif celltype is not None:
            self.celltype = celltype
        else:
            if isinstance(data, np.ndarray):
                self.celltype = data.dtype
            else:
                self.celltype = str
        if self.coltype:
            self._data = [ [ ct(i) for i, ct in zip(r, self.coltype) ] for r in data ]
        elif self.rowtype:
            self._data = [ [ rt(i) for i in r ] for r, rt in zip(data, self.rowtype) ]
        else:
            self._data = [ [ self.celltype(i) for i in r ] for r in data ]
        self.headerdata = {QtCore.Qt.Horizontal:chead,QtCore.Qt.Vertical:rhead}
        self.makeEditable(edit, resize)


    def makeEditable(self,edit=True,resize=None):
        """Make the table editable or not.

        - `edit`: bool: makes the items in the table editable or not.
        - `resize`: bool: makes the table resizable or not. If unspecified,
          it is set equal to the `edit`.
        """
        self._flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if edit:
            self._flags |= QtCore.Qt.ItemIsEditable
        self.edit = edit
        if resize is None:
            self.resize = edit
        else:
            self.resize = resize


    def rowCount(self,parent=None):
        """Return number of rows in the table"""
        return len(self._data)


    def columnCount(self,parent=None):
        """Return number of columns in the table"""
        return len(self._data[0])


    def data(self, index, role):
        """Return the data at the specified index"""
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            r, c = index.row(), index.column()
            return self._data[r][c]
        else:
            return None


    def cellType(self, r, c):
        """Return the type of the item at the specified position"""
        if self.coltype:
            itemtype = self.coltype[c]
        elif self.rowtype:
            itemtype = self.rowtype[r]
        else:
            itemtype = self.celltype
        return itemtype


    def setCellData(self, r, c, value):
        """Set the value of an individual table element.

        This changes the stored data, not the interface.
        """
        itemtype = self.cellType(r, c)
        if self.coltype:
            itemtype = self.coltype[c]
        elif self.rowtype:
            itemtype = self.rowtype[r]
        else:
            itemtype = self.celltype
        self._data[r][c] = itemtype(value)


    def setData(self,index,value,role=_EDITROLE):
        """Set the value of an individual table element."""
        if self.edit and role == QtCore.Qt.EditRole:
            try:
                r, c = [index.row(), index.column()]
                self.setCellData(r, c, value)
                self.dataChanged.emit(index, index) #not sure if needed
                return True
            except:
                raise
                print("Could not set the value")
                return False
        else:
            print("CAN  NOT EDIT")
        return False


    def headerData(self, col, orientation, role):
        """Return the header data for the sepcified row or column"""
        if orientation in self.headerdata and self.headerdata[orientation] and role == QtCore.Qt.DisplayRole:
            return self.headerdata[orientation][col]
        return None


    def insertRows(self,row=None,count=None):
        """Insert row(s) in table"""
        if row is None:
            row = self.rowCount()
        if count is None:
            count = 1
        last = row+count-1
        newdata = [ [ None ] * self.columnCount() ] * count
        self.beginInsertRows(QtCore.QModelIndex(), row, last)
        self._data[row:row] = newdata
        self.endInsertRows()
        return True


    def removeRows(self,row=None,count=None):
        """Remove row(s) from table"""
        if row is None:
            row = self.rowCount()
        if count is None:
            count = 1
        last = row+count-1
        self.beginRemoveRows(QtCore.QModelIndex(), row, last)
        self._data[row:row+count] = []
        self.endRemoveRows()
        return True


    def flags(self, index):
        """Return the TableModel flags."""
        return self._flags


# Generic Python types for numpy data types
_generic_nptype = {
    'i': int,
    'f': float,
    's': str,
    }

class ArrayModel(QtCore.QAbstractTableModel):
    """A model representing a two-dimensional numpy array.

    - `data`: a numpy array with two dimensions.
    - `chead`, `rhead`: column and row headers. The default will show column
      and row numbers.
    - `edit`: if True (default), the data can be edited. Set to False to make
      the data readonly.
    """

    def __init__(self,data,chead=None,rhead=None,edit=True):
        import numpy as np
        QtCore.QAbstractTableModel.__init__(self)
        self._data = np.asarray(data)
        self.generictype = _generic_nptype[self._data.dtype.kind]
        if rhead is None:
            rhead = np.arange(data.shape[0])
        if chead is None:
            chead = np.arange(data.shape[1])
        self.headerdata = {QtCore.Qt.Horizontal:chead,QtCore.Qt.Vertical:rhead}
        self.makeEditable(edit)


    def makeEditable(self,edit=True):
        """Make the table editable or not.

        - `edit`: bool: makes the items in the table editable or not.
         """
        self._flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if edit:
            self._flags |= QtCore.Qt.ItemIsEditable
        self.edit = edit


    def rowCount(self,parent=None):
        """Return number of rows in the table"""
        return self._data.shape[0]


    def columnCount(self,parent=None):
        """Return number of columns in the table"""
        return self._data.shape[1]


    def data(self, index, role):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            r, c = index.row(), index.column()
            return self.generictype(self._data[r, c])
        else:
            return None


    def cellType(self, r, c):
        """Return the type of the item at the specified position"""
        return self._data.dtype


    def setData(self,index,value,role=_EDITROLE):
        """Set the value of an individual table element."""
        if self.edit and role == QtCore.Qt.EditRole:
            try:
                k = self._data.dtype.kind
                if k == 'f':
                    value, ok = value.toDouble()
                elif k == 'i':
                    #value,ok = value.toInt()
                    print(type(value))
                    value, ok = int(value), True
                else:
                    ok = False
                if not ok:
                    pf.warning("Expected %s data" % self.generictype)
                    return False
                r, c = [index.row(), index.column()]
                self._data[r, c] = value
                self.dataChanged.emit(index, index) #not sure if needed
                return True
            except:
                raise
                print("Could not set the value")
                return False
        else:
             print("CAN  NOT EDIT")
        return False


    def headerData(self, col, orientation, role):
        """Return the header data for the sepcified row or column"""
        if orientation in self.headerdata and self.headerdata[orientation] and role == QtCore.Qt.DisplayRole:
            return self.headerdata[orientation][col]
        return None


    def flags(self, index):
        """Return the TableModel flags."""
        return self._flags


class Table(QtGui.QTableView):
    """A widget to show/edit a two-dimensional array of items.

    - `data`: a 2-D array of items, with `nrow` rows and `ncol` columns.

      If `data` is an numpy array, the Table will use the ArrayModel:
      editing the data will directly change the input data array; all
      items are of the same type; the size of the table can not be changed.

      Else a TableModel is used. Rows and columns can be added to or removed
      from the table. Item type can be set per row or per column or for the
      whole table.
    - `label`: currently unused (intended to display an optional label
      in the upper left corner if both `chead` and `rhead` are specified.
    - `parent`:
    - `autowidth`:
    - additionally, all other parameters for the initialization of the
      TableModel or ArrayModel may be passed
    """
    def __init__(self,data,chead=None,rhead=None,label=None,celltype=None,rowtype=None,coltype=None,edit=True,resize=None,parent=None,autowidth=True):
        """Initialize the Table widget."""
        import numpy as np
        QtGui.QTableView.__init__(self, parent)
        if isinstance(data, np.ndarray):
            self.tm = ArrayModel(data, chead, rhead, edit=edit)
        else:
            self.tm = TableModel(data, chead, rhead, celltype, rowtype, coltype, edit=edit, resize=resize)
        self.setModel(self.tm)
        self.horizontalHeader().setVisible(chead is not None)
        self.verticalHeader().setVisible(rhead is not None)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        #self.connect(tm,dataChanged
        self.autowidth = autowidth
        if self.autowidth:
            self.resizeColumnsToContents()
        self.setCornerButtonEnabled
        self.adjustSize()

    def colWidths(self):
        """Return the width of the columns in the table"""
        return [self.columnWidth(i) for i in range(self.tm.columnCount())]

    def rowHeights(self):
        """Return the height of the rows in the table"""
        return [self.rowHeight(i) for i in range(self.tm.rowCount())]

    def minimumSizeHint(self):
        #self.update()
        #minsize = size = QtGui.QTableView.sizeHint(self)
        #print("ORIG SIZE: %s, %s" % (size.width(),size.height()))
        size = self.size()
        #print("ACTUAL SIZE: %s, %s" % (size.width(),size.height()))
        width = sum(self.colWidths())
        height = sum(self.rowHeights())
        #print("NET SIZE: %s, %s" % (width,height))
        width += self.tm.columnCount() * 1 + 1
        height += self.tm.rowCount() * 1 + 1
        #print("SPACED SIZE: %s, %s" % (width,height))
        if self.horizontalHeader().isVisible():
            height += self.horizontalHeader().height()
        if self.verticalHeader().isVisible():
            width += self.verticalHeader().width()
        #print("HEADERED SIZE: %s, %s" % (width,height))
        size = QtCore.QSize(width, height)
        return size

    sizeHint = minimumSizeHint

    def dataChanged(self, ind1, ind2):
        print("DATA CHANGED")
        QtGui.QTableView.dataChanged(self, ind1, ind2)
        self.update()

    def update(self):
        """Update the table.

        This method should be called to update the widget when the data of
        the table have changed. If autowidth is True, this will also
        adjust the column widths.
        """
        print("UPDATE")
        QtGui.QTableView.update(self)
        if self.autowidth:
            print("ADJUSTING COLUMNS")
            self.resizeColumnsToContents()
        self.adjustSize()
        self.updateGeometry()



    def value(self):
        """Return the Table's value."""
        return self.tm._data



#####################################################################
########### Specialized Dialogs #####################################
#####################################################################


###################### File Selection Dialog #########################

def fileUrls(files):
    """Transform a list of local file names to urls"""
    return [ QtCore.QUrl.fromLocalFile(f) for f in files ]


class FileDialog(QtGui.QFileDialog):
    """A file selection dialog.

    The FileDialog dialog is a special purpose complex dialog widget
    that allows to interactively select a file or directory from the file
    system, possibly even multiple files, create new files or directories.

    Parameters:

    - `path`: the path shown on initial display of the dialog. It should
      be an existing path in the file system. The default is '.' for the
      current directory.
    - `pattern`: a string or a list of strings: specifies one or more UNIX
      glob patterns, used to limit the set of displayed filenames to those
      matching the glob. Each string can contain multiple globs, and an
      explanation string can be place in front::

        'Image files (*.png *.jpg)'

      The `pattern` argument is passed to the :func:`utils.fileDescription`
      function, together with the `compr` argument, to generate the actual
      pattern set. This allows the creation of filters for common file types
      with a minimal input.

      If a list of multiple strings is given, a combo box will allow the
      user to select between one of them.
    - `exist`: bool: if True, the filename must exist. The default will
      allow any new filename to be created.
    - `multi`: bool: if True, multiple files can be selected. The default is
      to allow only a single file.
    - `dir`: bool: if True, only directories can be selected. If dir evaluates
      to True, but is not the value True, either a directory or a filename can
      be selected.
    - `compr`: bool: if True, compressed files of the specified type will be
      selectable as well. This is passed together with the `pattern` argument
      to the :func:`utils.fileDescription` to generate the actual patterns.
    - `button`: string: the label to be displayed on the accept button. The
      default is set to 'Save' if new files are allowed or 'Open' if only
      existing files can be selected.

    """

    def accept_any(self):
        self.done(ACCEPTED)

    # Default timeout function
    timeout = accept_any


    def __init__(self,path='.',pattern='*',exist=False,multi=False,dir=False,compr=False,button=None,sidebar=None,caption=None,**kargs):
        """The constructor shows the widget."""
        QtGui.QFileDialog.__init__(self,**kargs)
        if os.path.isfile(path):
            self.setDirectory(os.path.dirname(path))
            self.selectFile(path)
        else:
            self.setDirectory(path)
        pattern = utils.fileDescription(pattern,compr)
        if isinstance(pattern, str):
            self.setFilter(pattern)
        else: # should be a list of patterns
            self.setFilters(pattern)
        if dir:
            if caption is None:
                caption = "Select a directory"
            if dir is True:
                mode = QtGui.QFileDialog.Directory
            else:
                mode = QtGui.QFileDialog.ExistingFile
                self.setOption(QtGui.QFileDialog.DontUseNativeDialog, True)
                l = self.findChild(QtGui.QListView, 'listView')
                l.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
                c = self.findChild(QtGui.QTreeView)
                c.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
                b = self.findChild(QtGui.QPushButton)
                b.clicked.disconnect()
                b.clicked.connect(self.accept_any)
        elif exist:
            if multi:
                mode = QtGui.QFileDialog.ExistingFiles
                if caption is None:
                    caption = "Select existing files"
            else:
                mode = QtGui.QFileDialog.ExistingFile
                if caption is None:
                    caption = "Open existing file"
        else:
            mode = QtGui.QFileDialog.AnyFile
            if caption is None:
                caption = "Save file as"

        self.setFileMode(mode)
        self.setWindowTitle(caption)
        #self.return_dir = bool(dir) and dir is not True
        if button is None:
            if dir:
                button = '&Select'
            elif exist:
                button = '&Open'
            else:
                button = '&Save'
        self.setLabelText(QtGui.QFileDialog.Accept, button)
        sidebarfiles = pf.cfg['gui/sidebarfiles']
        if sidebar:
            sidebarfiles.extend(sidebar)
        self.setSidebarUrls(fileUrls(sidebarfiles))


    def show(self,timeout=None,timeoutfunc=None,modal=False):
        self.setModal(modal)
        QtGui.QFileDialog.show(self)
        addTimeOut(self, timeout, timeoutfunc)


    def value(self):
        """Return the selected value"""
        ret = self.selectedFiles()
        if not pf.options.unicode:
            ret = [ str(r) for r in ret ]
        if self.fileMode() != QtGui.QFileDialog.ExistingFiles:
            # not multiple selection
            ret = ret[0]
            ## if self.return_dir:
            ##     # requested directory but have file
            ##     ret = os.path.dirname(ret)
        return ret


    def getResults(self,timeout=None):
        """Ask the user to fill in the dialog.

        Returns a dict.
        If the user accepts the results, the dict has a single entry with
        key 'fn' and the selected filename(s) as value.
        If the user hits CANCEL or ESC, an empty dict is returned.
        """
        self.show(timeout, modal=True)
        self.exec_()
        if self.result() == ACCEPTED:
            res = mydict.Dict()
            res.fn = self.value()
        else:
            # user canceled
            res = {}
        return res


    def getFilename(self,timeout=None):
        """Ask for filename(s) by user interaction.

        Returns the filename(s) selected by the user if the user
        accepts the selection. This is equivalent with
        `self.getResults(timeout)['fn']`.
        Returns None if the user hits CANCEL or ESC.
        """
        res = self.getResults(timeout)
        if res:
            return res['fn']


class GeometryFileDialog(FileDialog):
    """A file selection dialog specialized for opening pgf files.

    """
    def __init__(self,path=None,pattern=None,exist=False,
                 sep=' ', compression=4,
                 access=None,default=None,convert=True,
                 **kargs):
        """Create the dialog."""
        if path is None:
            path = pf.cfg['workdir']
        if pattern is None:
            pattern = 'pgf'
        FileDialog.__init__(self, path, pattern, exist, **kargs)
        grid = self.layout()
        nr = grid.rowCount()

        if access is None:
            access = [ 'rw', 'r' ] if exist else [ 'wr', 'rw', 'w', 'r' ]
        self.acc = InputRadio("Access Mode", default, choices=access)
        self.acc.setToolTip("wr=read if exist; rw=must exist; w=overwrite; r=readonly")
        grid.addWidget(self.acc, nr, 0, 1, -1)
        nr += 1

        ## if exist:
        ##     self.cvt = InputBool("Automatically convert file to latest format", convert)
        ##     self.cvt.setToolTip("It is recommended to automatically convert your project files to the latest format, to avoid future compatibility problems. The only reason to not convert is if you still need to read your files with older versions of pyFormex. The conversion will not be performed if pyFormex can not correctly read your file.")
        ##     grid.addWidget(self.cvt, nr, 0, 1, -1)
        ##     nr += 1

        if not exist:
            self.sep = InputString("Data separator (empty means binary)", sep,tooltip="This string will be used as separator between any two data. Standard is a single blank, for ascii format. Specifying an empty string will force binary format.")
            grid.addWidget(self.sep, nr, 0, 1, -1)
            nr += 1

            self.cpr = InputSlider("Compression level (0-9)", compression, min=0, max=9, ticks=1)
            self.cpr.setToolTip("Higher compression levels result in smaller files, but higher load and save times.")
            grid.addWidget(self.cpr, nr, 0, 1, -1)
            nr += 1


    def getResults(self,timeout=None):
        """Ask the user to fill in the dialog.

        Returns a Dict or dict.
        If the user accepts the results, a Dict with the following entries
        is returned: fn, acc, and optional sep, cpr, cvt
        If the user hits CANCEL or ESC, an empty dict is returned.
        """
        res = FileDialog.getResults(self,timeout)
        if res:
            res.acc = self.acc.value()
            if hasattr(self, 'sep'):
                res.sep = self.sep.value()
            if hasattr(self, 'cpr'):
                res.cpr = self.cpr.value()
            if hasattr(self, 'cvt'):
                res.cvt = self.cvt.value()
            print(res)
            return res

        else:
            return {}


class ProjectSelection(FileDialog):
    """A file selection dialog specialized for opening projects."""
    def __init__(self,path=None,pattern=None,exist=False,compression=4,
                 access=None,default=None,convert=True):
        """Create the dialog."""
        if path is None:
            path = pf.cfg['workdir']
        if pattern is None:
            pattern = 'pyf'
        FileDialog.__init__(self, path, pattern, exist)
        grid = self.layout()
        nr = grid.rowCount()

        if access is None:
            access = [ 'rw', 'r' ] if exist else [ 'wr', 'rw', 'w', 'r' ]
        self.acc = InputRadio("Access Mode", default, choices=access)
        self.acc.setToolTip("wr=read if exist; rw=must exist; w=overwrite; r=readonly")
        grid.addWidget(self.acc, nr, 0, 1, -1)
        nr += 1

        if exist:
            self.cvt = InputBool("Automatically convert file to latest format", convert)
            self.cvt.setToolTip("It is recommended to automatically convert your project files to the latest format, to avoid future compatibility problems. The only reason to not convert is if you still need to read your files with older versions of pyFormex. The conversion will not be performed if pyFormex can not correctly read your file.")
            grid.addWidget(self.cvt, nr, 0, 1, -1)
            nr += 1

        if not exist:
            self.cpr = InputSlider("Compression level (0-9)", compression, min=0, max=9, ticks=1)
            self.cpr.setToolTip("Higher compression levels result in smaller files, but higher load and save times.")
            grid.addWidget(self.cpr, nr, 0, 1, -1)
            nr += 1


    def getResults(self):
        self.exec_()
        if self.result() == ACCEPTED:
            opt = mydict.Dict()
            opt.fn = str(self.selectedFiles()[0])
            opt.acc = self.acc.value()
            opt.cpr = opt.cvt = None
            if hasattr(self, 'cpr'):
                opt.cpr = self.cpr.value()
            if hasattr(self, 'cvt'):
                opt.cvt = self.cvt.value()
            return opt

        else:
            return {}


class SaveImageDialog(FileDialog):
    """A dialog for saving to an image file.

    The dialog contains the normal file selection widget plus some
    extra fields to set the Save Image parameters:

    - `Grab Screen`: If checked, the image will be cropped from the
      screen video buffers. This is implied by the 'Whole Window'
      and 'Add Border' options

    - `Whole Window`: If checked, the whole pyFormex main window will be
      saved. If unchecked, only the current OpenGL viewport is saved.

    """
    default_size = None

    def __init__(self,path=None,pattern=None,exist=False,multi=False):
        """Create the dialog."""
        if path is None:
            path = pf.cfg['workdir']
        if pattern is None:
            pattern = ['img', 'icon', 'all']
        FileDialog.__init__(self, path, pattern, exist)
        grid = self.layout()
        nr = grid.rowCount()
        try:
            w, h = SaveImageDialog.default_size
        except:
            w, h = pf.canvas.getSize()
        from pyformex.gui import image
        formats = ['From Extension'] + image.imageFormats()
        self.fmt = InputCombo("Format:", None, choices=formats)
        self.qua = InputInteger("Quality:", -1)
        self.alp = QtGui.QCheckBox("Keep Alpha")
        self.ssz = InputCombo("Set Size:", None, choices=['None','Width','Height','Both'])
        self.siz = InputIVector("Size:", [w, h], fields=['W', 'H'])
        self.grb = QtGui.QCheckBox("Grab Screen")
        self.win = QtGui.QCheckBox("Whole Window")
        self.bor = QtGui.QCheckBox("Add Border")
        self.mul = QtGui.QCheckBox("Multi mode")
        self.hot = QtGui.QCheckBox("Activate '%s' hotkey" % pf.cfg['keys/save'])
        self.aut = QtGui.QCheckBox('Autosave mode')
        self.mul.setChecked(multi)
        self.hot.setChecked(multi)
        self.ssz.setToolTip("Adjust one or both image dimensions. Beware, this may result in incorrect results if transparency is used.")
        self.alp.setToolTip("Keep the alpha channel in the result (Not intended for normal use!).")
        self.grb.setToolTip("If checked, the image will be grabbed from the screen.\nThis requires that you have ImageMagick installed.")
        self.win.setToolTip("If checked in 'Grab Screen' mode,\nthe whole window is saved instead of just the canvas.")
        self.bor.setToolTip("If checked in `Whole Window' mode,\nthe window decorations will be included as well.")
        self.mul.setToolTip("If checked, multiple images can be saved\nwith autogenerated names.")
        self.hot.setToolTip("If checked, a new image can be saved\nby hitting the 'S' key when focus is in the Canvas.")
        self.aut.setToolTip("If checked, a new image will saved\non each draw() operation")

        grid.addWidget(self.fmt, nr, 0)
        grid.addWidget(self.qua, nr, 1)
        grid.addWidget(self.alp, nr, 2)
        nr += 1
        grid.addWidget(self.ssz, nr, 0)
        grid.addWidget(self.siz, nr, 1, 2)
        nr += 1
        grid.addWidget(self.grb, nr, 0)
        grid.addWidget(self.win, nr, 1)
        grid.addWidget(self.bor, nr, 2)
        nr += 1
        grid.addWidget(self.mul, nr, 0)
        grid.addWidget(self.hot, nr, 1)
        grid.addWidget(self.aut, nr, 2)


    def getResults(self):
        self.exec_()
        if self.result() == ACCEPTED:
            opt = mydict.Dict()
            opt.fm = self.fmt.value()
            opt.qu = SaveImageDialog.default_size = self.qua.value()
            opt.al = self.alp.isChecked()
            w,h = self.siz.value()
            resize = self.ssz.value()[0]
            if resize == 'W':
                h = -1
            elif resize == 'H':
                w = -1
            elif resize == 'N':
                w = h = -1
            opt.sz = (w,h)
            if resize == 'N':
                opt.sz = None  # THis forces grab from screen buffer
            opt.fn = str(self.selectedFiles()[0])
            opt.gr = self.grb.isChecked()
            opt.wi = self.win.isChecked()
            opt.bo = self.bor.isChecked()
            opt.mu = self.mul.isChecked()
            opt.hk = self.hot.isChecked()
            opt.au = self.aut.isChecked()
            return opt

        else:
            return {}


def selectFont():
    """Ask the user to select a font.

    A font selection dialog widget is displayed and the user is requested
    to select a font.
    Returns a font if the user exited the dialog with the :guilabel:`OK`
    button.
    Returns None if the user clicked :guilabel:`CANCEL`.
    """
    font, ok = QtGui.QFontDialog.getFont()
    if ok:
        return font
    else:
        return None



class ListSelection(InputDialog):
    """A dialog for selecting one or more items from a list.

    This is a convenient class which constructs an input dialog with a single
    input item: an InputList. It allows the user to select one or more items
    from a list. The constructor supports all arguments of the InputDialog and
    the InputList classes. The return value is the value of the InputList,
    not the result of the InputDialog.
    """
    def __init__(self,choices,caption='ListSelection',default=[],single=False,check=False,sort=False,*args,**kargs):
        """Create the SelectionList dialog."""
        InputDialog.__init__(self, caption=caption, items = [
            dict(name='input',value=default,itemtype='list',choices=choices,
                 text='',single=single,check=check,sort=sort,*args,**kargs),
            ],)


    def setValue(self, selected):
        """Mark the specified items as selected."""
        self['input'].setValue(selected)


    def value(self):
        """Return the selected items."""
        return self['input'].value()


    def getResults(self):
        """Show the modal dialog and return the list of selected values.

        If the user cancels the selection operation, the return value is None.
        Else, the result is always a list, possibly empty or with a single
        value.
        """
        self.exec_()
        if self.result() == ACCEPTED:
            return self.value()
        else:
            return None




# !! The QtGui.QColorDialog can not be instantiated or subclassed.
# !! The color selection dialog is created by the static getColor
# !! function.

def getColor(col=None,caption=None):
    """Create a color selection dialog and return the selected color.

    col is the initial selection.
    If a valid color is selected, its string name is returned, usually as
    a hex #RRGGBB string. If the dialog is canceled, None is returned.
    """
    col = QtGui.QColor.fromRgbF(*colors.GLcolor(col))
    dia = QtGui.QColorDialog
    col = dia.getColor(col)
    if col.isValid():
        return str(col.name())
    else:
        return None


# Can be replaced with InputDialog??
class GenericDialog(QtGui.QDialog):
    """A generic dialog widget.

    The dialog is formed by a number of widgets stacked in a vertical box
    layout. At the bottom is a horizontal button box with possible actions.

    - `widgets`: a list of widgets to include in the dialog
    - `title`: the window title for the dialog
    - `parent`: the parent widget. If None, it is set to pf.GUI.
    - `actions`: the actions to include in the bottom button box. By default,
      an 'OK' button is displayed to close the dialog. Can be set to None
      to avoid creation of a button box.
    - `default`: the default action, 'OK' by default.
    """

    def __init__(self,widgets,title=None,parent=None,actions=[('OK',)],default='OK'):
        """Create the Dialog"""
        if parent is None:
            parent = pf.GUI
        QtGui.QDialog.__init__(self, parent)
        if title is None:
            title = 'pyFormex Dialog'
        self.setWindowTitle(str(title))

        self.form = QtGui.QVBoxLayout()
        self.add(widgets)

        if actions is not None:
            but = ButtonBox(actions=actions, default=default, parent=self)
            self.form.addWidget(but)

        self.setLayout(self.form)


    def add(self,widgets,pos=-1):
        if not isinstance(widgets, list):
            widgets = [widgets]
        for w in widgets:
            if pos >= 0:
                ind = pos
            else:
                ind = pos+self.form.count()
            self.form.insertWidget(ind, w)


# Deprecated in 0.9.0
# Removed in 0.9.1
## class Tabs(QtGui.QTabWidget):
##     """_Present a list of widgets as a single tabbed widget.

##     - `items`: a list of (header,widget) tuples.
##     - `caption`:
##     - `parent`:
##     """
##     def __init__(self,items,parent=None):
##         """Create the TabWidget."""
##         utils.deprec("depr_tabs")
##         QtGui.QTabWidget.__init__(self,parent)
##         for header,widget in items:
##             self.addTab(widget,header)


# Deprecated in 0.9.0
# Removed in 0.9.1
## class TableDialog(GenericDialog):
##     """_A dialog widget to show/edit a two-dimensional array of items.

##     A convenience class representing a Table within a dialog.
##     """

##     def __init__(self,data,chead=None,rhead=None,title=None,parent=None,actions=[('OK',)],default='OK',edit=False):
##         """Create the Table dialog.

##         - data is a 2-D array of items, with nrow rows and ncol columns.
##         - chead is an optional list of ncol column headers.
##         - rhead is an optional list of nrow row headers.
##         """
##         utils.deprec("depr_tabledialog")
##         self.table = Table(data,chead=chead,rhead=rhead,edit=edit)
##         GenericDialog.__init__(self,
##                                [self.table],
##                                title=title, parent=parent,
##                                actions=actions,default=default)



#####################################################################
########### Text Display Widgets ####################################
#####################################################################


def updateText(widget,text,format=''):
    """Update the text of a text display widget.

    - `widget`: a widget that has the :meth:`setText`, :meth:`setPlainText`
      and :meth:`setHtml` methods to set the widget's text.
      Examples are :class:`QMessageBox` and :class:`QTextEdit`.
    - `text`: a multiline string with the text to be displayed.
    - `format`: the format of the text. If empty, autorecognition will be
      tried. Currently available formats are: ``plain``, ``html`` and
      ``rest`` (reStructuredText).

    This function allows to display other text formats besides the
    plain text and html supported by the widget.
    Any format other than ``plain`` or ``html`` will be converted to one
    of these before sending it to the widget. Currently, we convert the
    following formats:

    - ``rest`` (reStructuredText):
      If the :mod:docutils is available, `rest` text is converted to `html`,
      otherwise it will be displayed as plain text.
      A text is autorecognized as reStructuredText if its first
      line starts with '..'. Note: If you add a '..' line to your text to
      have it autorecognized as reST, be sure to have it followed with a
      blank line, or your first paragraph could be turned into comments.

    """
    # autorecognition
    if format not in ['plain', 'html', 'rest']:
        if isinstance(text, str) and text.startswith('..'):
            format = 'rest'

    # conversion
    if format == 'rest' and pf.cfg['gui/rst2html']:
        # Try conversion to html
        text = utils.rst2html(text)
        format = ''
        # We leave the format undefined, because we are not sure
        # that the conversion succeeded. QT will found out

    if format == 'plain':
        widget.setPlainText(text)
    elif format == 'html':
        widget.setHtml(text)
    else:
        # Default is to use QT's autorecognition
        if pf.PY3:
            if isinstance(text,bytes):
                text = text.decode()
        widget.setText(text)


class MessageBox(QtGui.QMessageBox):
    """A message box is a widget displaying a short text for the user.

    The message box displays a text, an optional icon depending on the level
    and a number of push buttons.

    - `text`: the text to be shown. This can be either plain text or html
      or reStructuredText.
    - `format`: the text format: either 'plain', 'html' or 'rest'.
      Any other value will try automatic recognition.
      Recognition of plain text and html is automatic.
      A text is autorecognized to be reStructuredText if its first
      line starts with '..' and is followed by a blank line.
    - `level`: defines the icon that will be shown together with the text.
      If one of 'question', 'info', 'warning' or 'error', a matching icon
      will be shown to hint the user about the type of message. Any other
      value will suppress the icon.
    - `actions`: a list of strings. For each string a pushbutton will be
      created which can be used to exit the dialog and remove the message.
      By default there is a single button labeled 'OK'.

    When the MessageBox is displayed with the :meth:`getResults()` method,
    a modal dialog is created, i.e. the user will have to click a button
    or hit the ESC key before he can continue.

    If you want a modeless dialog, allowing the user to continue while the
    message stays open, use the :meth:`show()` method to display it.
    """
    # TODO: This could be replaced with a generic InputDialog
    # Beware: the check option is used in warnings
    def __init__(self,text,format='',level='info',actions=['OK'],default=None,timeout=None,modal=None,parent=None,check=None):
        if parent is None:
            parent = pf.GUI
        QtGui.QMessageBox.__init__(self, parent)
        if modal is not None:
            self.setModal(modal)
        if default is None:
            default = actions[-1]
        updateText(self, text, format)
        icon = self.getIcon(level)
        if icon:
            self.setIcon(icon)

        # Get the buttons layout
        #layout = self.layout().itemAtPosition(2,0).widget().layout()
        #self._buttons = addActionButtons(layout, actions)

        for a in actions:
            b = self.addButton(a, QtGui.QMessageBox.AcceptRole)
            if a == default:
                self.setDefaultButton(b)

        addTimeOut(self, timeout, self.accept)
        self.checks = []
        if check:
            if not isinstance(check,list):
                check = [ check ]
            for text in check:
                self.checks.append(self.addCheck(text))

    def getIcon(self, level='noicon'):
        if level == 'info':
            return self.Information
        elif level == 'warning':
            return self.Warning
        elif level == 'error':
            return self.Critical
        elif level == 'question':
            return self.Question


    def addCheck(self, text):
        """Add a check field at the bottom of the layout."""
        grid = self.layout()
        nr = grid.rowCount()
        check = QtGui.QCheckBox(text)
        # Always use column 1: the icon is in column 0, the text in column 1
        grid.addWidget(check, nr, 1)
        return check


    def show(self,modal=False):
        self.setModal(modal)
        QtGui.QMessageBox.show(self)


    def getResults(self):
        """Display the message box and wait for user to click a button.

        This will show the message box as a modal dialog, so that the
        user has to click a button (or hit the ESC key) before he can continue.
        Returns the text of the button that was clicked or
        an empty string if ESC was hit.
        """
        self.show(modal=True)
        self.exec_()
        b = self.clickedButton()
        if not b:  # b == 0 or b is None
            b = self.defaultButton()
        if b:
            res = str(b.text())
        else:
            res = ''
        if self.checks:
            return res, [c.isChecked() for c in self.checks]
        else:
            return res


    def updateText(self,text,format=''):
        updateText(self._t, text, format)


class TextBox(QtGui.QDialog):
    """Display a text and wait for user response.

    Possible choices are 'OK' and 'CANCEL'.
    The function returns True if the OK button was clicked or 'ENTER'
    was pressed, False if the 'CANCEL' button was pressed or ESC was pressed.
    """
    def __init__(self,text,format=None,actions=[('OK',)],modal=None,parent=None,caption=None,mono=False,timeout=None,flags=None):
        if parent is None:
            parent = pf.GUI
        QtGui.QDialog.__init__(self, parent)
        if flags is not None:
            self.setWindowFlags(flags)
        if caption is None:
            caption = 'pyFormex-dialog'
        self.setWindowTitle('pyFormex Text Display')
        if modal is not None:
            self.setModal(modal)
        self._t = QtGui.QTextEdit()
        self._t.setReadOnly(True)
        updateText(self._t, text, format)
        self._b = ButtonBox(actions=actions, parent=self)#,stretch=[1,1])
        l = QtGui.QVBoxLayout()
        l.addWidget(self._t)
        l.addWidget(self._b)
        self.setLayout(l)
        self.resize(800, 400)
        if mono:
            font = QtGui.QFont("DejaVu Sans Mono")
            # font.setStyle(QtGui.QFont.StyleNormal)
            self.setFont(font)

        addTimeOut(self, timeout, self.accept)

    def getResults(self):
        return self.exec_() == ACCEPTED

    def updateText(self,text,format=''):
        updateText(self._t, text, format)


############################# Button box ###########################


def addActionButtons(layout,actions=[('Cancel',), ('OK',)],default=None,
                     parent=None):
    """Add a set of action buttons to a layout

    layout is a QLayout

    actions is a list of tuples (name,) or (name,function).
    If a function is specified, it will be executed on pressing the button.
    If no function is specified, and name is one of 'ok' or 'cancel' (case
    is ignored), the button will be bound to the dialog's 'accept'
    or 'reject' slot.
    If actions is None (default), it will be set to the default
    ``[('Cancel',),('OK',)]``.

    default is the name of the action to set as the default. If no default
    is given, it is set to the LAST button.

    Returns a list of QPushButtons.
    """
    if not pf.options.pyside:
        # In pyqt4, the clicked signal always sends a bool
        # We therefore provide a stripper function
        # We make the fist argument optional in case we get a case
        # that does not send the bool
        def stripFirstArg(func):
            def strippedFunc(bool=False):
                return func()
            return strippedFunc

    if actions is None:
        actions = [('Cancel',), ('OK',)]
    if actions and default is None:
        default = actions[-1][0].lower()
    blist = []
    for a in actions:
        name = a[0]
        if name == '---':
            spacer = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum )
            layout.addItem(spacer)
        else:
            if len(a) > 2:
                icon = a[2]
                icon = pyformexIcon(icon)
                b = QtGui.QPushButton(icon, '', parent)
            else:
                b = QtGui.QPushButton(name, parent)
            n = name.lower()
            if len(a) > 1 and callable(a[1]):
                slot = a[1]
            elif parent:
                if n == 'ok':
                    slot = parent.accept
                elif n == 'cancel':
                    slot = parent.reject
                else:
                    slot = parent.reject
            if not pf.options.pyside:
                # strip the bool arg off
                slot = stripFirstArg(slot)
            b.clicked.connect(slot)
            if n == default.lower():
                b.setDefault(True)
            layout.addWidget(b)
            blist.append(b)
    return blist


def addEffect(w,color=None):
    if color is not None:
        effect = QtGui.QGraphicsColorizeEffect()
        effect.setColor(QtGui.QColor(color))
        w.setGraphicsEffect(effect)

def addStyle(w,bgcolor=None):
    if bgcolor is not None:
        w.setStyleSheet("* { background-color: rgb(%s,%s,%s); }" % bgcolor)


class ButtonBox(QtGui.QWidget):
    """A box with action buttons.

    - `name`: a label to be displayed in front of the button box. An empty
      string will suppress it.
    - `actions`: a list of (button label, button function) tuples. The button
      function can be a normal callable function, or one of the values
      widgets.ACCEPTED or widgets.REJECTED. In the latter case, `parent`
      should be specified.
    - `default`: name of the action to set as the default. If no default
      is given, it will be set to the LAST button.
    - `parent`: the parent dialog holding this button box. It should be
      specified if one of the buttons actions is not specified or is
      widgets.ACCEPTED or widgets.REJECTED.
    """
    def __init__(self,name='',actions=None,default=None,parent=None,
                 spacer=False,stretch=[-1, -1],cmargin=(2, 2, 2, 2)):
        QtGui.QWidget.__init__(self, parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        layout = QtGui.QHBoxLayout()
        if name:
            self.label = QtGui.QLabel(name)
            layout.addWidget(self.label)
        if spacer:
            spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum )
            layout.addItem(spacer)
        for i in [0, -1]:
            if stretch[i] >= 0:
                layout.insertStretch(i, stretch[i])
        layout.setSpacing(0)
        #layout.setMargin(20)
        layout.setContentsMargins(*cmargin)
        self.buttons = addActionButtons(layout, actions, default, parent)
        self.setLayout(layout)

    def setText(self,text,index=0):
        """Change the text on button index."""
        self.buttons[index].setText(text)

    def setIcon(self,icon,index=0):
        """Change the icon on button index."""
        self.buttons[index].setIcon(icon)


############################# Coords box ###########################

# BV: this should be merged into InputPoint

class CoordsBox(QtGui.QWidget):
    """A widget displaying the coordinates of a point.


    """
    def __init__(self,ndim=3,readonly=False,*args):
        QtGui.QWidget.__init__(self,*args)
        layout = QtGui.QHBoxLayout(self)
        self.validator = QtGui.QDoubleValidator(self)
        self.values = []
        for name in ['x', 'y', 'z'][:ndim]:
            lbl = QtGui.QLabel(name)
            val = QtGui.QLineEdit('0.0')
            val.setValidator(self.validator)
            val.setReadOnly(readonly)
            layout.addWidget(lbl)
            layout.addWidget(val)
            self.values.append(val)
        self.setLayout(layout)

    def getValues(self):
        """Return the current x,y,z values as a list of floats."""
        return [ float(val.text()) for val in self.values ]

    def setValues(self, values):
        """Set the three values of the widget."""
        for v, val in zip(self.values, [float(v) for v in values]):
            v.setText(str(val))



############################# ImageView ###########################

class ImageView(QtGui.QLabel):
    """A widget displaying an image.

    """

    def __init__(self,image=None,maxheight=None,parent=None):
        """Create a new ImageView widget."""
        QtGui.QLabel.__init__(self, parent)
        self.setBackgroundRole(QtGui.QPalette.Base)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        if maxheight:
            self.setMaximumHeight(maxheight)
        if image is None:
            self.filename = self.image = None
        else:
            self.showImage(image, maxheight=maxheight)


    def showImage(self,image,maxheight=None):
        """Show an image in the viewer.

        image: either a filename or an existing QImage instance. If a filename,
        it should be an image file that can be read by the QImage constructor.
        Most image formats are understood by QImage. The variable
        gui.image.image_formats_qtr provides a list.
        """
        if isinstance(image, QtGui.QImage):
            filename = None
        else:
            filename = str(image)
            image = QtGui.QImage(filename)
            if image.isNull():
                try:
                    fname = pf.cfg['datadir']+'/image_not_loaded.png'
                    print(fname)
                    image = QtGui.QImage(pf.cfg['datadir']+'/image_not_loaded.png')
                except:
                    raise ValueError("Cannot load image file %s" % filename)
            if maxheight:
                image = image.scaledToHeight(maxheight)
        print("Size %sx%s" % (image.width(),image.height()))
        self.setPixmap(QtGui.QPixmap.fromImage(image))
        self.filename = filename
        self.image = image
        self.zoom = 1.0


    def value(self):
        return self.filename


# Deprecated aliases

FileSelection = FileDialog
GeometryFileSelection = GeometryFileDialog

# End
