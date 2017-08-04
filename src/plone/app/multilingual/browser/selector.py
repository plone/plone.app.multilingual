# -*- coding: utf-8 -*-
from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.app.multilingual import logger
from plone.app.multilingual.api import get_translation_manager
from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import NOTG
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryAdapter
from zope.component.hooks import getSite
from ZTUtils import make_query


def addQuery(request, url, exclude=tuple(), **extras):
    """Adds the incoming GET query to the end of the url
    so that is propagated through the redirect hoops
    """
    formvariables = {}
    for k, v in request.form.items():
        if k not in exclude:
            if isinstance(v, unicode):
                formvariables[k] = v.encode('utf-8')
            else:
                formvariables[k] = v
    formvariables.update(extras)
    try:
        if len(formvariables) > 0:
            url += '?' + make_query(formvariables)
    # Again, LinguaPlone did this try/except here so I'm keeping it.
    except UnicodeError:
        pass
    return url


def getPostPath(context, request):
    """Finds the path to be added at the end of a context.

    This is useful because you might have a view or even something more long
    (form and widget traversing) at the very end of the absolute_url
    of a translated item.
    When you get the translated item absolute_url,
    you want to also have the eventual views etc ported over:
    this function does that.
    """
    # This is copied over from LinguaPlone
    # because there's a lot of knowledge embed in it.

    # We need to find the actual translatable content object. As an
    # optimization we assume it is within the last three segments.
    path = context.getPhysicalPath()
    path_info = request.get('PATH_INFO', '')
    match = [p for p in path[-3:] if p]
    current_path = [pi for pi in path_info.split('/') if pi]
    append_path = []
    stop = False
    while current_path and not stop:
        check = current_path.pop()
        if check == 'VirtualHostRoot' or check.startswith('_vh_'):
            # Once we hit a VHM marker, we should stop
            break
        if check not in match:
            append_path.insert(0, check)
        else:
            stop = True
    if append_path:
        append_path.insert(0, '')
    return "/".join(append_path)


NOT_TRANSLATED_YET_TEMPLATE = '/not_translated_yet'


class LanguageSelectorViewlet(LanguageSelector):
    """Language selector for translatable content.
    """

    def languages(self):
        languages_info = super(LanguageSelectorViewlet, self).languages()
        registry = getUtility(IRegistry)
        always_show_selector = registry['plone.always_show_selector']
        results = []
        translations = []
        translation_group = queryAdapter(self.context, ITG)

        if translation_group is None:
            translation_group = NOTG

        # there is no translation_manager on site root
        # using try/except to prevent failing for now
        try:
            translation_manager = get_translation_manager(self.context)
            translations = translation_manager.get_translated_languages()
        except TypeError as e:
            logger.debug(e)

        for lang_info in languages_info:

            if not (always_show_selector or
                    lang_info['code'] in translations or
                    translation_group == 'notg'
                    ):
                continue

            # Avoid to modify the original language dict
            data = lang_info.copy()
            data['translated'] = lang_info['code'] in translations
            query_extras = {
                'set_language': data['code'],
            }
            post_path = getPostPath(self.context, self.request)
            if post_path:
                query_extras['post_path'] = post_path
            site = getSite()
            # if there is no translationgroup,
            # we still want to switch language in the same context
            if translation_group == 'notg':
                data['url'] = self.context.absolute_url() + \
                    '/?set_language=' + lang_info['code']
            else:
                data['url'] = addQuery(self.request,
                                       site.absolute_url().rstrip("/") +
                                       "/@@multilingual-selector/%s/%s" % (
                                           translation_group,
                                           lang_info['code']
                                       ),
                                       **query_extras)
            results.append(data)

        return results
