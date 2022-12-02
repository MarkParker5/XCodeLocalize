from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class FileGroup:
    directory: str
    filename: str

    @property
    def key(self) -> tuple[str, str]:
        return (self.directory, self.filename)

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key

    def __repr__(self):
        return f'{self.directory}\{self.filename}'


@dataclass
class String:
    key: str
    value: str
    comment: str = None

class StringsFile:

    path: Path
    strings: dict[str, String] = {}
    is_readed: bool = False

    def __init__(self, path: Path):
        self.path = path

    def __repr__(self):
        if self.is_readed:
            return f'<StringsFile with {len(self.strings)} strings>'
        else:
            return f'<StringsFile []>'

    def read(self) -> dict[str, str]:
        with open(self.path, 'r') as f:
            file = f.read().replace('%@', '_ARG_')

            pattern = re.compile(r'(\/\*(?P<comment>[\s\S]*?)\*\/)?[\s]+"(?P<key>[^"]+)"\s?=\s?"(?P<value>[^"]+)";')

            for match in pattern.finditer(file):
                groups = match.groupdict()

                if not all([groups.get('value'), groups.get('key')]):
                    continue

                key = groups['key']
                value = groups['value']
                comment = groups.get('comment') or ''

                self.strings[key] = String(key, value, comment.strip())

    def save(self):
        with open(self.path, 'w') as f:
            for string in self.strings.values():
                f.write(
                    f'\n/* {string.comment} */\n"{string.key}" = "{string.value}";\n' \
                        .replace('_ARG_', '%@') \
                        .replace('$ {','${')
                )