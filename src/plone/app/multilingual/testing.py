# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4:
import doctest
from plone.app.testing import (
    PLONE_FIXTURE,
    PloneSandboxLayer,
    applyProfile,
    IntegrationTesting,
    FunctionalTesting,
    setRoles,
    TEST_USER_ID,
)
from zope.configuration import xmlconfig
import plone.app.multilingual
import plone.app.dexterity


class PloneAppMultilingualLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        xmlconfig.file('configure.zcml', plone.app.multilingual,
                        context=configurationContext)

        xmlconfig.file('configure.zcml', plone.app.multilingual.tests,
                        context=configurationContext)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.app.multilingual.tests:testing')
        setRoles(portal, TEST_USER_ID, ['Manager'])


PLONEAPPMULTILINGUAL_FIXTURE = PloneAppMultilingualLayer()

PLONEAPPMULTILINGUAL_INTEGRATION_TESTING = IntegrationTesting(\
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,),\
    name="plone.app.multilingual:Integration")
PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING = FunctionalTesting(\
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,),\
    name="plone.app.multilingual:Functional")

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
