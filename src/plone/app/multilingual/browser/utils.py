# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_chain
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.app.multilingual.browser.selector import LanguageSelectorViewlet
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import ILanguageIndependentFolder
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import ITranslationLocator
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.manager import TranslationManager
from plone.i18n.locales.interfaces import IContentLanguageAvailability
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite


def is_language_independent(ob):
    if not ILanguageIndependentFolder.providedBy(ob):
        for element in aq_chain(ob):
            if ILanguageIndependentFolder.providedBy(element):
                return True
    return False


class BabelUtils(BrowserView):

    def __init__(self, context, request):
        super(BabelUtils, self).__init__(context, request)
        portal_state = getMultiAdapter((context, request),
                                       name="plone_portal_state")
        self.portal_url = portal_state.portal_url()
        # If there is any translation_info lets use it
        try:
            self.group = TranslationManager(request.translation_info['tg'])
        except AttributeError:
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
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema, prefix="plone")
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
            portal_factory = getToolByName(
                self.context,
                'portal_factory',
                None
            )
            context_language = ILanguage(context).get_language()
            if (portal_factory is None
                or not portal_factory.isTemporary(self.context)) \
               and lang_info['code'] == context_language:
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
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema, prefix="plone")
        return settings.buttons_babel_view_up_to_nr_translations


def multilingualMoveObject(content, language):
    """Move content object and its contained objects to a new language folder
    Also set the language on all the content moved

    """
    if is_language_independent(content):
        # Language independent content will be created into language roo
        target_folder = getattr(getSite(), language)
    else:
        target_folder = ITranslationLocator(content)(language)

    parent = aq_parent(content)

    copy_data = parent.manage_cutObjects(content.getId())
    list_ids = target_folder.manage_pasteObjects(copy_data)
    new_id = list_ids[0]['new_id']
    new_object = target_folder[new_id]

    new_object.reindexObject()

    return new_object
