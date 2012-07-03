import logging
from Products.CMFCore.utils import getToolByName
# The profile id of your package:
PROFILE_ID = 'profile-plone.app.multilingual:default'


def importReindexLanguageIndex(context, logger):
    catalog = getToolByName(context, 'portal_catalog')
    logger.info("Rebuilding catalog. This might take very long on large sites.")
    catalog.manage_catalogRebuild()


def add_catalog_indexes(context, logger):
    '''Add index 'language' to portal_catalog and uid_catalog
    '''
    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()
    wanted = (('language', 'FieldIndex'),)
    
    indexables = []
    for (name, meta_type) in wanted:
        if meta_type and name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info('Added %s for field %s.', meta_type, name)
    if len(indexables) > 0:
        logger.info('Indexing new indexes %s.', ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)

    uid_catalog = getToolByName(context, 'uid_catalog')
    uid_indexes = uid_catalog.indexes()

    indexables = []
    for (name, meta_type) in wanted:
        if meta_type and name not in uid_indexes:
            uid_catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info('Added %s for field %s.', meta_type, name)
    if len(indexables) > 0:
        logger.info('Indexing new indexes %s.', ', '.join(indexables))
        uid_catalog.manage_reindexIndex(ids=indexables)


def setup_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('plone.app.multilingual-reindex.txt') is None:
        return
    logger = context.getLogger('plone.app.multiligual')
    site = context.getSite()
    add_catalog_indexes(site, logger)
    # TODO: Do we really need to clear and rebuild? It might be enough that the 
    # new indexes are reindexed in add_catalog_indexes
    importReindexLanguageIndex(site, logger)
