from plone.app.multilingual.interfaces import ITranslationManager


def translate(content, target_language='en'):
    manager = ITranslationManager(content)
    manager.add_translation(target_language)
    return manager.get_translation(target_language)
