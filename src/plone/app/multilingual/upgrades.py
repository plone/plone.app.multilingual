from Acquisition import aq_base
from plone.app.multilingual import logger
from plone.base.interfaces import ILanguage
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from plone.base.utils import unrestricted_construct_instance
from time import time
from zope.component import getUtility

import transaction


SHARED_NAME = "shared"  # old shared folder name
OLD_PREFIX = "old_"  # temporary prefix while migrating
PROFILE_ID = "profile-plone.app.multilingual:default"


def reimport_css_registry(context):
    setup = getToolByName(context, "portal_setup")
    setup.runImportStepFromProfile(
        "profile-plone.app.multilingual:default",
        "cssregistry",
        run_dependencies=False,
        purge_old=False,
    )

    # Refresh css
    cssregistry = getToolByName(context, "portal_css")
    cssregistry.cookResources()


def migration_pam_1_to_2(context):
    """Migration plone.app.multilingual 1.x to 2.0 by renaming existing
    language folders and creating new LRF containers where existing
    objects are moved into. Old shared content is moved to portal
    root."""

    s1 = time()
    type_name = "LRF"
    ltool = getToolByName(context, "portal_languages")
    utool = getToolByName(context, "portal_url")
    wtool = getToolByName(context, "portal_workflow")
    portal = utool.getPortalObject()

    logger.info("Starting migration of language folders.")

    for code, name in ltool.listSupportedLanguages():
        if code not in portal:
            continue

        older = portal[code]

        if older.portal_type == type_name:
            logger.info(f"'{code}' is alredy a {type_name}, skipping.")
            continue

        # PHASE 1: rename old language folders
        s2 = time()
        old_id = OLD_PREFIX + older.id
        logger.info(f"{code} - Phase 1: Renaming to '{old_id}' ...")
        portal.manage_renameObject(older.id, old_id)
        logger.info(
            "{} - Phase 1: Renaming to '{}' took {:.2f}s.".format(
                code, old_id, time() - s2
            )
        )
        transaction.savepoint()

        # PHASE 2: move content to new LRF
        s3 = time()
        old = portal[old_id]
        logger.info(f"{code} - Phase 2: Moving objects into new LRF...")

        unrestricted_construct_instance(type_name, portal, code)
        new = portal[code]
        new.setTitle(name)
        ILanguage(new).set_language(code)

        state = wtool.getInfoFor(new, "review_state", None)
        available_transitions = [t["id"] for t in wtool.getTransitionsFor(new)]
        if state != "published" and "publish" in available_transitions:
            wtool.doActionFor(new, "publish")
        new.reindexObject()
        transaction.savepoint()

        new.manage_pasteObjects(old.manage_cutObjects(ids=old.objectIds()))

        logger.info(
            "{} - Phase 2: Moving objects to LRF took in {:.2f}s.".format(
                code, time() - s3
            )
        )

        transaction.savepoint()

        # PHASE 3: remove old language folders
        s4 = time()
        portal.manage_delObjects(
            ids=[
                old_id,
            ]
        )
        logger.info(
            "{} - Phase 3: Removing '{}' took {:.2f}s.".format(
                code, old_id, time() - s4
            )
        )

        transaction.savepoint()

    # PHASE 4: Old shared folder
    if SHARED_NAME in portal:
        s5 = time()
        shared = portal[SHARED_NAME]
        logger.info(f"{SHARED_NAME} - Phase 4: Moving content to root...")

        portal.manage_pasteObjects(shared.manage_cutObjects(ids=shared.objectIds()))

        logger.info(
            "{} - Phase 4: Moving objects into root took {:.2f}s.".format(
                SHARED_NAME, time() - s5
            )
        )

        transaction.savepoint()

        s6 = time()
        portal.manage_delObjects(
            ids=[
                SHARED_NAME,
            ]
        )
        logger.info(f"{SHARED_NAME} - Phase 5: Removing it took {time() - s6:.2f}s.")

    logger.info(f"All finished in {time() - s1}.")


def upgrade_to_3(context):
    registry = getUtility(IRegistry)

    # don't re-create if it already exists
    key = (
        "plone.app.multilingual.interfaces.IMultiLanguageExtraOptionsSchema."
        "bypass_languageindependent_field_permission_check"
    )
    if key in registry:
        return

    context.runImportStepFromProfile(
        PROFILE_ID.replace("default", "to_3"),
        "plone.app.registry",
    )


def upgrade_to_4(context):
    context.runImportStepFromProfile(
        PROFILE_ID.replace("default", "to_4"),
        "plone.app.registry",
    )


def update_old_layouts(context):
    """We may have no longer existing layouts layouts set."""
    DEFAULT = "folder_listing"
    MAPPING = {
        "folder_summary_view": "summary_view",
        "folder_full_view": "full_view",
        "folder_tabular_view": "tabular_view",
        "atct_album_view": "album_view",
    }
    types_tool = getToolByName(context, "portal_types")
    catalog = getToolByName(context, "portal_catalog")
    our_types = ["LIF", "LRF"]
    for type_name in our_types:
        fti = types_tool.get(type_name)
        if fti is None:
            # Should not happen, but I like upgrade steps to be forgiving.
            logger.warning("Could not find portal_type %s.", type_name)
            continue

        # First update the FTI.
        old_view_methods = fti.view_methods
        view_methods = []
        for name in fti.view_methods:
            name = MAPPING.get(name, name)
            view_methods.append(name)
        if DEFAULT not in view_methods:
            view_methods.append(DEFAULT)
        view_methods = tuple(view_methods)
        if old_view_methods != view_methods:
            fti.view_methods = view_methods
            logger.info("Updated old view methods in FTI %s.", type_name)
        if fti.default_view not in view_methods:
            default_view = MAPPING.get(fti.default_view, DEFAULT)
            logger.info("Set default_view of FTI %s to %s.", type_name, default_view)
            fti.default_view = default_view

        # Now update all instances of this FTI.
        for brain in catalog.unrestrictedSearchResults(portal_type=type_name):
            obj = brain.getObject()
            layout = obj.getProperty("layout", None)
            if layout is None or layout in view_methods:
                continue
            new_layout = MAPPING.get(layout)
            if not new_layout:
                # Use the default view: remove the explicit layout.
                obj._delProperty("layout")
                logger.info(
                    "Removed property 'layout' with value %r at %s",
                    layout,
                    "/".join(obj.getPhysicalPath()),
                )
                continue
            obj._updateProperty("layout", new_layout)
            logger.info(
                "Updated property 'layout' to %r at %s",
                new_layout,
                "/".join(obj.getPhysicalPath()),
            )
