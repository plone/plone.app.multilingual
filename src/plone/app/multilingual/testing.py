# -*- coding: utf-8 -*-
from OFS.Folder import Folder
from Testing import ZopeTestCase as ztc

from plone.testing.z2 import ZSERVER_FIXTURE
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import plone.app.multilingual
import plone.app.dexterity

from zope.configuration import xmlconfig

import doctest
import transaction


class PloneAppMultilingualLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

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

PLONEAPPMULTILINGUAL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,),
    name="plone.app.multilingual:Integration")
PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,),
    name="plone.app.multilingual:Functional")
PLONEAPPMULTILINGUAL_ROBOT_TESTING = FunctionalTesting(
    bases=(PLONEAPPMULTILINGUAL_FIXTURE, ZSERVER_FIXTURE),
    name="plone.app.multilingual:Robot")
optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
