"""Setup plone.app.multilingual."""
from setuptools import find_packages
from setuptools import setup


setup(
    # metadata in setup.cfg
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
