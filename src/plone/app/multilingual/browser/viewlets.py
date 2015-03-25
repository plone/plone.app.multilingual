# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.memoize import ram
from urllib import quote_plus
from zope.component import getUtility


def _cache_until_catalog_change(fun, self):
    catalog = getToolByName(self.context, 'portal_catalog')
    key = '{0}{1}{2}'
    key = key.format(
        fun.__name__,
        catalog.getCounter(),
        '/'.join(self.context.getPhysicalPath())
    )
    return key


class OneLanguageConfiguredNoticeViewlet(ViewletBase):
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


class AddFormIsATranslationViewlet(ViewletBase):
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

    def returnURL(self):
        # Get translation info for getting the translation source
        translation_info = getattr(self.request, 'translation_info', {})
        translation_group = translation_info.get('tg')
        source_language = translation_info.get('source_language')

        if not (translation_group or source_language):
            return ''

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(Language=source_language,
                         TranslationGroup=translation_group)
        if len(brains) != 1:
            return ''
        source = brains[0].getObject()

        # Get the factory
        types_tool = getToolByName(source, 'portal_types')

        # Note: we don't check 'allowed' or 'available' here,
        # because these are slow. We assume the 'allowedTypes'
        # list has already performed the necessary calculations
        actions = types_tool.listActionInfos(
            object=self.context,
            check_permissions=False,
            check_condition=False,
            category='folder/add',
        )

        addActionsById = dict([(a['id'], a) for a in actions])

        typeId = source.portal_type

        addAction = addActionsById.get(typeId, None)
        if addAction is None:
            url = None
        else:
            url = addAction['url']
        if not url:
            url = '%s/createObject?type_name=%s' % (
                source.absolute_url(),
                quote_plus(typeId)
            )
        return url

    def update(self):
        try:
            tg = self.request.translation_info['tg']
        except AttributeError:
            return
        self.available = True
        if ITranslatable.providedBy(self.context):
            self.lang = ILanguage(self.context).get_language()
        else:
            self.lang = 'NaN'
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'TranslationGroup': tg, 'Language': 'all'}
        self.origin = catalog.searchResults(query)


class AddFormATIsATranslationViewlet(AddFormIsATranslationViewlet):
    # XXX move this class to archetypes multilingual!
    # btw., it is not used in here.
    """ Notice the user that this AT add form is a translation
    """

    def update(self):
        """ It's only for AT on factory so we check """
        factory = getToolByName(self.context, 'portal_factory', None)
        if factory is None or not factory.isTemporary(self.context):
            return
        super(AddFormIsATranslationViewlet, self).update()


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

        plone_site = getUtility(IPloneSiteRoot)
        portal_path = '/'.join(plone_site.getPhysicalPath())
        portal_path_len = len(portal_path)
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
