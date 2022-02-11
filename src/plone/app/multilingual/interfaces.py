from plone.app.multilingual import _
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.i18n.interfaces import ILanguageSchema
from plone.supermodel import model
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


# CONSTANTS
SHARED_NAME = "shared"

LANGUAGE_INDEPENDENT = ""

ATTRIBUTE_NAME = "_plone.tg"

NOTG = "notg"


class ILanguageRootFolder(Interface):
    """Language Root Folder content type interface"""


class ILanguageIndependentFolder(Interface):
    """Language Independent Folder for content shared between languages"""


# Marker interface
class ITranslatable(Interface):
    """Marker interface for content types that support translation"""


# adapters
class ITranslationFactory(Interface):
    """Adapts ITranslated and is capable of returning
    a translation clone to be added.
    """

    def __call__(language):
        """Create a clone of the context
        for translation to the given language
        """


class ITranslationLocator(Interface):
    """Find a parent folder for a translation.
    Adapts ITranslated.
    """

    def __call__(language):
        """Return a parent folder into which a new translation can be added"""


class ITranslationIdChooser(Interface):
    """Find a valid id for a translation
    Adapts ITranslated.
    """

    def __call__(parent, language):
        """Return a valid id for the translation"""


class ITranslationCloner(Interface):
    """Subscription adapters to perform various aspects of cloning an object.
    Allows componentisation of things like workflow history cloning.
    Adapts ITranslated.
    """

    def __call__(object):
        """Update the translation copy that is being constructed"""


class ITranslationManager(Interface):
    def add_translation(object, intid):
        """
        create the translated content and register the translation
        """

    def remove_translation(language):
        """
        remove translation if exists (unregister the translation)
        """

    def get_translation(language):
        """
        get translation (translated object) if exists
        """

    def get_restricted_translation(language):
        """
        get translation (translated object) if exists and permitted
        """

    def get_translations():
        """
        get all the translated objects (including the context)
        """

    def get_restricted_translations():
        """
        get all the translated objects (including the context) if permitted
        """

    def get_translated_languages():
        """
        get a list of the translated languages
        (language-code like 'en', 'it' etc. )
        """

    def register_translation(language, content):
        """
        register an existing content as translation
        for context
        """

    def update():
        """
        update the item registered in the canonical
        check that there aren't two translations on the same language
        (used for changing the contexts language)
        """

    def query_canonical():
        """
        query if there is an canonical for the context
        used for migration
        """


class ILanguageIndependentFieldsManager(Interface):
    context = Attribute("context", "A translatable object")

    def copy_fields(translation):
        """Copy language independent fields to translation."""


class IMutableTG(Interface):
    """Adapt an object to this interface to manage the TG of an object

    Be sure of what you are doing. Translation Group (TG) is supposed to
    be stable and widely used
    """

    def get():
        """Return the TG of the context"""

    def set(tg):
        """Set the unique id of the context with the tg value."""


class ITG(Interface):
    """Abstract representation of a Translation Group (TG).

    Adapt an object to this interface to obtain its UUID. Adaptation will
    fail if the object does not have a TG (yet).
    """


class IPloneAppMultilingualInstalled(IPloneFormLayer):
    """layer inherits from PloneFormLayer for better LIF widget overriding"""


selector_policies = SimpleVocabulary(
    [
        SimpleTerm(
            value="closest",
            title=_("Search for closest translation in parent's content " "chain."),
        ),
        SimpleTerm(
            value="dialog",
            title=_(
                "Show user dialog with information about the " "available translations."
            ),
        ),
    ]
)


class IMultiLanguageExtraOptionsSchema(ILanguageSchema):
    """Interface for language extra options - control panel fieldset"""

    model.fieldset(
        "multilingual",
        label=_("Multilingual", default="Multilingual"),
        fields=[
            "filter_content",
            "redirect_babel_view",
            "bypass_languageindependent_field_permission_check",
            "buttons_babel_view_up_to_nr_translations",
            "google_translation_key",
            "selector_lookup_translations_policy",
        ],
    )

    filter_content = schema.Bool(
        title=_("heading_filter_content", default="Filter content by language."),
        description=_(
            "description_filter_content",
            default="Filter using language the content on folder_contents",
        ),
        default=True,
        required=False,
    )

    redirect_babel_view = schema.Bool(
        title=_(
            "heading_redirect_babel_view", default="Redirect on creation to babel view."
        ),
        description=_(
            "description_redirect_babel_view",
            default=("After creating a new translation redirecto to babel " "view"),
        ),
        default=True,
        required=False,
    )

    bypass_languageindependent_field_permission_check = schema.Bool(
        title=_(
            "heading_bypass_languageindependent_field_permission_check",
            default="Bypass language independent field permission check",
        ),
        description=_(
            "description_bypass_languageindependent_field_permission_check",
            default="When updating an object with language independent the "
            "field will be synced to all target languages. That can "
            "produce Unauthorized error messages because if the "
            "editor of the canonical object is not allowed to update "
            "the target language objects. Enabling this bypasses "
            "this permission check. This could also be dangerous, so "
            "think about possible security issues before enabling "
            "this.",
        ),
        default=False,
        required=False,
    )

    buttons_babel_view_up_to_nr_translations = schema.Int(
        title=_(
            "heading_buttons_babel_view_up_to_nr_translations",
            default="Use buttons in the bable view for up to how many " "translations?",
        ),
        description=_(
            "description_buttons_babel_view_up_to_nr_translations",
            default="When there are many translations for an item, the "
            "number of displayed buttons for them might get too "
            "large to fit inside the template. Choose here from "
            "which number onwards a drop-down menu will be displayed "
            "instead of buttons. Zero means that buttons will always "
            "be used.",
        ),
        default=7,
        required=False,
    )

    google_translation_key = schema.TextLine(
        title=_("heading_google_translation_key", default="Google Translation API Key"),
        description=_(
            "description_google_translation_key",
            default="Is a paying API in order to use google translation " "service",
        ),
        required=False,
    )

    selector_lookup_translations_policy = schema.Choice(
        title=_(
            "heading_selector_lookup_translations_policy",
            default="The policy used to determine how the lookup for "
            "available translations will be made by the language "
            "selector.",
        ),
        description=_(
            "description_selector_lookup_translations_policy",
            default="The default language used for the content "
            "and the UI of this site.",
        ),
        required=True,
        vocabulary=selector_policies,
    )
