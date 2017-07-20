"""Setup plone.app.multilingual."""
from setuptools import find_packages
from setuptools import setup

import os


version = '5.1.1'

setup(
    name='plone.app.multilingual',
    version=version,
    description='Multilingual Plone UI package, enables maintenance of '
                'translations for both Dexterity types and Archetypes',
    long_description='\n\n'.join([
        open('README.rst').read(),
        open(os.path.join('docs', 'CREDITS.txt')).read(),
        open('CHANGES.rst').read(),
    ]),
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 5.0',
        'Framework :: Plone :: 5.1',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url='https://github.com/plone/plone.app.multilingual',
    license='GPL',
    keywords='language multilingual content',
    author='Ramon Navarro, Victor Fernandez de Alba, awello et al',
    author_email='r.navarro@iskra.cat',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.CMFPlone>=5.0b1',
        'Products.GenericSetup>=1.8.2',
        # we want p.a.layout >= 2.5.22 on 2.5.x branch OR >= 2.6.3
        'plone.app.layout>=2.5.22,!=2.6.0,!=2.6.1,!=2.6.2',
        'plone.app.registry',
        'plone.app.z3cform',
        'plone.behavior',
        'plone.dexterity',
        'setuptools',
        'z3c.relationfield',
        'zope.publisher',
    ],
    extras_require={
        'archetypes': [
            'archetypes.multilingual',
        ],
        'test': [
            'plone.app.testing[robot]>=4.2.2',
            'plone.app.robotframework',
            'plone.app.contenttypes',
            'archetypes.multilingual',
            'decorator',  # BBB
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
