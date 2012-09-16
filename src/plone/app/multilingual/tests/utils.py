from plone.multilingual.interfaces import ITranslationManager


def makeContent(context, portal_type, id='doc', **kw):
    context.invokeFactory(portal_type, id, **kw)
    return getattr(context, id)


def makeTranslation(content, language='en'):
    manager = ITranslationManager(content)
    manager.add_translation(language)
    import transaction; transaction.commit()
    return manager.get_translation(language)
