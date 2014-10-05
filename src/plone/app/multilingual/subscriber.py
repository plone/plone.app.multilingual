# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from OFS.interfaces import IObjectWillBeAddedEvent
from OFS.interfaces import IObjectWillBeMovedEvent
from OFS.interfaces import IObjectWillBeRemovedEvent
from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.multilingual import BLACK_LIST_IDS
from plone.app.multilingual.browser.utils import is_language_independent
from plone.app.multilingual.browser.utils import is_shared
from plone.app.multilingual.browser.utils import is_shared_original
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
from plone.app.multilingual.interfaces import ILanguageIndependentFolder
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.multilingual.interfaces import IMutableTG
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.uuid.interfaces import IUUID
from zope.component.hooks import getSite
from zope.deprecation import deprecated
from zope.globalrequest import getRequest
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


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


def reindex_neutral(obj, event):
    """Neutral
    On shared elements, the uuid is different so we need to take care of
    them on catalog in case we modify any shared element
    """
    # is the given object Neutral?
    if IPloneSiteRoot.providedBy(obj) \
       or obj.getId() in BLACK_LIST_IDS \
       or (not is_shared(obj) and not is_shared_original(obj)):
        return

    parent = aq_parent(obj)
    if ILanguageRootFolder.providedBy(parent):
        # If it's parent is language root folder there is no need to reindex
        return

    site = getSite()
    language_tool = getToolByName(site, 'portal_languages')
    language_infos = language_tool.supported_langs
    if IPloneSiteRoot.providedBy(parent):
        # It's plone site root we need to look at LRF
        _reindex_site_root(obj, parent, language_infos)
        return

    # ok, we're very neutral
    content_id = IUUID(parent).split('-')[0]
    pc = getToolByName(site, 'portal_catalog')
    for language_info in language_infos:
        brains = pc.unrestrictedSearchResults(
            UID=content_id + '-' + language_info
        )
        if len(brains):
            # we have results, so parent was indexed before.
            brain = brains[0]
            obj.unrestrictedTraverse(
                brain.getPath() + '/' + obj.id).reindexObject()
deprecated('reindex_neutral',
           'reindex_neutral is removed by the next release')


def remove_ghosts(obj, event):
    """We are going to remove a object: we need to check if its neutral
       and remove their indexes also.
    """
    if not IObjectWillBeAddedEvent.providedBy(event) \
       and (IObjectWillBeMovedEvent.providedBy(event)
            or IObjectWillBeRemovedEvent.providedBy(event)):
        if not is_shared_original(obj):
            return

        content_id = IUUID(obj).split('-')[0]
        site = getSite()
        try:
            pc = getToolByName(site, 'portal_catalog')
        except AttributeError:
            # In case we are removing the site there is no portal_catalog
            return
        language_tool = getToolByName(site, 'portal_languages')
        language_infos = language_tool.supported_langs

        for language_info in language_infos:
            brains = pc.unrestrictedSearchResults(
                UID=content_id + '-' + language_info)
            for brain in brains:
                obj.unrestrictedTraverse(brain.getPath()).unindexObject()
            brains = pc.unrestrictedSearchResults(
                UID=content_id)
            for brain in brains:
                obj.unrestrictedTraverse(brain.getPath()).unindexObject()
    if IActionSucceededEvent.providedBy(event):
        reindex_neutral(obj, event)
deprecated('remove_ghosts',
           'remove_ghosts is removed by the next release')


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
        portal_factory = getToolByName(portal, 'portal_factory', None)

        request = getattr(event.object, 'REQUEST', getRequest())
        has_pam_old_lang_in_form = (
            request and
            'form.widgets.pam_old_lang' not in request.form
        )
        if (not has_pam_old_lang_in_form
                and 'tg' in session.keys()
                and 'old_lang' in session.keys()
                and (portal_factory is None
                     or not portal_factory.isTemporary(obj))):
            IMutableTG(obj).set(session['tg'])
            modified(obj)
            del session['tg']
            old_obj = ITranslationManager(obj)\
                .get_translation(session['old_lang'])
            ILanguageIndependentFieldsManager(old_obj).copy_fields(obj)
            del session['old_lang']
    else:
        set_recursive_language(obj, LANGUAGE_INDEPENDENT)
