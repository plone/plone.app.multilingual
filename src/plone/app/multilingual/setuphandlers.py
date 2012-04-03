from Products.CMFCore.utils import getToolByName


def importReindexLanguageIndex(context):
    if context.readDataFile("plone.app.multilingual-reindex.txt") is None:
        return
    site = context.getSite()
    logger = context.getLogger('plone.app.multilingual')
    catalog = getToolByName(site, 'portal_catalog')

    catalog.manage_catalogRebuild()