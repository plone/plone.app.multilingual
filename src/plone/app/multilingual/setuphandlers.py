import logging
from Products.CMFCore.utils import getToolByName
# The profile id of your package:
PROFILE_ID = 'profile-plone.app.multilingual:default'

def add_catalog_indexes(context, logger):
    '''Add index 'language' to portal_catalog and uid_catalog
    '''
    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()
    wanted = (('Language', 'FieldIndex'),)

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
