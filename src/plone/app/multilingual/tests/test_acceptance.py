import unittest

from plone.testing import layered
from plone.app.testing import applyProfile
# from plone.app.testing import PLONE_ZSERVER

from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_ACCEPTANCE_TESTING

import robotsuite

from zope.component.hooks import getSite
from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from Products.CMFCore.utils import getToolByName
from plone.dexterity.utils import createContentInContainer
from plone.multilingual.interfaces import ILanguage

import transaction


def setUp():
    portal = getSite()
    applyProfile(portal, 'plone.multilingualbehavior:default')

    language_tool = getToolByName(portal, 'portal_languages')
    language_tool.addSupportedLanguage('ca')
    language_tool.addSupportedLanguage('es')

    atdoc = makeContent(portal, 'Document', id='atdoc', title='EN doc')
    atdoc.setLanguage('en')
    atdoc_ca = makeTranslation(atdoc, 'ca')
    atdoc_ca.edit(title="CA doc", language='ca')

    dxdoc = createContentInContainer(portal, "dxdoc", id="dxdoc", title='EN doc')
    ILanguage(dxdoc).set_language('en')
    dxdoc_ca = makeTranslation(dxdoc, 'ca')
    dxdoc_ca.title = "CA doc"
    ILanguage(dxdoc_ca).set_language('ca')

    transaction.commit()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        # layered(robotsuite.RobotTestSuite("test_accessibility.txt"),
        #         layer=PLONE_ZSERVER),
        layered(robotsuite.RobotTestSuite("test_acceptance.txt", setUp=setUp),
                layer=PLONEAPPMULTILINGUAL_ACCEPTANCE_TESTING,
                ),
    ])
    return suite
