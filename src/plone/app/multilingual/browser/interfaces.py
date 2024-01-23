from Acquisition import aq_parent
from plone.app.multilingual import _
from plone.app.multilingual.browser.vocabularies import untranslated_languages
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.z3cform.widget import RelatedItemsFieldWidget
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
    current_object = context
    target_language = context.REQUEST.get('language')
    closest_translation = None
    while closest_translation is None:
        current_object = current_object.aq_parent
        tm = ITranslationManager(current_object)
        closest_translation = tm.get_translation(target_language)
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
        RelatedItemsFieldWidget,
        pattern_options={
            "basePath": make_relation_root_path,
        },
    )


interface.alsoProvides(IUpdateLanguage, IFormFieldProvider)
interface.alsoProvides(IConnectTranslation, IFormFieldProvider)
