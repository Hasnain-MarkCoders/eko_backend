# Task 4: Implement Internationalization (i18n) System

## Overview
Implement a comprehensive internationalization system to support dynamic error and success messages in multiple languages (English and French). This will allow the frontend to display localized messages to users based on their language preference.

## Problem Statement

### Current Issues
- **Hardcoded Messages**: All error and success messages are hardcoded in English
- **No Localization**: Messages cannot be displayed in user's preferred language
- **Inconsistent Messaging**: No centralized message management system
- **Poor UX**: Users see messages in English even if they prefer French

### Requirements
- Support for English and French languages
- Dynamic message selection based on user's language preference
- Centralized message management
- Easy addition of new languages in the future
- Fallback to English if language not supported

## Implementation Architecture

### 1. File Structure
```
locales/
├── en.json          # English messages
├── fr.json          # French messages
└── __init__.py      # Locale utilities
```

### 2. Message Categories

#### Authentication Messages
- Signup success/errors
- Login success/errors
- Password validation errors
- Forgot password messages

#### Profile Management Messages
- Profile update success/errors
- User deletion messages
- Welcome messages

#### General Messages
- Validation errors
- System errors
- Success confirmations

## Implementation Details

### 1. Create Locale Files

#### `locales/en.json`
```json
{
  "auth": {
    "signup": {
      "success": "User created successfully",
      "email_exists": "User with this email already exists",
      "password_too_short": "Password must be at least 8 characters long",
      "password_no_uppercase": "Password must contain at least one uppercase letter",
      "password_no_lowercase": "Password must contain at least one lowercase letter",
      "password_no_number": "Password must contain at least one number",
      "password_no_special": "Password must contain at least one special character",
      "password_common": "Password is too common. Please choose a stronger password",
      "password_sequential": "Password cannot contain sequential characters",
      "password_repeated": "Password cannot contain more than 2 repeated characters in a row",
      "passwords_no_match": "Passwords do not match",
      "weak_password": "Password is too weak. Use at least 6 characters."
    },
    "login": {
      "success": "Login successful",
      "user_not_found": "User not found",
      "account_deleted": "Account has been deleted",
      "brand_user": "Please use Sauced brand panel."
    },
    "forgot_password": {
      "success": "Password reset email sent successfully",
      "user_not_found": "User not found",
      "reset_failed": "Failed to generate password reset link"
    },
    "onboarding": {
      "success": "Onboarding completed successfully",
      "already_completed": "User has already completed onboarding. Welcome flag is false.",
      "invalid_user_id": "Invalid user ID format",
      "user_not_found": "User not found",
      "account_deleted": "Account has been deleted",
      "firebase_update_failed": "Failed to update display name in Firebase",
      "onboarding_failed": "Failed to complete onboarding"
    }
  },
  "profile": {
    "change_name": {
      "success": "User Name Changed Successfully",
      "name_empty": "Name cannot be empty",
      "same_name": "New name cannot be the same as current name",
      "firebase_update_failed": "Failed to update display name in Firebase",
      "user_not_found": "User not found"
    },
    "change_image": {
      "success": "User Image Changed Successfully",
      "image_empty": "Image URL cannot be empty",
      "user_not_found": "User not found"
    },
    "delete": {
      "success": "User account deleted successfully",
      "note": "Account has been deactivated and personal information removed. Firebase account has been deleted.",
      "already_deleted": "User account is already deleted",
      "user_not_found": "User not found"
    },
    "get_user": {
      "success": "User profile retrieved successfully",
      "user_not_found": "User not found"
    },
    "is_active": {
      "success": "User status retrieved successfully"
    },
    "welcome": {
      "welcome1": "Welcome 1",
      "welcome2": "Welcome 2",
      "user_not_found": "User not found"
    },
    "update_token": {
      "success": "Notification Token Updated Successfully",
      "user_not_found": "User not found"
    },
    "debug_name": {
      "success": "Name comparison retrieved successfully",
      "user_not_found": "User not found in MongoDB"
    }
  },
  "general": {
    "welcome": "Welcome to Eko Backend API",
    "health": "API is healthy",
    "invalid_user_id": "Invalid user ID format",
    "user_not_found": "User not found",
    "internal_error": "Internal server error",
    "validation_error": "Validation error"
  }
}
```

#### `locales/fr.json`
```json
{
  "auth": {
    "signup": {
      "success": "Utilisateur créé avec succès",
      "email_exists": "Un utilisateur avec cet email existe déjà",
      "password_too_short": "Le mot de passe doit contenir au moins 8 caractères",
      "password_no_uppercase": "Le mot de passe doit contenir au moins une lettre majuscule",
      "password_no_lowercase": "Le mot de passe doit contenir au moins une lettre minuscule",
      "password_no_number": "Le mot de passe doit contenir au moins un chiffre",
      "password_no_special": "Le mot de passe doit contenir au moins un caractère spécial",
      "password_common": "Le mot de passe est trop commun. Veuillez choisir un mot de passe plus fort",
      "password_sequential": "Le mot de passe ne peut pas contenir de caractères séquentiels",
      "password_repeated": "Le mot de passe ne peut pas contenir plus de 2 caractères répétés consécutivement",
      "passwords_no_match": "Les mots de passe ne correspondent pas",
      "weak_password": "Le mot de passe est trop faible. Utilisez au moins 6 caractères."
    },
    "login": {
      "success": "Connexion réussie",
      "user_not_found": "Utilisateur non trouvé",
      "account_deleted": "Le compte a été supprimé",
      "brand_user": "Veuillez utiliser le panneau de marque Sauced."
    },
    "forgot_password": {
      "success": "Email de réinitialisation du mot de passe envoyé avec succès",
      "user_not_found": "Utilisateur non trouvé",
      "reset_failed": "Échec de la génération du lien de réinitialisation du mot de passe"
    },
    "onboarding": {
      "success": "Intégration terminée avec succès",
      "already_completed": "L'utilisateur a déjà terminé l'intégration. Le drapeau de bienvenue est false.",
      "invalid_user_id": "Format d'ID utilisateur invalide",
      "user_not_found": "Utilisateur non trouvé",
      "account_deleted": "Le compte a été supprimé",
      "firebase_update_failed": "Échec de la mise à jour du nom d'affichage dans Firebase",
      "onboarding_failed": "Échec de l'intégration"
    }
  },
  "profile": {
    "change_name": {
      "success": "Nom d'utilisateur modifié avec succès",
      "name_empty": "Le nom ne peut pas être vide",
      "same_name": "Le nouveau nom ne peut pas être le même que le nom actuel",
      "firebase_update_failed": "Échec de la mise à jour du nom d'affichage dans Firebase",
      "user_not_found": "Utilisateur non trouvé"
    },
    "change_image": {
      "success": "Image d'utilisateur modifiée avec succès",
      "image_empty": "L'URL de l'image ne peut pas être vide",
      "user_not_found": "Utilisateur non trouvé"
    },
    "delete": {
      "success": "Compte utilisateur supprimé avec succès",
      "note": "Le compte a été désactivé et les informations personnelles ont été supprimées. Le compte Firebase a été supprimé.",
      "already_deleted": "Le compte utilisateur est déjà supprimé",
      "user_not_found": "Utilisateur non trouvé"
    },
    "get_user": {
      "success": "Profil utilisateur récupéré avec succès",
      "user_not_found": "Utilisateur non trouvé"
    },
    "is_active": {
      "success": "Statut utilisateur récupéré avec succès"
    },
    "welcome": {
      "welcome1": "Bienvenue 1",
      "welcome2": "Bienvenue 2",
      "user_not_found": "Utilisateur non trouvé"
    },
    "update_token": {
      "success": "Token de notification mis à jour avec succès",
      "user_not_found": "Utilisateur non trouvé"
    },
    "debug_name": {
      "success": "Comparaison de noms récupérée avec succès",
      "user_not_found": "Utilisateur non trouvé dans MongoDB"
    }
  },
  "general": {
    "welcome": "Bienvenue dans l'API Eko Backend",
    "health": "L'API est en bonne santé",
    "invalid_user_id": "Format d'ID utilisateur invalide",
    "user_not_found": "Utilisateur non trouvé",
    "internal_error": "Erreur interne du serveur",
    "validation_error": "Erreur de validation"
  }
}
```

### 2. Create Locale Utility

#### `locales/__init__.py`
```python
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
```

### 3. Update Controllers

#### Example: Updated Auth Controller
```python
from locales import get_message

class AuthController:
    def __init__(self):
        self.admin = initialize_admin()
    
    async def email_password_signup(self, email: str, password: str, confirm_password: str, language: str = "en"):
        """Enhanced email/password signup with i18n"""
        try:
            # Validate password confirmation
            if password != confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "auth.signup.passwords_no_match")
                )
            
            # Check if user already exists
            existing_user = await users.find_one({"email": email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "auth.signup.email_exists")
                )
            
            # ... rest of signup logic ...
            
            return {
                "success": True,
                "message": get_message(language, "auth.signup.success"),
                "data": {
                    # ... user data ...
                }
            }
            
        except Exception as error:
            # Handle Firebase errors with localized messages
            if "EMAIL_EXISTS" in str(error):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "auth.signup.email_exists")
                )
            elif "WEAK_PASSWORD" in str(error):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "auth.signup.weak_password")
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=get_message(language, "general.internal_error")
                )
```

### 4. Update Middleware

#### Enhanced Auth Middleware
```python
from locales import get_message

async def get_current_user(request: Request):
    """Enhanced auth middleware with language support"""
    try:
        # ... existing auth logic ...
        
        # Get user's language preference
        user_language = user.get("language", "en")
        
        # Add language to request state for use in controllers
        request.state.user_language = user_language
        
        return user
        
    except Exception as e:
        # Get language from request headers or default to English
        language = request.headers.get("Accept-Language", "en")[:2]
        if language not in ["en", "fr"]:
            language = "en"
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message(language, "general.unauthorized")
        )
```

### 5. Update All Controllers

Apply the same pattern to all controllers:

```python
# In each controller method
async def some_method(self, user_id: str, language: str = "en"):
    try:
        # ... business logic ...
        
        return {
            "success": True,
            "message": get_message(language, "module.action.success"),
            "data": result_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_message(language, "module.action.error")
        )
```

## Implementation Steps

### 1. Create Locale Infrastructure
- Create `locales/` directory
- Add `en.json` and `fr.json` files
- Create `locales/__init__.py` with `LocaleManager`

### 2. Update All Controllers
- Import `get_message` function
- Replace hardcoded messages with `get_message()` calls
- Add language parameter to all controller methods

### 3. Update Routes
- Pass language parameter from request to controllers
- Handle language detection from headers or user preference

### 4. Update Middleware
- Extract user language preference
- Add language to request state

### 5. Update Documentation
**CRITICAL**: Update API documentation to reflect the new internationalization system:

#### Documentation Update Requirements:
- Update `docs/documentation.md` to show localized response examples
- Add language parameter documentation for all endpoints
- Document supported languages (English, French)
- Add examples of error messages in both languages
- Update response field descriptions to mention localization
- Document language detection mechanism
- Add fallback behavior documentation
- Ensure all endpoint examples show localized messages

### 6. Testing
- Test all endpoints with English and French
- Verify fallback to English works
- Test with unsupported languages
- Verify documentation examples match actual responses

## Benefits

1. **Better UX**: Users see messages in their preferred language
2. **Scalability**: Easy to add new languages
3. **Maintainability**: Centralized message management
4. **Consistency**: Standardized message format across all endpoints
5. **Professional**: International-ready application

## Future Considerations

- Add more languages (Spanish, German, etc.)
- Implement pluralization rules
- Add date/time formatting by locale
- Consider using professional i18n libraries (Babel, etc.)
- Add language detection from browser headers
- Implement language switching without re-authentication

## Migration Strategy

1. **Phase 1**: Implement locale system with English messages
2. **Phase 2**: Add French translations
3. **Phase 3**: Update all controllers to use localized messages
4. **Phase 4**: **CRITICAL** - Update all documentation to reflect localized responses
5. **Phase 5**: Test and deploy
6. **Phase 6**: Add more languages as needed

## Documentation Consistency Requirements

**MANDATORY**: The following documentation must be updated to maintain consistency:

### API Documentation (`docs/documentation.md`)
- All response examples must show localized messages
- Add language parameter documentation
- Document supported languages
- Show examples in both English and French
- Update error response examples with localized messages

### Postman Collection
- Update all request examples
- Add language headers where applicable
- Update response examples with localized messages

### Code Comments
- Update all endpoint docstrings to mention localization
- Add comments explaining language detection logic
- Document fallback behavior in code comments

### README/Instructions
- Update setup instructions if needed
- Document locale file structure
- Explain how to add new languages

**CRITICAL**: Documentation must be updated before any deployment to prevent confusion between documented behavior and actual implementation.

This system will make your API truly international and provide a much better user experience for French-speaking users!
