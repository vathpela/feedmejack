#!/usr/bin/python3

from distutils.core import setup
from distutils import filelist
from distutils.command.sdist import sdist
import subprocess
import sys
import os

# this is copied straight from distutils.filelist.findall , but with os.stat()
# replaced with os.lstat(), so S_ISLNK() can actually tell us something.


def findall(dirname=os.curdir):
    from stat import ST_MODE, S_ISREG, S_ISDIR, S_ISLNK

    file_list = []
    stack = [dirname]
    pop = stack.pop
    push = stack.append

    while stack:
        dirname = pop()
        names = os.listdir(dirname)

        for name in names:
            if dirname != os.curdir:        # avoid the dreaded "./" syndrome
                fullname = os.path.join(dirname, name)
            else:
                fullname = name

            # Avoid excess stat calls -- just one will do, thank you!
            stat = os.lstat(fullname)
            mode = stat[ST_MODE]
            if S_ISREG(mode):
                file_list.append(fullname)
            elif S_ISDIR(mode) and not S_ISLNK(mode):
                push(fullname)

    return file_list

filelist.findall = findall

# Extend the sdist command
class feedmejack_sdist(sdist):
    def run(self):
        # Run the parent command
        sdist.run(self)

    def make_release_tree(self, base_dir, files):
        # Run the parent command first
        sdist.make_release_tree(self, base_dir, files)

        testSourceTree(base_dir, releaseMode=True)


data_files = [
]

setup(name='feedmejack',
      version='0.1',
      cmdclass={"sdist": feedmejack_sdist},
      description='Python module for all kinds of crap',
      author='Peter M. Jones', author_email='pmjones@gmail.com',
      url='https://github.com/vathpela/feedmejack',
      data_files=data_files,
      packages=['feedmejack',
                'feedmejack.exceptions',
                'feedmejack.gcode',
                'feedmejack.logger',
                'feedmejack.masks',
                'feedmejack.rasters',
                'feedmejack.shapes',
                'feedmejack.tools',
                'feedmejack.trace',
                'feedmejack.tracers',
                'feedmejack.xyz']
)
