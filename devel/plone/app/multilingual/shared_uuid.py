from Acquisition import aq_base, aq_chain

from zope.interface import implementer
from zope.component import adapter
import uuid

from plone.uuid.interfaces import IUUID, IAttributeUUID, ATTRIBUTE_NAME

from Products.Archetypes.config import UUID_ATTR
from archetypes.multilingual.interfaces import IArchetypesTranslatable

from plone.app.multilingual.dx.interfaces import IDexterityTranslatable
from plone.app.multilingual.content.lrf import ILanguageRootFolder
from plone.app.multilingual.interfaces import ISharedElement

@implementer(IUUID)
@adapter(ILanguageRootFolder)
def lrfUUID(context):
    return getattr(aq_base(context), UUID_ATTR, None)


@implementer(IUUID)
@adapter(IAttributeUUID)
def attributeUUID(context):
    child = context
    for element in aq_chain(context):
        if hasattr(child, '_v_is_shared_content') and ILanguageRootFolder.providedBy(element):
            uid = getattr(aq_base(context), ATTRIBUTE_NAME, None)
            return uid + '-' + element.id if uid is not None else None
        child = element
    return getattr(context, ATTRIBUTE_NAME, None)
