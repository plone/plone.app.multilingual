# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _Plone
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.controlpanel.bbb.language import LanguageControlPanelAdapter
from Products.CMFPlone.controlpanel.browser.language import LanguageControlPanelForm
from Products.CMFPlone.controlpanel.browser.language import LanguageControlPanel
from plone.app.form.validators import null_validator
from plone.app.multilingual import isLPinstalled
from plone.app.multilingual.browser.migrator import portal_types_blacklist
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.uuid.utils import uuidToObject
from plone.protect import CheckAuthenticator
from plone.registry import field as Record
from plone.registry import field as registry_field
from plone.registry.interfaces import IRegistry
from zc.relation.interfaces import ICatalog as IRelationCatalog
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.interface import implementsOnly
from zope.schema import Bool
from zope.schema.interfaces import IVocabularyFactory


import json

_ = MessageFactory('plone.app.multilingual')


class IControlPanelLanguageOptions(IMultiLanguageExtraOptionsSchema):

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


class MultiLanguageExtraOptionsAdapter(LanguageControlPanelAdapter):
    implementsOnly(IControlPanelLanguageOptions)

    def __init__(self, context):
        self.context = context
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(
            IMultiLanguageExtraOptionsSchema, check=False)

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

    def get_buttons_babel_view_up_to_nr_translations(self):
        return self.settings.buttons_babel_view_up_to_nr_translations

    def set_buttons_babel_view_up_to_nr_translations(self, value):
        # Backwards-compatibility for installations of PAM before this
        # field was added.
        # If no entry is present in the registry, initialize it with a
        # dummy value
        name = "%s.buttons_babel_view_up_to_nr_translations" % \
            IMultiLanguageExtraOptionsSchema.__identifier__
        if name not in self.registry.records:
            int_field = registry_field.Int()
            self.registry.records[name] = Record(int_field)
        self.settings.buttons_babel_view_up_to_nr_translations = value

    google_translation_key = property(get_google_translation_key,
                                      set_google_translation_key)

    filter_content = property(get_filter_content,
                              set_filter_content)

    redirect_babel_view = property(get_redirect_babel_view,
                                   set_redirect_babel_view)

    buttons_babel_view_up_to_nr_translations = property(
        get_buttons_babel_view_up_to_nr_translations,
        set_buttons_babel_view_up_to_nr_translations,
    )

    def set_bypass_languageindependent_field_permission_check(self, value):
        self.settings.bypass_languageindependent_field_permission_check = value

    def get_bypass_languageindependent_field_permission_check(self):
        return self.settings.bypass_languageindependent_field_permission_check

    bypass_languageindependent_field_permission_check = property(
        get_bypass_languageindependent_field_permission_check,
        set_bypass_languageindependent_field_permission_check,
    )

    def get_selector_lookup_translations_policy(self):
        return self.settings.selector_lookup_translations_policy

    def set_selector_lookup_translations_policy(self, value):
        self.settings.selector_lookup_translations_policy = value

    selector_lookup_translations_policy = property(
        get_selector_lookup_translations_policy,
        set_selector_lookup_translations_policy)


# selection = FormFieldsets(IMultiLanguageSelectionSchema)
# selection.label = _(u'Site languages')

# options = FormFieldsets(IMultiLanguageOptionsSchema)
# options.label = _(u'Negotiation scheme')

# extras = FormFieldsets(IMultiLanguageExtraOptionsSchema)
# extras.label = _(u'Extra options')

# policies = FormFieldsets(IMultiLanguagePolicies)
# policies.label = _(u'Policies')


class LanguageControlPanelPAM(LanguageControlPanelForm):
    """A modified language control panel, allows selecting multiple languages.
    """

    template = ViewPageTemplateFile('templates/controlpanel.pt')

    # form_fields = FormFieldsets(
    #     selection, options, policies, extras)

    label = _("Multilingual Settings")
    description = _("pam_controlpanel_description",
                    default=u"All the configuration of "
                            u"a multilingual Plone site")
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
    portal_types_blacklist = portal_types_blacklist
    try:
        catalog = getUtility(IRelationCatalog)
        hasRelationCatalog = True
    except ComponentLookupError:
        hasRelationCatalog = False


class MigrationViewAfter(BrowserView):
    """ The view for display the migration information, actions and results """
    __call__ = ViewPageTemplateFile('templates/cleanup.pt')

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

        self.request.response.setHeader(
            "Content-type", "application/json; charset=utf-8")

        pcatalog = getToolByName(self.context, 'portal_catalog')
        query = {}
        query['path'] = {'query': folder_path, 'depth': 1}
        query['sort_on'] = "sortable_title"
        query['sort_order'] = "ascending"
        query['Language'] = lang
        search_results = pcatalog.searchResults(query)
        resultat = {
            'id': 'root',
            'name': folder_path,
            'data': {},
            'children': []
        }
        supported_languages = tool.getSupportedLanguages()
        for sr in search_results:
            # We want to know the translated and missing elements
            translations = {}
            if 'TranslationGroup' in sr:
                # We look for the brain for each translation
                brains = pcatalog.unrestrictedSearchResults(
                    TranslationGroup=sr['TranslationGroup'])
                languages = {}
                for brain in brains:
                    languages[brain.Language] = brain.UID
                for lang in supported_languages:
                    if lang in languages.keys():
                        translated_obj = uuidToObject(languages[lang])
                        translations[lang] = {
                            'url': translated_obj.absolute_url(),
                            'title': translated_obj.getId(),
                        }
                    else:
                        url_to_create = sr.getURL() + \
                            "/@@create_translation?form.widgets.language"\
                            "=%s&form.buttons.create=1" % lang
                        translations[lang] = {
                            'url': url_to_create,
                            'title': _(u'Not translated'),
                        }
            if get_all:
                resultat['children'].append({
                    'id': sr['UID'],
                    'name': sr['Title'],
                    'data': translations,
                    'children': [],
                })
            else:
                pass
        return json.dumps(resultat)


class multilingualMapView(BrowserView):
    """ The view for display the current multilingual map for the site """
    __call__ = ViewPageTemplateFile('templates/mmap.pt')

    def languages(self):
        langs = getUtility(IVocabularyFactory,
                           name=u"plone.app.multilingual.vocabularies"
                                u".AllAvailableLanguageVocabulary")
        tool = getToolByName(self.context, 'portal_languages', None)
        lang = tool.getDefaultLanguage()
        return {'default': lang, 'languages': langs(self.context)}

    def canonicals(self):
        """ We get all the canonicals and see which translations are
            missing """
        # Get the language
        tool = getToolByName(self.context, 'portal_languages', None)
        pcatalog = getToolByName(self.context, 'portal_catalog', None)
        languages = tool.getSupportedLanguages()
        num_lang = len(languages)
        # Get the canonicals
        # Needs to be optimized
        not_full_translations = []
        already_added_canonicals = []
        brains = pcatalog.searchResults()
        for brain in brains:
            if not isinstance(brain.TranslationGroup, str):
                # is alone, with a Missing.Value
                missing_languages = [
                    lang for lang in languages if lang != brain.Language]
                translations = [{
                    'url': brain.getURL(),
                    'path': brain.getPath(),
                    'lang': brain.Language,
                }]
                not_full_translations.append({
                    'id': 'None',
                    'last_url': brain.getURL(),
                    'missing': missing_languages,
                    'translated': translations,
                })
            elif isinstance(brain.TranslationGroup, str):
                tg = brain.TranslationGroup
                brains_tg = pcatalog.searchResults(TranslationGroup=tg)
                if len(brains_tg) < num_lang \
                   and tg not in already_added_canonicals:
                    translated_languages = [a.Language for a in brains_tg]
                    missing_languages = [lang for lang in languages
                                         if lang not in translated_languages]
                    translations = []
                    last_url = ''
                    for brain_tg in brains_tg:
                        last_url = brain_tg.getURL()
                        translations.append({
                            'url': brain_tg.getURL(),
                            'path': brain_tg.getPath(),
                            'lang': brain_tg.Language,
                        })

                    not_full_translations.append({
                        'id': tg,
                        'last_url': last_url,
                        'missing': missing_languages,
                        'translated': translations,
                    })
                already_added_canonicals.append(tg)
        return not_full_translations

    isLPinstalled = isLPinstalled
