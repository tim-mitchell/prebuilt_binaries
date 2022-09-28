import os
import pathlib

from distutils.file_util import copy_file
from setuptools.command import build_ext
from setuptools import Extension


class PrebuiltExtension(Extension):
    def __init__(self, input_file, package=None):
        name = pathlib.Path(input_file).stem
        if package is not None:
            name = f'{package}.{name}'
        if not os.path.exists(input_file):
            raise ValueError(f'Prebuilt extension file not found\n{input_file}')
        self.input_file = input_file
        super().__init__(name, ['no-source-needed.c'])


class prebuilt_binary(build_ext.build_ext):

    def run(self):
        for ext in self.extensions:
            fullname = self.get_ext_fullname(ext.name)
            filename = self.get_ext_filename(fullname)
            if not os.path.exists(self.build_lib):
                os.makedirs(self.build_lib)
            dest_filename = os.path.join(self.build_lib,
                                         os.path.basename(filename))

            copy_file(
                ext.input_file, dest_filename, verbose=self.verbose,
                dry_run=self.dry_run
            )
        if self.inplace:
            self.copy_extensions_to_source()
