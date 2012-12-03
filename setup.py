#!/usr/bin/env python

# find_package data is
# (c) 2005 Ian Bicking and contributors; written for Paste
# (http://pythonpaste.org)
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import os
import subprocess
import sys
from fnmatch import fnmatchcase
from distutils.util import convert_path
from distutils.command.install import install

dependencies = [
    'doit>=0.16.1',
    'pygments',
    'pillow',
    'docutils',
    'mako>=0.6',
    'unidecode',
    'lxml',
    'yapsy',
    'configparser',
    'mock>=1.0.0',
]

# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ('*.pyc', '*$py.class', '*~', '.*', '*.bak')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')


def install_manpages(prefix):
    man_pages = [
        ('docs/man/nikola.1', 'share/man/man1/nikola.1'),
    ]
    join = os.path.join
    normpath = os.path.normpath
    for src, dst in man_pages:
        path_dst = join(normpath(prefix), normpath(dst))
        try:
            os.makedirs(os.path.dirname(path_dst))
        except OSError:
            pass
        rst2man_cmd = ['rst2man.py', 'rst2man']
        for rst2man in rst2man_cmd:
            try:
                subprocess.call([rst2man, src, path_dst])
            except OSError:
                continue
            else:
                break


class nikola_install(install):
    def run(self):
        install.run(self)
        install_manpages(self.prefix)


def find_package_data(
    where='.', package='',
    exclude=standard_exclude,
    exclude_directories=standard_exclude_directories,
    only_in_packages=True,
    show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {'package': [files]}

    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    """

    out = {}
    stack = [(convert_path(where), '', package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if (os.path.isfile(os.path.join(fn, '__init__.py'))
                    and not prefix):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append((fn, prefix + name + '/',
                    package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "File %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out

from distutils.core import setup

setup(name='Nikola',
      version='4.0.3',
      description='Static blog/website generator',
      author='Roberto Alsina and others',
      author_email='ralsina@netmanagers.com.ar',
      url='http://nikola.ralsina.com.ar/',
      packages=['nikola'],
      scripts=['scripts/nikola'],
      install_requires=dependencies,
      package_data=find_package_data(),
      cmdclass={'install': nikola_install},
      data_files=[
              ('share/doc/nikola', [
                      'docs/manual.txt',
                      'docs/theming.txt',
                      'docs/extending.txt']),
      ],
     )
