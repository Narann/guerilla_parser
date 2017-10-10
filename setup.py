from setuptools import setup

setup(name='guerilla_parser',
      version='0.1.0',
      scripts=['helloworld'],
      license='MIT',
      author='Dorian Fevrier',
      url='https://github.com/Narann/guerilla_parser',
      author_email='fevrier.dorian@yahoo.fr',
      description=('This python module provide an easy way to parse Guerilla '
                   'files (only .gproject files for now) and navigate into '
                   'parsed nodes and plugs.'),
      keywords='guerilla, parser, gproject',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
      ],
      )
