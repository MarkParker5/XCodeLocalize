import os
from pathlib import Path
from pprint import pprint
from enum import IntEnum

from Strings import FileGroup, StringsFile, String
from Translator import Translator


# DONE: parse using regex
# DONE: find all .strings, .storyboard, .intentdefinition files via glob
# DONE: get languages from project file ?

 # TODO: safe translate quoted strings
# result = ''
# if m := re.search(r'‘(.+?)’', value):
#     quoted = f'‘{m.group(1)}’'
#     value = value.replace(quoted, '_QUOTED_')
#     result = translate(text = value, lang = lang).replace('_QUOTED_', quoted)
# else:
#     result = translate(text = value, lang = lang)

# TODO: setttings from command line
# TODO: readme
# TODO: progress and colors

# ---------- Settings ----------

class LogLevel(IntEnum):
    info = 0
    group = 1
    file = 2
    string = 3

class Settings:
    base_language: str = 'en'
    override: bool = True # False

    files: list[str] = []
    keys: list[str] = []
    languages: list[str] = []

    log_level: LogLevel = LogLevel.string

os.system('clear')

# ---------- Search for files ----------

files: dict[FileGroup, dict[str, StringsFile]] = {}

for path in Path('.').rglob('*.lproj/*.strings'):
    directory = path.parent.parent
    language = path.parent.stem.lower()
    filename = path.stem
    
    file_group = FileGroup(str(directory), str(filename))
    
    if not files.get(file_group):
        files[file_group] = {}

    files[file_group][language] = StringsFile(path)

# print('Found files:', end = ' ')
# pprint(files)

# ---------- Translate files ----------

print('Translating...')

for file_group, languages in files.items():

    if Settings.files and file_group.filename not in Settings.files:
        continue

    base = languages.get('base') or languages.get(Settings.base_language)

    if not base:
        print(f'\n[x] No base language for {file_group}')
        continue

    try:
        base.read()
    except UnicodeDecodeError:
        print(f'\n[x] Error reading base file "{base.path}"')
        continue

    if Settings.log_level >= LogLevel.group:
        print(f'\nStarting {file_group} with {len(base.strings)} strings')

    for language, strings_file in languages.items():
        if strings_file.path == base.path:
            continue

        if Settings.languages and language not in Settings.languages:
            continue

        translator = Translator(target_lang = language, origin_lang = Settings.base_language)    
        
        try:
            strings_file.read()
        except UnicodeDecodeError:
            print(f'    [x] Error reading "{strings_file.path}"')
            continue

        if Settings.log_level >= LogLevel.file:
            print(f'    {file_group}.{language}')

        for base_string in base.strings.values():
            
            if not Settings.override or base_string.key in strings_file.strings:
                continue

            if Settings.keys and base_string.key not in Settings.keys:
                continue
            
            new_string = String(
                key = base_string.key,
                value = translator.translate(base_string.value),
                comment = base_string.comment
            )
            
            strings_file.strings[base_string.key] = new_string
            
            if Settings.log_level >= LogLevel.string:
                print(f'        {base_string.key} = {new_string.value}')
        
        try:
            strings_file.save()
        except UnicodeEncodeError:
            print(f'        [x] Error saving "{strings_file.path}"')