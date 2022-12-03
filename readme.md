# XCodeLocalize

## Requirments 

Python3.9+

## Installation

### Using pip:
```
pip3 install xcodelocalize 
```

## Usage

### Prepare a project

Go to the project settings, add the desired localization languages. Create localization files for all selected languages.

### Localize

`cd` to project root folder and run

```
xcodelocalize [OPTIONS]
```

or

```
python3 -m xcodelocalize [OPTIONS]
```

### Options

* `--base-language`: code of the language from which all strings will be translated. _[default: 'en']_

* `--override / --no-override`: a boolean value that indicates whether strings that already exist in the file will be translated. Retranslate if `override`, skip if `no-override`. _[default: no-override]_

* `--file`: Names of the strings files to be translated. Multiple files can be specified. If not specified, all files will be translated. _[default: None]_ 
```
xcodelocalize --file Info
xcodelocalize --file Info --file MainStoryboard --file Localizable 
```

* `--key`: Keys of the strings to be translated. Multiple keys can be specified. If not specified, all keys will be translated. _[default: None]_

* `--language`: Language codes of the strings files to be translated. Multiple language codes can be specified. If not specified, all files will be translated. _[default: None]_

* `--log-level`: One from [progress|errors|group|string].  _[default: group]_

* `--help`: Show info

## Features:

* The tool looks for .strings files in the current directory recursively, grouping and translating fully automatically. You can even run it in the root directory and localize all your projects at once.

* Regular .strings, Info.plist, storyboards and intentdefinition files are supported.

* Formated strings with %@ are supported.

* Multiline strings are supported.

* Key and value must **not contain double quotes `"`**. Other quotes are supported.

* Comments are supported and will be copied to all files. Comments must **not contain substrings in localizable strings format with comment, such as `/*[comment]*/ "[key]" = "[value]";`**.

## Automation

You can go to `Target -> Build Phases -> New Run Script Phase` in your xcode project and paste `xcodelocalize` there. It will localize necessary strings during build and your localization files will always be up to date.
