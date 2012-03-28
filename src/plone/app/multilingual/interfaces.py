from zope.interface import Interface
from zope import schema
from plone.app.multilingual import _
from plone.registry import field


class IPloneAppMultilingualInstalled(Interface):
    """ layer """


class IMultiLanguageExtraOptionsSchema(Interface):
    """ Interface for language extra options - control panel fieldset
    """

    filter_content = schema.Bool(
        title=_(u"heading_filter_content",
                default=u"Filter content by language."),
        description=_(u"description_filter_content",
                default=u"See the content that is in the same language as the actual one"),
        default=True,
        required=False,
        )

    google_translation_key = schema.TextLine(
        title=_(u"heading_google_translation_key",
                default=u"Google Translation API Key"),
        description=_(u"description_language_codes_in_URL",
                default=u"Is a paying API to use google translation service"),
        required=False,
        )