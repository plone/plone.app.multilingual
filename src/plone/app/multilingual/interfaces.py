from zope.interface import Interface
from zope import schema
from plone.app.multilingual import _

SHARED_NAME = 'shared'


class IPloneAppMultilingualInstalled(Interface):
    """ layer """


class IMultiLanguageExtraOptionsSchema(Interface):
    """ Interface for language extra options - control panel fieldset
    """

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
