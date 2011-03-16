#!/usr/bin/env pyformex

"""Exporting finite element models in code Aster file formats (.mail and .comm).

"""

from plugins.fe_abq import fmtData
from plugins.properties import *
from plugins.fe import *
from mydict import Dict,CDict
import pyformex as pf
from datetime import datetime
import os,sys



def astInputNames(job,extension='mail'):
    """Returns corresponding Code Aster input filename.

    job should be a jobname, with or without directory part, but without extension
    
    The extension can be mail or comm.
    
    The jobname is the basename without the extension and the directory part.
    The filename is the abspath of the job with extension.
    """
    jobname = os.path.basename(job)
    filename = os.path.abspath(job)
    if extension in ['mail','comm']:
        filename += '.%s' % extension
    else:
        raise ValueError,"Extension should be mail or comm"
    return jobname,filename


def nsetName(p):
    """Determine the name for writing a node set property."""
    if p.name is None:
        return 'Nall'
    else:
        return p.name


def esetName(p):
    """Determine the name for writing an element set property."""
    if p.name is None:
        return 'Eall'
    else:
        return p.name


def writeNodes(fil,nodes,type,name=None):
    """Write nodal coordinates.
    
    Type can be 2D or 3D.
    """
    if not type in ['2D','3D']:
        raise ValueError,"Type should be 2D or 3D"
    out = 'COOR_%s' % type
    if name is not None:
        out += ' nom = %s' % name
    fil.write('%s\n'% out)
    if type == '2D':
        nodes = nodes[:,:2]        
    nn = nodes.shape[1]
    fmt = 'N%d' + nn*' %14.6e' + '\n'
    for i,n in enumerate(nodes):
        fil.write(fmt % ((i,)+tuple(n)))
    fil.write('FINSF\n')
    fil.write('%\n')


def writeElems(fil,elems,type,name=None,eid=None,eofs=0,nofs=0):
    """Write element group of given type.

    elems is the list with the element node numbers.
    The elements are added to the named element set. 
    The eofs and nofs specify offsets for element and node numbers.
    If eid is specified, it contains the element numbers increased with eofs.
    """
    out = type
    if name is not None:
        out += ' nom = %s' % name
    fil.write('%s\n'% out)
    nn = elems.shape[1]
    if nn < 5:
        fmt = 'M%d' + nn*' N%d' + '\n'
    else:
        fl = nn/4
        fmt = 'M%d' + fl*(4*' N%d' + '\n')
        if nn%4 != 0:
            fmt += (nn%4)*' N%d' + '\n'
    
    if eid is None:
        eid = arange(elems.shape[0])
    else:
        eid = asarray(eid)
    for i,e in zip(eid+eofs,elems+nofs):
        fil.write(fmt % ((i,)+tuple(e)))

    fil.write('FINSF\n')
    fil.write('%\n')


def writeSet(fil,type,name,set):
    """Write a named set of nodes or elements (type=NSET|ELSET)

    `set` is a list of node/element numbers,
    in which case the `ofs` value will be added to them.
    """
    if not set.dtype.kind == 'S':
        if type == 'NSET':
            fil.write('GROUP_NO nom = %s\n' % name)
            cap = 'N'
        elif type == 'ELSET':
            fil.write('GROUP_MA nom = %s\n' % name)
            cap = 'M'
        else:
            raise ValueError,"Type should be NSET or ELSET"
            
        for i in set:
            fil.write('%s%d\n' % (cap,i))
        fil.write('FINSF\n')
        fil.write('%\n')


def fmtHeadingMesh(text=''):
    """Format the heading of the Code Aster mesh file (.mail)."""
    out = """TITRE
Code Aster mail file created by %s (%s)
%s
FINSF
""" % (pf.Version,pf.Url,text)
    return out


def fmtHeadingComm(text=''):
    """Format the heading of the Code Aster command file (.comm)."""
    out = """#
# Code Aster command file created by %s (%s)
# %s
""" % (pf.Version,pf.Url,text)
    return out


def fmtEquation(prop):
    """Format multi-point constraint using an equation
    
    Required:
    - name
    - equation
    
    Optional:
    - coefficient
    
    Equation should be a list, which contains the different terms of the equation.
    Each term is again a list with three values:
    - First value: node number
    - Second value: degree of freedom
    - Third value: multiplication coefficient of the term
    
    The sum of the different terms should be equal to the coefficient.
    If this coefficient is not specified, the sum of the terms should be equal to zero.
    
    Example: P.nodeProp(name='link',equation=[[209,1,1],[32,1,-1]])
    
    In this case, the displacement in Y-direction of node 209 and 32 should be equal.
    """
    
    dof = ['DX','DY','DZ']
    for p in prop:
        out = '%s = AFFE_CHAR_MECA(\n' % p.name
        out += '    MODELE=Model,\n'
        out += '    LIAISON_DDL=(\n'
        l1 = '        _F(NOEUD=('
        l2 = '           DDL=('
        l3 = '           COEF_MULT=('
        for i in p.equation:
            l1 += '\'N%s\',' % i[0]
            l2 += '\'%s\',' % dof[i[1]]
            l3 += '%s,' % i[2]
        out += l1 + '),\n' + l2 + '),\n' + l3 + '),\n'
        coef = 0
        if p.coefficient is not None:
            coef = p.coefficient
        out += '          COEF_IMPO=%s,),\n' % coef
    out += '          ),\n'
    out += '    );\n\n'
    return out


def fmtDisplacements(prop):
    """Format nodal boundary conditions
    
    Required:
    - set
    - name
    - displ
    
    Displ should be a a list of tuples (dofid,value)
    
    Set can be a list of node numbers, or a set name (string).
    
    Example 1: P.nodeProp(set='bottom',bound=[(0,0),(1,0),(2,0)])
    Example 2: P.nodeProp(name='rot',set=[2],bound=[(3,30)])
    
    In the first example, the displacements of the nodes in the set 'bottom' are zero.
    In the second example, a rotation is imposed around the X-axis on node number 2.
    """
    
    dof = ['DX','DY','DZ','DRX','DRY','DRZ']
    out = ''
    for i,p in enumerate(prop):
        out += 'displ%s = AFFE_CHAR_MECA(\n' % i
        out += '    MODELE=Model,\n'
        out += '    DDL_IMPO=\n'
        out += '        _F(GROUP_NO=(\'%s\'),\n' % p.name.upper()
        for j in p.displ:
            out += '           %s=%s,\n' % (dof[j[0]],j[1])
        out += '          ),\n'
        out += '    );\n'
    return out


def fmtMaterial(prop):
    """Write a material section.
    """
    
    # TO DO!!!

solid3d_elems = [
    'HEXA8',]
    

def fmtSections(prop):
    """Write element sections.

    prop is a an element property record with a section and eltype attribute
    """
    
    out1 = 'Model=AFFE_MODELE(\n'
    out1 += '    MAILLAGE=Mesh,\n'
    out1 += '    AFFE=(\n'
    out2 = ''
    out3 = 'Mat=AFFE_MATERIAU(\n'
    out3 += '    MAILLAGE=Mesh,\n'
    out3 += '    AFFE=(\n'

    for p in prop:
        setname = esetName(p)
        el = p.section
        eltype = p.eltype.upper()
        mat = el.material
        
        out1 += '        _F(GROUP_MA=\'%s\',\n' % setname.upper()
        out1 += '           PHENOMENE=\'MECANIQUE\',\n'      
        
        out3 += '        _F(GROUP_MA=\'%s\',\n' % setname.upper()
        
        if mat is not None:
            #out2 += fmtMaterial(mat)
            print 'hier'
        ############
        ## 3DSOLID elements
        ##########################
        if eltype in solid3d_elems:
            if el.sectiontype.upper() == '3DSOLID':
                out1 += '           MODELISATION=\'3D\'),\n'
                out3 += '           MATER=%s),\n' % mat.name

    out1 += '          ),\n'
    out1 += '    );\n'
    out3 += '          ),\n'
    out3 += '    );\n'
    
    return out1 + out2 + out3


class AstData(object):
    """Contains all data required to write the Code Aster mesh (.mail) and command (.comm) files.
        
    - `model` : a :class:`Model` instance.
    - `prop` : the `Property` database.
    - `steps` : a list of `Step` instances.
    - `res` : a list of `Result` instances.
    - `out` : a list of `Output` instances.
    - `bound` : a tag or alist of the initial boundary conditions.
      The default is to apply ALL boundary conditions initially.
      Specify a (possibly non-existing) tag to override the default.

    """
    
    def __init__(self,model,prop,nprop=None,eprop=None,steps=[],res=[],out=[],bound=None,type='3D'):
        """Create new AstData."""
        if not isinstance(model,Model) or not isinstance(prop,PropertyDB):
            raise ValueError,"Invalid arguments: expected Model and PropertyDB, got %s and %s" % (type(model),type(prop))
        
        self.model = model
        self.prop = prop
        self.nprop = nprop
        self.eprop = eprop
        self.bound = bound
        self.steps = steps
        self.res = res
        self.out = out
        self.type = type


    def writeMesh(self,jobname=None,header=''):
        """Write a Code Aster mesh file (.mail).
        """
        
        # Create the Code Aster mesh file
        if jobname is None:
            jobname,filename = 'Test',None
            fil = sys.stdout
        else:
            jobname,filename = astInputNames(jobname,extension='mail')
            fil = file(filename,'w')
            pf.message("Writing mesh to file %s" % (filename))
        
        fil.write(fmtHeadingMesh("""Model: %s     Date: %s      Created by pyFormex
Script: %s 
%s
""" % (jobname, datetime.now(), pf.scriptName, header)))

        # write coords
        nnod = self.model.nnodes()
        pf.message("Writing %s nodes" % nnod)
        writeNodes(fil,self.model.coords,self.type)


        # write elements
        pf.message("Writing elements and element sets")
        telems = self.model.celems[-1]
        nelems = 0
        for p in self.prop.getProp('e'):
            if p.set is not None:
                # element set is directly specified
                set = p.set
            elif p.prop is not None:
                # element set is specified by eprop nrs
                if self.eprop is None:
                    raise ValueError,"elemProp has a 'prop' field but no 'eprop' was specified"
                set = where(self.eprop == p.prop)[0]
            else:
                # default is all elements
                set = range(telems)
            
            setname = esetName(p)
            
            if p.has_key('eltype'):
                print('Writing elements of type %s: %s' % (p.eltype,set))
                gl,gr = self.model.splitElems(set)
                elems = self.model.getElems(gr)
    
                elnrs = array([]).astype(int)
                els = array([]).astype(int)
                for i in elems:
                    nels = len(i)
                    if nels > 0:
                        els = append(els,i).reshape(-1,i.shape[1])
                        nelems += nels
                writeElems(fil,els,p.eltype,name=setname,eid=set)
                
            else:
                pf.message("Writing element sets")
                writeSet(fil,'NSET',setname,set)

        pf.message("Total number of elements: %s" % telems)
        if nelems != telems:
            pf.message("!! Number of elements written: %s !!" % nelems)


        # write node sets
        pf.message("Writing node sets")
        for p in self.prop.getProp('n',attr=['set']):
            if p.set is not None:
                # set is directly specified
                set = p.set
            elif p.prop is not None:
                # set is specified by nprop nrs
                if self.nprop is None:
                    raise ValueError,"nodeProp has a 'prop' field but no 'nprop' was specified"
                set = where(self.nprop == p.prop)[0]
            else:
                # default is all nodes
                set = range(self.model.nnodes())
                
            setname = nsetName(p)
            writeSet(fil,'NSET',setname,set)


        ## # write element sets
        ## pf.message("Writing element sets")
        ## for p in self.prop.getProp('e',noattr=['eltype']):
            ## if p.set is not None:
                ## # element set is directly specified
                ## set = p.set
            ## elif p.prop is not None:
                ## # element set is specified by eprop nrs
                ## if self.eprop is None:
                    ## raise ValueError,"elemProp has a 'prop' field but no 'eprop' was specified"
                ## set = where(self.eprop == p.prop)[0]
            ## else:
                ## # default is all elements
                ## set = range(telems)

            ## setname = esetName(p)
            ## writeSet(fil,'ELSET',setname,set)
            
        
        fil.write('FIN')
            
        if filename is not None:
            fil.close()
        pf.message("Wrote Code Aster mesh file (.mail) %s" % filename)
    

    def writeComm(self,jobname=None,header=''):

        # Create the Code Aster command file
        if jobname is None:
            jobname,filename = 'Test',None
            fil = sys.stdout
        else:
            jobname,filename = astInputNames(jobname,extension='comm')
            fil = file(filename,'w')
            pf.message("Writing command to file %s" % (filename))
        
        fil.write(fmtHeadingComm("""Model: %s     Date: %s      Created by pyFormex
# Script: %s 
# %s
#
""" % (jobname, datetime.now(), pf.scriptName, header)))
        
        fil.write('DEBUT();\n')
        fil.write('Mesh=LIRE_MAILLAGE(INFO=2,);\n')
        
        prop = self.prop.getProp('e',attr=['section','eltype'])
        if prop:
            pf.message("Writing element sections")
            fil.write(fmtSections(prop))
        
        prop = self.prop.getProp('n',attr=['displ'])
        if prop:
            pf.message("Writing displacement boundary conditions")
            fil.write(fmtDisplacements(prop))

        prop = self.prop.getProp('n',attr=['equation'])
        if prop:
            pf.message("Writing constraint equations")
            fil.write(fmtEquation(prop))

        fil.write('FIN();\n')

        if filename is not None:
            fil.close()
        pf.message("Wrote Code Aster command file (.comm) %s" % filename)
  
# End