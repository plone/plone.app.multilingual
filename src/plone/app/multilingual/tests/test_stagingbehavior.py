import unittest2 as unittest

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IBaseline
from plone.app.iterate.interfaces import IWorkingCopy

from plone.app.stagingbehavior.utils import get_relations
from plone.app.stagingbehavior.utils import get_baseline

from plone.app.multilingual import testing

from plone.multilingual.interfaces import ILanguage
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.browser.utils import multilingualMoveObject

import transaction


class TestStagingBehavior(unittest.TestCase):
    """Check the behaviour of cut, copy, paste and update language on
    multilingual contents when these actions are performed on containers
    that contain working copies.
    """
    layer = testing.PLONEAPPMULTILINGUAL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.language_tool = getToolByName(self.portal, 'portal_languages')
        self.language_tool.addSupportedLanguage('ca')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        workflowTool = getToolByName(self.portal, "portal_workflow")
        workflowTool.setDefaultChain('simple_publication_workflow')
        setupTool = SetupMultilingualSite()
        setupTool.setupSite(self.portal)

    def _create_content_structure(self, folder_id):
        """create a folder that contains a page and its working copy
        """
        self.assertTrue(getattr(self.portal, 'en'))

        self.portal.en.invokeFactory(
            'dxfolder',
            folder_id,
            title=u"A Dexterity based folder"
        )
        folder = self.portal.en[folder_id]
        folder.invokeFactory(
            'dxdocwc',
            'doc',
            title=u"An Dexterity based doc"
        )
        doc = folder['doc']

        policy = ICheckinCheckoutPolicy(doc)
        wc = policy.checkout(folder)

        self.assertEqual(ILanguage(folder).get_language(), 'en')
        self.assertEqual(ILanguage(doc).get_language(), 'en')

        return folder, doc, wc

    def _check_wc_relations(self, baseline,  wc):
        self.assertTrue(IBaseline.providedBy(baseline))
        self.assertFalse(IBaseline.providedBy(wc))

        self.assertFalse(IWorkingCopy.providedBy(baseline))
        self.assertTrue(IWorkingCopy.providedBy(wc))

        self.assertEqual(get_baseline(wc), baseline)
        self.assertEqual(get_relations(baseline)[0].to_object, wc)

    def test_rename_wc_container(self):
        """When a folder that contains a working copy
        is renamed its content do not change and relation between
        the working copy and its baseline still working.
        """
        folder_id = 'test_folder1'
        folder, doc, wc = self._create_content_structure(folder_id)

        self.portal['en'].manage_renameObject(folder_id, '%s-x' % folder_id)
        self._check_wc_relations(doc,  wc)

    def test_wc_update_language(self):
        """When the language of a folder that contains a working copy
        is changed its content do not change and relation between
        the working copy and its baseline still working.
        """
        folder_id = 'test_folder2'
        folder, doc, wc = self._create_content_structure(folder_id)

        multilingualMoveObject(folder, 'ca')
        folder = self.portal.ca.get(folder_id)
        self.assertTrue(folder)
        self.assertIn('doc', folder.objectIds())
        self.assertIn('copy_of_doc', folder.objectIds())

        self.assertEqual(ILanguage(folder).get_language(), 'ca')
        self.assertEqual(ILanguage(folder['doc']).get_language(), 'ca')

        self._check_wc_relations(folder['doc'], folder['copy_of_doc'])

    def test_wc_copy_and_paste(self):
        """When a folder that contains a working copy
        is copied and pasted in another position its content
        relation between the working copy and its baseline will be lost.

        Archetypes content have the same behaviour
        """
        folder_en = self.portal['en']
        folder_id = 'test_folder3'
        folder, doc, wc = self._create_content_structure(folder_id)

        target_id = 'copy_destination_folder'
        self.portal.en.invokeFactory(
            'dxfolder',
            target_id,
            title=u"Destination folder"
        )

        target = self.portal.en[target_id]
        id_ = self.portal['en'].manage_copyObjects(folder_id)
        target.manage_pasteObjects(id_)

        # previous working copy still working
        self._check_wc_relations(doc, wc)

        folder = target.get(folder_id)
        self.assertIsNotNone(folder)

        baseline = folder['doc']
        wc = folder['copy_of_doc']
        self.assertTrue(IBaseline.providedBy(baseline))
        self.assertFalse(IBaseline.providedBy(wc))

        self.assertFalse(IWorkingCopy.providedBy(baseline))
        self.assertTrue(IWorkingCopy.providedBy(wc))

        self.assertIsNone(get_baseline(wc))
        self.assertEqual(get_relations(baseline), [])

    def test_wc_cut_and_paste(self):
        """When a folder that contains a working copy
        is cut and pasted in another place its content do not change
        and relation between the working copy and its baseline still working.
        """
        folder_en = self.portal['en']
        folder_id = 'test_folder4'
        folder, doc, wc = self._create_content_structure(folder_id)

        target_id = 'move_destination_folder'
        self.portal.en.invokeFactory(
            'dxfolder',
            target_id,
            title=u"Destination folder"
        )

        target = self.portal.en[target_id]
        id_ = folder_en.manage_cutObjects(folder_id)
        target.manage_pasteObjects(id_)

        self._check_wc_relations(doc, wc)

        folder = target.get(folder_id)
        self.assertIsNotNone(folder)
        self._check_wc_relations(folder['doc'], folder['copy_of_doc'])
