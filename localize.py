from enum import Enum
from dataclasses import dataclass
import os
from pathlib import Path

import typer
from rich import print

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

# DONE: setttings from command line
# TODO: readme
# TODO: progress and colors

# ---------- Settings ----------

class LogLevel(str, Enum):
    info = 'info'
    group = 'group'
    file = 'file'
    string = 'string'
    
    @property
    def int_value(self) -> int:
        return list(LogLevel).index(self)
    
    def __ge__(self, other):
        return self.int_value >= other.int_value

@dataclass
class Settings:
    base_language: str = 'en'
    override: bool = False

    files: list[str] = None # all
    keys: list[str] = None # all
    languages: list[str] = None # all

    log_level: LogLevel = LogLevel.string

Languages = dict[str, StringsFile]
SearchResult = dict[FileGroup, Languages]

# ---------- Search for files ----------

def search_groups() -> SearchResult:
    files: SearchResult = {}

    for path in Path('.').rglob('*.lproj/*.strings'):
        directory = path.parent.parent
        language = path.parent.stem.lower()
        filename = path.stem
        
        file_group = FileGroup(str(directory), str(filename))
        
        if not files.get(file_group):
            files[file_group] = {}

        files[file_group][language] = StringsFile(path)

    return files

# ---------- Translate files ----------

def translate_groups(groups: SearchResult, settings: Settings):
    for file_group, languages in groups.items():
        
        if settings.files and file_group.filename not in settings.files:
            continue

        base = languages.get('base') or languages.get(settings.base_language)

        if not base:
            print(f'\n[x] No base language for {file_group}')
            continue

        try:
            base.read()
        except UnicodeDecodeError:
            print(f'\n[x] Error reading base file "{base.path}"')
            continue

        if settings.log_level >= LogLevel.group:
            print(f'\nStarting {file_group} with {len(base.strings)} strings')
            
        translate_languages(languages, base = base, settings = settings)

def translate_languages(languages: Languages, base: StringsFile, settings: Settings):
    for language_code, strings_file in languages.items():
        
        if strings_file.path == base.path:
            continue

        if settings.languages and language_code not in settings.languages:
            continue

        translator = Translator(target_lang = language_code, origin_lang = settings.base_language)    
        
        try:
            strings_file.read()
        except UnicodeDecodeError:
            print(f'    [x] Error reading "{strings_file.path}"')
            continue

        if settings.log_level >= LogLevel.file:
            print(f'    {base.path.stem}.{language_code}')
            
        translate_strings(strings_file, base = base, translator = translator, settings = settings)
        
def translate_strings(strings_file: StringsFile, base: StringsFile, translator: Translator, settings: Settings):
    for base_string in base.strings.values():
            
        if not settings.override and base_string.key in strings_file.strings:
            continue

        if settings.keys and base_string.key not in settings.keys:
            continue
        
        new_string = String(
            key = base_string.key,
            value = translator.translate(base_string.value),
            comment = base_string.comment
        )
        
        strings_file.strings[base_string.key] = new_string
        
        if settings.log_level >= LogLevel.string:
            print(f'        {base_string.key} = {new_string.value}')
    
    try:
        strings_file.save()
    except UnicodeEncodeError:
        print(f'        [x] Error saving "{strings_file.path}"')
        
# ---------- Main ----------

def search_and_translate(settings: Settings):
    os.system('clear')
    groups = search_groups()
    translate_groups(groups, settings = settings)

def main(
    base_language: str = 'en',
    override: bool = False,
    file: list[str] = None, # all
    key: list[str] = None, # all
    language: list[str] = None, # all
    log_level: LogLevel = LogLevel.file):
    
    search_and_translate(
        Settings(
            base_language = base_language,
            override = override,
            files = file,
            keys = key,
            languages = language,
            log_level = log_level
        )
    )


# ---------- Run ----------

if __name__ == '__main__':
    typer.run(main)