from enum import Enum
from dataclasses import dataclass
import os
from pathlib import Path

import typer
from rich import print
from rich.progress import Progress
from rich.table import Table
from rich.console import Console

from Strings import FileGroup, StringsFile, String
from Translator import Translator


# DONE: parse using regex
# DONE: find all .strings, .storyboard, .intentdefinition files via glob
# DONE: get languages from project file ?

# DONE: setttings from command line
# DONE: progress and colors

# TODO: readme
# TODO: safe translate quoted strings
# result = ''
# if m := re.search(r'‘(.+?)’', value):
#     quoted = f'‘{m.group(1)}’'
#     value = value.replace(quoted, '_QUOTED_')
#     result = translate(text = value, lang = lang).replace('_QUOTED_', quoted)
# else:
#     result = translate(text = value, lang = lang)

# ---------- Settings ----------

class LogLevel(str, Enum):
    progress = 'progress'
    errors = 'errors'
    group = 'group'
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

# ---------- Global ----------

settings: Settings
progress: Progress
update_progress: callable

# ---------- Logging ----------

def error(text: str):
    global settings
    if settings.log_level >= LogLevel.errors:
        print(f'[red bold]:warning: {text}')
    
def table(groups: SearchResult):
    console = Console()
    
    table = Table('File', 'Languages', '')
    for group, languages in groups.items():
        table.add_row(group.filename, ', '.join(sorted([code for code in languages.keys()])), str(len(languages)))
    
    console.print(table)

# ---------- Search files ----------

def search_groups() -> SearchResult:
    global settings, progress, update_progress
    files: SearchResult = {}

    for path in Path('.').rglob('*.lproj/*.strings'):
        directory = path.parent.parent
        language = path.parent.stem.lower()
        filename = path.stem
        
        if settings.files and filename not in settings.files:
            continue
        
        if settings.languages and language not in [*settings.languages, settings.base_language, 'base']:
            continue
        
        file_group = FileGroup(str(directory), str(filename))
        
        if not files.get(file_group):
            files[file_group] = {}

        files[file_group][language] = StringsFile(path)

    return files

# ---------- Translate files ----------

def translate_groups(groups: SearchResult):
    global settings, progress, update_progress
    
    for file_group, languages in groups.items():

        base = languages.get('base') or languages.get(settings.base_language)

        if not base:
            error(f'No base language for {file_group}')
            update_progress(len(languages))
            continue

        try:
            base.read()
        except UnicodeDecodeError:
            error(f'Error reading base file "{base.path}"')
            update_progress(len(languages))
            continue

        if settings.log_level >= LogLevel.group:
            print(f'\n:information:Translating "{file_group}" with {len(base.strings)} strings for {len(languages)} languages')
            
        translate_languages(languages, base)

def translate_languages(languages: Languages, base: StringsFile):
    global settings, progress, update_progress
    
    for language_code, strings_file in languages.items():
        
        if strings_file.path == base.path:
            update_progress()
            continue

        translator = Translator(target_lang = language_code, origin_lang = settings.base_language)    
        
        try:
            strings_file.read()
        except UnicodeDecodeError:
            error(f'Error reading "{strings_file.path}"')
            update_progress()
            continue
        
        translate_strings(strings_file, base, translator)
        update_progress()
        
def translate_strings(strings_file: StringsFile, base: StringsFile, translator: Translator):
    global settings, progress
    
    filtered_base = [
        string for string in base.strings.values()
        if (not settings.keys or string.key in settings.keys) and
        (settings.override or not string.key in strings_file.strings)
    ]
    
    current_file_task = progress.add_task(
        f'{strings_file.path.stem} -> {translator.target_lang}', 
        total = len(filtered_base)
    )
    
    for base_string in filtered_base:
                    
        new_string = String(
            key = base_string.key,
            value = translator.translate(base_string.value),
            comment = base_string.comment
        )
        
        strings_file.strings[base_string.key] = new_string
        
        if settings.log_level >= LogLevel.string:
            print(f'\t{base_string.key} = {new_string.value}')
            
        progress.advance(current_file_task)
    
    try:
        strings_file.save()
    except UnicodeEncodeError:
        error(f'Error saving "{strings_file.path}"')
        
    progress.remove_task(current_file_task)
        
# ---------- Main ----------

def search_and_translate():
    global progress, update_progress, console
    
    groups = search_groups()
    table(groups)
    
    with Progress() as p:
        progress = p
        files_task = progress.add_task('Total progress', total = len([file for langs in groups.values() for file in langs]))
        update_progress = lambda count = 1: progress.advance(files_task, count)
        translate_groups(groups)

def main(
    base_language: str = 'en',
    override: bool = False,
    file: list[str] = None, # all
    key: list[str] = None, # all
    language: list[str] = None, # all
    log_level: LogLevel = LogLevel.group):
    
    global settings
    settings = Settings(
            base_language = base_language,
            override = override,
            files = file,
            keys = key,
            languages = language,
            log_level = log_level
        )
    
    search_and_translate()

# ---------- Run ----------

if __name__ == '__main__':
    typer.run(main)