#!/usr/bin/env pyformex
# $Id$
#
"""Wire stent analysis"""

#######################################################################
# Setting this path correctly is required to import the analysis module
# You need calpy >= 0.3.3
# It can be downloaded from ftp://bumps.ugent.be/calpy/
calpy_path = '/usr/local/lib/calpy-0.3.3'
calpy_path = '/home/bene/prj/calpy/calpy'
#######################################################################

from examples.WireStent import DoubleHelixStent
import datetime

# create a Doublehelix stent
stent_diameter = 10.
stent_length = 150.
wire_diameter = 0.2
number_wires = 6
pitch_angle = 30.

# during testing
stent_length = 20.
stent = DoubleHelixStent(stent_diameter,stent_length,
                         wire_diameter,number_wires,pitch_angle,nb=1).all()

if GD.options.gui:
    # draw it
    clear()
    draw(stent,view='iso')


############################################
##### NOW load the calpy analysis code #####

# Check if we have calpy:
import sys
sys.path.append(calpy_path)
try:
    import calpy
    calpy.options.optimize=True
    from fe_util import *
    from beam3d import *
except ImportError:
    import globaldata as GD
    warning("You need calpy-0.3.3 or higher to perform the analysis.\nIt can be obtained from ftp://bumps.ugent.be/calpy/\nYou should also set the correct calpy installation path\n in this example's source file\n(%s).\nThe calpy_path variable is set near the top of that file.\nIts current value is: %s" % (GD.cfg.curfile,calpy_path))
    exit()
    
############################################

nel = stent.nelems()
print "Number of elements: %s" % nel
print "Original number of nodes: %s" % stent.nnodes()
# Create FE model
message("Creating FE model: for a large model this can take a LOT of time!")
nodes,elems = stent.nodesAndElements()
nnod = nodes.shape[0]
print "Compressed number of nodes: %s" % nnod

# Create an extra node on the axis for beam orientations
extra_node = array([[-10.0,0.0,0.0]])
coords = concatenate([nodes,extra_node])
nnod = coords.shape[0]
print "Final number of nodes: %s" % nnod

# Create element definitions: i j k matnr, where k = nnod (the extra node)
# while incrementing node numbers with 1 (for calpy)
# (remember props are 1,2,3, so are OK)

thirdnode = nnod*ones(shape=(nel,1))
matnr = reshape(stent.p,(nel,1))
elements = concatenate([elems+1,thirdnode,matnr],1)

# Create endnode sets (with calpy numbering)
bb = stent.bbox()
zlo = bb[0][2]
zhi = bb[1][2]
zmi = (zhi+zlo)/2.
count = zeros(nnod)
for n in elems.flat:
    count[n] += 1
unconnected = arange(nnod)[count==1]
zvals = nodes[unconnected][:,2]
print zlo,zhi,zmi,zvals
end0 = unconnected[zvals<zmi]
end1 = unconnected[zvals>zmi]
print "Nodes at end 0:",end0
print "Nodes at end 1:",end1

# Boundary conditions
s = ""
for n in end0+1:   # NOTICE THE +1 !
    s += "  %d  1  1  1  1  1  1\n" % n
# Also clamp the fake extra node
s += "  %d  1  1  1  1  1  1\n" % nnod
print "Specified boundary conditions"
print s
bcon = ReadBoundary(nnod,6,s)
NumberEquations(bcon)

# Materials (E, G, rho, A, Izz, Iyy, J)
mats = zeros((3,7),float)
A = math.pi * wire_diameter ** 2
Izz = Iyy = math.pi * wire_diameter ** 4 / 4
J = math.pi * wire_diameter ** 4 / 2
E = 207000.
nu = 0.3
G = E/2/(1+nu)
rho = 0.
mats[0] = mats[2] = [ E, G, rho, A, Izz, Iyy, J ]
mats[1] = [E, 0.0, 0.0, A*10**3, Izz*10**6, Iyy*10**6, 0.0]

# Create loads
nlc = 1
ndof = bcon.max()
loads = zeros((ndof,nlc),float)
zforce = [ 0.0, 0.0, 1.0, 0.0, 0.0, 0.0 ]
for n in end1: # NO +1 HERE!
    loads[:,0] = AssembleVector(loads[:,0],zforce,bcon[n,:])

# Perform analysis
displ,frc = static(coords,bcon,mats,elements,loads,Echo=True)


################################
#Using pyFormex as postprocessor
################################

if GD.options.gui:

    from colorscale import *
    import decors

    # Creating a formex for displaying results is fairly easy
    elems = elements[:,:2]-1
    results = Formex(coords[elems])
    clear()
    draw(results,color=black)

    # Now try to give the formex some meaningful colors.
    # The frc array returns element forces and has shape
    #  (nelems,nforcevalues,nloadcases)
    # In this case there is only one resultant force per element (the
    # normal force), and only load case; we still need to select the
    # scalar element result values from the array into a onedimensional
    # vector val. 
    val = frc[:,0,0]
    # create a colorscale
    CS = ColorScale([blue,yellow,red],val.min(),val.max(),0.,2.,2.)
    cval = array(map(CS.color,val))
    #aprint(cval,header=['Red','Green','Blue'])
    clear()
    draw(results,color=cval)

    bgcolor('lightgreen')
    linewidth(3)
    drawtext('Normal force in the members',450,100,'tr24')
    CL = ColorLegend(CS,100)
    CLA = decors.ColorLegend(CL,10,10,30,200) 
    GD.canvas.addDecoration(CLA)
    GD.canvas.update()

    # and a deformed plot on multiple scales
    dscales = arange(1,6) * 1.0
    loadcase = 0
    for dscale in dscales:
        dcoords = coords + dscale * displ[:,0:3,loadcase]
        clear()
        GD.canvas.addDecoration(CLA)
        linewidth(1)
        draw(results,color='darkgreen',wait=False)
        linewidth(3)
        deformed = Formex(dcoords[elems])
        draw(deformed,color=cval)
        drawtext('Normal force in the truss members',450,100,'tr24')
        drawtext('Deformed geometry (scale %.2f)' % dscale,450,70,'tr24')


# End
