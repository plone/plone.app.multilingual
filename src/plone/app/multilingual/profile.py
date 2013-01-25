from zope.interface import implements

from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFQuickInstallerTool.interfaces import INonInstallable as INonQ


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return [
            u'plone.multilingual',
            u'plone.multilingual',
            u'archetypes.multilingual',
            u'archetypes.testcase',
            ]

class HiddenProducts(object):
    implements(INonQ)

    def getNonInstallableProducts(self):
        return [
            u'plone.multilingual',
            u'archetypes.multilingual',
            u'archetypes.testcase',
            ]