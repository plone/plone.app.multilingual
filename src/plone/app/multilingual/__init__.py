# -*- coding: utf-8 -*-
from Products.PloneLanguageTool.LanguageTool import LanguageBinding
from languagetool import setLanguageBindingsCookieWins
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
