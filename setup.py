"""Setup plone.app.multilingual."""
from setuptools import find_packages
from setuptools import setup

import os


version = '5.4.0'

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
        'Framework :: Plone :: 5.2',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
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
        'Products.CMFPlone>=5.2rc4',
        'setuptools',
        'six',
    ],
    extras_require={
        'archetypes': [
            'archetypes.multilingual',
        ],
        'test': [
            'plone.app.testing[robot]',
            'plone.app.robotframework',
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
