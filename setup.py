# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '1.2.3'

setup(name='plone.app.multilingual',
      version=version,
      description="Multilingual Plone UI package, enables maintenance of translations for both Dexterity types and Archetypes",
      long_description=open("README.rst").read() + "\n\n" +
                       open(os.path.join("docs", "CREDITS.txt")).read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      url='https://github.com/plone/plone.app.multilingual',
      license='GPL',
      author='Ramon Navarro, Victor Fernandez de Alba, awello et al',
      author_email='r.navarro@iskra.cat',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'five.grok',
        'plone.multilingual>=1.1',
        'z3c.relationfield',
        'plone.app.z3cform',
        'plone.app.registry',
        'plone.directives.form',
        'plone.formwidget.contenttree',
        'Products.PloneLanguageTool',
        'archetypes.multilingual < 2.0',  # required while archetypes is default in Plone
      ],
      extras_require={
          'dexterity': ['plone.multilingualbehavior'],
          'archetypes': ['archetypes.multilingual < 2.0'],
          'test': [
              'plone.api', # for skipping tests based on Plone version
              'plone.app.testing[robot]>=4.2.2',
              'plone.app.robotframework',
              'plone.multilingualbehavior',
              'archetypes.multilingual < 2.0',
              'Products.LinguaPlone',
              'decorator',  # BBB
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
 )
