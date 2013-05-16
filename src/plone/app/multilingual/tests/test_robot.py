from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_ROBOT_TESTING
from plone.app.testing import applyProfile
from plone.dexterity.utils import createContentInContainer
from plone.multilingual.interfaces import ILanguage
from plone.testing import layered
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

import os
import robotsuite
import transaction
import unittest


def setUp():
    portal = getSite()
    applyProfile(portal, 'plone.multilingualbehavior:default')

    language_tool = getToolByName(portal, 'portal_languages')
    language_tool.addSupportedLanguage('ca')
    language_tool.addSupportedLanguage('es')

    workflowTool = getToolByName(portal, "portal_workflow")
    workflowTool.setDefaultChain('simple_publication_workflow')

    setupTool = SetupMultilingualSite()
    setupTool.setupSite(portal)

    transaction.commit()

    atdoc = makeContent(portal['en'], 'Document', id='atdoc', title='EN doc')
    atdoc.setLanguage('en')
    atdoc_ca = makeTranslation(atdoc, 'ca')
    atdoc_ca.edit(title="CA doc", language='ca')

    dxdoc = createContentInContainer(portal['en'], "dxdoc", id="dxdoc", title='EN doc')
    ILanguage(dxdoc).set_language('en')
    dxdoc_ca = makeTranslation(dxdoc, 'ca')
    dxdoc_ca.title = "CA doc"
    ILanguage(dxdoc_ca).set_language('ca')

    transaction.commit()


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in
        os.listdir(robot_dir) if doc.endswith('.robot') and
        doc.startswith('test_')
    ]
    for test in robot_tests:
        suite.addTests([
            layered(robotsuite.RobotTestSuite(test, setUp=setUp),
                    layer=PLONEAPPMULTILINGUAL_ROBOT_TESTING),
        ])
    return suite
