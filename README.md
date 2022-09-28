# prebuilt_binaries
A setuptools command for packaging pre-built binary python extension modules.

If you are already using cmake as your build tool, having to then build your library 
with setuptools in order to package it can be annoying.  
 
prebuild_binaries allows you to pass an already built extension module (.pyd file) to setuptools 
for inclusion in a wheel.

Note that it is your responsibility to do this with the same python version as the file was created 
with - however this is pretty easy to get right when it's part of the same build chain. 

# API

`class PrebuiltExtension(input_filename, package=None)`

: where `input_filename` is the full path to the pre-built extension module (.pyd file)
The stem of `input_filename` is used for the name of the extension module.
If `package` is passed then the name of the extension module will be `<package>.<name>`

`class prebuilt_binary`

: setuptools command class that takes PrebuiltExtension instances as parameters and copies the input file
to the correct location.  It is a replacement for the setuptools `build_ext` command. 

# Minimal setup.py example
```python
import os
from setuptools import setup
from prebuilt_binaries import prebuilt_binary, PrebuiltExtension

ext_module = PrebuiltExtension(os.environ['PREBUILT_FILE'])

setup(
    name='my_package',
    version='version',
    cmdclass={
        'build_ext': prebuilt_binary,
    },
    ext_modules=[ext_module]
)
```
In this example the `PREBUILT_FILE` environment variable contains the desired path.  The `cmdclass` mapping is required to tell
setuptools to use the `prebuilt_binary` class to "build" the extensions specified in `ext_modules`.

# CMakeLists.txt example
```
find_package(Python REQUIRED)

file(GLOB build_wheel_SOURCE_FILES pyproject.toml setup.py)

add_custom_target(build_wheel
    COMMAND ${CMAKE_COMMAND} -E env PREBUILT_FILE=$<TARGET_FILE:py_module> ${Python_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/setup.py bdist_wheel
    SOURCES ${build_wheel_SOURCE_FILES}
    )

add_dependencies(build_wheel py_module)
```

In this example cmake file `py_module` is the name of the target that builds the extension module.  
It sets the `PREBUILT_FILE` environment variable used by `setup.py` to the output file of the `py_module` target.

# Build dependencies
Don't forget to set `prebuilt_binaries` as a build-time dependancy in your `pyproject.toml` file
```toml
[build-system]
requires = ["setuptools", "prebuilt_binaries"]

```
or in your `setup.cfg` file
```ini
[options]
setup_requires =
    setuptools
    prebuilt_binaries
```
