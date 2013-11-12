# -*- coding: utf-8 -*-
import doctest
from email.header import Header

from OFS.Folder import Folder
from Testing import ZopeTestCase as ztc
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from plone.rfc822 import constructMessageFromSchemata, initializeObjectFromSchemata
from plone.uuid.interfaces import IUUID
from zope.configuration import xmlconfig
from Products.CMFCore.utils import getToolByName
import transaction

from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.robotframework.remote import RemoteLibrary
from plone.app.robotframework import RemoteLibraryLayer
from plone.app.robotframework import AutoLogin
from plone.app.robotframework import Content
from plone.testing import z2
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import TEST_USER_ID, PLONE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import ploneSite
from plone.app.testing import setRoles
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.tests.utils import makeContent, makeTranslation
from plone.dexterity.utils import createContentInContainer, iterSchemata
from plone.app.multilingual.interfaces import ILanguage
import plone.app.multilingual
import plone.app.dexterity


class PloneAppMultilingualLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE, )

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def setUpZope(self, app, configurationContext):
        # load ZCML
        xmlconfig.file('configure.zcml', plone.app.multilingual,
                       context=configurationContext)

        xmlconfig.file('overrides.zcml', plone.app.multilingual,
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

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE, )

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
            atdoc_ca.setTitle(u"CA doc")
            atdoc_ca.setLanguage('ca')

            dxdoc = createContentInContainer(
                portal['en'], "dxdoc", id="dxdoc", title='EN doc')
            ILanguage(dxdoc).set_language('en')
            dxdoc_ca = makeTranslation(dxdoc, 'ca')
            dxdoc_ca.title = "CA doc"
            ILanguage(dxdoc_ca).set_language('ca')

TWO_LANGUAGES_FIXTURE = TwoLanguagesLayer()


class MultiLingual(RemoteLibrary):

    def create_translation(self, *args, **kwargs):
        """Create translation for an object with uid in the given
        target_language and return its UID

        Usage::

            Create translation  /plone/en/foo  ca  title=Translated
        """
        # XXX: **kwargs do not yet with Robot Framework remote libraries
        # Parse arguments:
        uid_or_path = args[0]
        target_language = args[1]
        kwargs = dict([arg.split('=', 1) for arg in args[2:]])

        # Look up translatable content
        pc = getToolByName(self, "portal_catalog")
        uid_results = pc.unrestrictedSearchResults(UID=uid_or_path)
        path_results = pc.unrestrictedSearchResults(
            path={'query': uid_or_path.rstrip('/'), 'depth': 0})
        obj = (uid_results or path_results)[0]._unrestrictedGetObject()

        # Translate
        manager = ITranslationManager(obj)
        manager.add_translation(target_language)
        translation = manager.get_translation(target_language)

        # Update fields
        data = constructMessageFromSchemata(obj, iterSchemata(obj))
        for key, value in kwargs.items():
            del data[key]
            data[key] = Header(value, 'utf-8')
        del data['language']
        initializeObjectFromSchemata(translation, iterSchemata(obj), data)
        notify(ObjectModifiedEvent(translation))

        # Return uid for the translation
        return IUUID(translation)


REMOTE_LIBRARY_BUNDLE_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=(AutoLogin, Content, MultiLingual),
    name="RemoteLibraryBundle:RobotRemote"
)

PLONEAPPMULTILINGUAL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,),
    name="plone.app.multilingual:Integration")
PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,),
    name="plone.app.multilingual:Functional")
PLONEAPPMULTILINGUAL_ROBOT_TESTING = FunctionalTesting(
    bases=(PLONEAPPMULTILINGUAL_FIXTURE,
           TWO_LANGUAGES_FIXTURE,
           REMOTE_LIBRARY_BUNDLE_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="plone.app.multilingual:Robot")
optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
