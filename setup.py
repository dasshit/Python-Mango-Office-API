#!/usr/bin/env python
from setuptools import setup
from io import open

def read(filename):
    with open(filename, encoding='utf-8') as file:
        return file.read()

setup(name='Python-Mango-Office-API',
      version='3.7.2',
      description='API wrapper for Mango Office.',
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      author='dasshit',
      author_email='v.korobov@mangotele.com',
      url='https://github.com/dasshit/Python-Mango-Office-API',
      packages=['mangoapi'],
      license='GPL2',
      keywords='mangooffice mango',
      install_requires=['requests', 'datetime'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      ]
      )
