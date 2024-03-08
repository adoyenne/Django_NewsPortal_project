from django import template
import re

register = template.Library()

@register.filter
def censor(text):
    if not isinstance(text, str):
        raise ValueError("The censor filter can only be applied to strings.")

    # Список нецензурных слов
    bad_words = ['редиска']  #  слова для цензора

    # Заменяем нецензурных слов на звездочки
    for word in bad_words:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        text = pattern.sub(word[0] + '*' * (len(word) - 1), text)

    return text