# -*- coding: UTF-8 -*-
from os.path import dirname
import unittest2 as unittest
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from plone.app.multilingual.testing import PLONEAPPMULTILINGUAL_INTEGRATION_TESTING, PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING
from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.component import provideAdapter
from zope.interface import directlyProvides
from zope.interface import implements
from zope.interface import Interface
# from zope.testing import cleanup
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

from Acquisition import Explicit
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.multilingual.browser.selector import LanguageSelectorViewlet
from plone.multilingual.interfaces import ITranslatable
# from Products.LinguaPlone.tests.base import LinguaPloneTestCase
from plone.app.multilingual.tests.utils import makeContent
from plone.app.multilingual.tests.utils import makeTranslation
from plone.app.multilingual.browser.controlpanel import IMultiLanguagePolicies
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual import browser
from plone.uuid.interfaces import IAttributeUUID
from plone.uuid.interfaces import IUUID
from plone.testing.z2 import Browser


class Dummy(Explicit):

    implements(IAttributeUUID, ITranslatable)

    # This avoids issues with tests that run without a
    # full-fledged securityManager
    _View_Permission = ('Anonymous', )

    portal_type = 'Dummy'

    def getTranslations(self, review_state=False):
        return {'en': self, 'nl': self}

    def getPhysicalPath(self):
        return getattr(self, 'physicalpath', [])


class DummyRequest(object):

    def __init__(self):
        self.form = {}

    def get(self, key, default):
        return self.__dict__.get(key, default)


class DummyState(object):

    def __init__(self, context, request):
        pass

    def canonical_object_url(self):
        return 'object_url'


class EvilObject(object):

    def __str__(self):
        raise UnicodeError

    def __unicode__(self):
        raise UnicodeError


class MockLanguageTool(object):

    use_cookie_negotiation = True

    def showSelector(self):
        return True

    def getAvailableLanguageInformation(self):
        return dict(en={'selected': True}, de={'selected': False},
                    nl={'selected': True}, no={'selected': True})

    def getLanguageBindings(self):
        # en = selected by user, nl = default, [] = other options
        return ('en', 'nl', [])

    def getSupportedLanguages(self):
        return ['nl', 'en', 'no']


class TestLanguageSelectorBasics(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
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

    def test_languages_full_translated_by_closest(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'closest'

        doc1 = makeContent(self.portal, 'Document', id='doc1')
        doc1.setLanguage('en')
        doc1_ca = makeTranslation(doc1, 'ca')
        doc1_ca.edit(title="Foo", language='ca')
        doc1_es = makeTranslation(doc1, 'es')
        doc1_es.edit(title="Foo", language='es')

        self.selector = LanguageSelectorViewlet(doc1,
                            self.request, None, None)

        self.selector.update()

        self.assertEqual(self.selector.languages(), [
            {'code': u'en',
             u'name': u'English',
             'url': 'http://nohost/plone/doc1?set_language=en',
             'selected': True,
             u'flag': u'/++resource++country-flags/gb.gif',
             'translated': True,
             u'native': u'English'},
             {'code': u'ca',
              u'name': u'Catalan',
              'url': 'http://nohost/plone/doc1-ca?set_language=ca',
              'selected': False,
              u'flag': u'/++resource++language-flags/ca.gif',
              'translated': True,
              u'native': u'Catal\xe0'},
              {'code': u'es',
              u'name': u'Spanish',
              'url': 'http://nohost/plone/doc1-es?set_language=es',
              'selected': False,
              u'flag': u'/++resource++country-flags/es.gif',
              'translated': True,
              u'native': u'Espa\xf1ol'}
        ])

    def test_languages_partially_translated_by_dialog(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'

        p1 = makeContent(self.portal, 'Document', id='partial')
        p1.setLanguage('en')
        p1_ca = makeTranslation(p1, 'ca')
        p1_ca.edit(title="Foo ca", language='ca')

        self.selector = LanguageSelectorViewlet(p1,
                            self.request, None, None)

        self.selector.update()

        self.assertEqual(self.selector.languages(), [
            {'code': u'en',
             u'name': u'English',
             'url': 'http://nohost/plone/partial?set_language=en',
             'selected': True,
             u'flag': u'/++resource++country-flags/gb.gif',
             'translated': True,
             u'native': u'English'},
             {'code': u'ca',
             u'name': u'Catalan',
             'url': 'http://nohost/plone/partial-ca?set_language=ca',
             'selected': False,
             u'flag': u'/++resource++language-flags/ca.gif',
             'translated': True,
             u'native': u'Catal\xe0'},
             {'code': u'es',
             u'name': u'Spanish',
             'url': 'http://nohost/plone/partial/not_translated_yet?set_language=es',
             'selected': False,
             u'flag': u'/++resource++country-flags/es.gif',
             'translated': False,
             u'native': u'Espa\xf1ol'}
        ])

    def test_languages_root_folders_by_dialog(self):
        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IMultiLanguagePolicies)
        self.settings.selector_lookup_translations_policy = 'dialog'

        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

        self.selector = LanguageSelectorViewlet(self.portal.en,
                            self.request, None, None)

        self.selector.update()

        self.assertEqual(self.selector.languages(), [
            {'code': u'en',
             u'name': u'English',
             'url': 'http://nohost/plone/en?set_language=en',
             'selected': True,
             u'flag': u'/++resource++country-flags/gb.gif',
             'translated': True,
             u'native': u'English'},
             {'code': u'ca',
             u'name': u'Catalan',
             'url': 'http://nohost/plone/ca?set_language=ca',
             'selected': False,
             u'flag': u'/++resource++language-flags/ca.gif',
             'translated': True,
             u'native': u'Catal\xe0'},
             {'code': u'es',
             u'name': u'Spanish',
             'url': 'http://nohost/plone/es?set_language=es',
             'selected': False,
             u'flag': u'/++resource++country-flags/es.gif',
             'translated': True,
             u'native': u'Espa\xf1ol'}
        ])

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

    # def test_languages_preserve_view_and_query(self):
    #     self.context.physicalpath = ['', 'fake', 'path']
    #     self.request.PATH_INFO = '/fake/path/to/object'
    #     self.selector.update()
    #     base = 'object_url/to/object?set_language='
    #     expected = [
    #         {'code': 'nl',
    #          'translated': True,
    #          'selected': False,
    #          'url': base + 'nl'},
    #         {'code': 'en',
    #          'translated': True,
    #          'selected': True,
    #          'url': base + 'en'},
    #         {'code': 'no',
    #          'translated': False,
    #          'selected': False,
    #          'url': base + 'no'}]
    #     self.assertEqual(self.selector.languages(), expected)


class TestLanguageSelectorFindPath(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.selector = LanguageSelectorViewlet(None,
                            None, None, None)
        self.fp = self.selector._findpath

    def test_findpath(self):
        result = self.fp(['', 'fake', 'path'], '/fake/path/object')
        self.assertEquals(result, ['', 'object'])

    def test_findpath_match(self):
        result = self.fp(['', 'fake', 'path'], '/fake/path')
        self.assertEquals(result, [])

    def test_findpath_match_slash(self):
        result = self.fp(['', 'fake', 'path'], '/fake/path/')
        self.assertEquals(result, [])

    def test_findpath_template(self):
        result = self.fp(['', 'fake', 'path'], '/fake/path/object/atct_edit')
        self.assertEquals(result, ['', 'object', 'atct_edit'])

    def test_findpath_view(self):
        result = self.fp(['', 'fake', 'path'], '/fake/path/object/@@sharing')
        self.assertEquals(result, ['', 'object', '@@sharing'])

    def test_findpath_vhr(self):
        result = self.fp(['', 'fake', 'path'],
            '/VirtualHostBase/http/127.0.0.1/fake/path/VirtualHostRoot/object')
        self.assertEquals(result, ['', 'object'])

    def test_findpath_vh_marker(self):
        result = self.fp(['', 'fake', 'path'],
            '/VirtualHostBase/http/127.0.0.1/fake/path//VirtualHostRoot/' +
            '_vh_secondlevel/object')
        self.assertEquals(result, ['', 'object'])

    def test_findpath_vhr_and_traverser(self):
        result = self.fp(['', 'fake', 'path'],
            '/VirtualHostBase/http/127.0.0.1/site/fake/path/++skin++theme/' +
            'VirtualHostRoot/object')
        self.assertEquals(result, ['', 'object'])


class TestLanguageSelectorFormVariables(unittest.TestCase):

    layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.selector = LanguageSelectorViewlet(None,
                            None, None, None)
        self.fv = self.selector._formvariables

    def test_formvariables(self):
        form = dict(one=1, two='2')
        self.assertEquals(self.fv(form), form)

    def test_formvariables_sequences(self):
        form = dict(one=('a', ), two=['b', 2])
        self.assertEquals(self.fv(form), form)

    def test_formvariables_unicode(self):
        uni = unicode('Før', 'utf-8')
        form = dict(one=uni, two=u'foo')
        self.assertEquals(self.fv(form),
                          dict(one=uni.encode('utf-8'), two=u'foo'))

    def test_formvariables_utf8(self):
        utf8 = unicode('Før', 'utf-8').encode('utf-8')
        form = dict(one=utf8, two=u'foo')
        self.assertEquals(self.fv(form), form)

    def test_formvariables_object(self):
        form = dict(one='1', two=EvilObject())
        self.assertEquals(self.fv(form), form)


# class TestLanguageSelectorRendering(unittest.TestCase):

#     layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

#     def setUp(self):
#         self.language_tool.addSupportedLanguage('de')
#         self.language_tool.addSupportedLanguage('no')
#         self.setLanguage('en')
#         self.english = makeContent(self.folder, 'SimpleType', 'doc')
#         self.english.setLanguage('en')
#         self.german = makeTranslation(self.english, 'de')
#         self.german.setLanguage('de')
#         self.attachRender(LanguageSelectorViewlet)

#     def attachRender(self, _class):
#         prefix = dirname(browser.__file__)
#         _class.render = ViewPageTemplateFile('languageselector.pt', _prefix=prefix)

#     def testRenderSelectorForAnonymous(self):
#         self.setRoles('Reviewer')
#         pw = self.portal.portal_workflow
#         pw.doActionFor(self.english, 'publish')
#         self.logout()
#         request = self.app.REQUEST
#         selector = LanguageSelectorViewlet(
#             self.english, request, None, None)
#         selector.update()
#         output = selector.render()
#         self.assert_('<ul id="portal-languageselector"' in output)
#         en_path = self.english.absolute_url()
#         en_link = '<a href="%s?set_language=en"' % en_path
#         self.assert_(en_link in output)
#         de_path = self.portal.absolute_url()
#         de_link = '<a href="%s?set_language=de"' % de_path
#         self.assert_(de_link in output)
#         no_path = self.portal.absolute_url()
#         no_link = '<a href="%s?set_language=no"' % no_path
#         self.assert_(no_link in output)

#     def testRenderSelector(self):
#         request = self.app.REQUEST
#         selector = LanguageSelectorViewlet(
#             self.english, request, None, None)
#         selector.update()
#         output = selector.render()
#         self.assert_('<ul id="portal-languageselector"' in output)
#         en_path = self.english.absolute_url()
#         en_link = '<a href="%s?set_language=en"' % en_path
#         self.assert_(en_link in output)
#         de_path = self.german.absolute_url()
#         de_link = '<a href="%s?set_language=de"' % de_path
#         self.assert_(de_link in output)
#         no_path = self.portal.absolute_url()
#         no_link = '<a href="%s?set_language=no"' % no_path
#         self.assert_(no_link in output)

#     def testRenderSelectorOnSiteRoot(self):
#         request = self.app.REQUEST
#         selector = LanguageSelectorViewlet(
#             self.portal, request, None, None)
#         selector.update()
#         output = selector.render()
#         path = self.portal.absolute_url()
#         de_link = '<a href="%s?set_language=de"' % path
#         self.assert_(de_link in output)
#         en_link = '<a href="%s?set_language=en"' % path
#         self.assert_(en_link in output)

#     def testRenderSelectorWithNavigationRoot(self):
#         request = self.app.REQUEST
#         directlyProvides(self.portal.Members, INavigationRoot)
#         selector = LanguageSelectorViewlet(
#             self.folder, request, None, None)
#         selector.update()
#         output = selector.render()
#         path = self.portal.Members.absolute_url()
#         folder_path = self.folder.absolute_url()
#         de_link = '<a href="%s?set_language=de"' % path
#         self.assert_(de_link in output)
#         en_link = '<a href="%s?set_language=en"' % folder_path
#         self.assert_(en_link in output)

#     def testRenderSelectorWithNavigationRootForAnonymous(self):
#         self.loginAsPortalOwner()
#         en_root = makeContent(self.portal, 'Folder', 'en')
#         en_root.setLanguage('en')
#         directlyProvides(en_root, INavigationRoot)
#         de_root = makeTranslation(en_root, 'de')
#         de_root.setLanguage('de')
#         directlyProvides(de_root, INavigationRoot)
#         no_root = makeTranslation(en_root, 'no')
#         no_root.setLanguage('no')
#         directlyProvides(no_root, INavigationRoot)

#         self.setRoles('Reviewer')
#         pw = self.portal.portal_workflow
#         pw.doActionFor(en_root, 'publish')
#         pw.doActionFor(de_root, 'publish')
#         self.logout()

#         request = self.app.REQUEST
#         selector = LanguageSelectorViewlet(
#             en_root, request, None, None)
#         selector.update()
#         output = selector.render()

#         en_path = en_root.absolute_url()
#         en_link = '<a href="%s?set_language=en"' % en_path
#         self.assert_(en_link in output)

#         de_path = de_root.absolute_url()
#         de_link = '<a href="%s?set_language=de"' % de_path
#         self.assert_(de_link in output)

#         self.assert_('set_language=no' not in output)

#     def testRenderSelectorWithFlags(self):
#         request = self.app.REQUEST
#         ltool = getToolByName(self.portal, 'portal_languages')
#         ltool.display_flags = True
#         selector = LanguageSelectorViewlet(
#             self.english, request, None, None)
#         selector.update()
#         output = selector.render()
#         self.assert_('de.gif' in output)
#         self.assert_('gb.gif' in output)

#     def testRenderSelectorWithoutCookieNegotiation(self):
#         request = self.app.REQUEST
#         ltool = getToolByName(self.portal, 'portal_languages')
#         ltool.use_cookie_negotiation = False
#         selector = LanguageSelectorViewlet(
#             self.english, request, None, None)
#         selector.update()
#         output = selector.render()
#         self.assertEquals(output.strip(), u'')


# class TestLanguageSelectorWithMixedTree(unittest.TestCase):

#     layer = PLONEAPPMULTILINGUAL_INTEGRATION_TESTING

#     def setUp(self):
#         self.addLanguage('de')
#         self.addLanguage('no')
#         self.setLanguage('en')
#         self.setRoles(['Manager'])
#         en = makeContent(self.portal, 'Folder', 'en')
#         en.setLanguage('en')
#         suben = makeContent(en, 'Folder', 'sub-en')
#         suben.setLanguage('en')
#         self.endoc = makeContent(suben, 'SimpleType', 'endoc')
#         self.endoc.setLanguage('en')
#         makeTranslation(en, 'de')
#         self.dedoc = makeTranslation(self.endoc, 'de')
#         neutral = makeContent(en, 'Folder', 'neutral')
#         neutral.setLanguage('')
#         self.doc = makeContent(neutral, 'SimpleType', 'doc')
#         self.doc.setLanguage('')

#     def test_selector_on_english_document(self):
#         request = self.app.REQUEST
#         selector = LanguageSelectorViewlet(
#             self.endoc, request, None, None)
#         selector.update()
#         languages = dict([(l['code'], l) for l in selector.languages()])
#         self.assertEqual(languages[u'en']['url'],
#             'http://nohost/plone/en/sub-en/endoc?set_language=en')
#         self.assertEqual(languages[u'de']['url'],
#             'http://nohost/plone/en/sub-en/endoc-de?set_language=de')
#         self.assertEqual(languages[u'no']['url'],
#             'http://nohost/plone?set_language=no')

#     def test_selector_on_sharing_view(self):
#         request = self.app.REQUEST
#         request['PATH_INFO'] = self.endoc.absolute_url() + '/@@sharing'
#         selector = LanguageSelectorViewlet(
#             self.endoc, request, None, None)
#         selector.update()
#         languages = dict([(l['code'], l) for l in selector.languages()])
#         self.assertEqual(languages[u'en']['url'],
#             'http://nohost/plone/en/sub-en/endoc/@@sharing?set_language=en')
#         self.assertEqual(languages[u'de']['url'],
#             'http://nohost/plone/en/sub-en/endoc-de/@@sharing?set_language=de')
#         self.assertEqual(languages[u'no']['url'],
#             'http://nohost/plone?set_language=no')

#     def test_selector_on_neutral_document(self):
#         request = self.app.REQUEST
#         selector = LanguageSelectorViewlet(
#             self.doc, request, None, None)
#         selector.update()
#         languages = dict([(l['code'], l) for l in selector.languages()])
#         self.assertEqual(languages[u'en']['url'],
#             'http://nohost/plone/en?set_language=en')
#         self.assertEqual(languages[u'de']['url'],
#             'http://nohost/plone/en-de?set_language=de')
#         self.assertEqual(languages[u'no']['url'],
#             'http://nohost/plone?set_language=no')
