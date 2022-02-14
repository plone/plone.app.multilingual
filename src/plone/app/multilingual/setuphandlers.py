from logging import getLogger
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.itg import addAttributeTG
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.utils import getToolByName
from zope.component.hooks import getSite
from zope.interface import implementer

import pkg_resources


try:
    pkg_resources.get_distribution("plone.app.contenttypes")
except pkg_resources.DistributionNotFound:
    HAS_PLONE_APP_CONTENTTYPES = False
else:
    HAS_PLONE_APP_CONTENTTYPES = True


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Prevents uninstall profile from showing up in the profile list
        when creating a Plone site.

        """
        return [
            "plone.app.multilingual:uninstall",
        ]


def init_pam(tool):
    """After installation run setup to create LRF and LIF."""
    setup_tool = SetupMultilingualSite()
    setup_tool.setupSite(getSite())


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
        behaviors = list(fti.behaviors)
        behaviors.extend(
            [
                "plone.translatable",
            ]
        )
        behaviors = tuple(set(behaviors))
        fti._updateProperty("behaviors", behaviors)


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

    log = getLogger("setuphandlers.disable_language_switcher")
    log.info("Language switcher disabled")
