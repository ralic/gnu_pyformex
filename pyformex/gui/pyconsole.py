# $Id$
##
##  This file is part of pyFormex
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
"""Interactive Python interpreter for pyFormex.

"""
from __future__ import print_function

import os
import re
import sys
import code
import readline
import atexit


from gui import QtGui, QtCore
from gui.guimain import Board
import utils


class HistoryConsole(code.InteractiveConsole):
    def __init__(self,locals=None,filename="<console>",
                 histfile=os.path.expanduser("~/.console-history")):
        code.InteractiveConsole.__init__(self,locals,filename)
        self.init_history(histfile)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline,"read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.save_history,histfile)

    def save_history(self, histfile):
        readline.write_history_file(histfile)


class PyConsole(QtGui.QTextEdit):

    def __init__(self,parent=None):

        super(PyConsole,self).__init__(parent)

        #sys.stdout = self
        #sys.stderr = self
        self.refreshMarker = False # to change back to >>> from ...
        self.multiLine = False # code spans more than one line
        self.command = '' # command to be ran
        self.history = [] # list of commands entered
        self.historyIndex = -1
        self.interpreterLocals = {}

        self.setAcceptRichText(False)
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
        self.setMinimumSize(24,24)
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)

        #self.buffer = ''
        font = QtGui.QFont("DejaVu Sans Mono")
        #font.setStyle(QtGui.QFont.StyleNormal)
        self.setFont(font)
        self.stdout = self.stderr = None # redirected streams


        # initilize interpreter with self locals
        interpreterLocals = locals()
        if interpreterLocals:
            # when we pass in locals, we don't want it to be named "self"
            # so we rename it with the name of the class that did the passing
            # and reinsert the locals back into the interpreter dictionary
            selfName = interpreterLocals['self'].__class__.__name__
            interpreterLocalVars = interpreterLocals.pop('self')
            self.interpreterLocals[selfName] = interpreterLocalVars
        else:
            self.interpreterLocals = interpreterLocals
        self.interpreter = code.InteractiveInterpreter(self.interpreterLocals)


    def write(self,s,color=None):
        """Write a string to the message board.

        If a color is specified, the text is shown in the specified
        color, but the default board color remains unchanged.
        """
        if color:
            savecolor = self.textColor()
            self.setTextColor(QtGui.QColor(color))
        else:
            savecolor = None
        # A single blank character seems to be generated by a print
        # instruction containing a comma: skip it
        if s == ' ':
            return
        #self.buffer += '[%s:%s]' % (len(s),s)
        if len(s) > 0:
            if not s.endswith('\n'):
                s += '\n'
            self.insertPlainText(s)
            textCursor = self.textCursor()
            textCursor.movePosition(QtGui.QTextCursor.End)
            self.setTextCursor(textCursor)
        if savecolor:
            self.setTextColor(savecolor)
        self.ensureCursorVisible()


    def save(self,filename):
        """Save the contents of the board to a file"""
        fil = open(filename,'w')
        fil.write(self.toPlainText())
        fil.close()


    def flush(self):
        self.update()


    def redirect(self,onoff):
        """Redirect standard and error output to this message board"""
        if onoff:
            sys.stderr.flush()
            sys.stdout.flush()
            self.stderr = sys.stderr
            self.stdout = sys.stdout
            sys.stderr = self
            sys.stdout = self
        else:
            if self.stderr:
                sys.stderr = self.stderr
            if self.stdout:
                sys.stdout = self.stdout
            self.stderr = None
            self.stdout = None


    def printBanner(self):
        self.write(sys.version)
        self.write(' on ' + sys.platform + '\n')
        msg = 'Type !hist for a history view and !hist(n) history index recall'
        self.write(msg + '\n')


    def marker(self):
        if self.multiLine:
            self.insertPlainText('... ')
        else:
            self.insertPlainText('>>> ')


    def updateInterpreterLocals(self, newLocals):
        self.interpreter.locals = newLocals


    def clearCurrentBlock(self):
        # block being current row
        length = len(self.document().lastBlock().text()[4:])
        if length == 0:
            return None
        else:
            # should have a better way of doing this but I can't find it
            [self.textCursor().deletePreviousChar() for x in xrange(length)]
        return True

    def recallHistory(self):
        # used when using the arrow keys to scroll through history
        self.clearCurrentBlock()
        if self.historyIndex <> -1:
            self.insertPlainText(self.history[self.historyIndex])
        return True

    def customCommands(self,command):

        if command == '!hist': # display history
            self.append('') # move down one line
            # vars that are in the command are prefixed with ____CC and deleted
            # once the command is done so they don't show up in dir()
            backup = self.interpreterLocals.copy()
            history = self.history[:]
            history.reverse()
            for i,x in enumerate(history):
                iSize = len(str(i))
                delta = len(str(len(history))) - iSize
                line = line = ' ' * delta + '%i: %s' % (i,x) + '\n'
                self.write(line)
            self.updateInterpreterLocals(backup)
            return True
        import re
        if re.match('!hist\(\d+\)',command): # recall command from history
            backup = self.interpreterLocals.copy()
            history = self.history[:]
            history.reverse()
            index = int(command[6:-1])
            self.clearCurrentBlock()
            command = history[index]
            if command[-1] == ':':
                self.multiLine = True
            self.write(command)
            self.updateInterpreterLocals(backup)
            return True

        return False

    def keyPressEvent(self,event):

        if event.key() == QtCore.Qt.Key_Escape:
            # proper exit
            self.interpreter.runsource('exit()')

        if event.key() == QtCore.Qt.Key_Down:
            if self.historyIndex == len(self.history):
                self.historyIndex -= 1
            try:
                if self.historyIndex > -1:
                    self.historyIndex -= 1
                    self.recallHistory()
                else:
                    self.clearCurrentBlock()
            except:
                pass
            return None

        if event.key() == QtCore.Qt.Key_Up:
            try:
                if len(self.history) - 1 > self.historyIndex:
                    self.historyIndex += 1
                    self.recallHistory()
                else:
                    self.historyIndex = len(self.history)
            except:
                pass
            return None

        if event.key() == QtCore.Qt.Key_Home:
            # set cursor to position 4 in current block. 4 because that's where
            # the marker stops
            blockLength = len(self.document().lastBlock().text()[4:])
            lineLength = len(self.document().toPlainText())
            position = lineLength - blockLength
            textCursor = self.textCursor()
            textCursor.setPosition(position)
            self.setTextCursor(textCursor)
            return None

        if event.key() in [QtCore.Qt.Key_Left,QtCore.Qt.Key_Backspace]:
            # don't allow deletion of marker
            if self.textCursor().positionInBlock() == 4:
                return None

        if event.key() in [QtCore.Qt.Key_Return,QtCore.Qt.Key_Enter]:
            # set cursor to end of line to avoid line splitting
            textCursor = self.textCursor()
            position = len(self.document().toPlainText())
            textCursor.setPosition(position)
            self.setTextCursor(textCursor)

            line = str(self.document().lastBlock().text())[4:] # remove marker
            line.rstrip()
            self.historyIndex = -1

            if self.customCommands(line):
                return None
            else:
                try:
                    line[-1]
                    self.haveLine = True
                    if line[-1] == ':':
                        self.multiLine = True
                    self.history.insert(0,line)
                except:
                    self.haveLine = False

                if self.haveLine and self.multiLine: # multi line command
                    self.command += line + '\n' # + command and line
                    self.append('') # move down one line
                    self.marker() # handle marker style
                    return None

                if self.haveLine and not self.multiLine: # one line command
                    self.command = line # line is the command
                    self.append('') # move down one line
                    self.interpreter.runsource(self.command)
                    self.command = '' # clear command
                    self.marker() # handle marker style
                    return None

                if self.multiLine and not self.haveLine: # multi line done
                    self.append('') # move down one line
                    self.interpreter.runsource(self.command)
                    self.command = '' # clear command
                    self.multiLine = False # back to single line
                    self.marker() # handle marker style
                    return None

                if not self.haveLine and not self.multiLine: # just enter
                    self.append('')
                    self.marker()
                    return None
                return None

        # allow all other key events
        super(PyConsole,self).keyPressEvent(event)



if utils.hasModule('ipython-qt'):


    from IPython.zmq.ipkernel import IPKernelApp
    from IPython.lib.kernel import find_connection_file
    from IPython.frontend.qt.kernelmanager import QtKernelManager
    from IPython.frontend.qt.console.rich_ipython_widget import RichIPythonWidget
    from IPython.utils.traitlets import TraitError
    from gui import QtGui, QtCore

    def event_loop(kernel):
        kernel.timer = QtCore.QTimer()
        kernel.timer.timeout.connect(kernel.do_one_iteration)
        kernel.timer.start(1000*kernel._poll_interval)

    def default_kernel_app():
        app = IPKernelApp.instance()
        app.initialize(['python', '--pylab=qt'])
        app.kernel.eventloop = event_loop
        return app

    def default_manager(kernel):
        connection_file = find_connection_file(kernel.connection_file)
        manager = QtKernelManager(connection_file=connection_file)
        manager.load_connection_file()
        manager.start_channels()
        atexit.register(manager.cleanup_connection_file)
        return manager

    def console_widget(manager):
        widget = RichIPythonWidget()
        widget.kernel_manager = manager
        return widget

    def terminal_widget(**kwargs):
        kernel_app = default_kernel_app()
        manager = default_manager(kernel_app)
        widget = console_widget(manager)
        #update namespace
        kernel_app.shell.user_ns.update(kwargs)
        kernel_app.start()
        return widget


    class mainWindow(QtGui.QMainWindow):
        def __init__(self, parent=None):
            super(mainWindow, self).__init__(parent)

            self.console = terminal_widget(testing=123)
            self.setCentralWidget(self.console)

# End
