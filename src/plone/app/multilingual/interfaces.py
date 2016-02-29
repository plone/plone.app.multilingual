# -*- coding: utf-8 -*-
from plone.app.multilingual import _
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFPlone.interfaces import ILanguageSchema
from plone.supermodel import model

# CONSTANTS
SHARED_NAME = 'shared'

LANGUAGE_INDEPENDENT = ''

ATTRIBUTE_NAME = '_plone.tg'

NOTG = 'notg'


class ILanguageRootFolder(Interface):
    """ Language Root Folder content type interface
    """


class ILanguageIndependentFolder(Interface):
    """ Language Independent Folder for content shared between languages
    """


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
        """ Return a valid id for the translation """


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
        """ Copy language independent fields to translation."""


class IMutableTG(Interface):
    """Adapt an object to this interface to manage the TG of an object

    Be sure of what you are doing. Translation Group (TG) is supposed to
    be stable and widely used
    """
    def get():
        """Return the TG of the context"""

    def set(tg):
        """Set the unique id of the context with the tg value.
        """


class ITG(Interface):
    """Abstract representation of a Translation Group (TG).

    Adapt an object to this interface to obtain its UUID. Adaptation will
    fail if the object does not have a TG (yet).
    """


class IPloneAppMultilingualInstalled(Interface):
    """ layer """


selector_policies = SimpleVocabulary(
    [SimpleTerm(value=u'closest',
                title=_(u'Search for closest translation in parent\'s content '
                        u'chain.')),
     SimpleTerm(value=u'dialog',
                title=_(u'Show user dialog with information about the '
                        u'available translations.'))]
)


class IMultiLanguageExtraOptionsSchema(ILanguageSchema):
    """ Interface for language extra options - control panel fieldset
    """

    model.fieldset(
        'multilingual',
        label=_(u'Multilingual', default=u'Multilingual'),
        fields=[
            'filter_content',
            'redirect_babel_view',
            'bypass_languageindependent_field_permission_check',
            'buttons_babel_view_up_to_nr_translations',
            'google_translation_key',
            'selector_lookup_translations_policy'
        ],
    )

    filter_content = schema.Bool(
        title=_(
            u"heading_filter_content",
            default=u"Filter content by language."),
        description=_(
            u"description_filter_content",
            default=u"Filter using language the content on folder_contents"),
        default=True,
        required=False,
        )

    redirect_babel_view = schema.Bool(
        title=_(
            u"heading_redirect_babel_view",
            default=u"Redirect on creation to babel view."),
        description=_(
            u"description_redirect_babel_view",
            default=(u"After creating a new translation redirecto to babel "
                     u"view")),
        default=True,
        required=False,
        )

    bypass_languageindependent_field_permission_check = schema.Bool(
        title=_(
            u"heading_bypass_languageindependent_field_permission_check",
            default=u"Bypass language independent field permission check"),
        description=_(
            u"description_bypass_languageindependent_field_permission_check",
            default=u"When updating an object with language independent the "
                    u"field will be synced to all target languages. That can "
                    u"produce Unauthorized error messages because if the "
                    u"editor of the canonical object is not allowed to update "
                    u"the target language objects. Enabling this bypasses "
                    u"this permission check. This could also be dangerous, so "
                    u"think about possible security issues before enabling "
                    u"this."),
        default=False,
        required=False,
    )

    buttons_babel_view_up_to_nr_translations = schema.Int(
        title=_(
            u"heading_buttons_babel_view_up_to_nr_translations",
            default=u"Use buttons in the bable view for up to how many "
                    u"translations?"),
        description=_(
            u"description_buttons_babel_view_up_to_nr_translations",
            default=u"When there are many translations for an item, the "
                    u"number of displayed buttons for them might get too "
                    u"large to fit inside the template. Choose here from "
                    u"which number onwards a drop-down menu will be displayed "
                    u"instead of buttons. Zero means that buttons will always "
                    u"be used."),
        default=7,
        required=False,
    )

    google_translation_key = schema.TextLine(
        title=_(
            u"heading_google_translation_key",
            default=u"Google Translation API Key"),
        description=_(
            u"description_google_translation_key",
            default=u"Is a paying API in order to use google translation "
                    u"service"),
        required=False,
    )

    selector_lookup_translations_policy = schema.Choice(
        title=_(u"heading_selector_lookup_translations_policy",
                default=u"The policy used to determine how the lookup for "
                        u"available translations will be made by the language "
                        u"selector."),
        description=_(u"description_selector_lookup_translations_policy",
                      default=u"The default language used for the content "
                              u"and the UI of this site."),
        required=True,
        vocabulary=selector_policies
    )
