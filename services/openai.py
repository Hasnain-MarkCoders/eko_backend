import openai
import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import httpx

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("⚠️ OPENAI_API_KEY not found in environment variables")
        else:
            openai.api_key = self.api_key
    
    async def generate_chat_name(self, user_language: str = "english") -> str:
        """
        Generate a friendly chat name using OpenAI API
        Falls back to timestamp-based name if API fails
        """
        if not self.api_key:
            return self._generate_fallback_name()
        
        try:
            # Convert database language to OpenAI language code
            language_code = "en" if user_language == "english" else "fr"
            
            prompt = self._build_chat_name_prompt(language_code)
            
            # Use async HTTP client for OpenAI API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant that generates short, friendly names for chat sessions in a psychological support app. Respond with only the chat name, nothing else."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 20,
                        "temperature": 0.7
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    chat_name = data["choices"][0]["message"]["content"].strip()
                    
                    # Clean up the response (remove quotes, extra text)
                    chat_name = chat_name.strip('"').strip("'").strip()
                    
                    # Ensure it's not too long
                    if len(chat_name) > 50:
                        chat_name = chat_name[:47] + "..."
                    
                    # Ensure it's not empty
                    if not chat_name:
                        return self._generate_fallback_name()
                    
                    print(f"✅ Generated chat name: '{chat_name}'")
                    return chat_name
                else:
                    print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
                    return self._generate_fallback_name()
                    
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return self._generate_fallback_name()
    
    def _build_chat_name_prompt(self, language_code: str) -> str:
        """Build the prompt for chat name generation based on language"""
        if language_code == "fr":
            return """Génère un nom court et amical pour une session de chat dans une application d'assistance psychologique. 
L'utilisateur commence une nouvelle conversation.
Contexte: Support et guidance psychologique
Format: 2-4 mots, encourageant et accueillant
Exemples: "Nouveau Départ", "Parlons-en", "Nouveau Voyage", "Nouveau Commencement"
Réponds seulement avec le nom du chat, rien d'autre."""
        else:
            return """Generate a short, friendly chat session name for a psychological assistant app. 
The user is starting a new conversation. 
Context: Psychological support and guidance
Format: 2-4 words, encouraging and welcoming
Examples: "New Journey", "Fresh Start", "Let's Talk", "New Beginning"
Respond with only the chat name, nothing else."""
    
    def _generate_fallback_name(self) -> str:
        """Generate a fallback name based on timestamp"""
        now = datetime.now()
        return f"Chat - {now.strftime('%b %d')}"
