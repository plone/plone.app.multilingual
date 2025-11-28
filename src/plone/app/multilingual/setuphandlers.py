from plone.app.multilingual import logger
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.itg import addAttributeTG
from plone.base.interfaces import INonInstallable
from plone.base.utils import get_installer
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Prevents uninstall profile from showing up in the profile list
        when creating a Plone site.

        """
        return [
            "plone.app.multilingual:uninstall",
        ]


def add_volto_blocks_behavior_to_lrf(portal):
    """Add volto.blocks behavior to LRF if plone.volto is installed.

    When plone.volto is installed before plone.app.multilingual, the LRF type
    should have the volto.blocks behavior to support Volto's block-based editing.
    """
    installer = get_installer(portal)

    if not installer.is_product_installed("plone.volto"):
        return

    types_tool = portal.portal_types
    lrf_fti = types_tool.get("LRF")
    if lrf_fti is None:
        return

    behaviors = list(getattr(lrf_fti, "behaviors", ()))
    if "volto.blocks" not in behaviors:
        behaviors.append("volto.blocks")
        lrf_fti.behaviors = tuple(behaviors)
        logger.info("Added volto.blocks behavior to LRF type")


def init_pam(tool):
    """After installation run setup to create LRF and LIF."""
    site = getSite()
    setup_tool = SetupMultilingualSite()
    setup_tool.setupSite(site)
    add_volto_blocks_behavior_to_lrf(site)


def step_default_various(context):
    if context.readDataFile("plone.app.multilingual_default.txt") is None:
        return
    portal = context.getSite()
    enable_translatable_behavior(portal)

    # Add the attribute to the site root now so plone.protect won't cry.
    addAttributeTG(portal, None)


def enable_translatable_behavior(portal):
    types_tool = portal.portal_types

    # Iterate through all Dexterity content type, except the site root
    all_ftis = types_tool.listTypeInfo()
    dx_ftis = (
        fti
        for fti in all_ftis
        if getattr(fti, "behaviors", False) and fti.getId() != "Plone Site"
    )
    for fti in dx_ftis:
        # Enable translatable behavior for all types
        if "plone.translatable" not in fti.behaviors:
            behaviors = list(fti.behaviors)
            behaviors.append("plone.translatable")
            fti._updateProperty("behaviors", tuple(behaviors))


def step_uninstall_various(context):
    if context.readDataFile("plone.app.multilingual_uninstall.txt") is None:
        return
    portal = context.getSite()
    disable_translatable_behavior(portal)
    disable_language_switcher(portal)


def disable_translatable_behavior(portal):
    """Remove p.a.multilingual behaviors from p.a.contenttypes types"""
    types_tool = portal.portal_types

    # Iterate through all Dexterity content type
    all_ftis = types_tool.listTypeInfo()
    dx_ftis = [x for x in all_ftis if getattr(x, "behaviors", False)]
    for fti in dx_ftis:
        # Disable translatable behavior from all types
        behaviors = [i for i in fti.behaviors if i != "plone.translatable"]
        fti._updateProperty("behaviors", behaviors)


def disable_language_switcher(portal):
    """Remove the use of language-switcher as default view for Plone Site"""
    tt = getToolByName(portal, "portal_types")
    site = tt["Plone Site"]
    site.view_methods = tuple(
        method for method in site.view_methods if method != "language-switcher"
    )
    if site.default_view == "language-switcher":
        site.default_view = "listing_view"

    logger.info("Language switcher disabled")
