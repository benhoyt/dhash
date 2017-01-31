"""Run "python setup.py install" to install dhash."""

import os
import re
from distutils.core import setup


# Because it's best not to import the module in setup.py
with open(os.path.join(os.path.dirname(__file__), 'dhash.py')) as f:
    for line in f:
        match = re.match(r"__version__.*'([0-9.]+)'", line)
        if match:
            version = match.group(1)
            break
    else:
        raise Exception("Couldn't find __version__ line in dhash.py")


# Read long_description from README.rst
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    long_description = f.read()


setup(
    name='dhash',
    version=version,
    author='Ben Hoyt',
    author_email='benhoyt@gmail.com',
    url='https://github.com/Jetsetter/dhash',
    license='MIT License',
    description='Calculate difference hash (percentual hash) for a given image, useful for detecting duplicates',
    long_description=long_description,
    py_modules=['dhash'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Graphics',
    ]
)
