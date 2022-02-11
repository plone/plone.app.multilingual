from AccessControl import getSecurityManager
from Acquisition import aq_parent
from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import ITranslateMenu
from plone.app.multilingual.browser.interfaces import ITranslateSubMenuItem
from plone.app.multilingual.browser.utils import is_language_independent
from plone.app.multilingual.browser.vocabularies import translated_languages
from plone.app.multilingual.browser.vocabularies import translated_urls
from plone.app.multilingual.browser.vocabularies import untranslated_languages
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.app.multilingual.permissions import ManageTranslations
from plone.memoize import view
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.defaultpage import is_default_page
from Products.CMFPlone.interfaces import ILanguage
from Products.CMFPlone.utils import safe_unicode
from zope.browsermenu.menu import BrowserMenu
from zope.browsermenu.menu import BrowserSubMenuItem
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer


@implementer(ITranslateMenu)
class TranslateMenu(BrowserMenu):
    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        # Settings
        site_url = getSite().absolute_url()
        language_tool = getToolByName(context, "portal_languages")
        show_flags = language_tool.showFlags
        try:
            lang_names = request.locale.displayNames.languages
        except AttributeError:
            lang_names = {}

        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IMultiLanguageExtraOptionsSchema, prefix="plone"
        )
        if settings.redirect_babel_view:
            translation_view = "babel_edit"
        else:
            translation_view = "edit"

        # Content
        content = context
        content_url = context.absolute_url()
        content_language = ILanguage(content).get_language()
        content_translatable = not (
            content_language == LANGUAGE_INDEPENDENT
            or is_language_independent(content)
            or ILanguageRootFolder.providedBy(content)
        )
        content_translated = translated_languages(content)
        content_untranslated = untranslated_languages(content)
        content_translation_group = ITG(content, "")
        if not ITranslatable.providedBy(content):
            content = None

        # Folder when content is default page
        folder = aq_parent(context)
        if not is_default_page(folder, context):
            folder = None
        if folder and ITranslatable.providedBy(folder):  # noqa
            folder_url = folder.absolute_url()
            folder_language = ILanguage(folder).get_language()
            folder_translatable = not (
                folder_language == LANGUAGE_INDEPENDENT
                or is_language_independent(folder)
                or ILanguageRootFolder.providedBy(folder)
            )
            folder_translated = translated_languages(folder)
            folder_untranslated = untranslated_languages(folder)
            folder_translation_group = ITG(folder, "")
        else:
            folder_url = ""
            folder_language = ""
            folder_translatable = False
            folder_translated = []
            folder_untranslated = []
            folder_translation_group = ""

        # Assets folder
        assets_folder_url = None
        assets_folder_title = None
        pc = getToolByName(getSite(), "portal_catalog")
        results = pc.unrestrictedSearchResults(
            portal_type="LIF", Language=ILanguage(context).get_language()
        )
        for brain in results:
            assets_folder_url = brain.getURL() + "/folder_contents"
            assets_folder_title = safe_unicode(brain.Title)
            break

        # Menu items
        results = []
        results_folder = []
        results_content = []

        if folder_translatable:
            # Folder translation view
            lang_name = lang_names.get(folder_language, folder_language)
            results_folder.append(
                {
                    "title": _(
                        "edit_translation",
                        default="Edit ${lang_name}",
                        mapping={"lang_name": lang_name},
                    ),
                    "description": _(
                        "description_babeledit_menu",
                        default="Edit {lang_name} with the two-column translation view",  # noqa
                        mapping={"lang_name": lang_name},
                    ),
                    "action": folder_url + "/" + translation_view,
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "_edit_folder_babel_edit",
                        "separator": None,
                        "class": "",
                    },
                    "submenu": None,
                }
            )

        if (
            folder and folder_untranslated and False
        ):  # disabled in favor of cut & paste  # noqa
            # Set folder language
            results_folder.append(
                {
                    "title": _("title_set_language", default="Change content language"),
                    "description": _(
                        "description_set_language",
                        default="Move the translation under another language folder",  # noqa
                    ),
                    "action": folder_url + "/update_language",
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "_set_folder_language",
                        "separator": None,
                        "class": "",
                    },
                    "submenu": None,
                }
            )

        if folder_translatable:
            for idx, lang in enumerate(folder_untranslated):
                lang_name = lang_names.get(lang.value, lang.title)
                lang_id = lang.value
                icon = (
                    show_flags and language_tool.getFlagForLanguageCode(lang_id) or None
                )  # noqa
                results_folder.append(
                    {
                        "title": _(
                            "create_translation",
                            default="Create ${lang_name}",
                            mapping={"lang_name": lang_name},
                        ),
                        "description": _(
                            "description_translate_into",
                            default="Translate into ${lang_name}",
                            mapping={"lang_name": lang_name},
                        ),
                        "action": "%s/@@create_translation?language=%s"
                        % (folder_url, lang_id),
                        "selected": False,
                        "icon": icon,
                        "width": "14",
                        "height": "11",
                        "extra": {
                            "id": "translate_folder_into_%s" % lang_id,
                            "separator": None,
                            "class": "contentmenuflags",
                        },
                        "submenu": None,
                    }
                )
            urls = translated_urls(folder)
            for lang in folder_translated:
                if lang.value not in urls.by_token:
                    # omit if translation is not permitted to access.
                    continue
                lang_name = lang_names.get(lang.value, lang.title)
                lang_id = lang.value
                icon = (
                    show_flags and language_tool.getFlagForLanguageCode(lang_id) or None
                )  # noqa
                results_folder.append(
                    {
                        "title": _(
                            "edit_translation",
                            default="Edit ${lang_name}",
                            mapping={"lang_name": lang_name},
                        ),
                        "description": _(
                            "description_babeledit_menu",
                            default="Edit {lang_name} with the two-column translation view",  # noqa
                            mapping={"lang_name": lang_name},
                        ),
                        "action": (
                            urls.getTerm(lang_id).title + "/" + translation_view
                        ),
                        "selected": False,
                        "icon": icon,
                        "width": "14",
                        "height": "11",
                        "extra": {
                            "id": "babel_edit_%s" % lang_id,
                            "separator": None,
                            "class": "contentmenuflags",
                        },
                        "submenu": None,
                    }
                )
            # Manage folder translations
            results_folder.append(
                {
                    "title": _(
                        "title_modify_translations", default="Manage translations"
                    ),
                    "description": _(
                        "description_modify_translations",
                        default="Add or delete translations",
                    ),
                    "action": folder_url + "/modify_translations",
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "_modify_folder_translations",
                        "separator": None,
                        "class": "",
                    },
                    "submenu": None,
                }
            )
            # Universal link
            if folder_translation_group:
                results_folder.append(
                    {
                        "title": _("universal_link", default="Universal link"),
                        "description": _(
                            "description_universal_link",
                            default="Universal link to the content in user's preferred language",  # noqa
                        ),
                        "action": "%s/@@multilingual-universal-link/%s"
                        % (site_url, folder_translation_group),
                        "selected": False,
                        "icon": None,
                        "extra": {
                            "id": "_universal_folder_link",
                            "separator": None,
                            "class": "",
                        },
                        "submenu": None,
                    }
                )

        if results_folder:
            # Folder translation separator
            results.append(
                {
                    "title": _(
                        "title_translate_current_folder", default="Folder translation"
                    ),
                    "description": "",
                    "action": None,
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "translateFolderHeader",
                        "separator": "actionSeparator",
                        "class": "plone-toolbar-submenu-header",
                    },
                    "submenu": None,
                }
            )
        results.extend(results_folder)

        lang_name = lang_names.get(content_language, content_language)

        # Content language
        if content_untranslated and False:  # disabled in favor of cut & paste
            results_content.append(
                {
                    "title": _("title_set_language", default="Change content language"),
                    "description": _(
                        "description_set_language",
                        default="Move the translation under another language folder",  # noqa
                    ),
                    "action": content_url + "/update_language",
                    "selected": False,
                    "icon": None,
                    "extra": {"id": "_set_language", "separator": None, "class": ""},
                    "submenu": None,
                }
            )

        if content_translatable:
            # Content translation view
            results_content.append(
                {
                    "title": _(
                        "edit_translation",
                        default="Edit ${lang_name}",
                        mapping={"lang_name": lang_name},
                    ),
                    "description": _(
                        "description_babeledit_menu",
                        default="Edit {lang_name} with the two-column translation view",  # noqa
                        mapping={"lang_name": lang_name},
                    ),
                    "action": content_url + "/" + translation_view,
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "_edit_babel_edit",
                        "separator": None,
                        "class": "",
                    },
                    "submenu": None,
                }
            )

        if content_translatable:
            for idx, lang in enumerate(content_untranslated):
                lang_name = lang_names.get(lang.value, lang.title)
                lang_id = lang.value
                icon = (
                    show_flags and language_tool.getFlagForLanguageCode(lang_id) or None
                )  # noqa
                results_content.append(
                    {
                        "title": _(
                            "create_translation",
                            default="Create ${lang_name}",
                            mapping={"lang_name": lang_name},
                        ),
                        "description": _(
                            "description_translate_into",
                            default="Translate into ${lang_name}",
                            mapping={"lang_name": lang_name},
                        ),
                        "action": "%s/@@create_translation?language=%s"
                        % (content_url, lang_id),
                        "selected": False,
                        "icon": icon,
                        "width": "14",
                        "height": "11",
                        "extra": {
                            "id": "translate_into_%s" % lang_id,
                            "separator": None,
                            "class": "contentmenuflags",
                        },
                        "submenu": None,
                    }
                )
            urls = translated_urls(content)
            for lang in content_translated:
                if lang.value not in urls.by_token:
                    # omit if translation is not permitted to access.
                    continue
                lang_name = lang_names.get(lang.value, lang.title)
                lang_id = lang.value
                icon = (
                    show_flags and language_tool.getFlagForLanguageCode(lang_id) or None
                )  # noqa
                results_content.append(
                    {
                        "title": _(
                            "edit_translation",
                            default="Edit ${lang_name}",
                            mapping={"lang_name": lang_name},
                        ),
                        "description": _(
                            "description_babeledit_menu",
                            default="Edit {lang_name} with the two-column translation view",  # noqa
                            mapping={"lang_name": lang_name},
                        ),
                        "action": (
                            urls.getTerm(lang_id).title + "/" + translation_view
                        ),
                        "selected": False,
                        "icon": icon,
                        "width": "14",
                        "height": "11",
                        "extra": {
                            "id": "babel_edit_%s" % lang_id,
                            "separator": None,
                            "class": "contentmenuflags",
                        },
                        "submenu": None,
                    }
                )
            # Manage content translations
            results_content.append(
                {
                    "title": _(
                        "title_modify_translations", default="Manage translations"
                    ),
                    "description": _(
                        "description_modify_translations",
                        default="Add or delete translations",
                    ),
                    "action": content_url + "/modify_translations",
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "_modify_translations",
                        "separator": None,
                        "class": "",
                    },
                    "submenu": None,
                }
            )
            # Universal link
            if content_translation_group:
                results_content.append(
                    {
                        "title": _("universal_link", default="Universal link"),
                        "description": _(
                            "description_universal_link",
                            default="Universal link to the content in user's preferred language",  # noqa
                        ),
                        "action": "%s/@@multilingual-universal-link/%s"
                        % (site_url, content_translation_group),
                        "selected": False,
                        "icon": None,
                        "extra": {
                            "id": "_universal_link",
                            "separator": None,
                            "class": "",
                        },
                        "submenu": None,
                    }
                )

        if results_folder and results_content:
            # Item translations separator
            results.append(
                {
                    "title": _(
                        "title_translate_current_item", default="Item translation"
                    ),
                    "description": "",
                    "action": None,
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "translateItemHeader",
                        "separator": "actionSeparator",
                        "class": "",
                    },
                    "submenu": None,
                }
            )
        results.extend(results_content)

        # Language independent assets folder
        if assets_folder_url:
            results.append(
                {
                    "title": _(
                        "shared_folder",
                        default="Open ${title} folder",
                        mapping={"title": assets_folder_title},
                    ),
                    "description": _(
                        "description_shared_folder",
                        default="Open the language independent assets folder",
                    ),
                    "action": assets_folder_url,
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "_shared_folder",
                        "separator": results and "actionSeparator" or None,
                        "class": "",
                    },
                    "submenu": None,
                }
            )

        # User preferred language root folder
        if not folder_translatable and not content_translatable:
            results.append(
                {
                    "title": _("language_folder", default="Return to language folder"),
                    "description": _(
                        "description_language_folder",
                        default="Go to the user's browser preferred language "
                        "related folder",
                    ),
                    "action": site_url
                    + "/"
                    + language_tool.getPreferredLanguage(),  # noqa
                    "selected": False,
                    "icon": None,
                    "extra": {
                        "id": "_language_folder",
                        "separator": (
                            (results and not assets_folder_url)
                            and "actionSeparator"
                            or None
                        ),
                        "class": "",
                    },
                    "submenu": None,
                }
            )

        return results


@implementer(ITranslateSubMenuItem)
class TranslateSubMenuItem(BrowserSubMenuItem):

    title = _("label_translate_menu", default="Translate")
    description = _(
        "title_translate_menu", default="Manage translations for your content."
    )
    submenuId = "plone_contentmenu_multilingual"
    order = 5
    extra = {"id": "plone-contentmenu-multilingual"}

    @property
    def action(self):
        return self.context.absolute_url() + "/add_translations"

    @property
    def extra(self):
        return {
            "id": "plone-contentmenu-multilingual",
            "li_class": "plonetoolbar-multilingual",
        }

    @view.memoize
    def available(self):
        # Is PAM installed?
        if not IPloneAppMultilingualInstalled.providedBy(self.request):
            return False

        # Do we have portal_languages?
        lt = getToolByName(self.context, "portal_languages", None)
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
