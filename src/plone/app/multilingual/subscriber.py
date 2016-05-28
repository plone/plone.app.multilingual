# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from plone.app.multilingual.browser.utils import is_language_independent
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
from plone.app.multilingual.interfaces import ILanguageIndependentFolder
from plone.app.multilingual.interfaces import IMutableTG
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.dexterity.interfaces import IDexterityContent
from plone.uuid.interfaces import IUUID
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled


def _reindex_site_root(obj, root, language_codes):
    for language_info in language_codes:
        lrf_to_reindex = getattr(root, language_info, None)
        to_reindex = getattr(lrf_to_reindex, obj.id, None)
        if to_reindex is not None:
            to_reindex.reindexObject()


def reindex_language_independent(ob, event):
    """Re-index language independent object for other languages

    Language independent objects are indexed once for each language with
    different, language code post-fixed, UUID for each. When ever a language
    independent object is modified in some language, it must be re-indexed
    for all the other languages as well.

    """
    if not is_language_independent(ob):
        return

    if IObjectRemovedEvent.providedBy(event):
        return

    pc = getToolByName(ob, 'portal_catalog')
    parent = aq_parent(ob)

    # Re-index objects just below the language independent folder
    if ILanguageIndependentFolder.providedBy(parent):
        brains = pc.unrestrictedSearchResults(portal_type='LIF')
        for brain in brains:
            lif = brain._unrestrictedGetObject()
            if lif != parent:
                lif[ob.id].indexObject()
    # Re-index objects deeper inside language independent folder
    else:
        language_tool = getToolByName(ob, 'portal_languages')
        language_codes = language_tool.supported_langs
        parent_uuid = IUUID(parent).split('-')[0] + '-'
        for code in language_codes:
            results = pc.unrestrictedSearchResults(UID=parent_uuid + code)
            # When we have results, parent has been indexed and we can reindex:
            for brain in results:
                tmp = ob.unrestrictedTraverse(brain.getPath() + '/' + ob.id)
                tmp.reindexObject()


def unindex_language_independent(ob, event):
    """Un-index language independent object for other languages

    Language independent objects are indexed once for each language with
    different, language code post-fixed, UUID for each. When ever a language
    independent object is removed in some language, we must un-indexed
    all the other languages as well.

    XXX: Removing any language independent folder will unindex contents of
    all language independent folders. When that happens, catalog clear
    and rebuild would restore contenst for the other folders.

    """
    if not is_language_independent(ob):
        return

    try:
        pc = getToolByName(ob, 'portal_catalog')
    except AttributeError:
        # When we are removing the site, there is no portal_catalog:
        return

    language_tool = getToolByName(ob, 'portal_languages')
    language_codes = language_tool.supported_langs

    uuid = IUUID(ob).split('-')[0]
    for code in language_codes:
        for brain in pc.unrestrictedSearchResults(UID=uuid + '-' + code):
            ob.unrestrictedTraverse(brain.getPath()).unindexObject()
        for brain in pc.unrestrictedSearchResults(UID=uuid):
            ob.unrestrictedTraverse(brain.getPath()).unindexObject()


# Multilingual subscribers
def reindex_object(obj):
    obj.reindexObject(
        idxs=("Language", "TranslationGroup", "path", "allowedRolesAndUsers")
    )


def set_recursive_language(ob, language):
    """Set the language for this object and its children in a recursive
    manner

    """
    if is_language_independent(ob):
        ILanguage(ob).set_language(None)

    elif ILanguage(ob).get_language() != language:
        ILanguage(ob).set_language(language)
        ITranslationManager(ob).update()
        reindex_object(ob)

    for child in (IFolderish.providedBy(ob) and ob.items() or ()):
        if ITranslatable.providedBy(child):
            set_recursive_language(child, language)


def createdEvent(obj, event):
    """ Subscriber to set language on the child folder

    It can be a
    - IObjectRemovedEvent - don't do anything
    - IObjectMovedEvent
    - IObjectAddedEvent
    - IObjectCopiedEvent
    """
    if IObjectRemovedEvent.providedBy(event):
        return

    request = getattr(event.object, 'REQUEST', getRequest())
    if not IPloneAppMultilingualInstalled.providedBy(request):
        return

    # On ObjectCopiedEvent and ObjectMovedEvent aq_parent(event.object) is
    # always equal to event.newParent.
    parent = aq_parent(event.object)

    # special parent handling
    if not ITranslatable.providedBy(parent):
        set_recursive_language(obj, LANGUAGE_INDEPENDENT)
        return

    # Normal use case
    # We set the tg, linking
    language = ILanguage(parent).get_language()
    set_recursive_language(obj, language)

    request = getattr(event.object, 'REQUEST', getRequest())
    try:
        ti = request.translation_info
    except AttributeError:
        return

    # AT check
    portal = getSite()
    portal_factory = getToolByName(portal, 'portal_factory', None)
    if (not IDexterityContent.providedBy(obj) and
            portal_factory is not None and
            not portal_factory.isTemporary(obj)):
        return

    IMutableTG(obj).set(ti['tg'])
    modified(obj)
    tm = ITranslationManager(obj)
    old_obj = tm.get_translation(ti['source_language'])
    ILanguageIndependentFieldsManager(old_obj).copy_fields(obj)
