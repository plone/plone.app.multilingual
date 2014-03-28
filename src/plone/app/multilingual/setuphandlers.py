from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from plone.dexterity.interfaces import IDexterityFTI
from zope.interface import implements


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        """
        Prevents uninstall profile from showing up in the profile list
        when creating a Plone site.
        """
        return [
            # u'plone.app.multilingual:default',  # XXX: TODO: this one too?
            u'plone.app.multilingual:uninstall',
        ]


def removeBehaviors(context):
    """Remove p.a.multilingual behaviors from p.a.contenttypes types."""

    if context.readDataFile('plone.app.multilingual_uninstall.txt') is None:
        return

    portal = context.getSite()
    portal_types = getToolByName(portal, 'portal_types')

    behavior = 'plone.app.multilingual.dx.interfaces.IDexterityTranslatable'
    # plone.app.contenttype types
    typeNames = [
        'Document',
        'File',
        'Folder',
        'Image',
        'Link',
        'News Item',
    ]
    for name in typeNames:
        type_ = portal_types.get(name)

        # safety first
        if not type_ or not IDexterityFTI.providedBy(type_):
            continue

        behaviors = list(type_.behaviors)
        behaviors.remove(behavior)
        type_.behaviors = tuple(behaviors)
