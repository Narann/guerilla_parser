import os.path
import sys
from setuptools import setup

_repo_path = os.path.split(__file__)[0]
sys.path.append(os.path.join(_repo_path, 'src'))

import guerilla_parser

with open('README.md', 'rt') as f:
    long_description = f.read()

setup(name='guerilla-parser',
      version=guerilla_parser.__version__,
      license='MIT',
      author='Dorian Fevrier',
      url='https://github.com/Narann/guerilla_parser',
      author_email='fevrier.dorian@yahoo.fr',
      description=('This python module provide an easy way to parse Guerilla '
                   'files and navigate into parsed nodes and plugs.'),
      long_description=long_description,
      long_description_content_type='text/markdown',
      include_package_data=True,  # enable MANIFEST.in
      keywords='guerilla, parser, gproject',
      packages=['guerilla_parser'],
      package_dir={'': 'src'},
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Operating System :: OS Independent',
      ],
      python_requires='>=2.7',
      options={'bdist_wheel': {'universal': True}},
      )
