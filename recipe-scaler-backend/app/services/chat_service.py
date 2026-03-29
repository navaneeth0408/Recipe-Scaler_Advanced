"""
Conversational assistant service for cooking and recipe questions
Maintains session-based context for multi-turn conversations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class MessageRole(str, Enum):
    """Message roles in conversation"""
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    """Represents a message in conversation"""
    role: MessageRole
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ConversationContext:
    """Maintains context for a conversation session"""
    session_id: str
    recipe_context: Optional[Dict[str, Any]] = None
    dietary_restrictions: List[str] = field(default_factory=list)
    cuisine_preference: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_message(self, role: MessageRole, content: str) -> Message:
        """Add a message to the conversation"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.last_updated = datetime.now().isoformat()
        return message
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get last N messages in conversation"""
        recent = self.messages[-limit:]
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in recent
        ]

class CookingAssistant:
    """AI-powered cooking assistant with context awareness"""
    
    # Knowledge base for cooking questions
    COOKING_KNOWLEDGE = {
        "substitutions": "I can suggest ingredient substitutions based on dietary preferences or availability.",
        "scaling": "I can help you scale recipes up or down while adjusting ingredients proportionally.",
        "timing": "I can provide cooking time estimates based on ingredient quantities.",
        "techniques": "I can explain various cooking techniques and methods.",
        "temperature": "I can help with cooking temperatures for different dishes.",
        "storage": "I can provide storage and preservation advice for ingredients and cooked food.",
    }
    
    def __init__(self):
        self.sessions: Dict[str, ConversationContext] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_session(self, session_id: str, recipe_context: Optional[Dict[str, Any]] = None) -> ConversationContext:
        """Create a new conversation session"""
        context = ConversationContext(
            session_id=session_id,
            recipe_context=recipe_context
        )
        self.sessions[session_id] = context
        self.logger.info(f"Created session {session_id}")
        return context
    
    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Get existing conversation session"""
        return self.sessions.get(session_id)
    
    def set_recipe_context(self, session_id: str, recipe: Dict[str, Any]) -> bool:
        """Set recipe context for the session"""
        if session_id not in self.sessions:
            self.create_session(session_id, recipe)
            return True
        
        self.sessions[session_id].recipe_context = recipe
        return True
    
    def set_dietary_restrictions(self, session_id: str, restrictions: List[str]) -> bool:
        """Set dietary restrictions for the session"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        self.sessions[session_id].dietary_restrictions = restrictions
        return True
    
    def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process a user message and generate response
        
        Args:
            session_id: Conversation session ID
            user_message: User's input message
        
        Returns:
            Dictionary with assistant response and context
        """
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        context = self.sessions[session_id]
        
        # Add user message to history
        context.add_message(MessageRole.USER, user_message)
        
        # Generate response based on context
        response = self._generate_response(user_message, context)
        
        # Add assistant response to history
        context.add_message(MessageRole.ASSISTANT, response)
        
        return {
            "session_id": session_id,
            "user_message": user_message,
            "assistant_response": response,
            "conversation_history": context.get_conversation_history(),
            "context": {
                "recipe": context.recipe_context,
                "dietary_restrictions": context.dietary_restrictions,
                "cuisine_preference": context.cuisine_preference,
            }
        }
    
    def _generate_response(self, message: str, context: ConversationContext) -> str:
        """
        Generate assistant response based on user message and context powered by AI models.
        """
        import os
        import json
        import requests
        
        system_prompt = (
            "You are a helpful, expert AI cooking assistant. "
            "You provide concise, accurate, and incredibly helpful culinary advice. "
            "Do not output markdown code blocks unnecessarily."
        )
        if context.recipe_context:
            system_prompt += f"The user is viewing or making: {json.dumps(context.recipe_context)}. "
        if context.dietary_restrictions:
            system_prompt += f"The user has dietary restrictions: {', '.join(context.dietary_restrictions)}. "
            
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history
        for msg in context.messages[-6:]:
            if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                messages.append({"role": msg.role.value, "content": msg.content})
                
        messages.append({"role": "user", "content": message})

        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        try:
            if groq_key:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json={
                        "model": "llama3-8b-8192",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    },
                    headers={"Authorization": f"Bearer {groq_key}"},
                    timeout=10
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
            
            if openai_key:
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    },
                    headers={"Authorization": f"Bearer {openai_key}"},
                    timeout=10
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                    
            return "I'm sorry, I cannot connect to my AI provider at the moment. Please configure GROQ_API_KEY or OPENAI_API_KEY in the backend."
            
        except Exception as e:
            self.logger.error(f"AI generation failed: {e}")
            return "I'm having trouble connecting to my AI brain right now."
    
    def _extract_ingredient(self, message: str) -> Optional[str]:
        """Extract ingredient name from user message"""
        # Simple extraction - in production, use NER model
        common_ingredients = [
            "flour", "sugar", "butter", "milk", "egg", "salt", "water", "oil",
            "chicken", "beef", "pork", "fish", "onion", "garlic", "tomato",
            "cheese", "bread", "rice", "pasta", "honey", "vanilla", "cinnamon"
        ]
        
        message_lower = message.lower()
        for ingredient in common_ingredients:
            if ingredient in message_lower:
                return ingredient
        
        return None
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a conversation session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get complete conversation history for a session"""
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id].get_conversation_history(limit=None)

# Global service instance
cooking_assistant = CookingAssistant()
