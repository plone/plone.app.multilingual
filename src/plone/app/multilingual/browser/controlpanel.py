from zope.interface import Interface
from zope.interface import implementsOnly
from zope.schema import Choice
from zope.schema import Bool, List

from plone.fieldsets.fieldsets import FormFieldsets


from plone.app.controlpanel.language import LanguageControlPanel as BasePanel
from plone.app.controlpanel.language import LanguageControlPanelAdapter
from plone.app.multilingual.browser.setup import SetupMultilingualSite

from Products.CMFCore.utils import getToolByName

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

    # show_original_on_translation = Bool(
    #     title=_(u"heading_show_original_on_translation",
    #             default=u"Show original on translation"),
    #     description=_(u"description_show_original_on_translation",
    #             default=u"Show the left column on translation"),
    #     )


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


class MultiLanguageControlPanelAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultiLanguageSelectionSchema)

    def __init__(self, context):
        super(MultiLanguageControlPanelAdapter, self).__init__(context)

    def get_available_languages(self):
        return [unicode(l) for l in self.context.getSupportedLanguages()]

    def set_available_languages(self, value):
        languages = [str(l) for l in value]
        self.context.supported_langs = languages
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.context)

    # def set_show_original_on_translation(self, value):
    #     prop = getToolByName(self.context, 'portal_properties').linguaplone_properties
    #     prop.hide_right_column_on_translate_form = value

    # def get_show_original_on_translation(self):
    #     prop = getToolByName(self.context, 'portal_properties').linguaplone_properties
    #     return prop.hide_right_column_on_translate_form

    available_languages = property(get_available_languages,
                                   set_available_languages)

    # show_original_on_translation = property(get_show_original_on_translation,
    #                                         set_show_original_on_translation)


selection = FormFieldsets(IMultiLanguageSelectionSchema)
selection.label = _(u'Site Languages')

options = FormFieldsets(IMultiLanguageOptionsSchema)
options.label = _(u'Negotiation Scheme')


class LanguageControlPanel(BasePanel):
    """A modified language control panel, allows selecting multiple languages.
    """

    form_fields = FormFieldsets(selection, options)

    label = _("Multilingual Settings")
    description = _("All the configuration of P.A.M.")
    form_name = _("Multilingual Settings")
