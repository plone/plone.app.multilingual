from zope.component import queryAdapter
from plone.multilingual.interfaces import ITG
from plone.app.i18n.locales.browser.selector import LanguageSelector
from .utils import propagateQuery, addPostPath


NOT_TRANSLATED_YET_TEMPLATE = '/not_translated_yet'
# Used when no tg is found.
# Hopefully UUIDS are just strings in indexes
# and we do not have the catalog explode.
# Else we have to find an invalid, "magic" UID
INVALID = '__no_translation_group__'


class LanguageSelectorViewlet(LanguageSelector):
    """Language selector for translatable content.
    """

    def languages(self):
        languages_info = super(LanguageSelectorViewlet, self).languages()
        results = []
        translation_group = queryAdapter(self.context, ITG)
        if translation_group is None:
            translation_group = INVALID
        for lang_info in languages_info:
            # Avoid to modify the original language dict
            data = lang_info.copy()
            data['translated'] = True
            data['url'] = propagateQuery(
                self.request,
                addPostPath(
                    self.context,
                    self.request,
                    self.context.absolute_url()
                ).rstrip("/") + "/@@multilingual-selector/%s/%s" % (
                    translation_group,
                    lang_info['code']
                )
            )
            results.append(data)
        return results
