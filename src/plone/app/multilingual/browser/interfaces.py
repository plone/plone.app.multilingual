from AccessControl import getSecurityManager
from plone.app.multilingual import _
from plone.app.multilingual.browser.vocabularies import untranslated_languages
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.z3cform.widgets.contentbrowser import ContentBrowserFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.base.interfaces import IPloneSiteRoot
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from zope import interface
from zope import schema
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.interfaces import IBrowserSubMenuItem
from zope.component.hooks import getSite
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


def make_relation_root_path(context):
    security_manager = getSecurityManager()
    site = getSite()

    # Use the old behavior if context is None or REQUEST is missing, otherwise
    # the code below will fail because REQUEST or aq_parent are missing
    if context is None or not getattr(context, "REQUEST", None):
        return "/".join(site.getPhysicalPath())

    # This should not happen, there's no View permission for the current object
    if not security_manager.checkPermission("View", context):
        return "/".join(site.getPhysicalPath())

    # Try to find the "closest" object in the target language
    current_object = context
    target_language = context.REQUEST.get("language", None)

    if target_language is None:
        return "/".join(site.getPhysicalPath())

    closest_translation = None
    while closest_translation is None:
        current_object = current_object.aq_parent
        translation_manager = ITranslationManager(current_object)
        closest_translation = translation_manager.get_translation(target_language)
        if IPloneSiteRoot.providedBy(closest_translation):
            break

    # If the closest translation has no View permission default to old behavior
    if not security_manager.checkPermission("View", closest_translation):
        return "/".join(site.getPhysicalPath())

    # Everything went well, return the translation's path
    return "/".join(closest_translation.getPhysicalPath())


class IMultilingualLayer(interface.Interface):
    """browser layer"""


class ITranslateSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the translate menu."""


class ITranslateMenu(IBrowserMenu):
    """The translate menu."""


class ICreateTranslation(interface.Interface):
    language = schema.Choice(
        title=_("title_language", default="Language"),
        source=untranslated_languages,
    )


class IUpdateLanguage(interface.Interface):
    language = schema.Choice(
        title=_("title_available_languages", default="Available languages"),
        description=_(
            "description_update_language",
            default="Untranslated languages from the current content",
        ),
        source=untranslated_languages,
        required=True,
    )


@provider(IContextAwareDefaultFactory)
def request_language(context):
    return context.REQUEST.form.get("language")


class IConnectTranslation(model.Schema):
    language = schema.Choice(
        title=_("title_language", default="Language"),
        source=untranslated_languages,
        defaultFactory=request_language,
        required=True,
    )
    content = RelationChoice(
        title=_("content"),
        vocabulary="plone.app.multilingual.RootCatalog",
        required=True,
    )
    directives.widget(
        "content",
        ContentBrowserFieldWidget,
        pattern_options={
            "basePath": make_relation_root_path,
        },
    )


interface.alsoProvides(IUpdateLanguage, IFormFieldProvider)
interface.alsoProvides(IConnectTranslation, IFormFieldProvider)
