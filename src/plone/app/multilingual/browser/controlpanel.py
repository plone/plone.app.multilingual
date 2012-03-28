from zope.interface import Interface
from zope.interface import implementsOnly
from zope.schema import Choice, TextLine
from zope.schema import Bool, List
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from plone.app.form.validators import null_validator

from plone.fieldsets.fieldsets import FormFieldsets

from zope.formlib import form

from plone.app.controlpanel.language import LanguageControlPanel as BasePanel
from plone.app.controlpanel.language import LanguageControlPanelAdapter
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.protect import CheckAuthenticator

from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from Products.CMFPlone.CatalogTool import CatalogTool
from plone.app.multilingual import catalog 

from Products.CMFPlone import PloneMessageFactory as _Plone
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
        required=False,
        )

    use_path_negotiation = Bool(
        title=_(u"heading_language_codes_in_URL",
                default=u"Use language codes in URL path for manual override."),
        description=_(u"description_language_codes_in_URL",
                default=u"Use language codes in URL path for manual override."),
        required=False,
        )

    use_cookie_negotiation = Bool(
        title=_(u"heading_cookie_manual_override",
                default=u"Use cookie for manual override. (Required for the language selector viewlet to be rendered.)"),
        description=_(u"description_cookie_manual_override",
                default=u"Use cookie for manual override. (Required for the language selector viewlet to be rendered.)"),
        required=False,
        )

    authenticated_users_only = Bool(
        title=_(u"heading_auth_cookie_manual_override",
                default=u"Authenticated users only."),
        description=_(u"description_auth_ookie_manual_override",
                default=u"Authenticated users only. Use cookie for manual override. (Required for the language selector viewlet to be rendered.)"),
        required=False,
        )

    set_cookie_everywhere = Bool(
        title=_(u"heading_set_language_cookie_always",
                default=u"Set the language cookie always, i.e. also when the 'set_language' request parameter is absent."),
        description=_(u"description_set_language_cookie_always",
                default=u"Set the language cookie always, i.e. also when the 'set_language' request parameter is absent."),
        required=False,
        )

    use_subdomain_negotiation = Bool(
        title=_(u"heading_use_subdomain",
                default=u"Use subdomain (e.g.: de.plone.org)."),
        description=_(u"description_use_subdomain",
                default=u"Use subdomain (e.g.: de.plone.org)."),
        required=False,
        )

    use_cctld_negotiation = Bool(
        title=_(u"heading_top_level_domain",
                default=u"Use top-level domain (e.g.: www.plone.de)."),
        description=_(u"description_top_level_domain",
                default=u"Use top-level domain (e.g.: www.plone.de)."),
        required=False,
        )

    use_request_negotiation = Bool(
        title=_(u"heading_browser_language_request_negotiation",
                default=u"Use browser language request negotiation."),
        description=_(u"description_browser_language_request_negotiation",
                default=u"Use browser language request negotiation."),
        required=False,
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

    available_languages = property(get_available_languages,
                                   set_available_languages)


class MultiLanguageExtraOptionsAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultiLanguageExtraOptionsSchema)

    def __init__(self, context):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguageExtraOptionsSchema)
        self.context = context

    def get_filter_content(self):
        return self.settings.filter_content

    def set_filter_content(self, value):
        self.settings.filter_content = value
        if not value:
            catalog.I18nDeAwareCatalog()
        else:
            catalog.I18nAwareCatalog()

    def get_google_translation_key(self):
        return self.settings.google_translation_key

    def set_google_translation_key(self, value):
        self.settings.google_translation_key = value

    google_translation_key = property(get_google_translation_key,
                              set_google_translation_key)

    filter_content = property(get_filter_content,
                              set_filter_content)

selection = FormFieldsets(IMultiLanguageSelectionSchema)
selection.label = _(u'Site Languages')

options = FormFieldsets(IMultiLanguageOptionsSchema)
options.label = _(u'Negotiation Scheme')

extras = FormFieldsets(IMultiLanguageExtraOptionsSchema)
extras.label = _(u'Extra options')

class LanguageControlPanel(BasePanel):
    """A modified language control panel, allows selecting multiple languages.
    """

    form_fields = FormFieldsets(selection, options, extras)

    label = _("Multilingual Settings")
    description = _("""All the configuration of P.A.M. If you want to set 
                       the default language to all the content without language
                       and move all the content on the root folder to the default 
                       language folder, press 'Save, set and move'. Otherwise 
                       use the 'Save and not move/set content'""")
    form_name = _("Multilingual Settings")

    @form.action(_(u'label_save_and_move_set_content', default=u'Save, set and move'), name=u'save_set_move')
    def handle_save_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _Plone("Changes saved.")
            self._on_save(data)
        else:
            self.status = _Plone("No changes made.")
        setupTool = SetupMultilingualSite()
        output = setupTool.setupSite(self.context, forceOneLanguage=True)
        self.status += output


    @form.action(_(u'Save and not move/set content'), name=u'not_content')
    def handle_safe_save_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _Plone("Changes saved.")
            self._on_save(data)
        else:
            self.status = _Plone("No changes made.")
        setupTool = SetupMultilingualSite()
        output = setupTool.setupSite(self.context, forceMovingAndSetting=False)
        self.status += output

    @form.action(_Plone(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_Plone("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''
