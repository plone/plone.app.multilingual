from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName
from plone.multilingual.interfaces import ITranslatable
from plone.multilingual.interfaces import ILanguage


class oneLanguageConfiguredNoticeViewlet(ViewletBase):
    """ Notice the user that PAM is installed and only one language
        is configured.
    """
    available = False

    def render(self):
        if self.available:
            return self.index()

        return u""

    def update(self):
        lt = getToolByName(self.context, 'portal_languages')
        supported = lt.getSupportedLanguages()
        self.available = len(supported) <= 1


class addFormIsATranslationViewlet(ViewletBase):
    """ Notice the user that this add form is a translation
    """
    available = False

    def language(self):
        return self.lang

    def origin(self):
        return self.origin

    def render(self):
        if self.available:
            return self.index()
        return u""

    def update(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if ITranslatable.providedBy(self.context):
            self.lang = ILanguage(self.context).get_language()
        else:
            self.lang = 'NaN'
        if 'tg' in session.keys():
            tg = session['tg']
            self.available = True
            ptool = getToolByName(self.context, 'portal_catalog')
            query = {'TranslationGroup': tg, 'Language': 'all'}
            results = ptool.searchResults(query)
            self.origin = results


class addFormATIsATranslationViewlet(ViewletBase):
    """ Notice the user that this add form is a translation
    """
    available = False

    def language(self):
        return self.lang

    def origin(self):
        return self.origin

    def render(self):
        if self.available:
            return self.index()
        return u""

    def update(self):
        """ It's only for AT on factory so we check """
        if self.context.portal_factory.isTemporary(self.context):
            sdm = self.context.session_data_manager
            session = sdm.getSessionData(create=True)
            if ITranslatable.providedBy(self.context):
                self.lang = ILanguage(self.context).get_language()
            else:
                self.lang = 'NaN'
            if 'tg' in session.keys():
                tg = session['tg']
                self.available = True
                ptool = getToolByName(self.context, 'portal_catalog')
                query = {'TranslationGroup': tg, 'Language': 'all'}
                results = ptool.searchResults(query)
                self.origin = results