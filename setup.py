from setuptools import setup, find_packages
import os

version = '3.0.1'

setup(
    name='plone.app.multilingual',
    version=version,
    description="Multilingual Plone UI package, enables maintenance of "
                "translations for both Dexterity types and Archetypes",
    long_description="\n\n".join([
        open("README.rst").read(),
        open(os.path.join("docs", "CREDITS.txt")).read(),
        open("CHANGES.rst").read(),
    ]),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
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
        'z3c.relationfield',
        'plone.behavior',
        'plone.dexterity',
        'plone.app.z3cform',
        'plone.app.registry',
        'archetypes.multilingual'
    ],
    extras_require={
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
