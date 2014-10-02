# -*- coding: utf-8 -*-
from Products.PloneLanguageTool.LanguageTool import LanguageBinding
from languagetool import setLanguageBindingsCookieWins
from plone.i18n.locales.languages import _combinedlanguagelist
from plone.i18n.locales.languages import _languagelist
from zope.i18nmessageid import MessageFactory
import logging
import pkg_resources

try:
    pkg_resources.get_distribution('Products.LinguaPlone')
except pkg_resources.DistributionNotFound:
    isLPinstalled = False
else:
    isLPinstalled = True

logger = logging.getLogger('plone.app.multilingual')
_ = MessageFactory('plone.app.multilingual')
LanguageBinding.setLanguageBindings = setLanguageBindingsCookieWins

# blacklisted means:
# * blocks traversal on LRF level
# * no multilingual indexing (for every language, as with language neutral)
#   if ids direct under portal, also contained objects are not indexed
#   multilingual.
BLACK_LIST_IDS = {
    'id-id',
    'members',
}
BLACK_LIST_IDS.update(_combinedlanguagelist)
BLACK_LIST_IDS.update(_languagelist)
