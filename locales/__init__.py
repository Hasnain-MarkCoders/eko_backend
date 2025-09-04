import json
import os
from typing import Dict, Any

class LocaleManager:
    def __init__(self):
        self.locales = {}
        self.default_language = "en"
        self.load_locales()
    
    def load_locales(self):
        """Load all locale files"""
        locales_dir = os.path.dirname(__file__)
        
        for filename in os.listdir(locales_dir):
            if filename.endswith('.json'):
                language = filename[:-5]  # Remove .json extension
                filepath = os.path.join(locales_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.locales[language] = json.load(f)
    
    def get_message(self, language: str, key_path: str, **kwargs) -> str:
        """
        Get localized message
        
        Args:
            language: User's preferred language (en, fr)
            key_path: Dot-separated path to message (e.g., 'auth.signup.success')
            **kwargs: Format parameters for message interpolation
        
        Returns:
            Localized message string
        """
        # Fallback to default language if requested language not supported
        if language not in self.locales:
            language = self.default_language
        
        # Navigate through nested dictionary using dot notation
        keys = key_path.split('.')
        message = self.locales[language]
        
        try:
            for key in keys:
                message = message[key]
            
            # Format message with provided parameters
            if kwargs:
                message = message.format(**kwargs)
            
            return message
            
        except (KeyError, TypeError):
            # Fallback to default language if key not found
            if language != self.default_language:
                return self.get_message(self.default_language, key_path, **kwargs)
            
            # If still not found, return the key path as fallback
            return f"Message not found: {key_path}"
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return list(self.locales.keys())

# Global instance
locale_manager = LocaleManager()

def get_message(language: str, key_path: str, **kwargs) -> str:
    """Convenience function to get localized message"""
    return locale_manager.get_message(language, key_path, **kwargs)
