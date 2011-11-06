#!/usr/bin/env python
##
##  This file is part of pyFormex 0.8.5     Sun Nov  6 17:27:05 CET 2011
##  pyFormex is a tool for generating, manipulating and transforming 3D
##  geometrical models by sequences of mathematical operations.
##  Home page: http://pyformex.org
##  Project page:  https://savannah.nongnu.org/projects/pyformex/
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
"""Python intro

A short introduction to some aspects of the Python programming language
"""

for light in [ 'green','yellow','red','black',None]:
    if light == 'red':
        print 'stop'
    elif light == 'yellow':
        print 'brake'
    elif light == 'green':
        print 'drive'
    else:
        print 'THE LIGHT IS BROKEN!'



appreciation = { 0: 'not driving', 30:'slow', 60:'normal', 90:'dangerous', 120:'suicidal'}

for i in range(5):
    speed = 30*i
    print "%s. Driving at speed %s is %s" % (i,speed,appreciation[speed])


