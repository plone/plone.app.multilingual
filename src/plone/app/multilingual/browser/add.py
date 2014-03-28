from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.multilingual import _
from plone.app.multilingual.browser.interfaces import IAddTranslation
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.interfaces import ILanguage
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from plone.z3cform.fieldsets import extensible
from plone.z3cform.fieldsets.interfaces import IFormExtender
from z3c.form import button
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import ComputedWidgetAttribute
from zope import schema
from zope.component import adapts
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import implements, alsoProvides
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError


class AddViewTraverser(object):
    """Add view traverser.
    """
    adapts(IFolderish, Interface)
    implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        ttool = getToolByName(self.context, 'portal_types')
        ti = ttool.getTypeInfo(name)
        if not IDexterityFTI.providedBy(ti):
            # we are not on DX content
            baseUrl = self.context.absolute_url()
            url = '%s/@@add_at_translation?type=%s' % (baseUrl, name)
            return self.request.response.redirect(url)
        # set the self.context to the place where it should be stored
        if not IFolderish.providedBy(self.context):
            self.context = self.context.__parent__
        if ti is not None:
            add_view = queryMultiAdapter((self.context, self.request, ti),
                                         name='babel_view')
            if add_view is None:
                add_view = queryMultiAdapter((self.context, self.request, ti))
            if add_view is not None:
                add_view.__name__ = ti.factory
                return add_view.__of__(self.context)

        raise TraversalError(self.context, name)


class MultilingualAddForm(DefaultAddForm):

    babel = ViewPageTemplateFile("templates/dexterity_edit.pt")

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

        for field in self.fields.keys():
            if field in self.schema:
                if ILanguageIndependentField.providedBy(self.schema[field]):
                    self.widgets[field].addClass('languageindependent')
            # With plone.autoform, fieldnames from additional schematas
            # reference their schema by prefixing their fieldname
            # with schema.__identifier__ and then a dot as a separator
            # See autoform.txt in the autoform package
            if '.' in field:
                schemaname, fieldname = field.split('.')
                for schema in self.additionalSchemata:
                    if schemaname == schema.__identifier__ \
                       and fieldname in schema:
                        if ILanguageIndependentField.providedBy(schema[fieldname]):  # noqa
                            self.widgets[field].addClass('languageindependent')
        self.babel_content = super(MultilingualAddForm, self).render()
        return self.babel()

    @property
    def max_nr_of_buttons(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
        return settings.buttons_babel_view_up_to_nr_translations


class IMultilingualAddFormMarkerFieldMarker(Interface):
    """Marker interfaces for add form marker fields"""


class IMultilingualAddFormMarker(model.Schema):
    """Marker metadata fields for multilingual add form"""
    directives.mode(pam_tg=HIDDEN_MODE)
    pam_tg = schema.ASCIILine(title=u"Translated content")
    pam_old_lang = schema.ASCIILine(title=u"Old language")

alsoProvides(IMultilingualAddFormMarker['pam_tg'],
             IMultilingualAddFormMarkerFieldMarker)

alsoProvides(IMultilingualAddFormMarker['pam_old_lang'],
             IMultilingualAddFormMarkerFieldMarker)


def get_multilingual_add_form_tg_value(adapter):
    session_manager = getToolByName(adapter.context, 'session_data_manager')
    session_data = session_manager.getSessionData()
    return session_data.get('tg', '')


MultilingualAddFormTgValue = ComputedWidgetAttribute(
    get_multilingual_add_form_tg_value,
    context=None, request=None, view=None, widget=None,
    field=IMultilingualAddFormMarker['pam_tg']
)


def get_multilingual_add_form_old_lang_value(adapter):
    session_manager = getToolByName(adapter.context, 'session_data_manager')
    session_data = session_manager.getSessionData()
    return session_data.get('old_lang', '')


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


class MultilingualAddFormExtender(extensible.FormExtender):
    implements(IFormExtender)
    adapts(Interface, IPloneAppMultilingualInstalled, MultilingualAddForm)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        groups = getattr(self.form, 'groups', None)
        if isinstance(groups, list) and len(groups):
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

    def __init__(self, context, request, ti):
        super(DefaultAddView, self).__init__(context, request)
        self.ti = ti

        # Set portal_type name on newly created form instance
        if self.form_instance is not None \
           and not getattr(self.form_instance, 'portal_type', None):
            self.form_instance.portal_type = ti.getId()


class AddTranslationsForm(AutoExtensibleForm, Form):

    schema = IFormFieldProvider(IAddTranslation)
    ignoreContext = True
    label = _(u"label_add_translations", default=u"Add translations")
    description = _(u"long_description_add_translations", default=
                    u"This form allows you to add currently existing "
                    u"objects to be the translations of the current "
                    u"object. You have to manually select both the "
                    u"language and the object.")

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
