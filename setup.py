from setuptools import setup, find_packages
import sys, os

version = '0.1a1'

setup(name='plone.app.multilingual',
      version=version,
      description="Multilingual plone ui package, it allow to maintain translation on Dexterity types and Archetypes",
      long_description="""\
Multilingual Plone UI package, in alpha stage, don't use in production
""",
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      url='http://svn.plone.org/svn/plone/plone.app.multilingual',
      license='GPL',
      author='Ramon Navarro, Victor Fernanez, awello et al',
      author_email='r.navarro@iskra.cat',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['plone','plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.multilingual',
        'z3c.relationfield',
        'plone.app.z3cform',
        'plone.app.registry',
        'plone.directives.form',
        'plone.formwidget.contenttree',
        'Products.PloneLanguageTool',
      ],
      extras_require = {
          'dexterity': ['plone.multilingualbehavior'],
          'archetypes': ['archetypes.multilingual'],
          'test': [ 'plone.app.testing',
                    'plone.multilingualbehavior',
                    'archetypes.multilingual'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
 )
