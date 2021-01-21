import os
import django
import pycountry
import sys
sys.path.append('..')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingomingo.settings')
django.setup()

from mainapp.models import Language

# https://www.wikiwand.com/en/List_of_most_commonly_learned_foreign_languages_in_the_United_States
lang_list_alpha_3 = ['spa', 'fra', 'deu', 'eng', 'jpn', 'ita', 'zho', 'ara', 'rus', 'kor', 'por', 'heb', 'hin',
                     'nep', 'fas', 'tgl', 'hin', 'afr', 'nld', 'ben', 'tur', 'swa', 'urd']

lang_list_alpha_3.sort()
lang_names = []
for lang in lang_list_alpha_3:
    lang_names.append(pycountry.languages.get(alpha_3=lang).name)
    obj, created = Language.objects.get_or_create(alpha_3=lang, name=pycountry.languages.get(alpha_3=lang).name)
    if created:
        str(obj) + ' was added to database'

print('language database addition script finished successfully')
3