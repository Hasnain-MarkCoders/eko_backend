from enum import Enum

class Language(str, Enum):
    """Database/Model language enum - stored values"""
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

class LanguageRequest(str, Enum):
    """Request body language enum - frontend sends these values"""
    EN = "EN"
    FR = "FR"
    
    @classmethod
    def get_default(cls):
        return cls.EN
    
    @classmethod
    def to_database_language(cls, request_lang: str) -> str:
        """Convert request language to database language"""
        if request_lang == cls.FR:
            return Language.FRENCH
        return Language.ENGLISH
