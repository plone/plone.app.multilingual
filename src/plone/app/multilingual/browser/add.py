# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import IAddTranslation
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.dx.interfaces import IMultilingualAddForm
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.multilingual.interfaces import ITG
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from plone.z3cform.fieldsets import extensible
from plone.z3cform.fieldsets.group import Group
from plone.z3cform.fieldsets.interfaces import IFormExtender
from z3c.form import button
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import ComputedWidgetAttribute
from zope import schema
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import alsoProvides
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
        self.info['target_language'] = ILanguage(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(UID=name)
        if len(brains) != 1:
            raise TraversalError(self.context, name)
        source = brains[0].getObject()

        # XXX: register this adapter on dx container and a second one for AT
        if not IDexterityContent.providedBy(source):
            # we are not on DX content, assume AT
            baseUrl = self.context.absolute_url()
            url = '%s/@@add_at_translation?type=%s' % (baseUrl, name)
            return self.request.response.redirect(url)

        self.info['source_language'] = ILanguage(source)
        self.info['portal_type'] = source.portal_type
        self.info['tg'] = ITG(source)

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

    def gtenabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
        return settings.google_translation_key != ''

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
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
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


class IMultilingualAddFormMarkerFieldMarker(Interface):
    """Marker interfaces for add form marker fields"""


class IMultilingualAddFormMarker(model.Schema):
    """Marker metadata fields for multilingual add form"""
    directives.mode(pam_tg=HIDDEN_MODE)
    pam_tg = schema.ASCIILine(title=u"Translated content")
    pam_old_lang = schema.ASCIILine(title=u"Old language")

alsoProvides(
    IMultilingualAddFormMarker['pam_tg'],
    IMultilingualAddFormMarkerFieldMarker
)

alsoProvides(
    IMultilingualAddFormMarker['pam_old_lang'],
    IMultilingualAddFormMarkerFieldMarker
)


def get_multilingual_add_form_tg_value(adapter):
    return adapter.request.translation_info['tg']


MultilingualAddFormTgValue = ComputedWidgetAttribute(
    get_multilingual_add_form_tg_value,
    context=None, request=None, view=None, widget=None,
    field=IMultilingualAddFormMarker['pam_tg']
)


def get_multilingual_add_form_old_lang_value(adapter):
    return adapter.request.translation_info['source_language']


MultilingualAddFormOldLangValue = ComputedWidgetAttribute(
    get_multilingual_add_form_old_lang_value,
    context=None, request=None, view=None, widget=None,
    field=IMultilingualAddFormMarker['pam_old_lang']
)


class FauxDataManager(object):
    """Data manager for marker fields, which are not meant to be saved"""

    def __init__(self, context, field):
        self.context = context
        self.field = field

    def get(self):
        raise AttributeError

    def query(self, default=NO_VALUE):
        return default

    def set(self, value):
        pass

    def canAccess(self):
        return False

    def canWrite(self):
        return False


@implementer(IFormExtender)
@adapter(Interface, IPloneAppMultilingualInstalled, MultilingualAddForm)
class MultilingualAddFormExtender(extensible.FormExtender):

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        groups = getattr(self.form, 'groups', None)
        if isinstance(groups, list) and len(groups):
            for group in groups:
                alsoProvides(group, IMultilingualAddForm)

            group = groups[-1].__name__
        else:
            group = None

        self.add(IMultilingualAddFormMarker, prefix='', group=group)

        if group is None:
            for name in IMultilingualAddFormMarker:
                self.form.fields[name].mode = HIDDEN_MODE
        else:
            for name in IMultilingualAddFormMarker:
                self.form.groups[-1].fields[name].mode = HIDDEN_MODE


class DefaultMultilingualAddView(DefaultAddView):
    """This is the default add view as looked up by the ++add++ traversal
    namespace adapter in CMF. It is an unnamed adapter on
    (context, request, fti).

    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """

    form = MultilingualAddForm


class AddTranslationsForm(AutoExtensibleForm, Form):

    schema = IFormFieldProvider(IAddTranslation)
    ignoreContext = True
    label = _(u"label_add_translations", default=u"Add translations")
    description = _(
        u"long_description_add_translations",
        default=u"This form allows you to add currently existing "
                u"objects to be the translations of the current "
                u"object. You have to manually select both the "
                u"language and the object."
    )

    @button.buttonAndHandler(_(u"add_translations",
                               default=u"Add translations"))
    def handle_add(self, action):
        data, errors = self.extractData()
        if not errors:
            content = data['content']
            language = data['language']
            ITranslationManager(self.context)\
                .register_translation(language, content)
            ILanguage(content).set_language(language)

        return self.request.response.redirect(
            self.context.absolute_url() + '/add_translations')
