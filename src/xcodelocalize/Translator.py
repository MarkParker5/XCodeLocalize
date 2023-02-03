import mtranslate


class Translator:

    # some language codes are different in the xcode and in the google translate
    xcode_aliases = {
        'zh-Hans': 'zh-CN', 
        'zh-Hant': 'zh-TW', 
        'pt-BR': 'pt',
        'he': 'iw'
    }

    origin_lang: str = 'en'
    target_lang: str = 'en'

    def __init__(self, target_lang: str, origin_lang: str = 'en'):
        self.origin_lang = origin_lang
        self.target_lang = target_lang    

    def translate(self, text: str) -> str:
        return mtranslate.translate(text, self.target_alias, self.origin_lang)

    @property
    def target_alias(self) -> str:
        return self.xcode_aliases.get(self.target_lang) or self.target_lang