from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.memoize import ram


def _cache_until_catalog_change(fun, self):
    key = StringIO()
    catalog = getToolByName(self.context, 'portal_catalog')

    print >> key, fun.__name__
    print >> key, catalog.getCounter()
    print >> key, '/'.join(self.context.getPhysicalPath())

    return key.getvalue()


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


class AlternateLanguagesViewlet(ViewletBase):
    """ Notice search engines about alternates languages of current
        content item
    """

    alternatives = []

    @ram.cache(_cache_until_catalog_change)
    def get_alternate_languages(self):
        """Cache relative urls only. If we have multilingual sites
           and multi domain site caching absolute urls will result in
           very inefficient caching. Build absolute url in template.
        """
        tm = ITranslationManager(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(TranslationGroup=tm.query_canonical())

        portal_path_len = len(
            '/'.join(self.portal_state.portal().getPhysicalPath()))

        alternates = []
        for item in results:
            path_len = portal_path_len + len('{0:s}/'.format(item.Language))
            url = item.getURL(relative=1)[path_len:]
            alternates.append({
                'lang': item.Language,
                'url': url.strip('/'),
            })

        return alternates

    def update(self):
        super(AlternateLanguagesViewlet, self).update()
        self.alternates = self.get_alternate_languages()

    @property
    def available(self):
        return len(self.alternates) > 1

    def render(self):
        if self.available:
            return self.index()
        return u""
