# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from email.header import Header
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.robotframework import AutoLogin
from plone.app.robotframework import Content
from plone.app.robotframework import RemoteLibraryLayer
from plone.app.robotframework.remote import RemoteLibrary
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import ploneSite
from plone.app.testing import setRoles
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import iterSchemata
from plone.dexterity.utils import iterSchemataForType
from plone.rfc822 import constructMessageFromSchemata
from plone.rfc822 import initializeObjectFromSchemata
from plone.testing import z2
from plone.uuid.interfaces import IUUID
from zope.configuration import xmlconfig
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.lifecycleevent import ObjectModifiedEvent
import plone.app.dexterity
import plone.app.multilingual
try:
    from plone.app.robotframework.utils import disableCSRFProtection
except ImportError:
    def disableCSRFProtection():
        pass


class PloneAppMultilingualLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Configure ZCML
        xmlconfig.file('testing.zcml', plone.app.multilingual,
                       context=configurationContext)

        xmlconfig.file('overrides.zcml', plone.app.multilingual,
                       context=configurationContext)

        # Enable languageindependent-field on IRelatedItems-behavior
        from plone.app.relationfield.behavior import IRelatedItems
        alsoProvides(IRelatedItems['relatedItems'], ILanguageIndependentField)

    def setUpPloneSite(self, portal):
        # Activate product
        applyProfile(portal, 'plone.app.multilingual:default')

        # Empower test user
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # Enable all errors
        error_log = getToolByName(portal, 'error_log')
        error_log._ignored_exceptions = ()

        # Set default workflow
        wftool = getToolByName(portal, 'portal_workflow')
        wftool.setDefaultChain('simple_publication_workflow')

        # Cleanup p.a.contenttypes stuff
        if 'robot-test-folder' in portal.objectIds():
            portal.manage_delObjects('robot-test-folder')

PLONE_APP_MULTILINGUAL_FIXTURE = PloneAppMultilingualLayer()

PLONE_APP_MULTILINGUAL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_MULTILINGUAL_FIXTURE,),
    name="plone.app.multilingual:Integration")


class PloneAppMultiLingualPresetLayer(PloneSandboxLayer):
    """Test installation with preset languages."""

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Configure ZCML
        xmlconfig.file('testing.zcml', plone.app.multilingual,
                       context=configurationContext)

        xmlconfig.file('overrides.zcml', plone.app.multilingual,
                       context=configurationContext)

        # Enable languageindependent-field on IRelatedItems-behavior
        from plone.app.relationfield.behavior import IRelatedItems
        alsoProvides(IRelatedItems['relatedItems'], ILanguageIndependentField)

    def setUpPloneSite(self, portal):
        # Define available languages before installing PAM
        # This simulates the behavior of having predefined languages
        # in GenericSetup before installing PAM
        language_tool = getToolByName(portal, 'portal_languages')
        language_tool.addSupportedLanguage('ca')
        language_tool.addSupportedLanguage('es')

        # Enable request negotiator
        language_tool.use_request_negotiation = True

        # Activate product
        applyProfile(portal, 'plone.app.multilingual:default')

        # Empower test user
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # Enable all errors
        error_log = getToolByName(portal, 'error_log')
        error_log._ignored_exceptions = ()

        # Set default workflow
        wftool = getToolByName(portal, 'portal_workflow')
        wftool.setDefaultChain('simple_publication_workflow')

        # Cleanup p.a.contenttypes stuff
        if 'robot-test-folder' in portal.objectIds():
            portal.manage_delObjects('robot-test-folder')

PLONE_APP_MULTILINGUAL_PRESET_FIXTURE = PloneAppMultiLingualPresetLayer()

PLONE_APP_MULTILINGUAL_PRESET_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_APP_MULTILINGUAL_PRESET_FIXTURE,),
    name="plone.app.multilingual:PresetIntegration")


class MultipleLanguagesLayer(z2.Layer):

    defaultBases = (PLONE_APP_MULTILINGUAL_PRESET_FIXTURE,)


MULTIPLE_LANGUAGES_LAYER = MultipleLanguagesLayer()

PLONE_APP_MULTILINGUAL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MULTIPLE_LANGUAGES_LAYER,),
    name="plone.app.multilingual:Functional")


class MultiLingual(RemoteLibrary):

    def create_content_type(self, portal_type):
        """Create dummy content type with a single custom field"""
        disableCSRFProtection()
        fti = DexterityFTI(str(portal_type), title=portal_type)
        fti.behaviors = (
            'plone.app.dexterity.behaviors.metadata.IBasic',
            'plone.app.multilingual.dx.interfaces.IDexterityTranslatable'
        )
        fti.model_source = u"""\
<model xmlns="http://namespaces.plone.org/supermodel/schema">
<schema>
<field name="custom" type="zope.schema.TextLine">
  <description />
  <required>False</required>
  <title>Custom field</title>
</field>
</schema>
</model>"""
        fti.global_allow = True
        self.portal_types._setObject(str(portal_type), fti)

        # TODO: This should be split into two separate keywords:
        # - Create content type
        # - Add content type field

    def set_field_language_independent(self, portal_type, field, value='1'):
        """Set the given field in the given portal type language independent
        or unset from being one
        """
        disableCSRFProtection()
        for schema in iterSchemataForType(portal_type):
            if field in schema:
                ob = schema[field]
                if ILanguageIndependentField.providedBy(ob):
                    if value.lower() not in ('true', 'on', 'yes', 'y', '1'):
                        noLongerProvides(schema[ob], ILanguageIndependentField)
                else:
                    if value.lower() in ('true', 'on', 'yes', 'y', '1'):
                        alsoProvides(ob, ILanguageIndependentField)

    def create_translation(self, *args, **kwargs):
        """Create translation for an object with uid in the given
        target_language and return its UID

        Usage::

            Create translation  /plone/en/foo  ca  title=Translated
        """
        disableCSRFProtection()
        # Parse arguments:
        uid_or_path = args[0]
        target_language = args[1]

        # BBB: Support keywords arguments with robotframework < 2.8.3
        kwargs.update(dict([arg.split('=', 1) for arg in args[2:]]))

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

PLONE_APP_MULTILINGUAL_ROBOT_TESTING = FunctionalTesting(
    bases=(MULTIPLE_LANGUAGES_LAYER,
           REMOTE_LIBRARY_BUNDLE_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="plone.app.multilingual:Robot")


PAM_INTEGRATION_TESTING = PLONE_APP_MULTILINGUAL_INTEGRATION_TESTING
PAM_INTEGRATION_PRESET_TESTING = \
    PLONE_APP_MULTILINGUAL_PRESET_INTEGRATION_TESTING
PAM_FUNCTIONAL_TESTING = PLONE_APP_MULTILINGUAL_FUNCTIONAL_TESTING
PAM_ROBOT_TESTING = PLONE_APP_MULTILINGUAL_ROBOT_TESTING
