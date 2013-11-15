# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope.event import notify
from zope.component import getUtility
import transaction
from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from zope.lifecycleevent import ObjectModifiedEvent
from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.dexterity.utils import createContentInContainer

from plone.testing.z2 import Browser
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual import api
from plone.app.multilingual.browser.controlpanel import IMultiLanguagePolicies
from plone.app.multilingual.browser.selector import LanguageSelectorViewlet
from plone.app.multilingual.browser.selector import NOT_TRANSLATED_YET_TEMPLATE
from plone.app.multilingual.browser.selector import getPostPath
from plone.app.multilingual.browser.selector import addQuery
from plone.app.multilingual.browser.helper_views import selector_view
from plone.app.multilingual.testing import PAM_FUNCTIONAL_TESTING
from plone.app.multilingual.testing import PAM_INTEGRATION_TESTING


class EvilObject(object):

    def __str__(self):
        raise UnicodeError

    def __unicode__(self):
        raise UnicodeError


SELECTOR_VIEW_TEMPLATE =\
    '%(url)s/@@multilingual-selector/%(tg)s/%(lang)s%(query)s'


class TestLanguageSelectorBasics(unittest.TestCase):

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        # Set test variables
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.request = self.layer['request']

        # Setup testbrowser
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

    def test_selector_viewlet_is_available(self):
        selector_viewlet = \
            LanguageSelectorViewlet(self.portal, self.request, None, None)
        selector_viewlet.update()
        self.assertTrue(selector_viewlet.available())

    def test_selector_viewlet_is_available_but_tool_is_not(self):
        selector_viewlet = \
            LanguageSelectorViewlet(self.portal, self.request, None, None)
        selector_viewlet.update()
        selector_viewlet.tool = None
        self.assertFalse(selector_viewlet.available())

    def test_selector_data_not_modified_by_viewlet(self):
        selector_viewlet = \
            LanguageSelectorViewlet(self.portal, self.request, None, None)
        selector_viewlet.update()
        selector_viewlet_languages = selector_viewlet.languages()

        selector_adapter = \
            LanguageSelector(self.portal, self.request, None, None)
        selector_adapter.update()
        selector_adapter_languages = selector_adapter.languages()

        self.assertNotEquals(selector_adapter_languages,
                             selector_viewlet_languages)

    def assertFullyTranslatedPages(self):
        a = createContentInContainer(
            self.portal['en'], 'Document', title=u"Test document")

        a_ca = api.translate(a, 'ca')
        a_ca.setTitle(u"Test Document (CA)")

        a_es = api.translate(a, 'es')
        a_es.setTitle(u"Test Document (ES)")

        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.doActionFor(a, 'publish')
        wftool.doActionFor(a_ca, 'publish')
        wftool.doActionFor(a_es, 'publish')

        notify(ObjectModifiedEvent(a))
        notify(ObjectModifiedEvent(a_ca))
        notify(ObjectModifiedEvent(a_es))

        selector_viewlet =\
            LanguageSelectorViewlet(a, self.request, None, None)
        selector_viewlet.update()
        selector_viewlet_languages = selector_viewlet.languages()

        self.assertEqual(selector_viewlet_languages, [{
            'code': u'en',
            u'flag': u'/++resource++country-flags/gb.gif',
            u'name': u'English',
            u'native': u'English',
            'url': SELECTOR_VIEW_TEMPLATE % {
                'url': self.portal_url,
                'tg': ITG(a),
                'lang': 'en',
                'query': '?set_language=en'
            },
            'selected': True,
            'translated': True,
        }, {
            'code': u'ca',
            u'flag': u'/++resource++language-flags/ca.gif',
            u'name': u'Catalan',
            u'native': u'Catal\xe0',
            'url': SELECTOR_VIEW_TEMPLATE % {
                'url': self.portal_url,
                'tg': ITG(a),
                'lang': 'ca',
                'query': '?set_language=ca'
            },
            'selected': False,
            'translated': True,
        }, {
            'code': u'es',
            u'flag': u'/++resource++country-flags/es.gif',
            u'name': u'Spanish',
            u'native': u'Espa\xf1ol',
            'url': SELECTOR_VIEW_TEMPLATE % {
                'url': self.portal_url,
                'tg': ITG(a),
                'lang': 'es',
                'query': '?set_language=es'
            },
            'selected': False,
            'translated': True,
        }])

        transaction.commit()

        self.browser.open(selector_viewlet_languages[0]['url'])
        self.assertEqual(self.browser.url,
                         a.absolute_url() + '?set_language=en')
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")

        self.browser.open(selector_viewlet_languages[1]['url'])
        self.assertEqual(self.browser.url,
                         a_ca.absolute_url() + '?set_language=ca')

        self.assertIn(u'lang="ca"'.encode("utf-8"), self.browser.contents)

        self.browser.open(selector_viewlet_languages[2]['url'])
        self.assertEqual(self.browser.url,
                         a_es.absolute_url() + '?set_language=es')
        self.assertIn(u'lang="es"'.encode("utf-8"), self.browser.contents)

    def test_languages_fully_translated_by_closest(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'

        self.assertFullyTranslatedPages()

    def test_languages_fully_translated_by_dialog(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'

        self.assertFullyTranslatedPages()

    def setUpPartiallyTranslatedContent(self):
        wftool = getToolByName(self.portal, 'portal_workflow')

        f_en = createContentInContainer(
            self.portal['en'], 'Folder', title=u"Test folder")
        wftool.doActionFor(f_en, 'publish')

        a_en = createContentInContainer(
            self.portal['en']['test-folder'], 'Document',
            title=u"Test document")
        wftool.doActionFor(a_en, 'publish')

        f_ca = api.translate(f_en, 'ca')
        f_ca.setTitle(u"Test folder CA")
        wftool.doActionFor(f_ca, 'publish')

        transaction.commit()

    def setUpFullyTranslatedContent(self):
        wftool = getToolByName(self.portal, 'portal_workflow')

        self.setUpPartiallyTranslatedContent()

        a_ca = api.translate(
            self.portal['en']['test-folder']['test-document'], 'ca')
        a_ca.setTitle(u"Test document CA")
        wftool.doActionFor(a_ca, 'publish')

        f_es = api.translate(
            self.portal['en']['test-folder'], 'es')
        f_es.setTitle(u"Test folder ES")
        wftool.doActionFor(f_es, 'publish')

        a_es = api.translate(
            self.portal['en']['test-folder']['test-document'], 'es')
        a_es.setTitle(u"Test document ES")
        wftool.doActionFor(a_es, 'publish')

        transaction.commit()

    def test_languages_untranslated_by_closest(self):
        # Define selector policy
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'

        document = createContentInContainer(
            self.portal['ca'], 'Document', title=u"Test document")
        document.setLanguage('ca')
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(document, 'publish')
        transaction.commit()
        view = selector_view(document, self.layer['request'])
        view.lang = 'es'
        view.tg = ITG(document)
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

        a_en = self.portal['en']['test-folder']['test-document']
        selector = LanguageSelectorViewlet(a_en, self.request, None, None)

        selector.update()
        selector_languages = selector.languages()
        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url, a_en.absolute_url()+'?set_language=en')
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])

        f_ca = self.portal['ca']['test-folder']
        self.assertEqual(
            self.browser.url, f_ca.absolute_url()+'?set_language=ca'
        )
        self.assertIn(
            u'lang="ca"'.encode("utf-8"),
            self.browser.contents
        )
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.es.absolute_url()+'?set_language=es'
        )
        self.assertIn(
            u'lang="es"'.encode("utf-8"),
            self.browser.contents
        )

    def test_languages_partially_translated_by_dialog(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'

        self.setUpPartiallyTranslatedContent()

        a_en = self.portal['en']['test-folder']['test-document']
        selector = LanguageSelectorViewlet(a_en, self.request, None, None)

        selector.update()
        selector_languages = selector.languages()
        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url, a_en.absolute_url()+'?set_language=en')

        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        tgid = selector_languages[1]['url'].split('/')[-2]
        self.browser.open(selector_languages[1]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.absolute_url() + \
                NOT_TRANSLATED_YET_TEMPLATE + '/' + tgid + '?set_language=ca'
        )
        self.assertIn(
            u'lang="ca"'.encode("utf-8"),
            self.browser.contents
        )
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.absolute_url() + \
                NOT_TRANSLATED_YET_TEMPLATE + '/' + tgid + '?set_language=es'
        )
        self.assertIn(
            u'lang="es"'.encode("utf-8"),
            self.browser.contents
        )

    def testSiteRoot(self):
        for policy in ['closest', 'dialog']:
            self.registry = getUtility(IRegistry)
            self.settings = self.registry.forInterface(IMultiLanguagePolicies)
            self.settings.selector_lookup_translations_policy = policy
            transaction.commit()
            self.selector_viewlet = LanguageSelectorViewlet(
                self.portal, self.request, None, None)
            self.selector_viewlet.update()
            selector_languages = self.selector_viewlet.languages()
            self.browser.open(selector_languages[0]['url'])
            #self.assertEqual(
            #    self.browser.url,
            #    self.portal.absolute_url()+'?set_language=en'
            #)
            self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
            self.assertEqual(
                selector_languages[1]['url'],
                self.portal.absolute_url()+'/@@multilingual-selector/notg/ca?set_language=ca'
            )
            self.browser.open(selector_languages[1]['url'])
            self.assertIn(
                u'lang="ca"'.encode("utf-8"),
                self.browser.contents
            )
            self.browser.open(selector_languages[2]['url'])
            self.assertEqual(
                selector_languages[2]['url'],
                self.portal.absolute_url()+'/@@multilingual-selector/notg/es?set_language=es'
            )
            self.assertIn(
                u'lang="es"'.encode("utf-8"),
                self.browser.contents
            )

    def assertRootFolders(self):
        self.selector_viewlet = LanguageSelectorViewlet(
                self.portal['en'], self.request, None, None)
        tg = ITG(self.portal['en'])

        self.selector_viewlet.update()
        selector_languages = self.selector_viewlet.languages()
        self.assertEqual(selector_languages, [{
            'code': u'en',
            u'flag': u'/++resource++country-flags/gb.gif',
            u'name': u'English',
            u'native': u'English',
            'url': SELECTOR_VIEW_TEMPLATE % {
                'url': self.portal.absolute_url(),
                'tg': tg,
                'lang': 'en',
                'query': '?set_language=en'
            },
            'selected': True,
            'translated': True,
        }, {
            'code': u'ca',
            u'flag': u'/++resource++language-flags/ca.gif',
            u'name': u'Catalan',
            u'native': u'Catal\xe0',
            'url': SELECTOR_VIEW_TEMPLATE % {
                'url': self.portal.absolute_url(),
                'tg': tg,
                'lang': 'ca',
                'query': '?set_language=ca'
            },
            'selected': False,
            'translated': True,
        }, {
            'code': u'es',
            u'flag': u'/++resource++country-flags/es.gif',
            u'name': u'Spanish',
            u'native': u'Espa\xf1ol',
            'url': SELECTOR_VIEW_TEMPLATE % {
                'url': self.portal.absolute_url(),
                'tg': tg,
                'lang': 'es',
                'query': '?set_language=es'
            },
            'selected': False,
            'translated': True,
        }])

        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal['en'].absolute_url()+'?set_language=en'
        )
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.ca.absolute_url()+'?set_language=ca'
        )
        self.assertIn(
            u'lang="ca"'.encode("utf-8"),
            self.browser.contents
        )
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.es.absolute_url()+'?set_language=es'
        )
        self.assertIn(
            u'lang="es"'.encode("utf-8"),
            self.browser.contents
        )

    def test_languages_root_folders_by_dialog(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'

        self.assertRootFolders()

    def test_languages_root_folders_by_closest(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'

        self.assertRootFolders()

    def test_languages_preserve_view(self):
        self.setUpPartiallyTranslatedContent()
        self.registry = getUtility(IRegistry)
        self.request['PATH_INFO'] = '/plone/en/test-folder/@@search'
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'
        transaction.commit()

        f_en = self.portal['en']['test-folder']
        selector = LanguageSelectorViewlet(f_en, self.request, None, None)
        selector.update()
        selector_languages = selector.languages()
        self.browser.open(selector_languages[0]['url'])
        self.assertEqual(
            self.browser.url,
            f_en.absolute_url()+'/@@search?set_language=en'
        )

        f_ca = self.portal['ca']['test-folder']
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])
        self.assertEqual(
            self.browser.url,
            f_ca.absolute_url()+'/@@search?set_language=ca'
        )
        self.assertIn(
            u'lang="ca"'.encode("utf-8"),
            self.browser.contents
        )
        # Here @@search isn't preserved because we've gone up a level
        self.browser.open(selector_languages[2]['url'])
        self.assertEqual(
            self.browser.url,
            self.portal.es.absolute_url()+'?set_language=es'
        )
        self.assertIn(
            u'lang="es"'.encode("utf-8"),
            self.browser.contents
        )

        # Shouldn't do for the not-translated-yet thingie when dialog is on
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'
        transaction.commit()
        f_en = self.portal['en']['test-folder']
        selector = LanguageSelectorViewlet(f_en, self.request, None, None)

        selector.update()
        selector_languages = selector.languages()
        self.browser.open(selector_languages[0]['url'])
        f_en = self.portal['en']['test-folder']
        self.assertEqual(
            self.browser.url,
            f_en.absolute_url()+'/@@search?set_language=en')
        self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
        self.browser.open(selector_languages[1]['url'])
        f_ca = self.portal['ca']['test-folder']
        self.assertEqual(
            self.browser.url,
            f_ca.absolute_url()+'/@@search?set_language=ca'
        )
        self.assertIn(
            u'lang="ca"'.encode("utf-8"),
            self.browser.contents
        )
        # Here @@search isn't preserved because we've got the dialog
        self.browser.open(selector_languages[2]['url'])
        tgid = selector_languages[2]['url'].split('/')[-3]

        self.assertEqual(
            self.browser.url,
            self.portal.absolute_url() + \
                NOT_TRANSLATED_YET_TEMPLATE + '/' + tgid + '?set_language=es'
        )
        self.assertIn(
            u'lang="es"'.encode("utf-8"),
            self.browser.contents
        )

    def test_languages_preserve_query(self):
        self.setUpPartiallyTranslatedContent()
        self.registry = getUtility(IRegistry)
        self.request['PATH_INFO'] = '/plone/en/test-folder/@@search'
        self.request.form['uni'] = u'pres\xd8rved'
        self.request.form['int'] = '1'

        f_en = self.portal['en']['test-folder']
        selector = LanguageSelectorViewlet(f_en, self.request, None, None)
        selector.update()
        selector_languages = selector.languages()
        tgid = selector_languages[2]['url'].split('/')[-3]

        untraslated_url = {
            'closest': self.portal.es.absolute_url() + \
                '?int=1&uni=pres%C3%98rved&set_language=es',
            'dialog': self.portal.absolute_url() + \
                NOT_TRANSLATED_YET_TEMPLATE + '/' + tgid + \
                '?int=1&uni=pres%C3%98rved&set_language=es'
        }
        for policy in ['closest', 'dialog']:
            self.settings = self.registry.forInterface(IMultiLanguagePolicies)
            self.settings.selector_lookup_translations_policy = policy
            transaction.commit()

            f_en = self.portal['en']['test-folder']
            selector = LanguageSelectorViewlet(f_en, self.request, None, None)

            selector.update()
            selector_languages = selector.languages()
            self.browser.open(selector_languages[0]['url'])
            self.assertEqual(
                self.browser.url,
                f_en.absolute_url() + \
                    '/@@search?int=1&uni=pres%C3%98rved&set_language=en'
            )
            self.assertRegexpMatches(self.browser.contents, r"You\s*are here")
            self.browser.open(selector_languages[1]['url'])
            f_ca = self.portal['ca']['test-folder']
            self.assertEqual(
                self.browser.url,
                f_ca.absolute_url() + \
                    '/@@search?int=1&uni=pres%C3%98rved&set_language=ca'
            )
            self.assertIn(
                u'lang="ca"'.encode("utf-8"),
                self.browser.contents
            )
            # Here @@search isn't preserved because we've got the dialog
            self.browser.open(selector_languages[2]['url'])

            self.assertEqual(
                self.browser.url,
                untraslated_url[policy]
            )
            self.assertIn(
                u'lang="es"'.encode("utf-8"),
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

    layer = PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = createContentInContainer(
            self.portal, 'Folder', title=u"Folder")
        self.document= createContentInContainer(
            self.portal, 'Document', title=u"Document")
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

    layer = PAM_INTEGRATION_TESTING

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
