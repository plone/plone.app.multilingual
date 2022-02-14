from BTrees.OOBTree import OOBTree
from plone.dexterity.content import Container
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite


def connect_with_others(ob, event):
    pc = getToolByName(getSite(), "portal_catalog")
    results = pc.unrestrictedSearchResults(portal_type="LIF")
    for result in results:
        lif = result._unrestrictedGetObject()
        ob._tree = lif._tree
        ob._count = lif._count
        ob._mt_index = lif._mt_index
        if not hasattr(lif, "__annotations__"):
            lif.__annotations__ = OOBTree()
        ob.__annotations__ = lif.__annotations__
        break
