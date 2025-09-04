from enum import Enum

class Language(str, Enum):
    ENGLISH = "english"
    FRENCH = "french"
    
    @classmethod
    def get_default(cls):
        return cls.ENGLISH
    
    @classmethod
    def get_locale_code(cls, language: str) -> str:
        """Convert language enum to locale code for get_message()"""
        if language == cls.FRENCH:
            return "fr"
        return "en"
