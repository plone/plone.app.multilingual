from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.multilingual.testing import PLONE_APP_MULTILINGUAL_INTEGRATION_TESTING  # noqa

import unittest

class TestUninstall(unittest.TestCase):

    layer = PLONE_APP_MULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['plone.app.multilingual'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if plone.app.multilingual is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'plone.app.multilingual'))

    def test_browserlayer_removed(self):
        """Test that IPloneAppMultilingualInstalled is removed."""
        from plone.app.multilingual.interfaces import \
            IPloneAppMultilingualInstalled
        from plone.browserlayer import utils
        self.assertNotIn(
           IPloneAppMultilingualInstalled,
           utils.registered_layers())

    def test_language_switcher_not_in_available_view_methods(self):
        self.assertNotIn(
            'language-switcher',
            self.portal.portal_types['Plone Site'].view_methods
        )

    def test_language_switcher_not_default_view_method(self):
        self.assertNotEqual(
            'language-switcher',
            self.portal.portal_types['Plone Site'].default_view
        )
