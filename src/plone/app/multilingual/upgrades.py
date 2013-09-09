from Products.CMFCore.utils import getToolByName


def reimport_css_registry(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(
        'profile-plone.app.multilingual:default', 'cssregistry',
        run_dependencies=False, purge_old=False)

    # Refresh css
    cssregistry = getToolByName(context, 'portal_css')
    cssregistry.cookResources()
