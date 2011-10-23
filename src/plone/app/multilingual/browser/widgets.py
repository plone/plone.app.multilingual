from zope.app.form.browser import ObjectWidget, ListSequenceWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.app import zapi
from zope.app.form.browser.objectwidget import ObjectWidgetView, ObjectWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from mpgsite.interfaces import IMpgSequenceField
from zope.app.form.browser.widget import BrowserWidget
from zope.app.form.interfaces import IDisplayWidget, IInputWidget
from zope.app.form import InputWidget
from zope.app.form.interfaces import WidgetInputError, MissingInputError
from zope.schema.interfaces import ValidationError, InvalidValue
from zope.app.i18n import MessageFactory
_=MessageFactory('mpgsite')
from zope.i18n import translate
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app.form.browser.widget import renderElement
from zope.app.form.interfaces import ConversionError
from zope.app.form.browser import TextWidget, SequenceDisplayWidget
from zope.security.proxy import removeSecurityProxy
import sys
from zope.schema import Object
from zope.annotation.interfaces import IAnnotations

class MpgTextWidget(TextWidget):
    def _toFieldValue(self, input):
        try:
            value = unicode(input)
        except ValueError, v:
            raise ConversionError(_("Invalid text data"), v)
        return value


class I18NTextLineWidget(MpgTextWidget):
   def __call__(self):
        value = self._getFormValue()
        if value is None or value == self.context.missing_value:
            value = ''

        kwargs = {'type': self.type,
                  'name': self.name,
                  'id': self.name,
                  'value': value,
                  'cssClass': self.cssClass,
                  'style': self.style,
                  'extra': self.extra}
        if self.displayMaxWidth:
            kwargs['maxlength'] = self.displayMaxWidth # TODO This is untested.

        return renderElement(self.tag, **kwargs)

class SimpleObjectWidget(ObjectWidget):
    """A Widget that shows all widgets of an object"""
    def __call__(self,context,request):
        xhtml=''
        for widget in context.subwidgets:
            xhtml +=widget()
        return xhtml


def ObjectInputWidgetDispatcher(context, request):
    """Dispatch widget for Object schema field to widget that is
    registered for (IObject, schema, IBrowserRequest) where schema
    is the schema of the object."""
    class Obj(object):
        implements(context.schema)

    widget=zapi.getMultiAdapter((context, Obj(), request), IInputWidget)
    return widget

class ObjectInputWidget(ObjectWidget):
    def getInputValue(self):
        errors = []
        content = self.factory()
        for name in self.names:
            try:
                setattr(content, name, self.getSubWidget(name).getInputValue())
            except Exception, e:
                errors.append(e)
                if self._error is None:
                    self._error = {}

                if name not in self._error:
                    self._error[name] = e

        # Don't raise errors when widget operations (add to list, remove element, ...) are processed
        if ( 'mpgsite.no_form_action' not in IAnnotations(self.request) ) and errors:
            raise errors[0]

        return content

def FileLocal(filename,depth):
    path='/'.join(sys._getframe(depth).f_globals['__file__'].split('/')[:-1])
    return path + '/' +  filename
    

class TemplateObjectWidget(ObjectWidget):
    """A Widget that uses a page template"""
    def __init__(self, context, request, factory, template_, **kw):
        super(TemplateObjectWidget, self).__init__(context, request, factory, **kw)
        class TemplateObjectWidgetView(ObjectWidgetView):
            template = ViewPageTemplateFile(template_)
        self.view = TemplateObjectWidgetView(self, request)

def TemplateObjectWidgetFactory(context,request,factory,template):
    widget=TemplateObjectWidget(context,request,factory,FileLocal(template,2))
    return widget


class TemplateSequenceWidget(ListSequenceWidget):
    def __init__(self, context, field, request, subwidget=None):
        super(TemplateSequenceWidget, self).__init__(context, field, request, subwidget)

        # This isn't really related to an ObjectView but provides a convinient
        # way of providing a template base Widget.
        class TemplateObjectWidgetView(ObjectWidgetView):
            template = ViewPageTemplateFile("mpgl1sequence.pt")

        self.view = TemplateObjectWidgetView(self, request)

    def __call__(self):
        return self.view()


def DictionaryWidgetFactory(field,request):
    widget=zapi.getMultiAdapter((field,field.key_type,field.value_type,request),IInputWidget)
    return widget



class SimpleDictionaryWidget(BrowserWidget, InputWidget):
    """A widget for editing arbitrary dictionaries
    
        key_editsubwidget - optional edit subwidget for key components
        key_displaysubwidget - optional display subwidget for key components
        value_editsubwidget - optional edit subwidget for value components
    """
    implements(IInputWidget)
    _type= dict
    
    def __init__(self,context,key_type,value_type,request,key_editsubwidget=None,key_displaysubwidget=None,value_editsubwidget=None):
        super(SimpleDictionaryWidget,self).__init__(context,request)
        self.key_editsubwidget=key_editsubwidget
        self.key_displaysubwidget=key_displaysubwidget
        self.value_editsubwidget=value_editsubwidget
        self.context.key_type.bind(object())
        self.mayadd=True

    def _widgetpostproc(self,widget,key,keyorvalue):
        """For manipulating css classes of given elements"""

    def _sortkeys(self,keys):
        newkeys=[x for x in keys.__iter__()]
        newkeys.sort()
        return newkeys

    def _renderKeyAndCheckBox(self,render,key,i):
        render.append('<input class="editcheck" type="checkbox" name="%s.remove_%d" />' %(self.name,i))
        keydisplaywidget=self._getWidget(str(i),IDisplayWidget,self.context.key_type,self.key_displaysubwidget,'key-display')
        self._widgetpostproc(keydisplaywidget,key,'key-display')
        keydisplaywidget.setRenderedValue(key)
        render.append(keydisplaywidget())

    def _renderitems(self,render):
        keys=self._data.keys()
        keys=self._sortkeys(keys)
        for i in range(len(keys)):
            key=keys[i]
            value=self._data[key]
            render.append('<div>')
            render.append('<span>')
            self._renderKeyAndCheckBox(render,key,i)
            keyhiddenwidget=self._getWidget(str(i),IInputWidget,self.context.key_type,self.key_editsubwidget,'key')
            keyhiddenwidget.setRenderedValue(key)
            render.append(keyhiddenwidget.hidden())
            render.append('</span>')
            valuewidget=self._getWidget(str(i),IInputWidget,self.context.value_type,self.value_editsubwidget,'value')
            self._widgetpostproc(valuewidget,key,'value-edit')
            valuewidget.setRenderedValue(value)
            render.append('<span>' + valuewidget() + '</span></div>')
    
    def _renderbuttons(self,render):
        buttons = ''
        if ( len(self._data)>0 ) and len(self._data) > self.context.min_length:
            button_label = _('remove-selected-items', "Remove selected items")
            button_label = translate(button_label, context=self.request,default=button_label)
            buttons += ('<input type="submit" value="%s" name="%s.remove"/>' % (button_label, self.name))
        if (self.context.max_length is None or len(self._data) < self.context.max_length) and self.mayadd:
            field = self.context.value_type
            button_label = _('Add %s')
            button_label = translate(button_label, context=self.request, default=button_label)
            button_label = button_label % (field.title or field.__name__)
            buttons += '<input type="submit" name="%s.add" value="%s" />' % (self.name, button_label)
            self._keypreproc()
            newkeywidget=self._getWidget('new',IInputWidget,self.context.key_type,self.key_editsubwidget,'key')
            self._keypostproc()
            self._widgetpostproc(newkeywidget,'','key-edit')
            render.append('<div><span>%s</span></div>' %(newkeywidget(),) )
        if buttons:
            render.append('<div><span>%s</span></div>' % buttons)
    
    def __call__(self):
        """Render the Widget"""
        assert self.context.key_type is not None
        assert self.context.value_type is not None
        render=[]
        render.append('<div><div id="%s">' % (self.name,))
        if not self._getRenderedValue():
            if self.context.default is not None:
                self._data=self.context.default
            else:
                self._data=self._type()
        
        self._renderitems(render)
        
        render.append('</div>')
        # possibly generate the "remove" and "add" buttons
        self._renderbuttons(render)
        
        render.append(self._getPresenceMarker(len(self._data)))
        render.append('</div>')
        text="\n".join(render)
        return text

    def _getWidget(self,i,interface,value_type,customwidget,mode):
        if customwidget is not None:
            widget=zapi.getMultiAdapter((value_type,self.request),interface,name=self.customwidget)
        else:
            widget=zapi.getMultiAdapter((value_type,self.request),interface)
        widget.setPrefix('%s.%s.%s.'%(self.name,i,mode))
        return widget

    def hidden(self):
        self._getRenderedValue()
        keys=self._data.keys()
        parts=[self._getPresenceMarker(len(self._data))]

        for i in range(len(keys)):
            key=keys[i]
            value=self._data[key]
            keywidget=self._getWidget(str(i),IInputWidget,self.context.key_type,self.key_displaysubwidget,'key')
            keywidget.setRenderedValue(key)
            valuewidget=self._getWidget(str(i),IInputWidget,self.context.value_type,self.value_editsubwidget,'value')
            parts.append(keywidget.hidden() + valuewidget.hidden())

        return "\n".join(parts)

    def _getPresenceMarker(self, count=0):
        return ('<input type="hidden" name="%s.count" value="%d" />'% (self.name, count))

    def _getRenderedValue(self):
        if not self._renderedValueSet():
            if self.hasInput():
                self._data=self._generateDict()
            else:
                self._data={}
        if self._data is None:
            self._data=self._type()
        if len(self._data) < self.context.min_length:
            """Don't know, what to do here :-("""
        return self._data

    def getInputValue(self):
        if self.hasInput():
            dict=self._type(self._generateDict())
            if dict != self.context.missing_value:
                self.context.validate(dict)
            elif self.context.required:
                raise MissingInputError(self.context.__name__,self.context.title)
            return dict
        raise MissingInputError(self.context.__name__, self.context.title)
    
    def applyChanges(self,content):
        field=self.context
        value=self.getInputValue()
        change=field.query(content,self) != value
        if change:
            field.set(content,value)
        return change

    def hasInput(self):
        return (self.name+".count") in self.request.form

    def _generateDict(self):
        len_prefix=len(self.name)
        adding=False
        removing=[]
        if self.context.value_type is None:
            return []

        try:
            count=int(self.request.form[self.name+".count"])
        except ValueError:
            raise WidgetInputError(self.context.__name__, self.context.title)

        keys={}
        values={}
        for i in range(count):
            remove_key="%s.remove_%d" % (self.name,i)
            if remove_key not in self.request.form:
                keywidget=self._getWidget(str(i),IInputWidget,self.context.key_type,self.key_displaysubwidget,'key')
                valuewidget=self._getWidget(str(i),IInputWidget,self.context.value_type,self.value_editsubwidget,'value')
                keys[i]=keywidget.getInputValue()
                values[i]=valuewidget.getInputValue()
        adding=(self.name+".add") in self.request.form
        
        mykeys=keys.items()
        mykeys.sort()
        dict={}
        for (i,key) in mykeys:
            dict[key]=values[i]
            
        if adding:
            newkeywidget=self._getWidget('new',IInputWidget,self.context.key_type,self.key_displaysubwidget,'key')
            newkey=newkeywidget.getInputValue()
            self.context.key_type.validate(newkey)
            if dict.has_key(newkey):
                raise InvalidValue
            dict[newkey]=self.context.value_type.missing_value
            
        return dict

    def _keypreproc(self):
        """Only for subclassing"""

    def _keypostproc(self):
        """Only for Subclassing"""

class FilterVocabulary(SimpleVocabulary):
    """Removes All terms from a vocabulary that are contained
        in a given dictionary. This is useful for filtering
        the vocabulary that is used to fill the new Choice-Widget
        of a Dict-Widget"""
    def __init__(self,vocabulary,dictionary):
        terms=[]
        self.empty=True
        for term in vocabulary._terms:
            if not dictionary.has_key(term.value):
                terms.append(term)
                self.empty=False
        SimpleVocabulary.__init__(self,terms)

class ChoicyDictionaryWidget(SimpleDictionaryWidget):
    """This widget reduces available choices in a key_value-choice to only
        include values not already used"""
    def _keypreproc(self):
        """We use the keypreproc-hook to install a filter vocabulary
            that removes all choices from the original vocabulary that
            are already used."""
        if self.context.key_type.vocabulary is None:
            return
        self.old_key_vocabulary=self.context.key_type.vocabulary
        self.context.key_type.vocabulary=FilterVocabulary(self.context.key_type.vocabulary,self._data)
        if self.context.key_type.vocabulary.empty:
            self.mayadd=False
            

    def _keypostproc(self):
        """Reinstall the original dictionary"""
        if self.context.key_type.vocabulary is None:
            return
        self.context.key_type.vocabulary=self.old_key_vocabulary

    def _renderbuttons(self,render):
        self._keypreproc()
        super(ChoicyDictionaryWidget,self)._renderbuttons(render)
        self._keypostproc()

class PathWidget(MpgTextWidget):
    """A Widget from zope.app.homefolder for entering absolute paths to objects"""
    def _toFieldValue(self, input):
        path = super(PathWidget, self)._toFieldValue(input)
        root = zapi.getRoot(self.context.context)
        try:
            proxy = zapi.traverse(root, path)
        except TraversalError, e:
            raise ConversionError(_('path is not correct !'), e)
        else:
            return removeSecurityProxy(proxy)

    def _toFormValue(self, value):
        if value is None:
            return ''
        return zapi.getPath(value)

class MpgSetInputWidget(ListSequenceWidget):
    _type=set
    def _generateSequence(self):
        """This is a modified method to provide functionality
            for a +/- -controlled SetWidget"""
        if self.context.value_type is None:
            return set([])
        try:
            count = int(self.request.form[self.name + ".count"])
        except ValueError:
            raise WidgetInputError(self.context.__name__, self.context.title)

        # pre-populate
        sequence=[]

        for i in range(count):
            widget = self._getWidget(i)
            if widget.hasValidInput():
                # catch and set sequence widget errors to ``_error`` attribute
                try:
                    sequence.append(widget.getInputValue())
                except WidgetInputError, error:
                    self._error = error
                    raise self._error

            remove_key = "%s.remove_%d" % (self.name, i)
            add_key = "%s.add_%d" % (self.name, i)
            if add_key in self.request.form:
                sequence.append(self.context.value_type.missing_value)
            if remove_key in self.request.form:
                del sequence[i]
        
        if (self.name + '.add') in self.request.form:
            sequence.append(self.context.value_type.missing_value)
        return set(sequence)
    
    def _getRenderedValue(self):
        value=super(MpgSetInputWidget,self)._getRenderedValue()
        return set(value)
    
    def __call__(self):
        self._update()
        class TemplateObjectWidgetView(ObjectWidgetView):
            template = ViewPageTemplateFile("mpgpml1set.pt")
        template = TemplateObjectWidgetView(self, self.request)
        
        return template()

class SetDisplayWidget(SequenceDisplayWidget):
    tag='ul'
    cssClass="setWidget"
    # TODO: missing-value-messages abgleichen


class MpgListInputWidget(ListSequenceWidget):
    def _generateSequence(self):
        """This is a modified method to provide functionality
            for a +/- -controlled SequenceWidget"""
        if self.context.value_type is None:
            return []
        try:
            count = int(self.request.form[self.name + ".count"])
        except ValueError:
            raise WidgetInputError(self.context.__name__, self.context.title)

        # pre-populate
        sequence = [None] * count
        found_up=None
        found_down=None
        found_remove=False
        found_add=None
        for i in reversed(range(count)):
            widget = self._getWidget(i)
            if widget.hasValidInput():
                # catch and set sequence widget errors to ``_error`` attribute
                try:
                    sequence[i] = widget.getInputValue()
                except WidgetInputError, error:
                    self._error = error
                    raise self._error

            remove_key = "%s.remove_%d" % (self.name, i)
            add_key = "%s.add_%d" % (self.name, i)
            up_key = "%s.up_%d" % (self.name,i)
            down_key = "%s.down_%d" % (self.name,i)
            if add_key in self.request.form:
                found_add=i
            if remove_key in self.request.form:
                del sequence[i]
                found_remove=True
            if down_key in self.request.form:
                found_down=i
            if up_key in self.request.form:
                found_up=i
        if not found_remove:
            if found_up is not None:
                temp=sequence[found_up-1]
                sequence[found_up-1]=sequence[found_up]
                sequence[found_up]=temp
            if found_down is not None:
                temp=sequence[found_down+1]
                sequence[found_down+1]=sequence[found_down]
                sequence[found_down+1]=temp
            if found_add is not None:
                sequence[found_add:0]=[self.context.value_type.default]
                    
        if (self.name + '.add') in self.request.form:
            new=self.context.value_type.default
            import pdb;pdb.set_trace()
            if (new is None) and isinstance(self.context.value_type,Object):
                widget=zapi.getMultiAdapter((self.context.value_type,self.request),IInputWidget)
                new=widget.factory()
            sequence.append(new)
            
        return sequence
    
    def __call__(self):
        self._update()
        self.listcontrollerclasses=''
        if isinstance(self.context.value_type ,Object):
            self.listcontrollerclasses='Object'

        class TemplateObjectWidgetView(ObjectWidgetView):
            template = ViewPageTemplateFile("mpgpml1sequence.pt")
        template = TemplateObjectWidgetView(self, self.request)
        return template()

    def _getRenderedValue(self):
        """Returns a sequence from the request or _data"""
        if self._renderedValueSet():
            if self._data is None:
                sequence=[]
            else:
                sequence = list(self._data)
        elif self.hasInput():
            sequence = self._generateSequence()
        else:
            sequence = []
        # ensure minimum number of items in the form
        while len(sequence) < self.context.min_length:
            # Shouldn't this use self.field.value_type.missing_value,
            # instead of None?
            sequence.append(self.context.value_type.default)
        return sequence


def ObjectSequenceWidget(listfield,objectfield,request):
    """Dispatcher Widget that tries to find a specialized list widget for a
        given Object()-schema with fallback to Object()-default-widget"""
    widget=zapi.queryMultiAdapter((listfield,objectfield.schema,request),IInputWidget)
    if widget is None:
        return MpgListInputWidget(listfield,objectfield,request)
    return widget
