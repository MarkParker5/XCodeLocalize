import os
import mtranslate
from pathlib import Path
import re

os.system('clear')

# -------------------------------    Settings -----------------------------------------------
#    XCode supported languages codes
languages = ['ru', 'es', 'zh-Hans', 'zh-Hant', 'th', 'ko', 'ja', 'fr', 'de', 'it', 'nl', 'tr', 'vi', 'hi', 'pt-BR', 'ar']

#    some language codes are different in xcode and in google translate
translatorLangCodes = {'zh-Hans': 'zh-CN', 'zh-Hant': 'zh-TW', 'pt-BR': 'pt'}

projectName  = 'CC'
stringsFiles = ['Localizable', 'InfoPlist']     # names of strings files

def getFilePath(lang, name = 'Localizable'):
    return f'../{projectName}/{lang}.lproj/{name}.strings'
# -------------------------------    /Settings ----------------------------------------------


# -------------------------------    Functions ----------------------------------------------
def translate(text, lang):
    return mtranslate.translate(text, translatorLangCodes.get(lang) or lang, 'en')

def clearLocalize():
    for lang in languages:
        #    clear Localizable.strings
        for name in stringsFiles:
            with open(getFilePath(lang, name), 'w') as f:
                f.write('')
# -------------------------------    /Functions ----------------------------------------------


# -------------------------------    Files Functions    -------------------------------------
def getBasePath(name = 'Localizable'):
    base = getFilePath('Base', name)
    en   = getFilePath('en', name)
    return base if os.path.exists(base) else en

# read language strings file as dictionary {key: value}
def getFileAsDict(file):
    langDict = {}
    with open(file, 'r') as f:
        file = f.read()
        #lines = re.sub(r'^\/\/[^\n\r]+[\n\r]', '', file).split(';') # remove comments
        for line in file.split(';'):
            try: key, value = [text.strip() for text in line.replace(';', '').replace('"', '').replace('%@', '_ARG_').split('=')]
            except: continue
            langDict[key] = value
    return langDict

# save dictionary as strings file
def addStringsDictToFile(dict, file):
    string = ''
    for key, value in dict.items():
        string += f'"{key}" = "{value}";\n'
    with open(file, 'a') as strings:
        strings.write(string.replace('_ARG_', '%@').replace('$ {','${'))
# -------------------------------    /Strings Functions -------------------------------------


# -------------------------------    Storyboard Functions -------------------------------------
# read storyboard strings file as dictionary {"/*comment*/": {key: value}}
def getStoryboardAsDict(file):
    storyboardDict = {}
    if not os.path.exists(file): return {}
    with open(file, 'r') as strings:
        lines = strings.readlines()
        comment = ''
        for line in lines:
            # find /* comment */
            if '/*' in line and '*/' in line:
                comment = line
                continue
            # find "key" = "value"; for last comment
            try:
                key, value = [text.strip() for text in line.replace(';', '').replace('"', '').replace('\n', '').split('=')]
                storyboardDict[comment] = [key, value]
            except: pass
    return storyboardDict

# save storyboards dictionary as Main.strings file
def addStoryboardDictToFile(dict, file):
    if not os.path.exists(file): return
    string = ''
    for comment, (key, value) in dict.items():
        string += f'{comment}"{key}" = "{value}";\n\n'
    with open(file, 'a') as strings:
        strings.write(string)

# -------------------------------    /Storyboard Functions -------------------------------------

# clearLocalize()
# exit()

# -------------------------------    Localize Strings Files ------------------------------------

print("\n\n\n\n\nLocalize Strings...")
for name in stringsFiles:
    baseDict = getFileAsDict(getBasePath(name))
    for lang in languages:
        print(f"\nLang: <{lang}>:")
        langDict = getFileAsDict(file = getFilePath(lang, name))    # old strings from file
        langNewDict = {}                                    # dictionary with new strings
        for key, value in baseDict.items():
            if key in langDict.keys(): continue                # skip if string is already localized
            langNewDict[key] = translate(text = value, lang = lang).replace("\"", "\\\"")
            print("\t"+key+" -> "+langNewDict[key])
        addStringsDictToFile(dict = langNewDict, file = getFilePath(lang, name))


# -------------------------------    Find and Localize Storyboards -----------------------------

print("\n\n\n\n\nLocalize Storyboards...")
for sb in list(Path('..').rglob('*.storyboard')):
    basePath = str(sb).replace('.storyboard', '.strings').replace('Base.lproj', 'en.lproj')
    baseDict = getStoryboardAsDict(file = basePath)
    print('\n\n', basePath)
    for lang in languages:
        print(f"\nLang: <{lang}>:")
        storyboardDict = getStoryboardAsDict(file = basePath.replace('en.lproj', f'{lang}.lproj'))    # old strings from file
        storyboardNewDict = {}                                                                        # dictionary with new strings
        for comment, (key, value) in baseDict.items():
            if comment in storyboardDict.keys(): continue                                             # skip if string is already localized
            storyboardNewDict[comment] = [key, translate(text = value, lang = lang)]
            print("\t"+value+" -> "+storyboardNewDict[comment][1])
        addStoryboardDictToFile(dict = storyboardNewDict, file = basePath.replace('en.lproj', f'{lang}.lproj'))

# -------------------------------    Find and Localize Shortcuts ---------------------------------

print("\n\n\n\n\nLocalize Shortcuts...")
for sb in list(Path('..').rglob('*.intentdefinition')):
    basePath = str(sb).replace('.intentdefinition', '.strings').replace('Base.lproj', 'en.lproj')
    baseDict = getFileAsDict(file = basePath)
    print('\n\n', basePath)
    for lang in languages:
        with open(basePath.replace('en.lproj', f'{lang}.lproj'), 'w'): pass                    # clear file before localisation
        print(f"\nLang: <{lang}>:")
        shortcutsDict = getFileAsDict(file = basePath.replace('en.lproj', f'{lang}.lproj'))    # old strings from file
        shortcutsNewDict = {}                                                                  # dictionary with new strings
        for key, value in baseDict.items():
            if key in shortcutsDict.keys(): continue                                           # skip if string is already localized
                        
            #   safe translate quoted strings
            result = ''
            if m := re.search(r'‘(.+?)’', value):
                quoted = f'‘{m.group(1)}’'
                value = value.replace(quoted, '_QUOTED_')
                result = translate(text = value, lang = lang).replace('_QUOTED_', quoted)
            else:
                result = translate(text = value, lang = lang)
            #   save
            shortcutsNewDict[key] = result
            print("\t"+value+" -> "+shortcutsNewDict[key])
        addStringsDictToFile(dict = shortcutsNewDict, file = basePath.replace('en.lproj', f'{lang}.lproj'))

print("\n\n\tFINISH!\n\n")
