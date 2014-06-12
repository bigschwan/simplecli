__author__ = 'clarkmatthew'


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
import simplecli

setup(name = "simplecli",
      version = simplecli.__version__,
      description = "CLI framework and utilities for a "
                    "Hybrid Eucalyptus Cloud environment",
      long_description="CLI framework and utilities for a "
                       "Hybrid Eucalyptus Cloud environment",
      author = "Matt Clark",
      author_email = "matt.clark@eucalyptus.com",
      url = "http://open.eucalyptus.com",
      install_requires = [],
      packages = find_packages(),
      license = 'BSD (Simplified)',
      platforms = 'Posix; MacOS X;',
      classifiers = [ 'Development Status :: 3 - Alpha',
                      'Intended Audience :: System Administrators',
                      'License :: OSI Approved :: BSD License',
                      'Operating System :: OS Independent',
                      'Topic :: System :: Systems Administration',
                      ],
      )
