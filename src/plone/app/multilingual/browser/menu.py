from zope.interface import implements
from zope.component import getMultiAdapter
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from zope.browsermenu.menu import BrowserMenu
from zope.browsermenu.menu import BrowserSubMenuItem
from plone.memoize.instance import memoize
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.defaultpage import isDefaultPage
from plone.app.multilingual.browser.interfaces import (
    ITranslateMenu,
    ITranslateSubMenuItem,
)
from plone.app.multilingual.browser.vocabularies import (
    untranslated_languages, translated_languages, translated_urls)
from plone.app.multilingual import _
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT, ITranslationManager, ILanguage
from plone.app.multilingual.interfaces import SHARED_NAME
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled

from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema


class TranslateMenu(BrowserMenu):
    implements(ITranslateMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        menu = []
        url = context.absolute_url()
        lt = getToolByName(context, "portal_languages")
        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        portal_url = portal_state.portal_url()
        showflags = lt.showFlags()
        context_id = ITranslationManager(context).tg
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
        edit_view = 'babel_edit' if settings.redirect_babel_view else 'edit'
        # In case is neutral language show set language menu only
        if LANGUAGE_INDEPENDENT != ILanguage(context).get_language() and not INavigationRoot.providedBy(context):
            menu.append({
                "title": _(u"title_babel_edit",
                       default=u"Edit with babel view"),
                "description": _(u"description_babel_edit",
                                default=u"Edit with the babel_edit"),
                "action": url + "/" + edit_view,
                "selected": False,
                "icon": None,
                "extra": {"id": "_edit_babel_edit",
                       "separator": None,
                       "class": ""},
                "submenu": None,
                })
                
            contexts = [context,]
            prt = aq_parent(context)
            if isDefaultPage(prt, context):
                contexts.append(prt)

            for idx,context in enumerate(contexts):
                url = context.absolute_url()
                
                langs = untranslated_languages(context)
                for lang in langs:
                    lang_name = lang.title
                    lang_id = lang.value
                    icon = showflags and lt.getFlagForLanguageCode(lang_id) or None
                    item = {
                        "description": _(u"description_translate_into",
                                        default=u"Translate into ${lang_name}",
                                        mapping={"lang_name": lang_name}),
                        "action": url + "/@@create_translation?language=%s" % lang_id,
                        "selected": False,
                        "icon": icon,
                        "width": "14",
                        "height": "11",
                        "extra": {"id": "translate_into_%s" % lang_id,
                                  "separator": None,
                                  "class": "contentmenuflags"},
                                  "submenu": None,
                        }
                    item['title'] = idx and _(u'create_translation_folder',
                                    default=u"Create ${lang_name} folder",
                                    mapping={"lang_name": lang_name}) \
                            or _(u'create_translation',
                                        default=u"Create ${lang_name}",
                                        mapping={"lang_name": lang_name})
                    menu.append(item)

                langs = translated_languages(context)
                urls = translated_urls(context)
                for lang in langs:
                    if lang not in urls:
                        # omit if translation is not permitted to access.
                        continue
                    lang_name = lang.title
                    lang_id = lang.value
                    icon = showflags and lt.getFlagForLanguageCode(lang_id) or None
                    item = {
                        "description": _(u"description_babeledit_menu",
                                        default=u"Babel edit ${lang_name}",
                                        mapping={"lang_name": lang_name}),
                        "action": urls.getTerm(lang_id).title + "/" + edit_view,
                        "selected": False,
                        "icon": icon,
                        "width": "14",
                        "height": "11",
                        "extra": {"id": "babel_edit_%s" % lang_id,
                                  "separator": None,
                                  "class": "contentmenuflags"},
                                  "submenu": None,
                        }
                    item['title'] = idx and _(u'edit_translation_folder',
                                    default=u"Edit ${lang_name} folder",
                                    mapping={"lang_name": lang_name}) \
                            or _(u'edit_translation',
                                                default=u"Edit ${lang_name}",
                                                mapping={"lang_name": lang_name})
                    menu.append(item)

                item = {
                    "description": _(u"description_add_translations",
                                    default=u"Add existing content as translation"),
                    "action": url + "/add_translations",
                    "selected": False,
                    "icon": None,
                    "extra": {"id": "_add_translations",
                           "separator": langs and "actionSeparator" or None,
                           "class": ""},
                    "submenu": None,
                    }
                item['title'] = idx and _(u"title_add_translations_folder",
                                    default=u"Add translations for folder...") \
                        or _(u"title_add_translations",
                                                        default=u"Add translations...")
                menu.append(item)

                item = {
                    "title": _(u"title_remove_translations",
                               default=u"Remove translations..."),
                    "description": _(
                        u"description_remove_translations",
                        default=u"Delete translations or remove the relations"),
                    "action": url + "/remove_translations",
                    "selected": False,
                    "icon": None,
                    "extra": {"id": "_remove_translations",
                           "separator": langs and "actionSeparator" or None,
                           "class": ""},
                    "submenu": None,
                    }
                menu.append(item)

        elif LANGUAGE_INDEPENDENT == ILanguage(context).get_language():
            menu.append({
                "title": _(u"language_folder",
                       default=u"Return to language folder"),
                "description": _(
                    u"description_language_folder",
                    default=u"Go to the user's browser preferred language related folder"),
                "action": portal_url + '/' + lt.getPreferredLanguage(),
                "selected": False,
                "icon": None,
                "extra": {"id": "_shared_folder",
                       "separator": None,
                       "class": ""},
                "submenu": None,
                })

        if LANGUAGE_INDEPENDENT != ILanguage(context).get_language():
            menu.append({
                "title": _(u"universal_link",
                       default=u"Universal Link"),
                "description": _(
                    u"description_universal_link",
                    default=u"Universal Language content link"),
                "action": portal_url + "/@@multilingual-universal-link/" + context_id,
                "selected": False,
                "icon": None,
                "extra": {"id": "_universal_link",
                       "separator": None,
                       "class": ""},
                "submenu": None,
                })

            menu.append({
                "title": _(u"shared_folder",
                       default=u"Go to shared folder"),
                "description": _(
                    u"description_shared_folder",
                    default=u"Show the language shared (neutral language) folder"),
                "action": portal_url + '/' + SHARED_NAME,
                "selected": False,
                "icon": None,
                "extra": {"id": "_shared_folder",
                       "separator": None,
                       "class": ""},
                "submenu": None,
                })

        menu.append({
            "title": _(u"title_set_language",
                        default=u"Set content language"),
            "description": _(u"description_set_language",
                             default=u"Set or change the current content language"),
            "action": url + "/update_language",
            "selected": False,
            "icon": None,
            "extra": {"id": "_set_language",
               "separator": None,
                   "class": ""},
                 "submenu": None,
            })

        return menu


class TranslateSubMenuItem(BrowserSubMenuItem):
    implements(ITranslateSubMenuItem)

    title = _(u"label_translate_menu", default=u"Translate")
    description = _(u"title_translate_menu",
                    default="Manage translations for your content.")
    submenuId = "plone_contentmenu_multilingual"
    order = 5
    extra = {"id": "plone-contentmenu-multilingual"}

    @property
    def action(self):
        return self.context.absolute_url() + "/add_translations"

    @memoize
    def available(self):
        if not IPloneAppMultilingualInstalled.providedBy(self.request):
            return False

        lt = getToolByName(self.context, 'portal_languages', None)
        if lt is None:
            return False

        supported = lt.listSupportedLanguages()
        if len(supported) < 2:
            return False

        return True

    def selected(self):
        return False
