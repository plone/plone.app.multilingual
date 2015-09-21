# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import ITranslateMenu
from plone.app.multilingual.browser.interfaces import ITranslateSubMenuItem
from plone.app.multilingual.browser.utils import is_language_independent
from plone.app.multilingual.browser.vocabularies import translated_languages
from plone.app.multilingual.browser.vocabularies import translated_urls
from plone.app.multilingual.browser.vocabularies import untranslated_languages
from Products.CMFPlone.defaultpage import is_default_page
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.permissions import ManageTranslations
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from zope.browsermenu.menu import BrowserMenu
from zope.browsermenu.menu import BrowserSubMenuItem
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implements


class TranslateMenu(BrowserMenu):
    implements(ITranslateMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form.
        """
        try:
            lang_names = request.locale.displayNames.languages
        except AttributeError:
            lang_names = {}
        menu = []
        url = context.absolute_url()
        lt = getToolByName(context, "portal_languages")

        site_url = getSite().absolute_url()
        showflags = lt.showFlags
        context_id = ITranslationManager(context).tg
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema, prefix="plone")
        edit_view = 'babel_edit' if settings.redirect_babel_view else 'edit'
        # In case is neutral language show set language menu only
        is_neutral_content = (
            ILanguage(context).get_language() == LANGUAGE_INDEPENDENT
            or is_language_independent(context)
        )

        shared_folder_url = site_url + '/folder_contents'
        pc = getToolByName(getSite(), 'portal_catalog')
        results = pc.unrestrictedSearchResults(
            portal_type='LIF', Language=ILanguage(context).get_language())
        for brain in results:
            shared_folder_url = brain.getURL() + '/folder_contents'

        if not is_neutral_content and not INavigationRoot.providedBy(context):
            menu.append({
                "title": _(
                    u"title_babel_edit",
                    default=u"Edit with babel view"
                ),
                "description": _(
                    u"description_babel_edit",
                    default=u"Edit with the babel_edit"
                ),
                "action": url + "/" + edit_view,
                "selected": False,
                "icon": None,
                "extra": {
                    "id": "_edit_babel_edit",
                    "separator": None,
                    "class": "",
                },
                "submenu": None,
            })

            if ITranslatable.providedBy(context):
                contexts = [context, ]
            else:
                contexts = []
            prt = aq_parent(context)
            if is_default_page(prt, context) and ITranslatable.providedBy(prt):
                contexts.append(prt)

            for idx, context in enumerate(contexts):
                url = context.absolute_url()
                ulangs = untranslated_languages(context)
                for lang in ulangs:
                    lang_name = lang_names.get(lang.value, lang.title)
                    lang_id = lang.value
                    icon = showflags and lt.getFlagForLanguageCode(lang_id)\
                        or None
                    item = {
                        "description": _(
                            u"description_translate_into",
                            default=u"Translate into ${lang_name}",
                            mapping={"lang_name": lang_name}
                        ),
                        "action": "%s/@@create_translation?language=%s" % (
                            url, lang_id),
                        "selected": False,
                        "icon": icon,
                        "width": "14",
                        "height": "11",
                        "extra": {"id": "translate_into_%s" % lang_id,
                                  "separator": None,
                                  "class": "contentmenuflags"},
                        "submenu": None,
                    }
                    item['title'] = idx and _(
                        u'create_translation_folder',
                        default=u"Create ${lang_name} folder",
                        mapping={"lang_name": lang_name}
                    ) or _(
                        u'create_translation',
                        default=u"Create ${lang_name}",
                        mapping={"lang_name": lang_name}
                    )
                    menu.append(item)
                langs = translated_languages(context)
                urls = translated_urls(context)
                for lang in langs:
                    if lang.value not in urls.by_token:
                        # omit if translation is not permitted to access.
                        continue
                    lang_name = lang_names.get(lang.value, lang.title)
                    lang_id = lang.value
                    icon = showflags and lt.getFlagForLanguageCode(lang_id)\
                        or None
                    item = {
                        "description": _(
                            u"description_babeledit_menu",
                            default=u"Babel edit ${lang_name}",
                            mapping={"lang_name": lang_name}
                        ),
                        "action": (urls.getTerm(lang_id).title + "/" +
                                   edit_view),
                        "selected": False,
                        "icon": icon,
                        "width": "14",
                        "height": "11",
                        "extra": {"id": "babel_edit_%s" % lang_id,
                                  "separator": None,
                                  "class": "contentmenuflags"},
                        "submenu": None,
                    }
                    item['title'] = idx and _(
                        u'edit_translation_folder',
                        default=u"Edit ${lang_name} folder",
                        mapping={"lang_name": lang_name}
                    ) or _(
                        u'edit_translation',
                        default=u"Edit ${lang_name}",
                        mapping={"lang_name": lang_name}
                    )
                    menu.append(item)

                item = {
                    "description": _(
                        u"description_add_translations",
                        default=u"Add existing content as translation"),
                    "action": url + "/add_translations",
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "_add_translations",
                        "separator": langs and "actionSeparator" or None,
                        "class": ""
                    },
                    "submenu": None,
                }
                item['title'] = idx and _(
                    u"title_add_translations_folder",
                    default=u"Add translations for folder..."
                ) or _(
                    u"title_add_translations",
                    default=u"Add translations..."
                )
                menu.append(item)

                item = {
                    "title": _(
                        u"title_remove_translations",
                        default=u"Remove translations..."
                    ),
                    "description": _(
                        u"description_remove_translations",
                        default=u"Delete translations or remove the relations"
                    ),
                    "action": url + "/remove_translations",
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "_remove_translations",
                        "separator": langs and "actionSeparator" or None,
                        "class": ""
                    },
                    "submenu": None,
                }
                menu.append(item)

        elif is_neutral_content:
            menu.append({
                "title": _(
                    u"language_folder",
                    default=u"Return to language folder"
                ),
                "description": _(
                    u"description_language_folder",
                    default=u"Go to the user's browser preferred language "
                            u"related folder"
                ),
                "action": site_url + '/' + lt.getPreferredLanguage(),
                "selected": False,
                "icon": None,
                "extra": {
                    "id": "_shared_folder",
                    "separator": None,
                    "class": ""
                },
                "submenu": None,
            })

        if not is_neutral_content:
            menu.append({
                "title": _(
                    u"universal_link",
                    default=u"Universal Link"
                ),
                "description": _(
                    u"description_universal_link",
                    default=u"Universal Language content link"
                ),
                "action": "%s/@@multilingual-universal-link/%s" % (
                    site_url, context_id),
                "selected": False,
                "icon": None,
                "extra": {
                    "id": "_universal_link",
                    "separator": None,
                    "class": ""
                },
                "submenu": None,
            })

            menu.append({
                "title": _(
                    u"shared_folder",
                    default=u"Go to shared folder"
                ),
                "description": _(
                    u"description_shared_folder",
                    default=u"Show the language shared (neutral language) "
                            u"folder"
                ),
                "action": shared_folder_url,
                "selected": False,
                "icon": None,
                "extra": {
                    "id": "_shared_folder",
                    "separator": None,
                    "class": ""},
                "submenu": None,
            })

        menu.append({
            "title": _(
                u"title_set_language",
                default=u"Set content language"
            ),
            "description": _(
                u"description_set_language",
                default=u"Set or change the current content language"
            ),
            "action": url + "/update_language",
            "selected": False,
            "icon": None,
            "extra": {
                "id": "_set_language",
                "separator": None,
                "class": ""
            },
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

    @view.memoize
    def available(self):
        # Is PAM installed?
        if not IPloneAppMultilingualInstalled.providedBy(self.request):
            return False

        # Do we have portal_languages?
        lt = getToolByName(self.context, 'portal_languages', None)
        if lt is None:
            return False

        # Do we have multiple languages?
        supported = lt.listSupportedLanguages()
        if len(supported) < 2:
            return False

        # And now check permissions
        sm = getSecurityManager()
        if not sm.checkPermission(ManageTranslations, self.context):
            return False

        return True

    def selected(self):
        return False
