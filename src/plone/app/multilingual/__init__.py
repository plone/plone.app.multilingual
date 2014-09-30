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


BLACK_LIST_IDS = {
    'id-id',
    'portal_catalog',
    'portal_url',
    'acl_users',
    'members',
}
BLACK_LIST_IDS.update(_combinedlanguagelist)
BLACK_LIST_IDS.update(_languagelist)
