from zope.interface import Interface
from zope.interface import implementsOnly
from zope.schema import Choice
from zope.schema import Bool, List
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView

from plone.app.form.validators import null_validator

from plone.fieldsets.fieldsets import FormFieldsets

from zope.formlib import form
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.app.controlpanel.language import LanguageControlPanel as BasePanel
from plone.app.controlpanel.language import LanguageControlPanelAdapter
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.protect import CheckAuthenticator

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName

from zope.schema.interfaces import IVocabularyFactory

from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID

import json

from plone.app.multilingual import isLPinstalled
from plone.multilingual.interfaces import IMultilingualStorage, ITranslationManager, ILanguage

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
        vocabulary=("plone.app.multilingual.vocabularies."
                    "AllContentLanguageVocabulary"))

    available_languages = List(
        title=_(u"heading_available_languages",
                default=u"Available languages"),
        description=_(u"description_available_languages",
                default=u"The languages in which the site should be "
                        u"translatable."),
        required=True,
        missing_value=set(),
        value_type=Choice(
            vocabulary=("plone.app.multilingual.vocabularies."
                        "AllContentLanguageVocabulary")))

    # show_original_on_translation = Bool(
    #     title=_(u"heading_show_original_on_translation",
    #             default=u"Show original on translation"),
    #     description=_(u"description_show_original_on_translation",
    #             default=u"Show the left column on translation"),
    #     )


class IMultiLanguageExtraOptionsSetupSchema(IMultiLanguageExtraOptionsSchema):

    set_default_language = Bool(
        title=_(u"heading_set_default_language",
                default=u"Set the default language"),
        description=_(
            u"description_set_default_language",
            default=(u"Set the default language on all content without "
                     u"language defined. This value is not stored so you need "
                     u"to check every time you want to run it")),
        default=False,
        required=False,
        )

    move_content_to_language_folder = Bool(
        title=_(u"heading_move_content_to_language_folder",
                default=u"Move root content to default language folder"),
        description=_(
            u"description_move_content_to_language_folder",
            default=(u"Move the content that is on the root folder to the "
                     u"default language folder. This value is not stored so "
                     u"you need to check every time you want to run it")),
        default=False,
        required=False,
        )


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
        title=_(
            u"heading_language_codes_in_URL",
            default=u"Use language codes in URL path for manual override."),
        description=_(
            u"description_language_codes_in_URL",
            default=u"Use language codes in URL path for manual override."),
        required=False,
        )

    use_cookie_negotiation = Bool(
        title=_(u"heading_cookie_manual_override",
                default=(u"Use cookie for manual override. (Required for "
                         u"the language selector viewlet to be rendered.)")),
        description=_(
            u"description_cookie_manual_override",
            default=(u"Use cookie for manual override. (Required for the "
                     u"language selector viewlet to be rendered.)")),
        required=False,
        )

    authenticated_users_only = Bool(
        title=_(u"heading_auth_cookie_manual_override",
                default=u"Authenticated users only."),
        description=_(
            u"description_auth_ookie_manual_override",
            default=(u"Authenticated users only. Use cookie for manual "
                     u"override. (Required for the language selector viewlet "
                     u"to be rendered.)")),
        required=False,
        )

    set_cookie_everywhere = Bool(
        title=_(
            u"heading_set_language_cookie_always",
            default=(u"Set the language cookie always, i.e. also when the "
                     u"'set_language' request parameter is absent.")),
        description=_(
            u"description_set_language_cookie_always",
            default=(u"Set the language cookie always, i.e. also when the "
                     u"'set_language' request parameter is absent.")),
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

selector_policies = SimpleVocabulary(
    [SimpleTerm(value=u'closest', title=_(u'Search for closest translation in parent\'s content chain.')),
     SimpleTerm(value=u'dialog', title=_(u'Show user dialog with information about the available translations.'))
    ]
)


class IMultiLanguagePolicies(Interface):
    """ Interface for language policies - control panel fieldset
    """

    selector_lookup_translations_policy = Choice(
        title=_(u"heading_selector_lookup_translations_policy",
                default=u"The policy used to determine how the lookup for available "
                         "translations will be made by the language selector."),
        description=_(u"description_selector_lookup_translations_policy",
                      default=u"The default language used for the content "
                              u"and the UI of this site."),
        required=True,
        vocabulary=selector_policies
    )


class MultiLanguageOptionsControlPanelAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultiLanguageOptionsSchema)

    def __init__(self, context):
        super(MultiLanguageOptionsControlPanelAdapter, self).__init__(context)

    def get_use_content_negotiation(self):
        return self.context.use_content_negotiation

    def set_use_content_negotiation(self, value):
        self.context.use_content_negotiation = value

    def get_use_path_negotiation(self):
        return self.context.use_path_negotiation

    def set_use_path_negotiation(self, value):
        self.context.use_path_negotiation = value

    def get_use_cookie_negotiation(self):
        return self.context.use_cookie_negotiation

    def set_use_cookie_negotiation(self, value):
        self.context.use_cookie_negotiation = value

    def get_authenticated_users_only(self):
        return self.context.authenticated_users_only

    def set_authenticated_users_only(self, value):
        self.context.authenticated_users_only = value

    def get_set_cookie_everywhere(self):
        return self.context.set_cookie_everywhere

    def set_set_cookie_everywhere(self, value):
        self.context.set_cookie_everywhere = value

    def get_use_subdomain_negotiation(self):
        return self.context.use_subdomain_negotiation

    def set_use_subdomain_negotiation(self, value):
        self.context.use_subdomain_negotiation = value

    def get_use_cctld_negotiation(self):
        return self.context.use_cctld_negotiation

    def set_use_cctld_negotiation(self, value):
        self.context.use_cctld_negotiation = value

    def get_use_request_negotiation(self):
        return self.context.use_request_negotiation

    def set_use_request_negotiation(self, value):
        self.context.use_request_negotiation = value

    use_content_negotiation = property(get_use_content_negotiation,
                                       set_use_content_negotiation)
    use_path_negotiation = property(get_use_path_negotiation,
                                    set_use_path_negotiation)
    use_cookie_negotiation = property(get_use_cookie_negotiation,
                                      set_use_cookie_negotiation)
    authenticated_users_only = property(get_authenticated_users_only,
                                        set_authenticated_users_only)
    set_cookie_everywhere = property(get_set_cookie_everywhere,
                                     set_set_cookie_everywhere)
    use_subdomain_negotiation = property(get_use_subdomain_negotiation,
                                         set_use_subdomain_negotiation)
    use_cctld_negotiation = property(get_use_cctld_negotiation,
                                     set_use_cctld_negotiation)
    use_request_negotiation = property(get_use_request_negotiation,
                                       set_use_request_negotiation)


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
    implementsOnly(IMultiLanguageExtraOptionsSetupSchema)

    def __init__(self, context):
        super(MultiLanguageExtraOptionsAdapter, self).__init__(context)
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(
            IMultiLanguageExtraOptionsSchema)

    def get_filter_content(self):
        return self.settings.filter_content

    def set_filter_content(self, value):
        self.settings.filter_content = value

    def get_google_translation_key(self):
        return self.settings.google_translation_key

    def set_google_translation_key(self, value):
        self.settings.google_translation_key = value

    def get_redirect_babel_view(self):
        return self.settings.redirect_babel_view

    def set_redirect_babel_view(self, value):
        self.settings.redirect_babel_view = value

    def get_set_default_language(self):
        return False

    def set_set_default_language(self, value):
        if value:
            SetupMultilingualSite(self.context).set_default_language_content()

    def get_move_content_to_language_folder(self):
        return False

    def set_move_content_to_language_folder(self, value):
        if value:
            SetupMultilingualSite(self.context).move_default_language_content()

    google_translation_key = property(get_google_translation_key,
                              set_google_translation_key)

    filter_content = property(get_filter_content,
                              set_filter_content)

    redirect_babel_view = property(get_redirect_babel_view,
                                   set_redirect_babel_view)

    set_default_language = property(get_set_default_language,
                                    set_set_default_language)

    move_content_to_language_folder = property(
        get_move_content_to_language_folder,
        set_move_content_to_language_folder)


class MultiLanguagePoliciesAdapter(LanguageControlPanelAdapter):
    implementsOnly(IMultiLanguagePolicies)

    def __init__(self, context):
        super(MultiLanguagePoliciesAdapter, self).__init__(context)
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)

    def get_selector_lookup_translations_policy(self):
        return self.settings.selector_lookup_translations_policy

    def set_selector_lookup_translations_policy(self, value):
        self.settings.selector_lookup_translations_policy = value

    selector_lookup_translations_policy = property(get_selector_lookup_translations_policy,
                                                   set_selector_lookup_translations_policy)

selection = FormFieldsets(IMultiLanguageSelectionSchema)
selection.label = _(u'Site Languages')

options = FormFieldsets(IMultiLanguageOptionsSchema)
options.label = _(u'Negotiation Scheme')

extras = FormFieldsets(IMultiLanguageExtraOptionsSetupSchema)
extras.label = _(u'Extra options')

policies = FormFieldsets(IMultiLanguagePolicies)
policies.label = _(u'Policies')


class LanguageControlPanel(BasePanel):
    """A modified language control panel, allows selecting multiple languages.
    """

    template = ViewPageTemplateFile('templates/controlpanel.pt')

    form_fields = FormFieldsets(selection, options, policies, extras)

    label = _("Multilingual Settings")
    description = _("All the configuration of P.A.M. If you want to set "
                    "the default language to all the content without language "
                    "and move all the content on the root folder to the "
                    "default language folder, go to Extra Options section ")
    form_name = _("Multilingual Settings")

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_save_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _Plone("Changes saved.")
            self._on_save(data)
        else:
            self.status = _Plone("No changes made.")
        setupTool = SetupMultilingualSite()
        output = setupTool.setupSite(self.context)
        self.status += output

    @form.action(_Plone(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(
            _Plone("Changes canceled."), type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''

    isLPinstalled = isLPinstalled


class MigrationView(BrowserView):
    """ The view for display the migration information, actions and results """
    __call__ = ViewPageTemplateFile('templates/migration.pt')

    isLPinstalled = isLPinstalled


class MigrationViewAfter(BrowserView):
    """ The view for display the migration information, actions and results """
    __call__ = ViewPageTemplateFile('templates/migration-after.pt')

    isLPinstalled = isLPinstalled


class multilingualMapViewJSON(BrowserView):
    """ Helper view to get json translations """

    def __call__(self):
        """ Get the JSON information about based on a nodeId
        """

        # We get the language we are looking for
        lang = ''
        tool = getToolByName(self.context, 'portal_languages', None)
        if 'lang' in self.request:
            lang = self.request['lang']

        if lang == '':
            lang = tool.getDefaultLanguage()

        # We want all or just the missing translations elements
        if 'all' in self.request:
            get_all = (self.request['all'] == 'true')
        else:
            get_all = True

        # Which is the root nodeId
        folder_path = ''
        if 'nodeId' in self.request:
            # We get the used UUID
            nodeId = (self.request['nodeId'])
            if (nodeId != 'root'):
                new_root = uuidToObject(nodeId)
                if ILanguage(new_root).get_language() == lang:
                    folder_path = '/'.join(new_root.getPhysicalPath())
        if folder_path == '':
            # We get the root folder
            root = getToolByName(self.context, 'portal_url')
            root = root.getPortalObject()
            folder_path = '/'.join(root.getPhysicalPath())

        self.request.response.setHeader("Content-type", "application/json; charset=utf-8")
        pcatalog = getToolByName(self.context, 'portal_catalog')
        query = {}
        query['path'] = {'query': folder_path, 'depth': 1}
        query['sort_on'] = "sortable_title"
        query['sort_order'] = "ascending"
        query['Language'] = lang
        search_results = pcatalog.searchResults(query)
        resultat = {'id': 'root', 'name': folder_path, 'data': {}, 'children': []}
        # Get the canonicals
        storage = getUtility(IMultilingualStorage)
        canonicals = storage.get_canonicals()
        supported_languages = tool.getSupportedLanguages()
        for sr in search_results:
            # We want to know the translated and missing elements
            translations = {}
            if sr['UID'] in canonicals:
                # We look for the brain for each translation
                canonical = canonicals[sr['UID']]
                for lang in supported_languages:
                    if lang in canonical.get_keys():
                        translated_obj = uuidToObject(canonical.get_item(lang))
                        translations[lang] = {'url': translated_obj.absolute_url(), 'title': translated_obj.getId()}
                    else:
                        url_to_create = sr.getURL() + "/@@create_translation?form.widgets.language"\
                            "=%s&form.buttons.create=1" % lang
                        translations[lang] = {'url': url_to_create, 'title': _(u'Not translated')}
            if get_all:
                resultat['children'].append({'id': sr['UID'], 'name': sr['Title'], 'data': translations, 'children': []})
            else:
                pass
        return json.dumps(resultat)


class multilingualMapView(BrowserView):
    """ The view for display the current multilingual map for the site """
    __call__ = ViewPageTemplateFile('templates/mmap.pt')

    def languages(self):
        langs = getUtility(IVocabularyFactory, name=u"plone.app.multilingual.vocabularies.AllAvailableLanguageVocabulary")
        tool = getToolByName(self.context, 'portal_languages', None)
        lang = tool.getDefaultLanguage()
        return {'default': lang, 'languages': langs(self.context)}

    def canonicals(self):
        """ We get all the canonicals and see which translations are missing """
        # Get the language
        tool = getToolByName(self.context, 'portal_languages', None)
        languages = tool.getSupportedLanguages()
        num_lang = len(languages)
        # Get the canonicals
        storage = getUtility(IMultilingualStorage)
        canonicals = storage.get_canonicals()
        # Needs to be optimized
        not_full_translations = []
        already_added_canonicals = []
        for canonical in canonicals.keys():
            canonical_object = canonicals[canonical]
            canonical_languages = canonical_object.get_keys()
            if len(canonical_languages) < num_lang and id(canonical_object) not in already_added_canonicals:
                missing_languages = [lang for lang in languages if lang not in canonical_languages]
                translations = []
                last_url = ''
                for canonical_language in canonical_languages:
                    obj = uuidToObject(canonical_object.get_item(canonical_language))
                    last_url = obj.absolute_url()
                    translations.append({'url': obj.absolute_url(),
                                         'path': '/'.join(obj.getPhysicalPath()),
                                         'lang': canonical_language})
                already_added_canonicals.append(id(canonical_object))
                not_full_translations.append({'id': canonical,
                                              'last_url': last_url,
                                              'missing': missing_languages,
                                              'translated': translations})
        return not_full_translations

    isLPinstalled = isLPinstalled
