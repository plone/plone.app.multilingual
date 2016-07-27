# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.multilingual import _
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.dx.interfaces import IMultilingualAddForm
from Products.CMFPlone.interfaces import ILanguage
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslationManager
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from plone.z3cform.fieldsets.group import Group
from z3c.form import button
from z3c.form.form import Form
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import implementer
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError
import logging


logger = logging.getLogger(__name__)


@adapter(IFolderish, Interface)
@implementer(ITraversable)
class AddViewTraverser(object):
    """Add view traverser.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.request.translation_info = dict()
        self.info = self.request.translation_info

    def traverse(self, name, ignored):
        # Populate translation info
        self.info['target_language'] = ILanguage(self.context).get_language()

        catalog = getToolByName(self.context, 'portal_catalog')
        # Search source object using unrestricted API,
        # because user may be anonymous during traverse.
        brains = catalog.unrestrictedSearchResults(UID=name)
        if len(brains) != 1:
            raise TraversalError(self.context, name)
        source = brains[0]._unrestrictedGetObject()

        self.info['source_language'] = ILanguage(source).get_language()
        self.info['portal_type'] = source.portal_type
        self.info['tg'] = ITG(source)

        # If source has already been translated to this language, just redirect
        for brain in catalog.unrestrictedSearchResults(
                TranslationGroup=self.info['tg'],
                Language=self.info['target_language']):
            self.request.response.redirect(brain.getURL())
            return u''

        # XXX: register this adapter on dx container and a second one for AT
        if not IDexterityContent.providedBy(source):
            # we are not on DX content, assume AT
            baseUrl = self.context.absolute_url()
            url = '%s/@@add_at_translation?type=%s' % (baseUrl,
                                                       source.portal_type)
            return self.request.response.redirect(url)

        # set the self.context to the place where it should be stored
        if not IFolderish.providedBy(self.context):
            self.context = self.context.__parent__

        # get the type information
        ttool = getToolByName(self.context, 'portal_types')
        ti = ttool.getTypeInfo(self.info['portal_type'])

        if ti is None:
            logger.error('No type information found for {0}'.format(
                self.info['portal_type'])
            )
            raise TraversalError(self.context, name)

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema,
                                         prefix="plone")

        if not settings.redirect_babel_view:
            add_view = None
        else:
            add_view = queryMultiAdapter(
                (self.context, self.request, ti),
                name='babel_view'
            )
        if add_view is None:
            add_view = queryMultiAdapter((self.context, self.request, ti))
            if add_view is not None:
                raise TraversalError(self.context, name)

        add_view.__name__ = ti.factory
        return add_view.__of__(self.context)


@implementer(IMultilingualAddForm)
class MultilingualAddFormGroup(Group):
    """Multilingual marked group
    """


@implementer(IMultilingualAddForm)
class MultilingualAddForm(DefaultAddForm):

    babel = ViewPageTemplateFile("templates/dexterity_edit.pt")

    group_class = MultilingualAddFormGroup

    def portal_url(self):
        portal_tool = getToolByName(self.context, 'portal_url', None)
        if portal_tool is not None:
            return portal_tool.getPortalObject().absolute_url()
        return None

    def render(self):
        self.request['disable_border'] = True
        self.babel_content = super(MultilingualAddForm, self).render()
        return self.babel()

    @property
    def max_nr_of_buttons(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema,
                                         prefix="plone")
        return settings.buttons_babel_view_up_to_nr_translations

    def _process_language_independent(self, fields, widgets):
        for field_key in fields.keys():
            if field_key in self.schema:
                schema_field = self.schema[field_key]
            else:
                # With plone.autoform, fieldnames from additional schematas
                # reference their schema by prefixing their fieldname
                # with schema.__identifier__ and then a dot as a separator
                # See autoform.txt in the autoform package
                if '.' not in field_key:
                    continue
                schema_name, field_name = field_key.split('.')
                for aschema in self.additionalSchemata:
                    if schema_name == aschema.__name__ \
                       and field_name in aschema:
                        schema_field = aschema[field_name]
                        break

            if ILanguageIndependentField.providedBy(schema_field):
                widgets[field_key].addClass('languageindependent')

    def update(self):
        super(MultilingualAddForm, self).update()
        # process widgets to be shown as language independent
        self._process_language_independent(self.fields, self.widgets)
        for group in self.groups:
            self._process_language_independent(group.fields, group.widgets)


class DefaultMultilingualAddView(DefaultAddView):
    """This is the default add view as looked up by the ++add++ traversal
    namespace adapter in CMF. It is an unnamed adapter on
    (context, request, fti).

    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """

    form = MultilingualAddForm
