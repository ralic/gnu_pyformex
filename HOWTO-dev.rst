.. $Id$

..
  This file is part of the pyFormex project.
  pyFormex is a tool for generating, manipulating and transforming 3D
  geometrical models by sequences of mathematical operations.
  Home page: http://pyformex.org
  Project page:  https://savannah.nongnu.org/projects/pyformex/
  Copyright (C) Benedict Verhegghe (benedict.verhegghe@feops.com)
  Distributed under the GNU General Public License version 3 or later.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see http://www.gnu.org/licenses/.

.. |date| date::

..
  This document is written in ReST. To see a nicely formatted PDF version
  you can compile this document with the rst2pdf command.

.. _`homepage`: http://pyformex.nongnu.org
.. _`install guide`: http://pyformex.nongnu.org/doc/install.html

=============================
HOWTO for pyFormex developers
=============================
:Date: |date|
:Author: benedict.verhegghe@feops.com

.. warning: This document is currently under development!

This document describes the different tasks to be performed by pyFormex
developers, the prefered way(s) that should be followed to perform these
tasks, and the tools available to help with performing the tasks.

In the current version of this document we use the term *developer* for
a pyFormex group member. All developers have the same tasks and privileges.
The project manager of course has some extra tasks and extra privileges.
We will handle these separately at the end of this document.

In the future however, we might create distinct classes of group members
with different tasks: coding, documenting, providing support and promotion.
The term *developer* might then get a narrower meaning, but for now we use
it to designate any pyFormex group member.

First, let's list the different tasks that an open source software project
may entail:

- code development
- program testing and bug reporting
- providing and testing examples
- writing documentation
- documentation proofreading
- creating source releases
- packaging and distribution
- porting to other platforms/OSes
- website development/maintenance/proofreading
- support (helping users, providing small solutions, resolving bugs)
- publicity and distribution
- organizing user meetings
- discussion and planning

Until now, code development has got the most attention, but if we want
pyFormex to remain useful and attract more users, other tasks will become
more important.


For new pyFormex developers
===========================

How to become a pyFormex developer
----------------------------------

- register on `Savannah <http://savannah.nongnu.org>`_
- request membership of the pyFormex group

License
-------
pyFormex is distributed under the GNU GPL version 3 or later. This means that all contributions you make to the pyFormex project will be distributed with this license. By becoming a pyFormex group member and by contributing code or text of any kind, you implicitely agree with the distribution under this license.

The only exception we can make is for material on the pyFormex website that is
not distributed with pyFormex. Media (images, movies) and data files may be placed there under other compatible licenses, but you should explicitely state the license and ask the project manager for approval.


Install required basic tools
----------------------------

You will need a computer running Linux. We advice Debian GNU/Linux, but
other distributions can certainly be used as well. Make sure that you
have internet connection from your Linux system.

.. note:: We should describe alternative linux systems here

- In order to run pyFormex, you need to have some other software packages
  installed on your computer. See the `install guide`_ in the documentation
  for a full list of the prerequisites. On a Debian system you can install these
  with::

    apt-get install python-dev python-numpy python-opengl python-qt4-gl

- You certainly need to (learn to) use a decent text editor. pyFormex
  code, documentation, website, tools: everything is based on source text
  files. Since we use a lot of `Python` code, an editor that can nicely
  highlight the Python syntax is recommended. We suggest `emacs` with the
  `python-mode.el` extension (it has a somewhat steep learning curve, but
  this will be rewarded)::

    apt-get install emacs python-mode.el

  Of course, many other editors will qualify as well.

.. note:: We should add a list of other good editors here

- Make sure you have `git` installed. This is the revision control system used
  by pyFormex. And the graphical tool `gitk` may also be helpful.
  To install on Debian GNU/Linux::

    apt-get install git gitk

- Configure git by setting your user name and email address::

    git config --global user.name "John Doe"
    git config --global user.email john.doe@some.where


- We also recommend you to install some aliases as shortcuts for some
  often used commands. For example, add the following section to your
  `~/.gitconfig` file::

    [alias]
	su = status
	st = status -uno
	co = checkout
	ci = commit
	br = branch
	last = log -1 HEAD
	df = diff --ignore-space-change
	find = log --pretty=\"format:%Cgreen%H %Cblue%s\" --name-status --grep


- If you want to work on the documentation (and as a developer you really
  should), then you need `python-sphinx` and `dvipng`::

    apt-get install python-sphinx dvipng

  The installed version of sphinx needs to be patched however. See further
  for how to do this.

- If you want to create source distributions (.tar.gz), you also need::

    apt-get install python-git


Get access to the repositories
------------------------------

While anybody can get read access to the repositories on Savannah,
write access is restricted to pyFormex group members. To authenticate
yourself on Savannah, you need to provide an SSH key. Your SSH key is
a pair of files `id_rsa` and `id_rsa.pub` the directory `.ssh` under
your home directory.

- If you do not have such files, create them first, using the command::

    ssh-keygen

  You can just accept all defaults by clicking 'ENTER'. After that, you
  will have an SSH private,public keypair in your directory `.ssh`.

.. warning:: Never give the private part (`id_rsa`) of your key to anybody
  or do not make it accessible by anybody but yourself!

- The public part (`id_rsa.pub`) should be registered on Savannah
  to get easy developer access to the pyFormex repository.
  Login to Savannah and go to
  *My Account Conf*. Under *Authentication Setup* you can enter your
  public SSH key. Just copy/paste the contents of the file *.ssh/id_rsa.pub*.

.. note::

  If you are connecting from an Ubuntu system, and you find that you still can
  not get access after more than one day, you may try the following:

  - Check the end part of the public SSH key you pasted on Savannah, with the
    help of the scroll bar.
  - If it ends with '/' before "username@host.domain", replace the '/' with '=='.
  - After the update, wait for another day for the server to refresh, then try
    again to access the repository.


Currently, we are also using a developer repository, located on the server
`bumps.ugent.be`. You should also have an ssh account on that server. If
you do not have an account on the bump* servers yet, ask one: mailto:benedict.verhegghe@ugent.be.

Then copy your ssh key to the bumps server::

  ssh-copy-id username@bumps.ugent.be

Note that your username at bumps may be different from that at Savannah

Now you are all set to checkout the pyFormex repository.

Further reading
---------------

This basic guide can not tell you everything you need to know as pyFormex
group member. Depending on your tasks you may at times have to study some
other resources. Hereafter we give a list of the basic tools and software
packages that are needed in developing/documenting/managing/using pyFormex.
For all of these information is widely available on the internet.

.. note:: Maybe add here some good links.


- Python
- Numerical Python (NumPy)
- reStructuredText: http://docutils.sourceforge.net/rst.html
- Sphinx
- OpenGL (PyOpenGL)
- QT4 (PyQt4)
- git: `man git COMMAND` or
  http://www.kernel.org/pub/software/scm/git/docs/ or
  http://git-scm.com/documentation or
  http://gitref.org/index.html or
  http://sitaramc.github.com/gcs/index.html


Using the git repository
------------------------

Read http://sitaramc.github.com/gcs/index.html for definition of some git terms.

Quick overview
..............

- Clone the pyFormex developer repository into a directory `pyformex` (using
  your at the bump* servers)::

    git clone USERNAME@bumps.ugent.be:/srv/git/pyformex.git

  This will create a working directory `pyformex` with a clone of the
  repository (in a hidden subdir `.git`) and a checked out working copy
  of the master branch of the repository. You should be able to run
  pyformex directly from it, just like you previously did with a
  Subversion checkout.

.. note: In case you only want to run/change some version of pyFormex and
   do not want to contribute any changes back to the pyFormex project, you
   can also clone the repository anonymously (see the install manual).

- The .git directory in your repository also contains a config file,
  where you can set configuration items special for this git repository.
  The above mentioned ~/.gitconfig holds for all your git repositories.

  Add the following section to your .git/config::

    [filter "idexpansion"]
	clean = id_clean
	smudge = id_smudge
    [filter "idnoexpansion"]
	clean = id_clean

  This will take care of transformation of `$Id$` fields (see further)
  in the source code on checkout and commit.


- See a status of what has changed (use it often!)::

    git status

  If you have installed the aliases as mentioned above, you can also use the
  short form `git st`. This will give you the status report,without the
  untracked files, which is handy if you tend to collect many files in your git
  directory that should not be in the repository. If you want to see the
  untracked files as well, use `git su` (or `git status`).

- Pull in the changes from the remote repository (like `svn up`)::

    git pull

  Make sure you have a clean working directory (i.e. no changes) before
  doing that.

- Commit your changes to the remote repository (like `svn ci`). This is now
  a two-step (or even 3-step) procedure. First you commit the changes to
  your local copy of the repository::

    git commit -a

  Like before with `svn ci`, you will need to specify a commit message.

  Next you can push your changes up to the remote repository::

    git push



Working with multiple branches
..............................

.. note: This needs to be added


Working with multiple repos
...........................

Once you get sufficiently comfortable with using git, you can also add
the public repository as a remote (using your Savannah username)::

  git remote add public USERNAME@git.sv.gnu.org:/srv/git/pyformex.git

Now the command ::

  git remote -v

will give you something like (replace the user names)::

  origin	bene@bumps.ugent.be:/srv/git/pyformex.git (fetch)
  origin	bene@bumps.ugent.be:/srv/git/pyformex.git (push)
  public	bverheg@git.sv.gnu.org:/srv/git/pyformex.git (fetch)
  public	bverheg@git.sv.gnu.org:/srv/git/pyformex.git (push)

The default remote is 'origin' (the one you initially cloned from).
The 'public' is where you can push changes to make them available to
the general public.

To push your changes to the public repository, you have to specify both the
repository name and branch::

    git push public master

.. warning: Current project policy is that only the project manager pushes
   to the public repository. Other developers should (for now) only push to
   the local remote at bumps.ugent.be.



Switch the master branch
........................

You have a (public) branch NEW, which you want to become the master, while
the current master branch should be kept under the name OLD. We suppose
that both the NEW and master branches are already (updated) in the remote
repository, while OLD is non-existing in the remote.

First make a copy of the current master under the name OLD and save
it to the remote::

  git br OLD
  git push -u origin OLD

The NEW branch has diverted a lot from master, but you still need to
keep the changes from the master branch. So first merge the master
into your NEW branch::

  git co NEW
  git merge --strategy=ours --no-commit master
  git commit          # add information to the template merge message

.. note: If you do not want to provide a commit message, you can do the
   last two commands at once: git merge -s ours master

Finally, got to the master and merge the NEW branch in it::

  git co master
  git merge new


Structure of the pyFormex repository
====================================
After you checked out the trunk, you will find the following in the top
directory of your local copy.

:pyformex: This is where all the pyFormex source code (and more) is located.
  Everything that is included in the distributed releases should be located
  under this directory.

:pkg: This directory is where we have the tools for building Debian packages.

:screenshots: This contains some (early) screenshots. It could develop into
  a container for all kinds of promotional material (images, movies, ...)

:sphinx: This is where we build the documentation (not surprisingly, we use
  **Sphinx** for this task). The built documents are copied in `pyformex/doc`
  for inclusion in the release.

:stats: Contains some statistics and tools to gather them.

:user: Contains the minutes of pyFormex user meetings.

:website: Holds the source for the pyFormex website. Since the move to
  Savannah recently, we also use Sphinx to build the website.
  Since the whole html documentation tree is also published as part of
  the website (`<http://www.nongnu.org/pyformex/doc/>`_) we could actually
  integrate the *sphinx* part under *website*. The reasons for keeping them
  apart are:

  - the html documents under *sphinx* are made part of the release (for use
    as local documentation accessible from the pyFormex GUI), but the
    *website* documents are not, and
  - the *sphinx* documents need to be regenerated more often, because of the
    fast development process of pyFormex, while the *website* is more static.

Furthermore the top directory contains a bunch of other files, mostly managing tools. The most important ones will be treated further.



Commit messages
===============

When committing something to a repository, you always need to specify
a commit message. The message should be brief and to the point, but still
complete: describing what was changed and possibly why.

The structure of the commit message should be as follow: a single line
with a short contents, followed by a blank line and then multiple lines
describing all the changes. If you only made a single change,
a single line message is allowed.

If you find yourself writing a very long list of changes, consider
splitting your commit into smaller parts.  Prefixing your comments
with identifiers like Fix or Add is a good way of indicating what type
of change you did.  It also makes it easier to filter the content
later, either visually, by a human reader, or automatically, by a
program.

If you fixed a specific bug or implemented a specific change request,
it is recommended to reference the bug or issue number in the commit
message. Some tools may process this information and generate a link
to the corresponding page in a bug tracking system or automatically
update the issue based on the commit.


Solution to common git problems
===============================

Commit only some changes
------------------------
For each file that you want to commit, do::

  git add file_to_commit.py

Then do::

  git commit


Revert changes that have not been commited yet
----------------------------------------------
If you have changed a file, then decide you want to undo these
changes before you have added them, just check out that file
again, and it will be restored to the version in the repo::

  git checkout file_to_revert.py

If you already added them, but did not commit yet, use::

  git reset file_to_revert.py

Your branch and 'origin/master' have diverged
---------------------------------------------
After a `git pull` I had the following situation::

  bene@bumpy 13:31 ~/prj/pyformex $ git st
  # On branch master
  # Your branch and 'origin/master' have diverged,
  # and have 1 and 3 different commits each, respectively.
  #
  nothing to commit (working directory clean)

This is a common situation. I had commited a change to my local repository,
but did not push the changes to the remote repo. Meanwhile 3 other changes
are pushed to the remote. Thus my local master branch is now diverging from
the remote. To solve it, I could just merge the remote branch into my local
branch, using `git merge origin/master`. Instead I choose here for another
solution: rebase my commit. This will take my commit out of my local branch,
then pull in the changes from the remote first, and then reapply my changes::

  bene@bumpy 13:31 ~/prj/pyformex $ git rebase origin/master
  First, rewinding head to replay your work on top of it...
  Applying: Fix bug #37833: mesh (deep) copy
  bene@bumpy 13:33 ~/prj/pyformex $ git st
  # On branch master
  # Your branch is ahead of 'origin/master' by 1 commit.
  #
  nothing to commit (working directory clean)

The difference between the more commonly used 'merge' method and the 'rebase'
method, is that in the first case, a new commit will be made to merge the
diverged branches together again. In the second case however, the divergence
is avoided and a linear branch history is kept. In both cases, my local branch
is ready to be push up to the remote again.


Please, commit your changes or stash them before you can merge.
---------------------------------------------------------------

This situation occurs if you pull changes from the remote, and you have
local changes. An example::

  bene@bumper 14:29 ~/prj/pyformex $ git pull
  remote: Counting objects: 47, done.
  remote: Compressing objects: 100% (24/24), done.
  remote: Total 24 (delta 23), reused 0 (delta 0)
  Unpacking objects: 100% (24/24), done.
  From bumps.ugent.be:/srv/git/pyformex
     fd5bb16..8585d05  master     -> origin/master
  Updating fd5bb16..8585d05
  error: Your local changes to the following files would be overwritten by merge:
         pyformex/plugins/trisurface.py
  Please, commit your changes or stash them before you can merge.
  Aborting

If they are important, you can stash away your changes in a work directory::

  git stash

In both cases then just redo the pull::

  git pull

which will now succeed.


Stash your local changes to allow a pull
----------------------------------------
When you do a ::

  git pull

to update your local working directory from the remote repository, you may
get an error like this::

  error: Your local changes to the following files would be overwritten by merge:
	<SOME FILES>
  Please, commit your changes or stash them before you can merge.
  Aborting

Remember that the pull actually does two things:
first it fetches the required commits from the
remote to update your local repository, and then it checks out these
changes from your local repository and merges them into your working
directory. This is equivalent with::

  git fetch
  git co

As the error shows, it is the merging that is failing, because you have
local changes. Here are four ways to solve this problem:

- if you know your changes are ok: commit them first,

- if you know your changes are unneeded/unwanted, remove them::

   rm MODIFIED_FILE

- you can check first what you have changed::

    git diff MODIFIED_FILE

and see if your changes are important, and then proceed along one of the first
paths.

- in most cases however you will not want to find out now what changes
  to keep, but rather wait until you have merged the incoming changes.
  The easiest way to proceed then is to stash away your changes to
  allow the merge, and possibly continue to work on them later::

    git stash

  and after that the pull (or checkout) command will work. You then get your
  changes back with::

    git stash pop



Resolving merge conflicts
-------------------------
Merge operations (whether explicit, or implicit during a `git pull`, or
`git stash apply`) can lead to conflicts. Here is an example output of a
`git stash apply`::

  Auto-merging pyformex/plugins/trisurface.py
  CONFLICT (content): Merge conflict in pyformex/plugins/trisurface.py
  Auto-merging pyformex/gui/draw.py
  Auto-merging HOWTO-dev.rst

Two files got merged fine, one created a problem. Conflicts should be
resolved immediately, before adding/committing new changes, even before
you can run pyFormex. The `git st` says::

  #
  # Unmerged paths:
  #   (use "git reset HEAD <file>..." to unstage)
  #   (use "git add/rm <file>..." as appropriate to mark resolution)
  #
  #	both modified:      pyformex/plugins/trisurface.py
  #

In the file, you will find the conflicting parts marked by markers such
as the following::

  <<<<<<< Updated upstream
      Lines that were changed upstream and pulled in
  =======
      Lines that were changed in the local (stashed away) version
  >>>>>>> Stashed changes

In this case the stashed changes were wrong, so I just restored the checkout
version::

  git co -- pyformex/plugins/trisurface.py



Using the *make* command
========================
A lot of the recipes below use the *make* command. There is no place here to give a full description of what this command does (see http://www.gnu.org/software/make/). But for those unfamiliar with the command: *make* creates derived files according to recipes in a file *Makefile*. Usually a target describing what is to be made is specified in the make command (see many examples below). The *-C* option allows to change directory before executing the make. Thus, the command::

  make -C pyformex/lib debug

will excute *make debug* in the directory *pyformex/lib*. We use this a lot to mallow most *make* commands be executed from the top level directory.

A final tip: if you add a *-n* option to the make command, make will not actually execute any commands, but rather show what it would execute if the *-n* is left off. A good thing to try if you are unsure.


Create the pyFormex acceleration library
========================================
Most of the pyFormex source code is written in the Python scripting language: this allows for quick development, elegant error recovery and powerful interfacing with other software. The drawback is that it may be slow for loop operations over large data sets. In pyFormex, that problem has largely been solved by using **Numpy**, which handles most such operations by a call to a (fast) compiled C-library.

Some bottlenecks remained however, and therefore we have developed our own compiled C-libraries to further speed up some tasks. While we try to always provide Python equivalents for all the functions in the library, the penalty for using those may be quite high, and we recommend everyone to always try to use the compiled libraries. Therefore, after creating a new local svn tree, you should first proceed to compiling these libraries.

Prerequisites for compiling the libraries
-----------------------------------------
These are Debian GNU/Linux package names. They will most likely be available
under the same names on Debian derivatives and Ubuntu and derivatives.

- make
- gcc
- python-dev
- libglu1-mesa-dev


Creating the libraries
----------------------
The source for the libraries are the '.c' files in the `pyformex/lib`
directory of your svn tree. You will find there also the equivalent
Python implementations. To compile the liraries, got to ``TOPDIR`` and execute
the command::

  make lib

Note that this command is executed automatically when you run pyFormex directly
from the SVN sources (sse below). This is to ensure that you pick up any changes made to
the library. If compilation of the libraries during startup fails,


Run pyFormex from the checked-out source
========================================
In the toplevel directory, execute the command::

  pyformex/pyformex

and the pyFormex GUI should start. If you want to run this version as your
default pyFormex, it makes sense to create a link in a directory that is in
your *PATH*. On many systems, users have their own *~/bin* directory that is
in the front of the *PATH*. You can check this with::

  echo $PATH

The result may e.g. contain */home/USER/bin*. If not, add the following to your
*.profile* or *.bash_profile*::

  PATH=$HOME/bin:$PATH
  export PATH

and make sure that you create the bin directory if it does not exist.
Then create the link with the following command::

  ln -sfn TOPDIR/pyformex/pyformex ~/bin/pyformex

where ``TOPDIR`` is the absolute path of the top directory (created from the
repository checkout). You can also use a relative path, but this should be
as seen from the ``~/bin`` directory.

After starting a new terminal, you should be able to just enter the command
``pyformex`` to run your svn version from anywhere.

When pyformex starts up from the svn source, it will first check that the
compiled acceleration libraries are not outdated, and if they are, pyformex
will try to recompile them by invoking the 'make lib' command from the
parent directory. This is to avoid nasty crashes when the implementation of
the library has changed. If this automatic compilation fails, pyformex will
nevertheless continue, using the old compiled libraries or the slower Python
implementation.


Searching the pyFormex sources
==============================
While developing or using pyFormex, it is often desirable to be able to search
the pyFormex sources, e.g.

- to find examples of similar constructs for what you want to do,
- to find the implementation place of some feature you want to change,
- to update all code dependent on a feature you have changed.

The ``pyformex`` command provides the necessary tool to do so::

    pyformex --search -- [OPTIONS] PATTERN

This will actually execute the command::

    grep OPTIONS PATTERN FILES

where ``FILES`` will be replaced with the list of Python source files in the
pyformex directories. The command will list all occasions of ``PATTERN`` in
these files. All normal ``grep`` options (see ``man grep``) can be added, like
'-f' to search for a plain string instead of a regular expression, or '-i'
make the search case insensitive.

If you find the pyformext command above to elaborate, you can just define a
shorter alias. If you put the following line in your ``.bashrc``
file ::

    alias pysea='pyformex --search --'

you will be able to just do ::

    pysea PATTERN


Style guidelines for source and text files
==========================================

Here are some recommendations on the style to be used for source (mainly
Python) and other text files in the pyFormex repository.


General guidelines
------------------

- Name of .py files should be only lowercase, except for the approved
  examples distributed with pyFormex, which should start with an upper case.

- All new (Python, C) source and other text files in the pyFormex repository
  should be created with the following line as the first line::

    # $Id$

  If the file is an executable Python script, it should be started
  with the following two lines::

    #!/usr/bin/env python
    # $Id$

  Start reStructuredText with the following two lines (the second being
  an empty line)::

    .. $Id$

  On your next ``git checkout`` the ``$Id$`` fields will be sustituted
  by the date, time and developer name of the last push operation.
  Never edit this ``$Id$`` field information directly.

  This feature has to be activated by defining the 'idexpansion' filter
  in your .git/config file (see above).
  Files that have the idexpansion filter set (in .gitattributes) will see
  translation of the `$Id$` field.

- Python source files should end with a line::

    # End

  and .rst files should end with::

    .. End

  These lines help us in detecting that no part of a file has been cut off
  by accident.

- In Python files, always use 4 blanks for indenting, never TABs. Use
  a decent Python-aware editor that allows you to configure this. The
  main author of pyFormex uses ``Emacs`` with ``python-mode.el``.


pyFormex modules
----------------
- pyFormex modules should always contain a docstring of at least 3 lines,
  the first of which can not be empty. Immediately after the docstring you
  should enforce the use of the print function instead of the print
  statement, like below::

    """Test module

    """
    from __future__ import print_function

- pyFormex modules providing a functionality that can be used under
  plain Python can, and probably should, end with a section to test
  the modules::

    if __name__ == "__main__":
        # Statements to test the module functionality


  The statements in this section will be executed when the module is
  run with the command::

    python module.py


imports
-------
All import statements in the pyFormex Python source should use absolute
imports, starting with the pyformex main package. Imports should by preference
be ordered as in the following example, putting first (sub)package imports,
then module imports, and finally individual definition imports.
The subpackages should be in the order lib, gui, opengl, plugins, examples.
By preference put only one import per line.

Wildcard imports are should not be used. There are still a lot them for
historical reasons, but we should remove them as much as possible.

::

    # Example of an extensive import list
    from __future__ import print_function

    import pyformex as pf
    from pyformex import plugins           # import a subpackge
    from pyformex import utils             # import module
    from pyformex import arraytools as at  # import module with alias
    from pyformex.gui import draw, image   # !!! DEPRECATED multiple import
    from pyformex.plugins import geometry_menu
    from pyformex.utils import command     # import individual function
    from pyformex.gui.draw import *        # !!! DEPRECATED wildcard
    from pyformex.plugins.curve import Arc, PolyLine

    import os, sys               # import non-pyformex parts


pyFormex scripts
----------------

- pyFormex scripts (this includes the examples provided with pyFormex)
  can test the ``__name__`` variable to find out whether the script is
  running under the GUI or not::

    if __name__ == "draw":
        # Statements to execute when run under the GUI

    elif __name__ == "script":
        # Statements to execute when run without the GUI


Coding style
------------

- Variables, functions, classes and their methods should be named
  as closely as possible according to the following scheme:

  - classes: ``UpperUpperUpper``
  - functions and methods: ``lowerUpperUpper``
  - variables: ``lowercaseonly``

  Lower case only names can have underscores inserted to visually separate
  the constituant parts: ``lower_case_only``.

  Local names that are not supposed to be used directly by the user
  or application programmer, can have underscores inserted or
  appended.

  Local names may start with an underscore to hide them from the user.
  These names will indeed not be made available by Python's ``import``
  statements.

- For whitespace in expressions and statements, try to follow the rules in
  http://www.python.org/dev/peps/pep-0008/#whitespace-in-expressions-and-statements.
  More precisely, do not put a whitespace directly inside delimiters
  or around mathematic operators.

  But *do* put spaces around the assignment operator ('='), except in argument
  lists. Also put a blank after commas. Thus::

    def inc(x, y=1):
        z = x+y
        return z

- Always start a new line after the colon (``:``) in ``if`` and ``for``
  statements.

- Always try to use implicit for loops instead of explicit ones.

- Numpy often provides a choice of using an attribute, a method or a
  function to get to the same result. The preference ordering is:
  attribute > method > function. E.g. use ``A.shape`` and not ``shape(A)``.


print
-----
All print statements should be replaced with print() function calls,
and the import of print_function is required in all pyformex modules.

raise Error
-----------
When raising an Error, the error message should be put in parentheses as
an argument to the Error class::

  raise SomeError('Some error occurred')

iteritems
---------
dict.iteritems() should not be used: just use dict.items(). We know this is
a (slight) performance hit, but it will help in porting to Python3.


Docstrings
----------

- All functions, methods, classes and modules should have a docstring,
  consisting of a single first line with the short description,
  possibly followed by a blank line and an extended description. It
  is recommended to add an extended description for all but the trivial
  components.

- Docstrings should end and start with triple double-quotes (""").

.. warning: Try not to use lines starting with the word 'class' in a
   multiline docstring: it tends to confuse emacs+python-mode.

- Docstrings should not exceed the 80 character total line length.
  Python statements can exceed that length, if the result is more easy
  to read than splitting the line.

- Docstrings should be written with `reStructuredText (reST)
  <http://docutils.sourceforge.net/rst.html>`_ syntax. This allows us
  to use the docstrings to autmoatically generate the reference
  manual in a nice layout, while the docstrings keep being easily
  readible. Where in doubt, try to follow the `Numpy documentation guidelines
  <http://projects.scipy.org/numpy/wiki/CodingStyleGuidelines>`_.

- reStructuredText is very keen to the precise indentation (but as Python
  coders we are already used to that). All text belonging to the same
  logical unit should get the same indentation. And beware espacially for
  the required blank lines to delimit different section. A typical
  example is that of a bullet list::

    Text before the bullet list.

    - Bullet item 1
    - Bullet item 2, somewhat longer and continued
      on the next line.
    - Bullet item 3

    Text below the bullet item


- The extended description should contain a section describing the parameters
  and one describing the return value (if any). These should
  be structured as follows::

    Parameters:

    - `par1`: type: meaning of parameter 1.
    - `par2`: type: meaning of parameter 2.
    - `par3`, `par4`: type(s): meaning of parameters 3 and 4.

    Returns:

    - `ret1`: type: return value 1.
    - `ret2`: type: return value 2.

  If two or more parameters or return values are decribed in the same item,
  be sure to leave a space after the comma in the list of names!
  If there is just a single return value, its type and value can also be
  described in a single sentence, e.g.::

    Returns an int which is zero upon success.

- The parameters of class constructor methods (``__init__``) should be
  documented in the Class docstring, not in the ``__init__`` method
  itself.

- Special sections (note, warning) can be used to draw special attention of
  the user. Format these as follows (leave a space after '..')::

    .. note::

      This is a note.

    .. warning::

      Be careful!

- Wherever possible add an example of the use of the function. By preference
  this should be a live example that can be used through the --doctest
  framework. This should be structured as follows::

    Examples:

      >>> F = Formex('3:012934',[1,3])
      >>> print F.coords
      [[[ 0.  0.  0.]
       [ 1.  0.  0.]
       [ 1.  1.  0.]]

      [[ 1.  1.  0.]
       [ 0.  1.  0.]
       [ 0.  0.  0.]]]

  Lines starting with '>>>' should be executable Python (pyFormex) code.
  If the code creates any output, that output should be added exactly as
  generated (but aligned with the '>>>' below the code line.
  When the module is tested with::

    pyformex --doctest MODULENAME

  Python will execute all these code and check that the results match.
  In order to get good quality formatting in both the HTML and PDF versions,
  both the code lines and the output it generates should be kept short.
  You can use intermediate variables in the code to obtain this. For the
  output, you may have to use properly formatted printing of the data or
  subdata. E.g., a ``print F`` above instead of ``print F.coords`` would
  result in a too long line.

  See also the documentation for arraytools.uniqueOrdered for another
  example.


Automatic code style checking
=============================

In an effort to improve code quality, readability and maintainability, we
promote the use of some specialized tools for code style checking and
rewriting. Developers should install the following packages::

  apt-get install pep8 python-autopep8 pylint

In future we will use these tools to check all code automatically at commit
time. For now, the tools are made available recommended configurations are
tested and will lead to further instructions here. All of you can help with
cleaning up the existing code.

Checking with pep8
------------------

PEP8 is a Python Enhancement Proposal holding general recommendations
for Python coding style. The *pep8* command will check conformance of
your code to this guide. There is however no unanimous consent on what
is good style. Therefore we will not enforce all recommendations.
We will for example allow comments line starting with two hash marks (##),
for the following reasons:

- *emacs* uses '##' to comment out regions (which themselves might contain
  comments) and to uncomment them again;
- our custom *stamp* program responsible for adding the copyright section
  at the start of files uses '##' to identify the stamped part.

Therefore, the recommended way to execute pep8 is::

  pep8 --ignore=E265 myfile.py

This will produce a list of fixes (mostly whitespace) which you should
implement. You can use *autopep8* to help you.

Creating beautified code with autopep8
--------------------------------------

*autopep8* restructures your code according to pep8. It will mostly do
whitespace corrections. While it can automatically change the code inplace,
it is not recommended to do so. Instead, create the new code, compare it
with the old, and port the changes one by one after your approval.
There are diff tools available for most editors to help with that.
The following command produces a cleaned source *myfile_pep8.py*::

  autopep8 --ignore=E265,W6 myfile.py > myfile_pep8.py

Do not feel forced to accept all changes! There might be reasons to
divert from standard rules. The restructured file might break some
nice vertical alignment, or break lines at strange places. If the result
is not more readable than the original, do not change it.
Also, autopep8 does not fix all the pep8 failures.

Thus, for two files that were converted already (simple.py, varray.py),
the first one still produces quite some message. This is no problem, as
we consider the code better in that way, than in the conforming version.


Checking with pylint
--------------------

The ultimate testing of the code will be done with *pylint*. Policy
is set in the pylintrc configuration file. The command::

  pylint myfile.py

produces a long report with recommendations, and a global evaluation
with a score on 10.
Try to fix as many of the reported issues, and run the code again.
The score will increase. The first file that was analyzed and fixed
(varray.py) now has a score of 9.47/10. But do not worry if your initial
score is *a lot* lower: varray.py started at a negative score, as will
probably most of our modules. *simple.py* has at the time of this writing
a score of -42.38 :( largely due to wildcard imports.

Testing after changes
---------------------

Be sure to always retest the module after the changes you have made::

  pyformex --doctest pkg.myfile



Creating pyFormex documentation
===============================

The pyFormex documentation (as well as the website) are created by the
**Sphinx** system from source files written in ReST (ReStructuredText).
The source files are in the ``sphinx`` directory of your svn tree and
have an extension ``.rst``.

Install Sphinx
--------------
You need a (slightly) patched version of Sphinx. The patch adds a small
functionality leaving normal operation intact.
Therefore, if you have root
access, we advise to just patch a normally installed version of Sphinx.

- First, install the required packages. On Debian GNU/Linux do ::

    apt-get install dvipng python-sphinx

- Then patch the sphinx installation. Find out where the installed Sphinx
  package resides. On Debian this is ``/usr/share/pyshared/sphinx``.
  The pyformex source tree contains the required patch in a file
  ``sphinx/sphinx-1.1.3-bv.diff``. It was created for Sphinx 1.1.3 but will
  probably work for slightly older or newer versions as well.
  Do the following as root::

    cd /usr/share/pyshared/sphinx
    patch -p1 --dry-run < TOPDIR/sphinx/sphinx-1.1.3-bv.diff

  This will only test the patching. If all hunks succeed, run the
  command again without the '--dry-run'::

    patch -p1 < ???/pyformex/sphinx/sphinx-1.1.3-bv.diff

The patched version allows you to specify a negative number for the
`:numbered:` option in a toctree. See the following extract from `refman.rst`
for an example::

  .. toctree::
     :maxdepth: 1
     :numbered: -1

This means that the modules listed thereafter will be descended 1 level deep
and be numbered one level deep. But unlike the default working of sphinx (with
positive value), the modules in different toctrees in the same document are
numbered globally over the document, instead of restarting at 1 for every
toctree.


Writing documentation source files
----------------------------------
Documentation is written in ReST (ReStructuredText). The source files are
in the ``sphinx`` directory of your svn tree and have an extension ``.rst``.

When you create a new .rst files with the following header::

  .. $Id$
  .. pyformex documentation --- chaptername
  ..
  .. include:: defines.inc
  .. include:: links.inc
  ..
  .. _cha:partname:

Replace in this header chaptername with the documentation chapter name.

See also the following links for more information:

- guidelines for documenting Python: http://docs.python.org/documenting/index.html
- Sphinx documentation: http://sphinx.pocoo.org/
- ReStructuredText page of the docutils project: http://docutils.sourceforge.net/rst.html

When refering to pyFormex as the name of the software or project,
always use the upper case 'F'. When refering to the command to run
the program, or a directory path name, use all lower case: ``pyformex``.

The source .rst files in the ``sphinx/ref`` directory are automatically
generated with the ``py2rst.py`` script. They will generate the pyFormex
reference manual automatically from the docstrings in the Python
source files of pyFormex. Never add or change any of the .rst files in
``sphinx/ref`` directly. Also, these files should *not* be added to the
svn repository.


Adding image files
------------------

- Put original images in the subdirectory ``images``.

- Create images with a transparent or white background.

- Use PNG images whenever possible.

- Create the reasonable size for inclusion on a web page. Use a minimal canvas size and maximal zooming.

- Give related images identical size (set canvas size and use autozoom).

- Make composite images to combine multiple small images in a single large one.
  If you have ``ImageMagick``, the following command create a horizontal
  composition ``result.png``  of three images::

     convert +append image-000.png image-001.png image-003.png result.png


Create the pyFormex manual
--------------------------

The pyFormex documentation is normally generated in HTML format, allowing it
to be published on the website. This is also the format that is included in
the pyFormex distributions. Alternative formats (like PDF) may also be
generated and made available online, but are not distributed with pyFormex.

The ``make`` commands to generate the documentation are normally executed
from the ``sphinx`` directory (though some work from the ``TOPDIR`` as well).

- Create the html documentation ::

   make html

  This will generate the documentation in `sphinx/_build/html`, but
  these files are *not* in the svn tree and will not be used in the
  pyFormex **Help** system, nor can they be made available to the public
  directly.
  Check the correctness of the generated files by pointing your
  browser to `sphinx/_build/html/index.html`.

- The make procedure often produces a long list of warnings and errors.
  You may therefore prefer to use the following command instead ::

    make html 2>&1 | tee > errors

  This will log the stdout and stderr to a file ``errors``, where you
  can check afterwards what needs to be fixed.

- When the generated documentation seems ok, include the files into
  the pyFormex SVN tree (under ``pyformex/doc/html``) and thus into
  the **Help** system of pyFormex ::

   make incdoc

  Note: If you created any *new* files, do not forget to ``svn add`` them.

- A PDF version of the full manual can be created with ::

   make latexpdf

  This will put the PDF manual in ``sphinx/_build/latex``.

The newly generated documentation is not automatically published on the
pyFormex website. Currently, only the project manager can do that. After you
have made substantial improvements (and checked them in), you should contact
the project manager and ask him to publish the new docs.


Create a distribution
=====================

A distribution (or package) is a full set of all pyFormex files
needed to install and run it on a system, packaged in a single archive
together with an install procedure. This is primarily targeted at normal
users that want a stable system and are not doing development work.

Distribution of pyFormex is done in the form of a 'tarball' (.tar.gz) archive.
You need to have `python-git` and `python-docutils` installed to create the
distribution tarball. Also, you need to create a subdirectory `dist` in
your pyFormex source tree.

Before creating an official distribution, update your tree and commit your
last modifications. Then, in the top directory of your git repo, do ::

  make dist

This will create the package file `pyformex-${VERSION}.tar.gz` in
`dist/`. The version is read from the `RELEASE` file in the top
directory. Do not change the *VERSION* or *RELEASE* settings in this
file by hand: we have `make` commands to do this (see below). Make sure
that the *RELEASE* contains a trailing field (*aNUMBER*).
This means that it is an (alpha) intermediate, unsupported release.
Official, supported releases do not have the trailer.

Any developer can create intermediate release tarballs and distribute them.
However, *currently only the project manager is allowed
to create and distribute official releases!*

After you have tested that pyFormex installation and operation from the
resulting works fine, you can distribute the package to other users, e.g.
by passing them the package file explicitely (make sure they understand the
alpha status) or by uploading the file to our local file server.
Once the package file has been distributed by any means, you should immediately
bump the version, so that the next created distribution will have a higher number::

  make bumpversion
  git ci -m "Bump version after creating distribution file"

.. note:: There is a (rather small) risk here that two developers might
  independently create a release with the same number.


Things that have to be done by the project manager
==================================================

Extra needed packages:

- cvs, for the pyFormex website at Savannah::

    apt-get install cvs

Make file(s) public
-------------------
This is for interim releases, not for an official release ! See below
for the full procedure to make and publish an official release tarball.

- Make a distribution file (tarball) available on our own FTP server ::

   make publocal

- Make a distribution file available on Savannah FTP server ::

   make pub

- Bump the pyFormex version. While any developer can bump the version,
  it really should only be done after publishing a release (official
  or interim) or when there is another good reason to change the
  version number. Therefore it is included here with the manager's
  tasks. ::

   make bumpversion

Publish the documentation
-------------------------
- Put the html documention on the website ::

   make pubdoc
   ./publish # This should currently be done by the project manager
             # on his laptop!
   # now add the missing files by hand : cvs add FILE
   make commit

- Publish a PDF manual ::

   make pubpdf


Release a distribution to the general public
--------------------------------------------

First, create the distribution and test it out locally: both the installation
procedure and the operation of the installed program. A working development
version is not enough. Proceed only when everything works fine.

- Set the final version in RELEASE (RELEASE==VERSION) ::

   edt RELEASE    # Remove the a* tail
   make version

- Stamp the files with the version ::

   make stampall

- Create updated documentation ::

   make html
   make latexpdf
   make incdoc

- Check in (creating the dist may modify some files) ::

   git commit -a -m "Creating release ..."

- Set the revision number in stats/pyformex-release.fdb. Compute it from the
  latest and add the increment from the pyFormex version::

    pyFormex 0.9.0 (0.8.9r5-249-ga162aca)
                            ^^^

  In this example we have 249 past release 0.8.9 (actually 0.8.9-r5, but this
  had the same revision number as 0.8.9). Release 0.8.9 was revision 2557,
  thus the new revision number is 2557 + 249 = 2806.

- Create a Tag ::

   make tag
   make pushtag

- Push source to Savannah::

   git push public master
   git push public RELEASETAG

- Create the distribution ::

   make dist

- Put the release files on Savannah::

   make pubrelease
   make pubpdf
   make pubn
   make pub

- Announce the release on the pyFormex news

  * news
  * submit

    text: pyFormex Version released....

- Put the files on our local FTP server ::

   make publocal_off

- Put the documentation on the web site ::

   make pubdoc
   ./publish
   make commit

- Upload to the python package index ::

   (NOT CORRECT) make upload  # should replace make sdist above

- Add the release data to the database ::

   edt stats/pyformex-releases.fdb

- Create statistics ::

   make stats   # needs more work to get git commit count

- Bump the RELEASE and VERSION variables in the file RELEASE, then ::

   make bumpversion
   make lib
   svn ci -m 'Bump version after release'

Well, that was easy, uh? ~)_do build


Change the pyFormex website
---------------------------

The top tree of the website (everything not under Documentation) has its
source files in the `website` directory. It uses mostly rest and sphinx,
just like the documentation. To create the website::

  cd website
  make html

Look at the result under the _build subdirectory. Some links (notably to
the documentation) will not work from the local files.
If the result is ok, it can be published as follows::

  make pub

This moves the resulting files to the `www` subdirectory, which is a
cvs mirror of the website. Upload the files just as for the documentation::

   cd ..
   ./publish
   make commit


Creating (official) Debian packages
-----------------------------------

.. note: This section needs further clarification

Debian packages are create in the `pkg` subdirectory of the trunk.
The whole process is controlled by the script `_do`. The debian-template
subdirectory contains starting versions of the `debian` files packaging.
They will need to be tuned for the release.

- Install needed software packages for the build process::

    apt-get install debhelper devscripts python-all-dev

  Furthermore you also need to have installed all dependencies for the build,
  as declared in the variables `Build-Depends` and `Build-Depends-Indep` in
  the file `control`.

- Other packages: lintian, libfile-fcntllock-perl

- Go to the `pkg` directory. The `_do` procedure should always be executed
  from here.

- Prepare the package creation. This will set an entry in the debian/changelog
  file. If the package to be created is for a new pyFormex version/release,
  use::

    _do prepare

  If the new package is a fix for the previous package of the same pyFormex
  release, use::

    _do preparefix

  Then carefully edit the changelog file, respecting all whitespace.

  - Replace UNRELEASED with unstable.
  - Add the reason for the new package next to the *
  - Remove all entries below that have a ~a field in the release.

- Unpack latest release::

    _do unpack

  This unpacks the latest source
  distribution (from the `dist/` or `dist/pyformex/` subdirectory) in
  a directory `pyformex-VERSION` and copies the `debian-template` as a
  starting `debian` subdirectory.
- Edit the files in the generated `pyformex-VERSION/debian` subdirectory.
  At least a new entry in the file `changelog` needs to be added.
  Other files that are likely to require changes are `control` and `rules`.

.. note: If errors occur during the build, you will most likely have to fix
   the files in `debian` and then rerun the build. Often a rebuild requires
   a clean first. Beware that this will remove your changes and reinstall
   the original `debian` files. It is therefore adviced to edit the
   files in `debian-template` instead of those in `pyformex-VERSION/debian`.
   Then do a `_do clean unpack`.

- Build the packages::

    _do build | tee log

  This will build the python modules,
  the compiled libraries and the extra binaries under a path
  `pyformex-VERSION/debian/tmp` and install the needed files into
  the package directories `pyformex`, `pyformex-lib` and `pyformex-extras`.

  Check that no errors occur during the procedure. A log file is written
  for each package.

- Test installing and running of the packages::

    _do install

- If OK, build final (signed)::

    _do clean unpack final | tee log

- upload to Debian mentors::

    _do upload

- upload to local repository and make available::

    _do uploadlocal
    _do publocal




.. End
