# -*- coding: utf-8 -*-
from Acquisition import aq_base
from OFS.ObjectManager import BadRequestException
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.ZCatalog.Lazy import LazyMap
from plone.app.content.namechooser import NormalizingNameChooser
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.multilingual import BLACK_LIST_IDS
from plone.app.multilingual.interfaces import ILanguageRootFolder
from plone.app.multilingual.interfaces import ITranslationIdChooser
from plone.dexterity.content import Container
from plone.folder.default import DefaultOrdering
from plone.folder.interfaces import IExplicitOrdering
from plone.folder.ordered import CMFOrderedBTreeFolderBase
from zope.component import adapter
from zope.component.hooks import getSite
from zope.container.interfaces import INameChooser
from zope.interface import implementer

_marker = object()


@implementer(ILanguageRootFolder, INavigationRoot, IPloneSiteRoot)
class LanguageRootFolder(Container):
    """ Language root folder type that holds the shared and is navigation root
    """

    def has_key(self, item_id):
        """Indicates whether the folder has an item by ID.
        """
        return (
            CMFOrderedBTreeFolderBase.has_key(self, item_id)  # noqa
            or (
                item_id in getSite()
                and item_id not in BLACK_LIST_IDS
            )
        )

    hasObject = has_key

    def _checkId(self, item_id, allow_dup=0):
        """ check only locally """
        if not allow_dup and item_id in CMFOrderedBTreeFolderBase.objectIds(
                self, None, False):
            raise BadRequestException('The id "%s" is invalid--'
                                      'it is already in use.' % item_id)

    def objectMap(self):
        # Returns a tuple of mappings containing subobject meta-data.

        return LazyMap(lambda (k, v):
                       {'id': k, 'meta_type': getattr(v, 'meta_type', None)},
                       self._tree.items(), self._count())

    def __contains__(self, name):
        return self.has_key(name)  # noqa

    def __getattr__(self, name):
        try:
            return super(LanguageRootFolder, self).__getattr__(name)
        except AttributeError:
            # Check if it's on shared folder
            # Search for the content on the shared folder
            portal = getSite()
            if portal is None \
               or name not in portal \
               or name.startswith('_') \
               or name in BLACK_LIST_IDS:
                raise
            new_object = aq_base(getattr(portal, name)).__of__(self)
            new_object._v_is_shared_content = True
            return new_object

    def _getOb(self, item_id, default=_marker):
        obj = CMFOrderedBTreeFolderBase._getOb(self, item_id, default)
        if obj is not default:
            return obj

        aliased = getSite()
        if aliased and item_id not in BLACK_LIST_IDS:
            obj = aliased._getOb(item_id, default)
            if obj is default:
                return default
            new_object = aq_base(obj).__of__(self)
            new_object._v_is_shared_content = True
            return new_object
        if default is not _marker:
            return default

    def objectIds(self, spec=None, ordered=True):
        # XXX : need to find better aproach
        aliased = getSite()
        aliased_objectIds = set()
        if aliased is not None:
            try:
                # spec = ['Dexterity Container',
                #         'Dexterity Item',
                #         'ATFolder',
                #         'ATDocument']
                aliased_objectIds.update(aliased.objectIds(spec))
                aliased_objectIds -= BLACK_LIST_IDS
            except AttributeError:
                pass
        own_elements = CMFOrderedBTreeFolderBase.objectIds(self, spec, False)
        return [item for item in own_elements] + list(aliased_objectIds)

    def __getitem__(self, key):
        aliased = getSite()
        try:
            obj = aliased.__getitem__(key)
            if obj.getId() not in BLACK_LIST_IDS:
                new_object = aq_base(obj).__of__(self)
                new_object._v_is_shared_content = True
                return new_object
        except KeyError:
            return CMFOrderedBTreeFolderBase.__getitem__(self, key)


@implementer(IExplicitOrdering)
@adapter(ILanguageRootFolder)
class LRFOrdering(DefaultOrdering):
    """This implementation checks if there is any object that is not on the
    list in case its a shared object so you can move.
    """

    def idsInOrder(self):
        """ see interfaces.py """
        to_renew = [
            x for x in self.context.objectIds()
            if x not in self._pos().keys()
        ]
        to_remove = [
            x for x in self._pos().keys()
            if x not in self.context.objectIds()
        ]
        for item_id in to_renew:
            self.notifyAdded(item_id)
        for item_id in to_remove:
            self.notifyRemoved(item_id)
        return list(self._order())

    def getObjectPosition(self, item_id):
        """ see interfaces.py """
        pos = self._pos()
        if item_id in pos:
            return pos[item_id]
        else:
            aliased = getSite()
            if id in aliased.objectIds():
                self.notifyAdded(item_id)
                pos = self._pos()
                return pos[item_id]
            else:
                return 0
                # raise ValueError('No object with id "%s" exists.' % id)


@implementer(INameChooser)
@adapter(ILanguageRootFolder)
class LRFNameChooser(NormalizingNameChooser):
    """Special name chooser to fix issue where createContentInContainer is
    used to create a new content into LRF with an id, which exists already
    in the parent folder.
    """

    def chooseName(self, name, object):
        chosen = super(LRFNameChooser, self).chooseName(name, object)
        if chosen in self.context.objectIds():
            old_id = getattr(object, 'id', None)
            object.id = chosen
            chooser = ITranslationIdChooser(object)
            chosen = chooser(self.context, self.context.getId())
            object.id = old_id
        return chosen
