# -*- coding: utf-8 -*-
import unittest2 as unittest

from zope.interface import implements
from zope.component import getUtility

import transaction
from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from plone.app.i18n.locales.browser.selector import LanguageSelector

from plone.multilingual.interfaces import ITranslatable
from plone.multilingual.interfaces import ITG
from plone.app.multilingual.browser.controlpanel import IMultiLanguagePolicies
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.browser.selector import LanguageSelectorViewlet
from plone.app.multilingual.browser.selector import NOT_TRANSLATED_YET_TEMPLATE
from plone.app.multilingual.browser.selector import getPostPath
from plone.app.multilingual.browser.selector import addQuery
from plone.app.multilingual.browser.helper_views import selector_view
from plone.app.multilingual.testing import (
    PLONEAPPMULTILINGUAL_INTEGRATION_TESTING,
    PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
)
from plone.app.multilingual.tests.utils import makeContent
from plone.app.multilingual.tests.utils import makeTranslation


class EvilObject(object):

    def __str__(self):
        raise UnicodeError

    def __unicode__(self):
        raise UnicodeError


SELECTOR_VIEW_TEMPLATE = ('%(url)s/@@multilingual-selector'
                          '/%(tg)s/%(lang)s%(query)s')


class TestLanguageSelectorBasics(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal.error_log._ignored_exceptions = ()
        self.request = self.layer['request']
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.portal_url = self.portal.absolute_url()
        self.language_tool = getToolByName(self.portal, 'portal_languages')
        self.language_tool.addSupportedLanguage('ca')
        self.language_tool.addSupportedLanguage('es')

        self.selector = LanguageSelectorViewlet(self.portal,
                            self.request, None, None)

    def test_available(self):
        self.selector.update()
        self.assertEquals(self.selector.available(), True)

    def test_available_no_tool(self):
        self.selector.update()
        self.selector.tool = None
        self.assertEquals(self.selector.available(), False)

    def test_original_selector_data_not_modified_by_viewlet(self):
        self.selector.update()
        multilingual_lang_info = self.selector.languages()
        original_selector = LanguageSelector(self.portal,
                            self.request, None, None)
        original_selector.update()
        original_lang_info = original_selector.languages()

        self.assertNotEquals(original_lang_info, multilingual_lang_info)

    def assertFullyTranslatedPages(self):
        doc1 = makeContent(self.portal, 'Document', id='doc1')
        doc1.setLanguage('en')
        doc1_tg = ITG(doc1)
        doc1_ca = makeTranslation(doc1, 'ca')
        doc1_ca.edit(title="Foo", language='ca')
        doc1_es = makeTranslation(doc1, 'es')
        doc1_es.edit(title="Foo", language='es')

        self.selector = LanguageSelectorViewlet(doc1,
                            self.request, None, None)

        self.selector.update()
        selector_languages = self.selector.languages()
        self.assertEqual(selector_languages, [
            {
                'code': u'en',
                u'name': u'English',
                'url': SELECTOR_VIEW_TEMPLATE % {
                    'url': doc1.absolute_url(),
                    'tg': doc1_tg,
                    'lang': 'en',
                    'query': '?set_language=en'
                },
                'selected': True,
                u'flag': u'/++resource++country-flags/gb.gif',
                'translated': True,
                u'native': u'English'
            },
            {
                'code': u'ca',
                u'name': u'Catalan',
                'url': SELECTOR_VIEW_TEMPLATE % {
                    'url': doc1.absolute_url(),
                    'tg': doc1_tg,
                    'lang': 'ca',
                    'query': '?set_language=ca'
                },
                'selected': False,
                u'flag': u'/++resource++language-flags/ca.gif',
                'translated': True,
                u'native': u'Catal\xe0'
            },
            {
                'code': u'es',
                u'name': u'Spanish',
                'url': SELECTOR_VIEW_TEMPLATE % {
                    'url': doc1.absolute_url(),
                    'tg': doc1_tg,
                    'lang': 'es',
                    'query': '?set_language=es'
                },
                'selected': False,
                u'flag': u'/++resource++country-flags/es.gif',
                'translated': True,
                u'native': u'Espa\xf1ol'
            }
        ])

        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url,
            doc1.absolute_url()+'?set_language=en'
        )
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])
        self.assertEqual(
            self.browser.url,
            doc1_ca.absolute_url()+'?set_language=ca'
        )
        self.assertIn(
            u"Inici".encode("utf-8"),
            self.browser.contents
        )
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            doc1_es.absolute_url()+'?set_language=es'
        )
        self.assertIn(
            u"Usted está aquí".encode("utf-8"),
            self.browser.contents
        )

    def test_languages_full_translated_by_closest(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'

        self.assertFullyTranslatedPages()

    def test_languages_full_translated_by_dialog(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'

        self.assertFullyTranslatedPages()

    def setUpPAMFolders(self):
        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)
        transaction.commit()
        return workflowTool

    def setUpPartiallyTranslatedContent(self):
        wftool = self.setUpPAMFolders()
        folder = makeContent(self.portal.en, 'Folder', id='folder')
        folder.setLanguage('en')
        wftool.doActionFor(folder, 'publish')
        document = makeContent(folder, 'Document', id='document')
        document.setLanguage('en')
        wftool.doActionFor(document, 'publish')
        folder_ca = makeTranslation(folder, 'ca')
        folder_ca.edit(title="Foo", language='ca')
        wftool.doActionFor(folder_ca, 'publish')
        transaction.commit()
        return wftool

    def setUpFullyTranslatedContent(self):
        wftool = self.setUpPartiallyTranslatedContent()
        document_ca = makeTranslation(self.portal.en.folder.document, 'ca')
        document_ca.edit(title="Foo", language='ca')
        wftool.doActionFor(document_ca, 'publish')
        folder_es = makeTranslation(self.portal.en.folder, 'es')
        folder_es.edit(title="Foo", language='es')
        wftool.doActionFor(folder_es, 'publish')
        document_es = makeTranslation(self.portal.en.folder.document, 'es')
        document_es.edit(title="Foo", language='es')
        wftool.doActionFor(document_es, 'publish')
        transaction.commit()
        return wftool

    def test_languages_untranslated_by_closest(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'
        self.setUpPAMFolders()

        document = makeContent(self.portal.ca, 'Document', id='untranslated')
        document.setLanguage('ca')
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(document, 'publish')
        transaction.commit()

        view = selector_view(document, self.layer['request'])
        view.lang = 'es'
        url = view.getClosestDestination()
        self.assertEqual(url, self.portal.es.absolute_url())

        view.lang = 'it'
        url = view.getClosestDestination()
        self.assertEqual(url, self.portal.absolute_url())

    def test_languages_partially_translated_by_closest(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'
        self.setUpPartiallyTranslatedContent()

        selector = LanguageSelectorViewlet(
            self.portal.en.folder.document,
            self.request,
            None,
            None
        )

        selector.update()
        selector_languages = selector.languages()
        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.en.folder.document.absolute_url()+'?set_language=en'
        )
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.ca.folder.absolute_url()+'?set_language=ca'
        )
        self.assertIn(
            u"Inici".encode("utf-8"),
            self.browser.contents
        )
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.es.absolute_url()+'?set_language=es'
        )
        self.assertIn(
            u"Usted está aquí".encode("utf-8"),
            self.browser.contents
        )

    def test_languages_partially_translated_by_dialog(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'

        self.setUpPartiallyTranslatedContent()

        selector = LanguageSelectorViewlet(
            self.portal.en.folder.document,
            self.request,
            None,
            None
        )

        selector.update()
        selector_languages = selector.languages()
        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.en.folder.document.absolute_url()+'?set_language=en'
        )
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.en.folder.document.absolute_url() + \
                NOT_TRANSLATED_YET_TEMPLATE + '?set_language=ca'
        )
        self.assertIn(
            u"Inici".encode("utf-8"),
            self.browser.contents
        )
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.en.folder.document.absolute_url() + \
                NOT_TRANSLATED_YET_TEMPLATE + '?set_language=es'
        )
        self.assertIn(
            u"Usted está aquí".encode("utf-8"),
            self.browser.contents
        )

    def test_site_root(self):
        for policy in ['closest', 'dialog']:
            self.registry = getUtility(IRegistry)
            self.settings = self.registry.forInterface(IMultiLanguagePolicies)
            self.settings.selector_lookup_translations_policy = policy
            transaction.commit()
            self.selector = LanguageSelectorViewlet(
                self.portal,
                self.request,
                None,
                None
            )
            self.selector.update()
            selector_languages = self.selector.languages()
            self.browser.open(selector_languages[0]['url'])
            self.assertEqual(
                self.browser.url,
                self.portal.absolute_url()+'?set_language=en'
            )
            self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
            self.browser.open(selector_languages[1]['url'])
            self.assertEqual(
                self.browser.url,
                self.portal.absolute_url()+'?set_language=ca'
            )
            self.assertIn(
                u"Inici".encode("utf-8"),
                self.browser.contents
            )
            self.browser.open(selector_languages[2]['url'])
            self.assertEqual(
                self.browser.url,
                self.portal.absolute_url()+'?set_language=es'
            )
            self.assertIn(
                u"Usted está aquí".encode("utf-8"),
                self.browser.contents
            )

    def assertRootFolders(self):
        self.selector = LanguageSelectorViewlet(self.portal.en,
                                                self.request, None, None)
        tg = ITG(self.portal.en)

        self.selector.update()
        selector_languages = self.selector.languages()
        self.assertEqual(selector_languages, [
            {
                'code': u'en',
                u'name': u'English',
                'url': SELECTOR_VIEW_TEMPLATE % {
                    'url': self.portal.en.absolute_url(),
                    'tg': tg,
                    'lang': 'en',
                    'query': '?set_language=en'
                },
                'selected': True,
                u'flag': u'/++resource++country-flags/gb.gif',
                'translated': True,
                u'native': u'English'},
            {
                'code': u'ca',
                u'name': u'Catalan',
                'url': SELECTOR_VIEW_TEMPLATE % {
                    'url': self.portal.en.absolute_url(),
                    'tg': tg,
                    'lang': 'ca',
                    'query': '?set_language=ca'
                },
                'selected': False,
                u'flag': u'/++resource++language-flags/ca.gif',
                'translated': True,
                u'native': u'Catal\xe0'
            },
            {
                'code': u'es',
                u'name': u'Spanish',
                'url': SELECTOR_VIEW_TEMPLATE % {
                    'url': self.portal.en.absolute_url(),
                    'tg': tg,
                    'lang': 'es',
                    'query': '?set_language=es'
                },
                'selected': False,
                u'flag': u'/++resource++country-flags/es.gif',
                'translated': True,
                u'native': u'Espa\xf1ol'
            }
        ])

        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.en.absolute_url()+'?set_language=en'
        )
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.ca.absolute_url()+'?set_language=ca'
        )
        self.assertIn(
            u"Inici".encode("utf-8"),
            self.browser.contents
        )
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.es.absolute_url()+'?set_language=es'
        )
        self.assertIn(
            u"Usted está aquí".encode("utf-8"),
            self.browser.contents
        )

    def test_languages_root_folders_by_dialog(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'

        self.setUpPAMFolders()

        self.assertRootFolders()

    def test_languages_root_folders_by_closest(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'

        self.setUpPAMFolders()

        self.assertRootFolders()

    def test_languages_preserve_view(self):
        self.setUpPartiallyTranslatedContent()
        self.registry = getUtility(IRegistry)
        self.request['PATH_INFO'] = '/plone/en/folder/@@search'
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'
        transaction.commit()
        selector = LanguageSelectorViewlet(
            self.portal.en.folder,
            self.request,
            None,
            None
        )
        selector.update()
        selector_languages = selector.languages()
        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.en.folder.absolute_url()+'/@@search?set_language=en'
        )
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.ca.folder.absolute_url()+'/@@search?set_language=ca'
        )
        self.assertIn(
            u"Inici".encode("utf-8"),
            self.browser.contents
        )
        # Here @@search isn't preserved because we've gone up a level
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.es.absolute_url()+'?set_language=es'
        )
        self.assertIn(
            u"Usted está aquí".encode("utf-8"),
            self.browser.contents
        )

        # Shouldn't do for the not-translated-yet thingie when dialog is on
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'
        transaction.commit()
        selector = LanguageSelectorViewlet(
            self.portal.en.folder,
            self.request,
            None,
            None
        )
        selector.update()
        selector_languages = selector.languages()
        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.en.folder.absolute_url()+'/@@search?set_language=en'
        )
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.ca.folder.absolute_url()+'/@@search?set_language=ca'
        )
        self.assertIn(
            u"Inici".encode("utf-8"),
            self.browser.contents
        )
        # Here @@search isn't preserved because we've got the dialog
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.en.folder.absolute_url() + \
                NOT_TRANSLATED_YET_TEMPLATE + '?set_language=es'
        )
        self.assertIn(
            u"Usted está aquí".encode("utf-8"),
            self.browser.contents
        )

    def test_languages_preserve_query(self):
        self.setUpPartiallyTranslatedContent()
        self.registry = getUtility(IRegistry)
        self.request['PATH_INFO'] = '/plone/en/folder/@@search'
        self.request.form['uni'] = u'pres\xd8rved'
        self.request.form['int'] = '1'
        untraslated_url = {
            'closest': self.portal.es.absolute_url() + \
                '?int=1&uni=pres%C3%98rved&set_language=es',
            'dialog': self.portal.en.folder.absolute_url() + \
                NOT_TRANSLATED_YET_TEMPLATE + \
                '?int=1&uni=pres%C3%98rved&set_language=es'
        }
        for policy in ['closest', 'dialog']:
            self.settings = self.registry.forInterface(IMultiLanguagePolicies)
            self.settings.selector_lookup_translations_policy = policy
            transaction.commit()
            selector = LanguageSelectorViewlet(
                self.portal.en.folder,
                self.request,
                None,
                None
            )
            selector.update()
            selector_languages = selector.languages()
            self.browser.open(selector_languages[0]['url'])
            self.assertEqual(
                self.browser.url,
                self.portal.en.folder.absolute_url() + \
                    '/@@search?int=1&uni=pres%C3%98rved&set_language=en'
            )
            self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
            self.browser.open(selector_languages[1]['url'])
            self.assertEqual(
                self.browser.url,
                self.portal.ca.folder.absolute_url() + \
                    '/@@search?int=1&uni=pres%C3%98rved&set_language=ca'
            )
            self.assertIn(
                u"Inici".encode("utf-8"),
                self.browser.contents
            )
            # Here @@search isn't preserved because we've got the dialog
            self.browser.open(selector_languages[2]['url'])
            self.assertEqual(
                self.browser.url,
                untraslated_url[policy]
            )
            self.assertIn(
                u"Usted está aquí".encode("utf-8"),
                self.browser.contents
            )

    # XXX: this seems to me like a demented use case.
    # If you put the VH _after_ the jail,
    # for example mapping mysite.cat to /plone/ca and mysite.com to /plone/en,
    # then I can't possibly make the whole language switcher work
    # because I have no idea to which domain I should reroute the request
    # (that information is sitting in nginx|apache config,
    # therefore I cannot conceivably gather it).
    # Therefore, while PAM knows which is the translation object,
    # it can't figure out its URL correctly.
    # At most, it can leverage acquisition so that,
    # if you switch from mysite.com/my/object to catalan,
    # it goes to mysite.com/ca/my/object
    # (which has a path of /plone/en/my/object/ca/my/object),
    # but that is too fragile and sucky for me to take care of supporting it.
    #
    # The original test case is below: if you wrote it,
    # I'll be glad to hear which was the use case
    # and what is your idea to make it work.
    #
    # def test_languages_vhr(self):
    #     registry = getUtility(IRegistry)
    #     settings = registry.forInterface(IMultiLanguagePolicies)
    #     settings.selector_lookup_translations_policy = 'dialog'

    #     from Products.CMFCore.interfaces import ISiteRoot
    #     from zope.interface import alsoProvides
    #     provideAdapter(DummyState, adapts=(Dummy, DummyRequest),
    #                    provides=Interface, name="plone_context_state")
    #     context = Dummy()
    #     context.__parent__ = self.portal
    #     context.portal_url = Dummy()
    #     container = Dummy()
    #     context = context.__of__(container)
    #     alsoProvides(container, ISiteRoot)
    #     request = DummyRequest()
    #     import ipdb;ipdb.set_trace()
    #     selector = LanguageSelectorViewlet(context, request, None, None)
    #     context.physicalpath = ['', 'fake', 'path']
    #     vbase = '/VirtualHostBase/http/127.0.0.1/'
    #     request.PATH_INFO = vbase + 'fake/path/VirtualHostRoot/to/object'
    #     request.form['uni'] = u'pres\xd8rved'
    #     request.form['int'] = '1'
    #     notify(ObjectCreatedEvent(context))
    #     IUUID(context, None)
    #     selector.update()
    #     selector.tool = MockLanguageTool()
    #     base = 'object_url/to/object?int=1&uni='
    #     expected = [
    #         {'code': 'nl',
    #          'translated': True,
    #          'selected': False,
    #          'url': base + 'pres%C3%98rved&set_language=nl'},
    #         {'code': 'en',
    #          'translated': True,
    #          'selected': True,
    #          'url': base + 'pres%C3%98rved&set_language=en'},
    #         {'code': 'no',
    #          'translated': False,
    #          'selected': False,
    #          'url': base + 'pres%C3%98rved&set_language=no'}]
    #     self.assertEqual(selector.languages(), expected)


class TestLanguageSelectorPostPath(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = makeContent(self.portal, 'Folder', id='folder')
        self.document = makeContent(self.folder, 'Document', id='document')
        self.request = self.layer['request']

    def test_findpath(self):
        self.request['PATH_INFO'] = '/plone/folder/document/whatever'
        self.assertEqual(
            getPostPath(self.document, self.request),
            '/whatever'
        )

    def test_findpath_match(self):
        self.request['PATH_INFO'] = '/plone/folder/document'
        self.assertEqual(
            getPostPath(self.document, self.request),
            ''
        )

    def test_findpath_match_slash(self):
        self.request['PATH_INFO'] = '/plone/folder/document/'
        self.assertEqual(
            getPostPath(self.document, self.request),
            ''
        )

    def test_findpath_template(self):
        self.request['PATH_INFO'] = ('/plone/folder/document/'
                                     'whatever/foo/atct_edit')
        self.assertEqual(
            getPostPath(self.document, self.request),
            '/whatever/foo/atct_edit'
        )

    def test_findpath_view(self):
        self.request['PATH_INFO'] = '/plone/folder/document/@@search'
        self.assertEqual(
            getPostPath(self.document, self.request),
            '/@@search'
        )

    def test_findpath_vhr(self):
        self.request['PATH_INFO'] = ('/VirtualHostBase/http/127.0.0.1'
                                     '/plone/folder/document/'
                                     'VirtualHostRoot/whatever')
        self.assertEqual(
            getPostPath(self.document, self.request),
            '/whatever'
        )

    def test_findpath_vh_marker(self):
        self.request['PATH_INFO'] = ('/VirtualHostBase/http/127.0.0.1'
                                     '/plone/folder/document/'
                                     'VirtualHostRoot/_vh_foo/whatever')
        self.assertEqual(
            getPostPath(self.document, self.request),
            '/whatever'
        )

    def test_findpath_vhr_and_traverser(self):
        self.request['PATH_INFO'] = ('/VirtualHostBase/http/127.0.0.1'
                                     '/plone/folder/document/++theme++foo/'
                                     'VirtualHostRoot/whatever')
        self.assertEqual(
            getPostPath(self.document, self.request),
            '/whatever'
        )


class TestLanguageSelectorAddQuery(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']
        self.url = '/foo/bar/'

    def test_formvariables(self):
        self.request.form['one'] = 1
        self.request.form['two'] = 2
        self.assertEqual(
            addQuery(self.request, self.url),
            self.url+'?two:int=2&one:int=1'
        )

    def test_formvariables_sequences(self):
        self.request.form['one'] = ('a', )
        self.request.form['two'] = ['b', 2]
        self.assertEqual(
            addQuery(self.request, self.url),
            self.url+'?two:list=b&two:int:list=2&one=%28%27a%27%2C%29'
        )

    def test_formvariables_unicode(self):
        self.request.form['one'] = u'Før'
        self.request.form['two'] = u'foo'
        self.assertEqual(
            addQuery(self.request, self.url),
            self.url+'?two=foo&one=F%C3%B8r'
        )

    def test_formvariables_utf8(self):
        self.request.form['one'] = u'Før'.encode("utf-8")
        self.request.form['two'] = u'foo'
        self.assertEqual(
            addQuery(self.request, self.url),
            self.url+'?two=foo&one=F%C3%B8r'
        )

    def test_formvariables_object(self):
        self.request.form['one'] = '1'
        self.request.form['two'] = EvilObject()
        self.assertEqual(
            addQuery(self.request, self.url),
            self.url
        )

    def test_formvariables_exclude(self):
        self.request.form['one'] = 1
        self.request.form['two'] = 2
        self.assertEqual(
            addQuery(self.request, self.url, exclude=('two',)),
            self.url+'?one:int=1'
        )

    def test_formvariables_extras(self):
        self.request.form['one'] = 1
        self.request.form['two'] = 2
        self.assertEqual(
            addQuery(self.request, self.url, three=3),
            self.url+'?one:int=1&three:int=3&two:int=2'
        )
