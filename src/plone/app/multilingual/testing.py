# -*- coding: utf-8 -*-
from OFS.Folder import Folder
from Testing import ZopeTestCase as ztc

from plone.testing import z2
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import ploneSite
from plone.app.testing import setRoles
from zope.configuration import xmlconfig
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from plone.app.robotframework.testing import REMOTE_LIBRARY_ROBOT_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.multilingual.interfaces import ILanguage

from Products.CMFCore.utils import getToolByName

import plone.app.multilingual
import plone.app.dexterity
import doctest
import transaction


class PloneAppMultilingualLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def setUpZope(self, app, configurationContext):
        # load ZCML
        xmlconfig.file('configure.zcml', plone.app.multilingual,
                       context=configurationContext)

        xmlconfig.file('configure.zcml', plone.app.multilingual.tests,
                       context=configurationContext)

        # Support sessionstorage in tests
        app.REQUEST['SESSION'] = self.Session()
        if not hasattr(app, 'temp_folder'):
            tf = Folder('temp_folder')
            app._setObject('temp_folder', tf)
            transaction.commit()

        ztc.utils.setupCoreSessions(app)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.app.multilingual:default')
        applyProfile(portal, 'plone.app.multilingual.tests:testing')
        setRoles(portal, TEST_USER_ID, ['Manager'])

PLONEAPPMULTILINGUAL_FIXTURE = PloneAppMultilingualLayer()


class TwoLanguagesLayer(z2.Layer):

    defaultBases = (PLONE_FIXTURE, )

    def setUp(self):
        with ploneSite() as portal:
            language_tool = getToolByName(portal, 'portal_languages')
            language_tool.addSupportedLanguage('ca')
            language_tool.addSupportedLanguage('es')

            setupTool = SetupMultilingualSite()
            setupTool.setupSite(portal)

            atdoc = makeContent(
                portal['en'], 'Document', id='atdoc', title='EN doc')
            atdoc.setLanguage('en')
            atdoc_ca = makeTranslation(atdoc, 'ca')
            atdoc_ca.edit(title="CA doc", language='ca')

            dxdoc = createContentInContainer(
                portal['en'], "dxdoc", id="dxdoc", title='EN doc')
            ILanguage(dxdoc).set_language('en')
            dxdoc_ca = makeTranslation(dxdoc, 'ca')
            dxdoc_ca.title = "CA doc"
            ILanguage(dxdoc_ca).set_language('ca')

TWO_LANGUAGES_FIXTURE = TwoLanguagesLayer()

PLONEAPPMULTILINGUAL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,),
    name="plone.app.multilingual:Integration")
PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,),
    name="plone.app.multilingual:Functional")

PLONEAPPMULTILINGUAL_ROBOT_TESTING = FunctionalTesting(
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,
           TWO_LANGUAGES_FIXTURE,
           REMOTE_LIBRARY_ROBOT_TESTING,
           z2.ZSERVER_FIXTURE),
    name="plone.app.multilingual:Robot")


optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
