from zope.interface import Interface
from zope.interface import implementsOnly
from zope.schema import Choice
from zope.schema import Tuple, Bool
from zope.formlib.form import FormFields
from plone.app.controlpanel.language import LanguageControlPanel as BasePanel
from plone.app.controlpanel.language import LanguageControlPanelAdapter

from Products.CMFCore.utils import getToolByName

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone.app.multilingual')


class IMultiLanguageSelectionSchema(Interface):

    default_language = Choice(
        title=_(u"heading_site_language",
                default=u"Default site language"),
        description=_(u"description_site_language",
                      default=u"The default language used for the content "
                              u"and the UI of this site."),
        required=True,
        vocabulary="plone.app.multilingual.vocabularies.AllContentLanguageVocabulary")

    available_languages = Tuple(
        title=_(u"heading_available_languages",
                default=u"Available languages"),
        description=_(u"description_available_languages",
                default=u"The languages in which the site should be "
                        u"translatable."),
        required=True,
        missing_value=set(),
        value_type=Choice(
            vocabulary="plone.app.multilingual.vocabularies.AllContentLanguageVocabulary"))

    show_original_on_translation = Bool(
        title=_(u"heading_show_original_on_translation",
                default=u"Show original on translation"),
        description=_(u"description_show_original_on_translation",
                default=u"Show the left column on translation"),
        )
        


class MultiLanguageControlPanelAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultiLanguageSelectionSchema)

    def __init__(self, context):
        super(MultiLanguageControlPanelAdapter, self).__init__(context)

    def get_available_languages(self):
        return [unicode(l) for l in self.context.getSupportedLanguages()]

    def set_available_languages(self, value):
        languages = [str(l) for l in value]
        self.context.supported_langs = languages

    def set_show_original_on_translation(self, value):
        prop = getToolByName(self.context,'portal_properties').linguaplone_properties
        prop.hide_right_column_on_translate_form = value

    def get_show_original_on_translation(self):
        prop = getToolByName(self.context,'portal_properties').linguaplone_properties
        return prop.hide_right_column_on_translate_form

    available_languages = property(get_available_languages,
                                   set_available_languages)

    show_original_on_translation = property(get_show_original_on_translation,
                                            set_show_original_on_translation)

class LanguageControlPanel(BasePanel):
    """A modified language control panel, allows selecting multiple languages.
    """

    form_fields = FormFields(IMultiLanguageSelectionSchema)