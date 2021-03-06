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

#
# Makefile for creating pyFormex releases
#

include RELEASE

PKGNAME= pyformex

PYFORMEXDIR= pyformex

LIBDIR= ${PYFORMEXDIR}/lib
DOCDIR= ${PYFORMEXDIR}/doc
BINDIR= ${PYFORMEXDIR}/bin
EXTDIR= ${PYFORMEXDIR}/extra
DATADIR= ${PYFORMEXDIR}/data
SPHINXDIR= sphinx

SOURCE= ${PYFORMEXDIR}/pyformex \
	$(wildcard ${PYFORMEXDIR}/*.py) \
	$(wildcard ${PYFORMEXDIR}/gui/*.py) \
	$(wildcard ${PYFORMEXDIR}/plugins/*.py) \
	$(wildcard ${LIBDIR}/*.py) \

LIBSOURCE= ${addprefix ${LIBDIR}/, misc_.c nurbs_.c}
LIBOBJECTS= $(CSOURCE:.c=.o)
LIBOBJECTS= $(CSOURCE:.c=.so)

BINSOURCE= \
	$(wildcard ${BINDIR}/*.awk) \
	${addprefix ${BINDIR}/, gambit-neu gambit-neu-hex} \

EXTSOURCE= \
	$(wildcard ${EXTDIR}/*/README*) \
	$(wildcard ${EXTDIR}/*/Makefile) \
	$(wildcard ${EXTDIR}/*/*.rst) \
	$(wildcard ${EXTDIR}/*/install.sh) \
	$(wildcard ${EXTDIR}/*/*.h) \
	$(wildcard ${EXTDIR}/*/*.c) \
	$(wildcard ${EXTDIR}/*/*.cc) \
	$(wildcard ${EXTDIR}/*/*.py) \
	${addprefix ${EXTDIR}/pygl2ps/, gl2ps.i setup.py} \

EXAMPLES= \
	$(wildcard ${PYFORMEXDIR}/examples/*.py) \
	$(wildcard ${PYFORMEXDIR}/examples/Demos/*.py) \

EXAMPLEDATA= $(wildcard ${DATADIR}/*.db)

DOCSOURCE= \
	$(wildcard ${SPHINXDIR}/*.rst) \
	$(wildcard ${SPHINXDIR}/*.py) \
	$(wildcard ${SPHINXDIR}/*.inc) \
	$(wildcard ${SPHINXDIR}/static/scripts/[A-Z]*.py) \
	${SPHINXDIR}/Makefile \
	${SPHINXDIR}/ref/Makefile

EXECUTABLE= ${PYFORMEXDIR}/pyformex ${PYFORMEXDIR}/sendmail.py \
	${BINDIR}/read_abq_inp.awk \
	pyformex-viewer \
	${SPHINXDIR}/py2rst.py


OTHERSTAMPABLE= README Makefile ReleaseNotes \
	manifest.py setup.py \
	${PYFORMEXDIR}/pyformex.conf \
	${EXAMPLEDATA} \
	$(wildcard ${DOCDIR}/*.rst)

NONSTAMPABLE= COPYING

STAMPABLE= ${SOURCE} \
	${EXECUTABLE} ${CSOURCE} ${EXAMPLES} ${DOCSOURCE} ${BINSOURCE} \
	${LIBSOURCE} \
	$(filter-out ${EXTDIR}/pygl2ps/gl2ps_wrap.c,${EXTSOURCE}) \
	${OTHERSTAMPABLE}

STATICSTAMPABLE= Description History HOWTO-dev.rst add_Id \
	create_revision_graph install-pyformex-svn-desktop-link \
	pyformex-viewer searchpy sloc.py slocstats.awk \
	user/Makefile $(wildcard user/*.rst) \
	website/Makefile $(wildcard website/scripts/*.py) \
	$(wildcard website/src/examples/*.txt)

STATICDIRS= pyformex/data/README pyformex/icons/README \
	pyformex/lib/README \
	screenshots/README \
	sphinx/images/README sphinx/static/scripts/README \
	website/README website/images/README website/src/README \
	website/src/examples/README

STAMP= stamp
VERSIONSTRING= __version__ = ".*"
NEWVERSIONSTRING= __version__ = "${RELEASE}"

PKGVER= ${PKGNAME}-${RELEASE}.tar.gz
PKGDIR= dist
PUBDIR= ${PKGDIR}/pyformex
LATEST= ${PKGNAME}-latest.tar.gz

# our local ftp server
FTPLOCAL= bumps:/var/ftp/pub/pyformex
# ftp server on Savannah
FTPPUB= bverheg@dl.sv.nongnu.org:/releases/pyformex/

.PHONY: dist sdist signdist cleandist pub clean distclean html latexpdf pubdoc minutes website dist.stamped version tag register bumprelease bumpversion stampall stampstatic stampstaticdirs pubrelease

##############################

default:
	@echo Please specify a target

clean:
	find . -name '*~' -delete
	make -C pyformex/extra clean

distclean: clean
	find . \( -name '*.so' -or -name '*.pyc' \)

# Create the C library
lib:
	python setup.py build_ext
	find build -name '*.so' -exec mv {} pyformex/lib \;
	rm -rf build

# Create the C library for Python3
lib3:
	python3 setup.py build_ext
	find build -name '*.so' -exec mv {} pyformex/lib \;
	rm -rf build


# Create the minutes of the user meeting
minutes:
	make -C user

# Create the website
website:
	make -C website


# Bump the version/release
bumpversion:
	@OLD=$$(expr "${VERSION}" : '.*\([0-9])*\)$$'); \
	 NEW=$$(expr $$OLD + 1); \
	 DOC=$$(expr "${VERSION}" : '\(.*\)\.[^.]*'); \
	 sed -i "/^VERSION=/s|$$OLD$$|$$NEW|;s|^DOCVERSION =.*|DOCVERSION = $$DOC|;/^RELEASE=/s|}.*|}-a1|" RELEASE
	make version
	@echo "Bumped Version to $$(grep VERSION= RELEASE), $$(grep RELEASE= RELEASE)"

# This increases the tail only: minor number or alpha number
bumprelease:
	@OLD=$$(expr "${RELEASE}" : '.*-a\([0-9])*\)$$'); \
	 if [ -z "$$OLD" ]; then NEW=1; else NEW=$$(expr $$OLD + 1); fi; \
	 sed -i "/^RELEASE=/s|}.*|}-a$$NEW|" RELEASE
	make version
	@echo "Bumped Release to $$(grep VERSION= RELEASE), $$(grep RELEASE= RELEASE)"

revision:
	sed -i "s|__revision__ = .*|__revision__ = '$$(git describe --always)'|" ${PYFORMEXDIR}/__init__.py

version: ${PYFORMEXDIR}/__init__.py setup.py ${SPHINXDIR}/conf.py ${LIBSOURCE}

${PYFORMEXDIR}/__init__.py: RELEASE
	sed -i 's|${VERSIONSTRING}|${NEWVERSIONSTRING}|' $@
	sed -i "/^Copyright/s|2004-....|2004-$$(date +%Y)|" $@

${SPHINXDIR}/conf.py: RELEASE
	sed -i "s|^version =.*|version = '${VERSION}'|;s|^release =.*|release = '${RELEASE}'|" $@

setup.py: RELEASE
	sed -i "s|__RELEASE__ = '.*'|__RELEASE__ = '${RELEASE}'|" $@

${LIBDIR}/%.c: RELEASE
	sed -i 's|${VERSIONSTRING}|${NEWVERSIONSTRING}|' $@

# Stamp files with the version/release date

Stamp.stamp: Stamp.template RELEASE
	${STAMP} -t$< header="This file is part of pyFormex ${VERSION}  ($$(env LANG=C date))" -s$@

stampall: Stamp.stamp
	${STAMP} -p -t$< -i ${STAMPABLE}


printstampable:
	@for f in ${STAMPABLE}; do echo $$f; done

Stamp.static: Stamp.template
	${STAMP} -t$< header='This file is part of the pyFormex project.' -s$@

stampstatic: Stamp.static
	${STAMP} -t$< -i ${STATICSTAMPABLE}

Stamp.staticdir: Stamp.template
	${STAMP} -t$< header='The files in this directory are part of the pyFormex project.' -s$@

stampstaticdirs: Stamp.staticdir
	${STAMP} -t$< -i ${STATICDIRS}


# Create the distribution
cleandist:
	mkdir -p ${PKGDIR}
	rm -f ${PKGDIR}/${PKGVER}

dist: cleandist manpages ${PKGDIR}/${LATEST} clean

# Sign the distribution
signdist: ${PKGDIR}/${PKGVER}.sig

${PKGDIR}/${LATEST}: ${PKGDIR}/${PKGVER}
	ln -sfn ${PKGVER} ${PKGDIR}/${LATEST}

${PKGDIR}/${PKGVER}: RELEASE
	make sdist

sdist:
	@echo "Creating ${PKGDIR}/${PKGVER}"
	python setup.py sdist --no-defaults | tee makedist.log
	python manifest_check.py

${PKGDIR}/${PKGVER}.sig: ${PKGDIR}/${PKGVER}
	cd ${PKGDIR}; gpg -b ${PKGVER}

# Create all our manpages
manpages:
	make -C pyformex/doc manpages
	make -C pyformex/extra manpages

# Publish the distribution to our ftp server
#
# We should make a difference between official and interim releases!
#
publocal_int: ${PKGDIR}/${LATEST} ${PKGDIR}/${PKGVER}.sig
	rsync -ltv ${PKGDIR}/${PKGVER} ${PKGDIR}/${LATEST} ${PKGDIR}/${PKGVER}.sig ${FTPLOCAL}

publocal_off: ${PUBDIR}/${LATEST} ${PUBDIR}/${PKGVER}.sig
	rsync -ltv ${PUBDIR}/${PKGVER} ${PUBDIR}/${LATEST} ${PUBDIR}/${PKGVER}.sig ${FTPLOCAL}


# Move the create tar.gz to the public directory
pubrelease: ${PKGDIR}/${LATEST} ${PKGDIR}/${PKGVER}.sig
	mkdir -p ${PUBDIR}
	mv ${PKGDIR}/${PKGVER} ${PKGDIR}/${LATEST} ${PKGDIR}/${PKGVER}.sig ${PUBDIR}
	ln -s pyformex/${LATEST} ${PKGDIR}

# and sign the packages  (THIS IS NOW DONE BEFORE MOVING)
#sign: ${PUBDIR}/${PKGVER}
#	cd ${PUBDIR}; gpg -b --use-agent ${PKGVER}

pubn: ${PUBDIR}/${PKGVER}.sig
	rsync ${PUBDIR}/* ${FTPPUB} -rtlvn

pub: ${PUBDIR}/${PKGVER}.sig
	rsync ${PUBDIR}/* ${FTPPUB} -rtlv

# Register with the python package index
register:
	python setup.py register

upload:
	python setup.py sdist upload --show-response

# Tag the release in the git repository
tag:
	git tag -s -a release-${RELEASE} -m "This is the ${RELEASE} release of the 'pyFormex' project."

# Push the release tag to origin
pushtag:
	git push origin release-${RELEASE}


# Creates statistics
stats:
	make -C stats

# Create the Sphinx documentation
html:
	make -C ${SPHINXDIR} html
	@echo "Remember to do 'make incdoc' to make the new docs available in pyformex-svn"

incdoc:
	make -C ${SPHINXDIR} incdoc

latexpdf:
	make -C ${SPHINXDIR} latexpdf

# Publish the documentation on the website

pubdoc:
	make -C ${SPHINXDIR} pubdoc


# Publish the website
publish:
	./publish

commit:
	cd www; cvs commit; cd ..

# Make the PDF manual available for download

pubpdf:
	make -C ${SPHINXDIR} pubpdf


# Test all modules
# Currently this tests only the core modules
testall:
	cd pyformex; for f in *.py; do pyformex --doctest $${f%.py}; done


# End
