#!/usr/bin/env python3

import locale
from setuptools import find_packages, setup

try:
    locale.getlocale()
except (ValueError, UnicodeError):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

with open('test-requirements.txt') as requirements:
    test_required = requirements.read().splitlines()

if __name__ == '__main__':
    setup(name='coala-quickstart',
          version='0.4.0',
          description='A quickstart tool for coala',
          author='The coala developers',
          maintainer='Satwik Kansal, Adrian Zatreanu, Alexandros Dimos, '
                     'Adhityaa Chandrasekar',
          maintainer_email=('satwikkansal@gmail.com, '
                            'adrianzatreanu1@gmail.com, '
                            'alexandros.dimos.95@gmail.com, '
                            'c.adhityaa@gmail.com'),
          url='https://github.com/coala/coala-quickstart',
          platforms='any',
          packages=find_packages(exclude=['build.*', '*.tests.*', '*.tests']),
          install_requires=required,
          tests_require=test_required,
          license='AGPL-3.0',
          long_description='coala-quickstart is a tool to help you '
                           'quickly and easily get started with '
                           'coala.',
          entry_points={
              'console_scripts': [
                  'coala-quickstart = coala_quickstart.coala_quickstart:main',
                  ]},
          # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=[
              'Development Status :: 4 - Beta',

              'Environment :: Console',
              'Environment :: MacOS X',
              'Environment :: Win32 (MS Windows)',

              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',

              'License :: OSI Approved :: GNU Affero General Public License '
              'v3 or later (AGPLv3+)',

              'Operating System :: OS Independent',

              'Programming Language :: Python :: Implementation :: CPython',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3 :: Only',

              'Topic :: Scientific/Engineering :: Information Analysis',
              'Topic :: Software Development :: Quality Assurance',
              'Topic :: Text Processing :: Linguistic'])
