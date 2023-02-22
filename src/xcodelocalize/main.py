from pathlib import Path
from typing import Callable, Any

import typer
from rich import print
from rich.progress import Progress
from rich.table import Table
from rich.console import Console

from .Strings import FileGroup, StringsFile, String
from .Translator import Translator
from .Settings import Settings, LogLevel, SearchResult, Languages


# ---------- Global ----------

settings: Settings
progress: Progress
total_progress_task: Any

# ---------- Logging ----------

def error(text: str):
    global settings
    if settings.log_level >= LogLevel.errors:
        print(f'\n[red bold]:warning: {text}')
    
def table(groups: SearchResult):
    console = Console()
    
    table = Table('File', 'Languages', '')
    for group, languages in groups.items():
        table.add_row(group.filename, ', '.join(sorted([code for code in languages.keys()])), str(len(languages)))
    
    console.print(table)

# ---------- Search files ----------

def search_groups() -> SearchResult:
    global settings
    files: SearchResult = {}

    for path in Path('.').rglob('*.lproj/*.strings'):
        directory = path.parent.parent
        language = path.parent.stem
        filename = path.stem
        
        if settings.files and filename not in settings.files:
            continue
        
        if settings.languages and language not in [*settings.languages, settings.base_language, 'Base']:
            continue
        
        file_group = FileGroup(str(directory), str(filename))
        
        if not files.get(file_group):
            files[file_group] = {}

        files[file_group][language] = StringsFile(path)

    return files

# ---------- Translate files ----------

def translate_groups(groups: SearchResult):
    global settings
    
    for file_group, languages in groups.items():

        base = languages.get('Base') or languages.get(settings.base_language)

        if not base:
            error(f'No base language for {file_group}')
            continue

        try:
            base.read()
        except UnicodeDecodeError:
            error(f'Error reading base file "{base.path}"')
            continue
        
        if settings.format_base:
            try:
                base.save()
            except UnicodeEncodeError:
                error(f'Error saving "{base.path}"')

        if settings.log_level >= LogLevel.group:
            print(f'\n:information: Translating "{file_group}" with {len(base.strings)} strings for {len(languages)} languages')
            
        translate_languages(languages, base)

def translate_languages(languages: Languages, base: StringsFile):
    global settings
    
    for language_code, strings_file in languages.items():
        
        if strings_file.path == base.path:
            continue

        translator = Translator(target_lang = language_code, origin_lang = settings.base_language)    
        
        try:
            strings_file.read()
        except UnicodeDecodeError:
            error(f'Error reading "{strings_file.path}"')
            continue
        
        translate_strings(strings_file, base, translator)
        
def translate_strings(strings_file: StringsFile, base: StringsFile, translator: Translator):
    global settings, progress, total_progress_task
    
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
        progress.advance(total_progress_task)
        
    progress.advance(total_progress_task, advance = len(base.strings) - len(filtered_base))
    progress.remove_task(current_file_task)
    
    try:
        strings_file.save()
    except UnicodeEncodeError:
        error(f'Error saving "{strings_file.path}"')
        
# ---------- Main ----------

def search_and_translate():
    global progress, total_progress_task
    
    groups = search_groups()
    table(groups)
    
    with Progress() as p:
        progress = p
        
        total = 0
        for languages in groups.values():
            base = languages.get('Base') or languages.get(settings.base_language)
            if not base: continue
            try: base.read()
            except UnicodeDecodeError: continue
            total += len(base.strings) * (len(languages) - 1)
            base.strings.clear()
            base.is_read = False
            
        total_progress_task = progress.add_task('Total progress', total = total)
        translate_groups(groups)

def main(
    base_language: str = 'en',
    override: bool = False,
    format_base: bool = False,
    file: list[str] = None,
    key: list[str] = None,
    language: list[str] = None,
    log_level: LogLevel = LogLevel.group):
    
    global settings
    settings = Settings(
            base_language = base_language,
            override = override,
            format_base = format_base,
            files = file,
            keys = key,
            languages = language,
            log_level = log_level
        )
    
    search_and_translate()

# ---------- Run ----------

def run():
    typer.run(main)

if __name__ == '__main__':
    run()