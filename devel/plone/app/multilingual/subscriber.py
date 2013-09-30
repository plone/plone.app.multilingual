# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import IMutableTG
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import ITranslatable
from plone.uuid.interfaces import IUUID

from zope.component.hooks import getSite
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

from OFS.interfaces import IObjectWillBeMovedEvent, IObjectWillBeAddedEvent, IObjectWillBeRemovedEvent

# On shared elements, the uuid is different so we need to take care of them on catalog in case we modify any shared element

def reindex_neutral(obj, event):
    # we need to look for the parent that is already indexed
    if IPloneSiteRoot.providedBy(obj) or ILanguage(obj).get_language() != LANGUAGE_INDEPENDENT:
        return
    parent = aq_parent(obj)
    site = getSite()
    language_tool = getToolByName(site, 'portal_languages')
    language_infos = language_tool.supported_langs
    if IPloneSiteRoot.providedBy(parent):
        # It's plone site root we need to look at LRF
        for language_info in language_infos:
            lrf_to_reindex = getattr(parent, language_info, None)
            to_reindex = getattr(lrf_to_reindex, obj.id, None)
            if to_reindex is not None:
                to_reindex.reindexObject()
    else:
        content_id = IUUID(parent).split('-')[0]
        pc = getToolByName(site, 'portal_catalog')
        for language_info in language_infos:
            brains = pc.unrestrictedSearchResults(UID=content_id + '-' + language_info)
            if len(brains):
                obj.unrestrictedTraverse(brains[0].getPath() + '/' + obj.id).reindexObject()
    return

def remove_ghosts(obj, event):
    """
    We are going to remove a object: we need to check if its neutral and remove their indexes also.
    """
    if not IObjectWillBeAddedEvent.providedBy(event) and (IObjectWillBeMovedEvent.providedBy(event) or IObjectWillBeRemovedEvent.providedBy(event)):
        if ILanguage(obj).get_language() != LANGUAGE_INDEPENDENT:
            return
        content_id = IUUID(obj).split('-')[0]
        site = getSite()
        pc = getToolByName(site, 'portal_catalog')
        language_tool = getToolByName(site, 'portal_languages')
        language_infos = language_tool.supported_langs

        for language_info in language_infos:
            brains = pc.unrestrictedSearchResults(UID=content_id + '-' + language_info)
            if len(brains):
                obj.unrestrictedTraverse(brains[0].getPath() + '/' + obj.id).unindexObject()

# Multilingual subscribers

def reindex_object(obj):
    obj.reindexObject(idxs=("Language", "TranslationGroup",
                            "path", "allowedRolesAndUsers"), )


def set_recursive_language(obj, language):
    """ Set the language at this object and recursive
    """
    if ILanguage(obj).get_language() != language:
        ILanguage(obj).set_language(language)
        ITranslationManager(obj).update()
        reindex_object(obj)
    if IFolderish.providedBy(obj):
        for item in obj.items():
            if ITranslatable.providedBy(item):
                set_recursive_language(item, language)


# Subscriber to set language on the child folder
def createdEvent(obj, event):
    """ It can be a
        IObjectRemovedEvent - don't do anything
        IObjectMovedEvent
        IObjectAddedEvent
        IObjectCopiedEvent
    """
    if IObjectRemovedEvent.providedBy(event):
        return

    portal = getSite()

    # On ObjectCopiedEvent and ObjectMovedEvent aq_parent(event.object) is
    # always equal to event.newParent.
    parent = aq_parent(event.object)

    if ITranslatable.providedBy(parent):
        # Normal use case
        # We set the tg, linking
        language = ILanguage(parent).get_language()
        set_recursive_language(obj, language)
        sdm = obj.session_data_manager
        session = sdm.getSessionData()
        portal = getSite()

        if 'tg' in session.keys() and \
           not portal.portal_factory.isTemporary(obj):
            IMutableTG(obj).set(session['tg'])
            modified(obj)
            del session['tg']
    else:
        set_recursive_language(obj, LANGUAGE_INDEPENDENT)

