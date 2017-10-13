import os.path
import sys
from setuptools import setup

_repo_path = os.path.split(__file__)[0]
sys.path.append(os.path.join(_repo_path, 'src'))

import guerilla_parser

setup(name='guerilla_parser',
      version=guerilla_parser.__version__,
      license='MIT',
      author='Dorian Fevrier',
      url='https://github.com/Narann/guerilla_parser',
      author_email='fevrier.dorian@yahoo.fr',
      description=('This python module provide an easy way to parse Guerilla '
                   'files (only .gproject files for now) and navigate into '
                   'parsed nodes and plugs.'),
      long_description=open('README.md').read(),
      include_package_data=True,  # enable MANIFEST.in
      keywords='guerilla, parser, gproject',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
      ],
      )
