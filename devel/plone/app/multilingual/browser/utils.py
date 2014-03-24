from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_chain
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.app.multilingual.browser.selector import LanguageSelectorViewlet
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import ITranslationLocator
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.manager import TranslationManager
from plone.i18n.locales.interfaces import IContentLanguageAvailability
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite


class BabelUtils(BrowserView):

    def __init__(self, context, request):
        super(BabelUtils, self).__init__(context, request)
        portal_state = getMultiAdapter((context, request),
                                       name="plone_portal_state")
        self.portal_url = portal_state.portal_url()
        # If there is any session tg lets use the session tg
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if 'tg' in session.keys():
            self.group = TranslationManager(session['tg'])
        else:
            self.group = ITranslationManager(self.context)

    def getGroup(self):
        return self.group

    def getTranslatedLanguages(self):
        return self.group.get_translated_languages()

    def getPortal(self):
        portal_url = getToolByName(self.context, 'portal_url')
        return portal_url

    def objToTranslate(self):
        return self.context

    def gtenabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
        key = settings.google_translation_key
        return key is not None and len(key.strip()) > 0

    def languages(self):
        """ Deprecated """
        context = aq_inner(self.context)

        ls = LanguageSelector(context, self.request, None, None)
        ls.update()
        results = ls.languages()

        supported_langs = [v['code'] for v in results]
        missing = set([str(c) for c in supported_langs])

        lsv = LanguageSelectorViewlet(context, self.request, None, None)
        translations = lsv._translations(missing)

        # We want to see the babel_view
        append_path = ('', 'babel_view',)
        non_viewable = set()
        for data in results:
            code = str(data['code'])
            data['translated'] = code in translations.keys()

            appendtourl = '/'.join(append_path)

            if data['translated']:
                trans, direct, has_view_permission = translations[code]
                if not has_view_permission:
                    # shortcut if the user cannot see the item
                    non_viewable.add((data['code']))
                    continue
                data['url'] = trans.absolute_url() + appendtourl
            else:
                non_viewable.add((data['code']))

        # filter out non-viewable items
        results = [r for r in results if r['code'] not in non_viewable]

        return results

    def translated_languages(self):
        context = aq_inner(self.context)
        tool = getToolByName(context, 'portal_languages', None)
        checkPermission = getSecurityManager().checkPermission
        translations = self.group.get_translations()
        translated_info =\
            [dict(code=key,
                  info=tool.getAvailableLanguageInformation()[key],
                  obj=translations[key]) for key in translations]

        default_language = tool.getDefaultLanguage()

        translated_shown = []

        for lang_info in translated_info:
            # Mark the default language as the first translation shown
            if lang_info['code'] == default_language:
                lang_info['isDefault'] = True
            else:
                lang_info['isDefault'] = False

            # Remove the translation of the content currently being
            # translated In case it's temporal we show as language is not
            # already set on AT
            portal_factory = getToolByName(self.context, 'portal_factory')
            context_language = ILanguage(context).get_language()
            if (not portal_factory.isTemporary(self.context)
                    and lang_info['code'] == context_language):
                continue

            # Remove the translation in case the translator user does not
            # have permissions over it
            has_view_permission =\
                bool(checkPermission('View', lang_info['obj']))
            if not has_view_permission:
                continue

            translated_shown.append(lang_info)
        return translated_shown

    def current_language_name(self):
        """ Get the current language native name """
        adapted = ILanguage(self.context)
        lang_code = adapted.get_language()
        util = getUtility(IContentLanguageAvailability)
        data = util.getLanguages(True)
        lang_info = data.get(lang_code)
        return lang_info.get('native', None) or lang_info.get('name')

    def max_nr_of_buttons(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
        return settings.buttons_babel_view_up_to_nr_translations


def is_shared(content):
    """
    Check if it's a ghost object
    """
    child = content
    for element in aq_chain(content):
        if (hasattr(child, '_v_is_shared_content')
                and child._v_is_shared_content
                and ILanguageRootFolder.providedBy(element)):
            return True
        child = element
    return False


def is_shared_original(content):
    """
    Check if it's a shared real object
    """
    child = content
    for element in aq_chain(content):
        if (IPloneSiteRoot.providedBy(element)
                and ILanguageRootFolder.providedBy(child)):
            return False
    return True


def get_original_object(content):
    """
    Get the original object of a shared content
    """
    path = []
    child = content

    for element in aq_chain(content):
        if (hasattr(child, '_v_is_shared_content')
                and child._v_is_shared_content
                and ILanguageRootFolder.providedBy(element)):
            break
        child = element
        path.insert(0, element.id)

    if ILanguageRootFolder.providedBy(element):
        # it's a ghost element
        site = getSite()
        return site.restrictedTraverse('/'.join(path))
    else:
        # It's the root element
        return content


def multilingualMoveObject(content, language):
    """
    Move content object and its contained objects to a new language folder
    Also set the language on all the content moved
    """
    if is_shared(content):
        # In case is shared we are going to create it on the language root
        # folder

        orig_content = get_original_object(content)
        target_folder = getattr(getSite(), language)
        # It's going to be a non shared content so we remove it from
        # portal_catalog

    else:
        orig_content = content
        target_folder = ITranslationLocator(orig_content)(language)

    parent = aq_parent(orig_content)
    cb_copy_data = parent.manage_cutObjects(orig_content.getId())
    list_ids = target_folder.manage_pasteObjects(cb_copy_data)
    new_id = list_ids[0]['new_id']
    new_object = target_folder[new_id]

    if hasattr(new_object, '_v_is_shared_content'):
        new_object._v_is_shared_content = False
    new_object.reindexObject()

    return new_object
