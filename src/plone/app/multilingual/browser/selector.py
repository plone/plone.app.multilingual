from zope import component
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.multilingual.interfaces import ITranslationManager, ITranslatable
from zope.security import checkPermission
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT
from plone.app.multilingual.interfaces import IMultilinguaSettings

class LanguageSelectorViewlet(ViewletBase):
    """Language selector for translatable content.
    """

    def available(self):
        language_tool = getToolByName(self.context, 'portal_languages')
        supported_languages = language_tool.getSupportedLanguages()
        return len(supported_languages) > 1

    def languages(self):
        result = []
        translations = {}
        language_tool = getToolByName(self.context, 'portal_languages')
        languages = language_tool.getAvailableLanguages()
        manager = component.queryAdapter(self.context, ITranslationManager)
        if manager is not None:
            translations = manager.get_translations()
            for key in translations.keys():
                if checkPermission('zope2.View', translations[key]):
                    if key != LANGUAGE_INDEPENDENT:
                        result.append({
                            'code': key,
                            'flag': languages[key].get('flag', ''),
                            'name': languages[key].get('name', key),
                            'url': "%s/switchLanguage?set_language=%s" % (translations[key].absolute_url(),key),
                            'selected': translations[key] == self.context,
                        })
        settings = component.getUtility(IRegistry).forInterface(IMultilinguaSettings)
        if settings.show_selector_always:
            supported_languages = language_tool.getSupportedLanguages()
            for key in supported_languages:
                if key not in translations.keys():
                    result.append({
                        'code': key,
                        'flag': languages[key].get('flag', ''),
                        'name': languages[key].get('name', key),
                        'url': "%s/switchLanguage?set_language=%s" % (self.context.absolute_url(), key),
                        'selected': self.request.get('LANGUAGE') == key,
                    })

        return result
