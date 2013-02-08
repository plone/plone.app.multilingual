import unittest

from plone.testing import layered
# from plone.app.testing import PLONE_ZSERVER

from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_ACCEPTANCE_TESTING

import robotsuite

from zope.component.hooks import getSite
from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from Products.CMFCore.utils import getToolByName

import transaction


def setUp():
    portal = getSite()
    language_tool = getToolByName(portal, 'portal_languages')
    language_tool.addSupportedLanguage('ca')
    language_tool.addSupportedLanguage('es')

    doc1 = makeContent(portal, 'Document', id='doc1', title='EN doc')
    doc1.setLanguage('en')
    doc1_ca = makeTranslation(doc1, 'ca')
    doc1_ca.edit(title="CA doc", language='ca')
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
