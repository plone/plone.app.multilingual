# make this a package

import pkg_resources
import logging

logger = logging.getLogger('plone.app.multilingual')

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone.app.multilingual')

from Products.PloneLanguageTool.LanguageTool import LanguageBinding
from languagetool import setLanguageBindingsCookieWins
LanguageBinding.setLanguageBindings = setLanguageBindingsCookieWins

try:
    pkg_resources.get_distribution('Products.LinguaPlone')
except pkg_resources.DistributionNotFound:
    isLPinstalled = False
else:
    isLPinstalled = True
