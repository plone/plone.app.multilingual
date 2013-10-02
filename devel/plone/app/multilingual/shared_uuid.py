from Acquisition import aq_base, aq_chain
from Products.Archetypes.config import UUID_ATTR

from plone.app.multilingual.content.lrf import ILanguageRootFolder
<<<<<<< HEAD
from plone.uuid.interfaces import IUUID, IAttributeUUID, ATTRIBUTE_NAME
from zope.component import adapter
from zope.interface import implementer

=======
from plone.app.multilingual.interfaces import ISharedElement
from plone.app.multilingual.browser.utils import is_shared
>>>>>>> Working on 2.0 merge

@implementer(IUUID)
@adapter(ILanguageRootFolder)
def lrfUUID(context):
    return getattr(aq_base(context), ATTRIBUTE_NAME, None)


@implementer(IUUID)
@adapter(IAttributeUUID)
def attributeUUID(context):
    child = context
    for element in aq_chain(context):
<<<<<<< HEAD
        if hasattr(child, '_v_is_shared_content') \
           and ILanguageRootFolder.providedBy(element):
=======
        if hasattr(child, '_v_is_shared_content') and child._v_is_shared_content and ILanguageRootFolder.providedBy(element):
>>>>>>> Working on 2.0 merge
            uid = getattr(aq_base(context), ATTRIBUTE_NAME, None)
            return uid + '-' + element.id if uid is not None else None
        child = element
    return getattr(context, ATTRIBUTE_NAME, None)
