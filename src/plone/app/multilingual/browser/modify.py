# -*- coding: utf-8 -*-
from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import IConnectTranslation
from plone.app.multilingual.interfaces import ITranslationManager
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.interfaces import IFormFieldProvider
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ILanguage
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form.form import Form
from zope.component import getUtility
import logging

logger = logging.getLogger(__name__)


class ModifyTranslationsForm(BrowserView):

    def available_languages(self):
        registry = getUtility(IRegistry)
        return registry['plone.available_languages']

    def get_translation(self, language):

        manager = ITranslationManager(self.context)
        return manager.get_translation(language)


class ConnectTranslation(AutoExtensibleForm, Form):

    schema = IFormFieldProvider(IConnectTranslation)
    ignoreContext = True
    label = _(u"label_connect_translation", default=u"Connect translation")
    description = _(
        u"long_description_connect_translation",
        default=u"This form allows you to connect a currently existing "
                u"translations of the current object."
    )

    @button.buttonAndHandler(_(u"connect_translation",
                               default=u"Connect translation"))
    def handle_add(self, action):
        data, errors = self.extractData()
        if not errors:
            content = data['content']
            language = data['language']
            ITranslationManager(self.context)\
                .register_translation(language, content)
            ILanguage(content).set_language(language)

        return self.request.response.redirect(
            self.context.absolute_url() + '/modify_translations')


class DisconnectTranslation(BrowserView):

    tpl = ViewPageTemplateFile('templates/disconnect_translation.pt')

    def __call__(self):

        if self.request.form.get('submitted'):
            language = self.request.form['language']
            catalog = getToolByName(self.context, 'portal_catalog')
            context = catalog.unrestrictedSearchResults(
                UID=self.request.form['came_from'])
            if context:
                context = context[0].getObject()
            if language and context:
                manager = ITranslationManager(context)
                try:
                    manager.remove_translation(language)
                except Exception, e:
                    messages = IStatusMessage(self.request)
                    messages.addStatusMessage(e, type='error')

                return self.request.response.redirect(
                    context.absolute_url() + '/modify_translations')

        return self.tpl()
