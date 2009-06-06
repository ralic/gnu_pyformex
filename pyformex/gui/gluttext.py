# $Id$

"""2D text decorations using GLUT fonts"""

import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT

from drawable import *
from decors import Decoration


# Needed to initialize the fonts
GLUT.glutInit([])

import colors

### Some drawing functions ###############################################

# These are the available GLUT fonts.
GLUTFONTS = {
    '9x15' : GLUT.GLUT_BITMAP_9_BY_15,
    '8x13' : GLUT.GLUT_BITMAP_8_BY_13,
    'tr10' : GLUT.GLUT_BITMAP_TIMES_ROMAN_10,
    'tr24' : GLUT.GLUT_BITMAP_TIMES_ROMAN_24,
    'hv10' : GLUT.GLUT_BITMAP_HELVETICA_10,
    'hv12' : GLUT.GLUT_BITMAP_HELVETICA_12,
    'hv18' : GLUT.GLUT_BITMAP_HELVETICA_18,
}

GLUTFONTALIAS = {
    'fixed' : ('9x15','8x13'),
    'serif' : ('times','tr10','tr24'),
    'sans'  : ('helvetica','hv10','hv12','hv18'),
    }

def glutFontSelect(font=None,size=None):
    """Select one of the glut fonts using a font + size description.

    font is one of: 'fixed', 'serif', 'sans'
    size is an int that will be rounded to the nearest available size.
    """
    if size is None and font in GLUTFONTS:
        return font
    if font is None:
        font = 'fixed'
    for k in GLUTFONTALIAS:
        if font in GLUTFONTALIAS[k]:
            font = k
            break
    if size is None or not size > 0:
        size = 14
    if font == 'fixed':
        selector = [ (0,'8x13'), (14,'9x15') ]
    elif font == 'serif':
        selector = [ (0,'tr10'), (16,'tr24') ]
    else:
        selector = [ (0,'hv10'), (12,'hv12'), (16,'hv18') ]
    sel = selector[0]
    for s in selector[1:]:
        if s[0] <= size:
            sel = s

    return sel[1]


def getFont(font,size):
    return glutFont(glutFontSelect(font,size))


def glutFont(font):
    """Return GLUT font designation for the named font.

    The recognized font names are:
      fixed: '9x15', '8x13',
      times-roman: 'tr10', 'tr24'
      helvetica:   'hv10', 'hv12',  'hv18'
    If an unrecognized string is  given, the default is 9x15.
    """
    return GLUTFONTS.get(font,GLUTFONTS['9x15'])



def glutFontHeight(font):
    """Return the height of the named glut font.

    This supposes that the last two characters of the name
    hold the font height.
    """
    return int(font[-2:])


def glutRenderText(text,font):
    """Draw a text in given font at the current rasterpoint.

    font should be one  of the legal fonts returned by glutFont().
    If text is not a string, it will be formatted to a string
    before drawing.
    After drawing, the rasterpos will have been updated!
    """
    for character in str(text):
        GLUT.glutBitmapCharacter(font, ord(character))


def glutBitmapLength(font, text):
    """ Compute the length in pixels of a text string in given font.

    We use our own fucntion to calculate the length because the builtin
    has a bug.
    """
    len = 0
    for c in text:
        len += GLUT.glutBitmapWidth(font, ord(c))
    return len


def glutDrawText(text, x,y, font='9x15', adjust='left'):
    """Draw the given text at given 2D position in window.

    If adjust == 'center', the text will be horizontally centered on
    the insertion point.
    If adjust == 'right', the text will be right aligned on the point.
    Any other setting will align the text left.
    Default is to center.
    """
    font = '9x15'
    height = glutFontHeight(font)
    if type(font) == str:
        font = glutFont(font)
    #print "font = ",font
    if adjust != 'left':
        len1 = glutBitmapLength(font, text)
##  UNCOMMENT THESE LINES TO SEE WHEN glutBitmapLength GOES WRONG !
##        len2 = GLUT.glutBitmapLength(font, text)
##        if len1 != len2:
##            print "incorrect glutBitmapLength",len1,len2
        if adjust == 'center':
            x -= len1/2
        elif adjust == 'right':
            x -= len1
        elif adjust == 'under':
            x -= len1/2
            y -= 2* height
        elif adjust == 'above':
            x -= len1/2
            y += height
    GL.glRasterPos2f(float(x),float(y));
    glutRenderText(text,font)


class GlutText(Decoration):
    """A viewport decoration showing a text."""

    def __init__(self,text,x,y,font='9x15',size=None,adjust='left',color=None):
        """Create a text actor"""
        Decoration.__init__(self,x,y)
        self.text = str(text)
        self.font = glutFontSelect(font,size)
        #print "SELECTED GLUT TEXT FONT %s" % self.font 
        self.adjust = adjust
        self.color = saneColor(color)

    def drawGL(self,mode='wireframe',color=None):
        """Draw the text."""
        #print 'DRAWING THE TEXT'
        if self.color is not None: 
            GL.glColor3fv(self.color)
        glutDrawText(self.text,self.x,self.y,self.font,self.adjust)


# End
