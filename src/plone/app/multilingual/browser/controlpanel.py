# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.controlpanel.browser.language import \
    LanguageControlPanelForm
from plone.app.registry.browser import controlpanel

from plone.app.multilingual import isLPinstalled
from plone.app.multilingual.browser.migrator import portal_types_blacklist
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.uuid.utils import uuidToObject
from zc.relation.interfaces import ICatalog as IRelationCatalog
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.i18nmessageid import MessageFactory
from zope.schema.interfaces import IVocabularyFactory
from z3c.form import button


import json

_ = MessageFactory('plone.app.multilingual')


class LanguageControlPanelFormPAM(LanguageControlPanelForm):
    """A modified language control panel, allows selecting multiple languages.
    """
    label = _("Multilingual Settings")
    description = _("pam_controlpanel_description",
                    default=u"All the configuration of "
                            u"a multilingual Plone site")
    schema = IMultiLanguageExtraOptionsSchema

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # We need to check if the default language is in available languages
        if 'default_language' in data and 'available_languages' in data and \
                data['default_language'] not in data['available_languages']:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Default language not in available languages"),
                "error")

            # e = Invalid(_(u"Default language not in available languages"))
            # raise WidgetActionExecutionError('default_language', e)
            return

        self.applyChanges(data)

        setupTool = SetupMultilingualSite()
        output = setupTool.setupSite(self.context)
        self.status += output

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes canceled."), "info")
        self.request.response.redirect("%s/%s" % (
            self.context.absolute_url(),
            self.control_panel_view))


class LanguageControlPanel(controlpanel.ControlPanelFormWrapper):
    form = LanguageControlPanelFormPAM
    index = ViewPageTemplateFile('templates/controlpanel.pt')
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
