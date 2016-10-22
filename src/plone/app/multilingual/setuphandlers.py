# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from zope.component.hooks import getSite
from zope.interface import implementer

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_PLONE_APP_CONTENTTYPES = False
else:
    HAS_PLONE_APP_CONTENTTYPES = True


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Prevents uninstall profile from showing up in the profile list
        when creating a Plone site.

        """
        return [
            u'plone.app.multilingual:uninstall',
        ]


def init_pam(tool):
    """After installation run setup to create LRF and LIF."""
    setup_tool = SetupMultilingualSite()
    setup_tool.setupSite(getSite())


def step_default_various(context):
    if context.readDataFile('plone.app.multilingual_default.txt') is None:
        return
    portal = context.getSite()
    enable_translatable_behavior(portal)


def enable_translatable_behavior(portal):
    types_tool = portal.portal_types

    # Iterate through all Dexterity content type
    all_ftis = types_tool.listTypeInfo()
    dx_ftis = [x for x in all_ftis if getattr(x, 'behaviors', False)]
    for fti in dx_ftis:

        # Enable translatable behavior for all types
        behaviors = list(fti.behaviors)
        behaviors.extend([
            'plone.app.multilingual.dx.interfaces.IDexterityTranslatable',
        ])
        behaviors = tuple(set(behaviors))
        fti._updateProperty('behaviors', behaviors)


def step_uninstall_various(context):
    if context.readDataFile('plone.app.multilingual_uninstall.txt') is None:
        return
    portal = context.getSite()
    disable_translatable_behavior(portal)


def disable_translatable_behavior(portal):
    """Remove p.a.multilingual behaviors from p.a.contenttypes types
    """
    types_tool = portal.portal_types

    # Iterate through all Dexterity content type
    all_ftis = types_tool.listTypeInfo()
    dx_ftis = [x for x in all_ftis if getattr(x, 'behaviors', False)]
    for fti in dx_ftis:

        # Disable translatable behavior from all types
        behaviors = [
            i for i in fti.behaviors if i !=
            'plone.app.multilingual.dx.interfaces.IDexterityTranslatable'
        ]
        fti._updateProperty('behaviors', behaviors)
