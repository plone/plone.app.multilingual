from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def reimport_css_registry(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(
        'profile-plone.app.multilingual:default', 'cssregistry',
        run_dependencies=False, purge_old=False)

    # Refresh css
    cssregistry = getToolByName(context, 'portal_css')
    cssregistry.cookResources()


def upgrade_2_to_3_add_missing_registry_entry(context):
    registry = getUtility(IRegistry)

    # don't re-create if it already exists
    key = ('plone.app.multilingual.interfaces.'
           'IMultiLanguageExtraOptionsSchema.'
           'bypass_languageindependent_field_permission_check')
    if key in registry:
        return

    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile(
        'profile-plone.app.multilingual.upgrades:3')
