from flask import session
import locale
import glob
import json

def switch_language():
     # set language
    app_language = 'ja_JP'
    locale.setlocale(locale.LC_ALL, app_language)
    languages = {}
    language_list = glob.glob("website/language/*.json")
    for lang in language_list:
      filename = lang.split('/')
      lang_code = filename[2].split('.')[0]

      with open(lang, 'r', encoding='utf8') as file:
          languages[lang_code] = json.loads(file.read())
    return languages

    # end set languages
