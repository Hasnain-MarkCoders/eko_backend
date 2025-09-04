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
    
    async def generate_bot_response(self, conversation_context: list, user_language: str = "english") -> str:
        """
        Generate EKO bot response using OpenAI API
        """
        if not self.api_key:
            return self._generate_fallback_response()
        
        try:
            # Convert database language to OpenAI language code
            language_code = "en" if user_language == "english" else "fr"
            
            # Build system prompt for EKO bot
            system_prompt = self._build_bot_system_prompt(language_code)
            
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_context)
            
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
                        "messages": messages,
                        "max_tokens": 500,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    bot_response = data["choices"][0]["message"]["content"].strip()
                    
                    print(f"✅ Generated bot response: '{bot_response[:100]}...'")
                    return bot_response
                else:
                    print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
                    return self._generate_fallback_response()
                    
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return self._generate_fallback_response()
    
    def _build_bot_system_prompt(self, language_code: str) -> str:
        """Build the system prompt for EKO bot based on language"""
        if language_code == "fr":
            return """Tu es EKO, un assistant psychologique conversationnel. Tu es là pour fournir un soutien émotionnel, des conseils bienveillants et une écoute attentive.

Caractéristiques d'EKO:
- Tu es empathique, compréhensif et non-jugeant
- Tu encourages l'expression des émotions et des pensées
- Tu fournis des conseils pratiques pour le bien-être mental
- Tu restes professionnel tout en étant chaleureux
- Tu poses des questions réfléchies pour mieux comprendre
- Tu offres des techniques de relaxation et de gestion du stress

Réponds de manière naturelle et conversationnelle, comme si tu parlais à un ami de confiance. Garde tes réponses concises mais significatives."""
        else:
            return """You are EKO, a conversational psychological assistant. You are here to provide emotional support, gentle guidance, and a listening ear.

EKO's characteristics:
- You are empathetic, understanding, and non-judgmental
- You encourage expression of emotions and thoughts
- You provide practical advice for mental well-being
- You remain professional while being warm and approachable
- You ask thoughtful questions to better understand
- You offer relaxation and stress management techniques

Respond naturally and conversationally, as if speaking to a trusted friend. Keep your responses concise but meaningful."""
    
    def _generate_fallback_response(self) -> str:
        """Generate a fallback response when OpenAI fails"""
        fallback_responses = [
            "I'm here to listen and support you. How are you feeling today?",
            "Thank you for sharing that with me. I'm here to help you work through this.",
            "I understand this might be difficult to talk about. Take your time, I'm here to listen.",
            "Your feelings are valid and important. Let's explore this together.",
            "I'm here to support you through whatever you're going through."
        ]
        import random
        return random.choice(fallback_responses)
