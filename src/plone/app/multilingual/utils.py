from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def get_parent(obj):
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory is not None and portal_factory.isTemporary(obj):
        # created by portal_factory
        parent = aq_parent(aq_parent(aq_parent(aq_inner(obj))))
    else:
        parent = aq_parent(aq_inner(obj))
    return parent
