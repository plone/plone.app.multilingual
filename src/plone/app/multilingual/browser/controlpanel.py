from zope.interface import Interface
from zope.interface import implementsOnly
from zope.interface import implements
from zope.schema import Choice, ASCII, Object
from zope.schema import Tuple, Bool, List, TextLine

from zope.formlib.form import FormFields
from plone.fieldsets.fieldsets import FormFieldsets

from plone.app.multilingual.interfaces import IMultilinguaSettings

from plone.app.controlpanel.language import LanguageControlPanel as BasePanel
from plone.app.controlpanel.language import LanguageControlPanelAdapter
from plone.app.multilingual.browser.setup import SetupMultilingualSite

from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import ListSequenceWidget

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone.app.multilingual')


class IMultiLanguageSelectionSchema(Interface):
    """ Interface for language selection - control panel fieldset
    """

    default_language = Choice(
        title=_(u"heading_site_language",
                default=u"Default site language"),
        description=_(u"description_site_language",
                      default=u"The default language used for the content "
                              u"and the UI of this site."),
        required=True,
        vocabulary="plone.app.multilingual.vocabularies.AllContentLanguageVocabulary")

    available_languages = List(
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


class IMultiLanguageOptionsSchema(Interface):
    """ Interface for language options - control panel fieldset
    """

    use_content_negotiation = Bool(
        title=_(u"heading_language_of_the_content",
                default=u"Use the language of the content item."),
        description=_(u"description_language_of_the_content",
                default=u"Use the language of the content item."),
        )

    use_path_negotiation = Bool(
        title=_(u"heading_language_codes_in_URL",
                default=u"Use language codes in URL path for manual override."),
        description=_(u"description_language_codes_in_URL",
                default=u"Use language codes in URL path for manual override."),
        )

    use_cookie_negotiation = Bool(
        title=_(u"heading_cookie_manual_override",
                default=u"Use cookie for manual override. (Required for the language selector viewlet to be rendered.)"),
        description=_(u"description_cookie_manual_override",
                default=u"Use cookie for manual override. (Required for the language selector viewlet to be rendered.)"),
        )

    authenticated_users_only = Bool(
        title=_(u"heading_auth_cookie_manual_override",
                default=u"Authenticated users only."),
        description=_(u"description_auth_ookie_manual_override",
                default=u"Authenticated users only. Use cookie for manual override. (Required for the language selector viewlet to be rendered.)"),
        )

    set_cookie_everywhere = Bool(
        title=_(u"heading_set_language_cookie_always",
                default=u"Set the language cookie always, i.e. also when the 'set_language' request parameter is absent."),
        description=_(u"description_set_language_cookie_always",
                default=u"Set the language cookie always, i.e. also when the 'set_language' request parameter is absent."),
        )

    use_subdomain_negotiation = Bool(
        title=_(u"heading_use_subdomain",
                default=u"Use subdomain (e.g.: de.plone.org)."),
        description=_(u"description_use_subdomain",
                default=u"Use subdomain (e.g.: de.plone.org)."),
        )

    use_cctld_negotiation = Bool(
        title=_(u"heading_top_level_domain",
                default=u"Use top-level domain (e.g.: www.plone.de)."),
        description=_(u"description_top_level_domain",
                default=u"Use top-level domain (e.g.: www.plone.de)."),
        )

    use_request_negotiation = Bool(
        title=_(u"heading_browser_language_request_negotiation",
                default=u"Use browser language request negotiation."),
        description=_(u"description_browser_language_request_negotiation",
                default=u"Use browser language request negotiation."),
        )


class ILangAttrPair(Interface):
    """ Lang/url pair for mapping root folder - control panel widget
    """
    lang = TextLine(title=u"lang-code", max_length=5, readonly=True)
    url = TextLine(title=u"URL")


class IMultilinguaRootFolderForm(Interface):
    """ Lang/url pair list for mapping root folder - control panel fieldset
    """
    default_layout_languages = List(
        title=_(u'Layouts'),
        description=_(u"This languages are mapped at Root Folder"),
        default=[],
        value_type=Object(ILangAttrPair, title=u"map"),
        required=False)


class MultiLanguageOptionsControlPanelAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultiLanguageOptionsSchema)

    def __init__(self, context):
        super(MultiLanguageOptionsControlPanelAdapter, self).__init__(context)
        self.tool = getToolByName(self.context, 'portal_languages')

    def get_use_content_negotiation(self):
        return self.tool.use_content_negotiation

    def set_use_content_negotiation(self, value):
        self.tool.use_content_negotiation = value

    def get_use_path_negotiation(self):
        return self.tool.use_path_negotiation

    def set_use_path_negotiation(self, value):
        self.tool.use_path_negotiation = value

    def get_use_cookie_negotiation(self):
        return self.tool.use_cookie_negotiation

    def set_use_cookie_negotiation(self, value):
        self.tool.use_cookie_negotiation = value

    def get_authenticated_users_only(self):
        return self.tool.authenticated_users_only

    def set_authenticated_users_only(self, value):
        self.tool.authenticated_users_only = value

    def get_set_cookie_everywhere(self):
        return self.tool.set_cookie_everywhere

    def set_set_cookie_everywhere(self, value):
        self.tool.set_cookie_everywhere = value

    def get_use_subdomain_negotiation(self):
        return self.tool.use_subdomain_negotiation

    def set_use_subdomain_negotiation(self, value):
        self.tool.use_subdomain_negotiation = value

    def get_use_cctld_negotiation(self):
        return self.tool.use_cctld_negotiation

    def set_use_cctld_negotiation(self, value):
        self.tool.use_cctld_negotiation = value

    def get_use_request_negotiation(self):
        return self.tool.use_request_negotiation

    def set_use_request_negotiation(self, value):
        self.tool.use_request_negotiation = value

    use_content_negotiation = property(get_use_content_negotiation, set_use_content_negotiation)
    use_path_negotiation = property(get_use_path_negotiation, set_use_path_negotiation)
    use_cookie_negotiation = property(get_use_cookie_negotiation, set_use_cookie_negotiation)
    authenticated_users_only = property(get_authenticated_users_only, set_authenticated_users_only)
    set_cookie_everywhere = property(get_set_cookie_everywhere, set_set_cookie_everywhere)
    use_subdomain_negotiation = property(get_use_subdomain_negotiation, set_use_subdomain_negotiation)
    use_cctld_negotiation = property(get_use_cctld_negotiation, set_use_cctld_negotiation)
    use_request_negotiation = property(get_use_request_negotiation, set_use_request_negotiation)


class LangAttrPair:
    implements(ILangAttrPair)

    def __init__(self, lang='', url=''):
        self.lang = lang
        self.url = url


class MultilinguaRootFolderAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultilinguaRootFolderForm)

    def __init__(self, context):
        super(MultilinguaRootFolderAdapter, self).__init__(context)
        registry = getUtility(IRegistry)
        self.root_folder = registry.forInterface(IMultilinguaSettings)

    def get_url_languages(self):
        l = []
        for key in self.root_folder.default_layout_languages.keys():
            l.append(LangAttrPair(lang=key, url=self.root_folder.default_layout_languages[key]))
        return l

    def set_url_languages(self, value):
        for v in value:
            if v.lang in self.root_folder.default_layout_languages.keys():
                self.root_folder.default_layout_languages[v.lang] = v.url

    default_layout_languages = property(get_url_languages, set_url_languages)


class MultiLanguageControlPanelAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultiLanguageSelectionSchema)

    def __init__(self, context):
        super(MultiLanguageControlPanelAdapter, self).__init__(context)

    def get_available_languages(self):
        return [unicode(l) for l in self.context.getSupportedLanguages()]

    def set_available_languages(self, value):
        import ipdb;ipdb.set_trace()
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.context)
        languages = [str(l) for l in value]
        self.context.supported_langs = languages

    def set_show_original_on_translation(self, value):
        prop = getToolByName(self.context, 'portal_properties').linguaplone_properties
        prop.hide_right_column_on_translate_form = value

    def get_show_original_on_translation(self):
        prop = getToolByName(self.context, 'portal_properties').linguaplone_properties
        return prop.hide_right_column_on_translate_form

    available_languages = property(get_available_languages,
                                   set_available_languages)

    show_original_on_translation = property(get_show_original_on_translation,
                                            set_show_original_on_translation)


selection = FormFieldsets(IMultiLanguageSelectionSchema)
selection.label = _(u'Site Languages')

options = FormFieldsets(IMultiLanguageOptionsSchema)
options.label = _(u'Negotiation Scheme')

languages = FormFieldsets(IMultilinguaRootFolderForm)
languages.label = _(u'Default language URLs')


langattr_widget = CustomWidgetFactory(ObjectWidget, LangAttrPair)
combination_widget = CustomWidgetFactory(ListSequenceWidget,
                                         subwidget=langattr_widget)


class LanguageControlPanel(BasePanel):
    """A modified language control panel, allows selecting multiple languages.
    """

    languages['default_layout_languages'].custom_widget = combination_widget

    form_fields = FormFieldsets(selection, options, languages)

    label = _("Multilingual Settings")
    description = _("All the configuration of P.A.M.")
    form_name = _("Multilingual Settings")
