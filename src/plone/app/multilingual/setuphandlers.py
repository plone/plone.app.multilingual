from Products.CMFCore.utils import getToolByName
# The profile id of your package:
PROFILE_ID = 'profile-plone.app.multilingual:default'


def add_catalog_indexes(context, logger):
    '''Add index 'language' to portal_catalog and uid_catalog
    '''
    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()
    schema = catalog.schema()
    wanted = (('Language', 'FieldIndex'), ('TranslationGroup', 'FieldIndex'))

    indexables = []
    metadata = []
    for (name, meta_type) in wanted:
        if meta_type and name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info('Added %s for field %s.', meta_type, name)
        if name not in schema:
            catalog.addColumn(name)
            metadata.append(name)
            logger.info('Added catalog metadata column for field %s.' % name)
    if len(indexables) > 0 or len(metadata) > 0:
        logger.info('Indexing new indexes %s.', ', '.join(indexables))
        # We don't call catalog.manage_reindexIndex(ids=indexables)
        # because that method will not update the metadata.
        # Therefore the code of manage_reindexIndex is copied below, but
        # update_metadata is set to True
        paths = catalog._catalog.uids.keys()
        for p in paths:
            obj = catalog.resolve_path(p)
            if obj is None:
                obj = catalog.resolve_url(p, context.REQUEST)
            if obj is None:
                logger.error(
                    'reindexIndex could not resolve an object from the uid '
                    '%r.' % p)
            else:
                # Here we explicitly want to also update the metadata
                catalog.catalog_object(
                    obj, p, idxs=indexables, update_metadata=1)


def setup_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('plone.app.multilingual-reindex.txt') is None:
        return
    logger = context.getLogger('plone.app.multiligual')
    site = context.getSite()
    add_catalog_indexes(site, logger)
