"""Setup plone.app.multilingual."""

from setuptools import find_packages
from setuptools import setup


setup(
    # metadata in setup.cfg
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "BTrees",
        "plone.app.content",
        "plone.app.contentmenu",
        "plone.app.dexterity",
        "plone.app.event",
        "plone.app.i18n",
        "plone.app.layout",
        "plone.app.querystring",
        "plone.app.registry",
        "plone.app.uuid",
        "plone.app.z3cform",
        "plone.autoform",
        "plone.base",
        "plone.behavior",
        "plone.dexterity",
        "plone.i18n>=4.0.4",
        "plone.indexer",
        "plone.locking",
        "plone.memoize",
        "plone.protect",
        "plone.registry",
        "plone.schemaeditor",
        "plone.supermodel",
        "plone.uuid",
        "plone.z3cform",
        "Products.CMFCore",
        "Products.CMFPlone",
        "Products.GenericSetup",
        "Products.statusmessages",
        "setuptools",
        "z3c.form",
        "z3c.relationfield",
        "zc.relation",
        "zope.browsermenu",
        "zope.intid",
        "zope.pagetemplate",
        "Zope",
    ],
    extras_require={
        "test": [
            "plone.app.testing[robot]",
            "plone.app.robotframework",
            "lxml",
            "plone.api",
            "plone.app.contenttypes",
            "plone.app.relationfield",
            "plone.browserlayer",
            "plone.rfc822",
            "plone.testing",
            "robotsuite",
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
