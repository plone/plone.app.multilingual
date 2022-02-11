from plone import api
from plone.app.multilingual.testing import (  # noqa
    PLONE_APP_MULTILINGUAL_INTEGRATION_TESTING,
)
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.utils import get_installer

import unittest


class TestUninstall(unittest.TestCase):

    layer = PLONE_APP_MULTILINGUAL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer = get_installer(self.portal)
        self.installer.uninstall_product("plone.app.multilingual")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if plone.app.multilingual is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("plone.app.multilingual"))

    def test_browserlayer_removed(self):
        """Test that IPloneAppMultilingualInstalled is removed."""
        from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
        from plone.browserlayer import utils

        self.assertNotIn(IPloneAppMultilingualInstalled, utils.registered_layers())

    def test_language_switcher_not_in_available_view_methods(self):
        self.assertNotIn(
            "language-switcher", self.portal.portal_types["Plone Site"].view_methods
        )

    def test_language_switcher_not_default_view_method(self):
        self.assertNotEqual(
            "language-switcher", self.portal.portal_types["Plone Site"].default_view
        )
