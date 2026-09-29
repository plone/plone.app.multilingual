from plone.app.multilingual.dx.cloner import LanguageIndependentFieldsManager
from plone.base.interfaces import ILanguage
from zope.interface import implementer

import unittest


class DummyContent:
    """A minimal stand-in for a dexterity content object.

    It intentionally does not provide ``IDexterityContent``, so no
    ``ILanguage`` adapter will be found for it, and it has a
    ``portal_type`` that is not registered anywhere, so
    ``iterSchemata`` will simply yield nothing for it.
    """

    portal_type = "NoSuchPortalType"


@implementer(ILanguage)
class LanguageAwareContent(DummyContent):
    """A content stand-in that itself provides ILanguage directly.

    ``queryAdapter`` returns the object itself when it already provides
    the requested interface, so this lets us exercise the "adapter
    found" branch without any component registry setup.
    """

    def get_language(self):
        return "en"

    def set_language(self, language):
        pass


class TestLanguageIndependentFieldsManagerCopyFields(unittest.TestCase):
    """Regression tests for LanguageIndependentFieldsManager.copy_fields.

    See https://github.com/plone/plone.app.multilingual/issues/504
    """

    def test_copy_fields_without_language_adapter_does_not_raise(self):
        # When no ILanguage adapter can be found for the translation,
        # copy_fields used to blow up with an AttributeError because it
        # called get_language() straight on the queryAdapter() result
        # without checking for None first.
        manager = LanguageIndependentFieldsManager(DummyContent())
        result = manager.copy_fields(DummyContent())
        self.assertFalse(result)

    def test_copy_fields_with_language_adapter_still_works(self):
        # Sanity check that the normal case, where an ILanguage adapter
        # is actually found, keeps working the same as before.
        manager = LanguageIndependentFieldsManager(DummyContent())
        result = manager.copy_fields(LanguageAwareContent())
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
