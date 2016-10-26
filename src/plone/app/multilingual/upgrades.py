# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from plone.app.multilingual import logger
from Products.CMFPlone.interfaces import ILanguage
from time import time

import transaction


SHARED_NAME = 'shared'  # old shared folder name
OLD_PREFIX = 'old_'  # temporary prefix while migrating
PROFILE_ID = 'profile-plone.app.multilingual:default'


def reimport_css_registry(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(
        'profile-plone.app.multilingual:default', 'cssregistry',
        run_dependencies=False, purge_old=False)

    # Refresh css
    cssregistry = getToolByName(context, 'portal_css')
    cssregistry.cookResources()


def migration_pam_1_to_2(context):
    """Migration plone.app.multilingual 1.x to 2.0 by renaming existing
       language folders and creating new LRF containers where existing
       objects are moved into. Old shared content is moved to portal
       root."""

    s1 = time()
    type_name = 'LRF'
    ltool = getToolByName(context, 'portal_languages')
    utool = getToolByName(context, 'portal_url')
    wtool = getToolByName(context, 'portal_workflow')
    portal = utool.getPortalObject()

    logger.info("Starting migration of language folders.")

    for code, name in ltool.listSupportedLanguages():

        if code not in portal:
            continue

        older = portal[code]

        if older.portal_type == type_name:
            logger.info("'{0}' is alredy a {1}, skipping.".format(
                code, type_name))
            continue

        # PHASE 1: rename old language folders
        s2 = time()
        old_id = OLD_PREFIX + older.id
        logger.info("{0} - Phase 1: Renaming to '{1}' ..."
                    .format(code, old_id))
        portal.manage_renameObject(older.id, old_id)
        logger.info("{0} - Phase 1: Renaming to '{1}' took {2:.2f}s."
                    .format(code, old_id, time() - s2))
        transaction.savepoint()

        # PHASE 2: move content to new LRF
        s3 = time()
        old = portal[old_id]
        logger.info("{0} - Phase 2: Moving objects into new LRF..."
                    .format(code))

        _createObjectByType(type_name, portal, code)
        new = portal[code]
        new.setTitle(name)
        ILanguage(new).set_language(code)

        state = wtool.getInfoFor(new, 'review_state', None)
        available_transitions = [t['id'] for t in wtool.getTransitionsFor(new)]
        if state != 'published' and 'publish' in available_transitions:
            wtool.doActionFor(new, 'publish')
        new.reindexObject()
        transaction.savepoint()

        new.manage_pasteObjects(
            old.manage_cutObjects(ids=old.objectIds()))

        logger.info("{0} - Phase 2: Moving objects to LRF took in {1:.2f}s."
                    .format(code, time() - s3))

        transaction.savepoint()

        # PHASE 3: remove old language folders
        s4 = time()
        portal.manage_delObjects(ids=[old_id, ])
        logger.info("{0} - Phase 3: Removing '{1}' took {2:.2f}s."
                    .format(code, old_id, time() - s4))

        transaction.savepoint()

    # PHASE 4: Old shared folder
    if SHARED_NAME in portal:

        s5 = time()
        shared = portal[SHARED_NAME]
        logger.info("{0} - Phase 4: Moving content to root..."
                    .format(SHARED_NAME))

        portal.manage_pasteObjects(
            shared.manage_cutObjects(ids=shared.objectIds()))

        logger.info("{0} - Phase 4: Moving objects into root took {1:.2f}s."
                    .format(SHARED_NAME, time() - s5))

        transaction.savepoint()

        s6 = time()
        portal.manage_delObjects(ids=[SHARED_NAME, ])
        logger.info("{0} - Phase 5: Removing it took {1:.2f}s."
                    .format(SHARED_NAME, time() - s6))

    logger.info("All finished in {0}.".format(time() - s1))


def upgrade_to_4(context):
    context.runImportStepFromProfile(
        PROFILE_ID.replace('default', 'to_4'),
        'plone.app.registry'
    )
