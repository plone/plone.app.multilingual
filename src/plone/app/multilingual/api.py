from plone.app.multilingual.interfaces import ITG
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager


def get_translation_group(content):
    """Get the translation group.

    :param content: Content object which is part of the translation group.
    :type content: Content object
    :returns: UID string identifier of the translation group
    :raises:
        ValueError
    """
    tg = ITG(content)
    if tg is None:
        raise ValueError("No translation group found.")
    return tg


def get_translation_manager(content):
    """Get the translation manager.

    :param content: Content for which the tranlation manager is needed.
    :type content: Content object
    :returns: translation manager instance.
    :raises:
        ValueError
    """
    tm = ITranslationManager(content)
    if tm is None:
        raise ValueError("No translation manager available for this content.")
    return tm


def translate(content, target_language="en"):
    """Translate content into target language.

    :param content: Content to be translated.
    :type content: Content object
    :param target_language: Language to be translated to.
    :type target_language: String
    :returns: Content object in new language
    """
    manager = get_translation_manager(content)
    manager.add_translation(target_language)
    return manager.get_translation(target_language)


def is_translatable(content):
    """Checks if content is translatable.

    :param content: Content to be translated.
    :type content: Content object
    :returns: Boolean
    """
    return ITranslatable.providedBy(content)
