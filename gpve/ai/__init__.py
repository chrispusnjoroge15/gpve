"""AI module - Multi-AI orchestration"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import os
import logging

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"  # ChatGPT


@dataclass
class AIResponse:
    """Response from an AI"""
    provider: AIProvider
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Any = None
    error: Optional[str] = None
    
    def __repr__(self):
        return f"AIResponse({self.provider.value}, {len(self.content)} chars)"


class AIBase(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = ""):
        self.api_key = api_key or self._get_api_key()
        self.model = model
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate a response"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if API key is configured"""
        pass
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment"""
        return None


class GeminiAI(AIBase):
    """Google Gemini AI"""
    
    MODEL_DEFAULT = "gemini-2.0-flash"
    
    def __init__(self, api_key: Optional[str] = None, model: str = MODEL_DEFAULT):
        super().__init__(api_key, model)
        self._client = None
        self._try_import()
    
    def _try_import(self):
        """Try to import the Gemini client"""
        try:
            import google.generativeai as genai
            self._genai = genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
        except ImportError:
            logger.warning("google-generativeai not installed")
    
    def _get_api_key(self) -> Optional[str]:
        return os.environ.get("GEMINI_API_KEY")
    
    def is_available(self) -> bool:
        return self._genai is not None and bool(self.api_key)
    
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        if not self.is_available():
            return AIResponse(
                provider=AIProvider.GEMINI,
                content="",
                model=self.model,
                error="Gemini not configured. Set GEMINI_API_KEY."
            )
        
        try:
            model = self._genai.GenerativeModel(self.model)
            response = model.generate_content(prompt, **kwargs)
            
            return AIResponse(
                provider=AIProvider.GEMINI,
                content=response.text,
                model=self.model,
                raw_response=response
            )
        except Exception as e:
            return AIResponse(
                provider=AIProvider.GEMINI,
                content="",
                model=self.model,
                error=str(e)
            )


class DeepSeekAI(AIBase):
    """DeepSeek AI"""
    
    MODEL_DEFAULT = "deepseek-chat"
    
    def __init__(self, api_key: Optional[str] = None, model: str = MODEL_DEFAULT):
        super().__init__(api_key, model)
        self._client = None
        self.base_url = "https://api.deepseek.com"
        self._try_import()
    
    def _try_import(self):
        try:
            import openai
            self._openai = openai
            self._openai.api_key = self.api_key
            self._openai.base_url = self.base_url
        except ImportError:
            logger.warning("openai package needed for DeepSeek")
    
    def _get_api_key(self) -> Optional[str]:
        return os.environ.get("DEEPSEEK_API_KEY")
    
    def is_available(self) -> bool:
        return self._openai is not None and bool(self.api_key)
    
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        if not self.is_available():
            return AIResponse(
                provider=AIProvider.DEEPSEEK,
                content="",
                model=self.model,
                error="DeepSeek not configured. Set DEEPSEEK_API_KEY."
            )
        
        try:
            self._openai.api_key = self.api_key
            response = self._openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            return AIResponse(
                provider=AIProvider.DEEPSEEK,
                content=response.choices[0].message.content,
                model=self.model,
                usage={"tokens": response.usage.total_tokens} if response.usage else {},
                raw_response=response
            )
        except Exception as e:
            return AIResponse(
                provider=AIProvider.DEEPSEEK,
                content="",
                model=self.model,
                error=str(e)
            )


class ChatGPT(AIBase):
    """OpenAI ChatGPT"""
    
    MODEL_DEFAULT = "gpt-4o"
    
    def __init__(self, api_key: Optional[str] = None, model: str = MODEL_DEFAULT):
        super().__init__(api_key, model)
        self._client = None
        self._try_import()
    
    def _try_import(self):
        try:
            import openai
            self._openai = openai
            if self.api_key:
                self._openai.api_key = self.api_key
        except ImportError:
            logger.warning("openai package needed for ChatGPT")
    
    def _get_api_key(self) -> Optional[str]:
        return os.environ.get("OPENAI_API_KEY")
    
    def is_available(self) -> bool:
        return self._openai is not None and bool(self.api_key)
    
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        if not self.is_available():
            return AIResponse(
                provider=AIProvider.OPENAI,
                content="",
                model=self.model,
                error="OpenAI not configured. Set OPENAI_API_KEY."
            )
        
        try:
            self._openai.api_key = self.api_key
            response = self._openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            return AIResponse(
                provider=AIProvider.OPENAI,
                content=response.choices[0].message.content,
                model=self.model,
                usage={"tokens": response.usage.total_tokens} if response.usage else {},
                raw_response=response
            )
        except Exception as e:
            return AIResponse(
                provider=AIProvider.OPENAI,
                content="",
                model=self.model,
                error=str(e)
            )


class AIOrchestrator:
    """
    Orchestrates multiple AI providers.
    
    Features:
    - Route prompts to multiple AIs
    - Aggregate responses
    - Fallback when one fails
    - Compare responses
    """
    
    def __init__(self):
        self.providers: Dict[AIProvider, AIBase] = {}
        self._register_default_providers()
    
    def _register_default_providers(self):
        """Register default AI providers"""
        self.register(GeminiAI())
        self.register(DeepSeekAI())
        self.register(ChatGPT())
    
    def register(self, provider: AIBase) -> None:
        """Register an AI provider"""
        if isinstance(provider, GeminiAI):
            self.providers[AIProvider.GEMINI] = provider
        elif isinstance(provider, DeepSeekAI):
            self.providers[AIProvider.DEEPSEEK] = provider
        elif isinstance(provider, ChatGPT):
            self.providers[AIProvider.OPENAI] = provider
    
    def available(self) -> List[AIProvider]:
        """Get list of available providers"""
        return [p for p, a in self.providers.items() if a.is_available()]
    
    def generate(
        self, 
        prompt: str, 
        providers: Optional[List[AIProvider]] = None,
        **kwargs
    ) -> Dict[AIProvider, AIResponse]:
        """
        Generate responses from multiple AIs.
        
        Returns dict of provider -> response
        """
        if providers is None:
            providers = list(self.providers.keys())
        
        results = {}
        
        for provider in providers:
            if provider in self.providers:
                ai = self.providers[provider]
                results[provider] = ai.generate(prompt, **kwargs)
        
        return results
    
    def generate_with_fallback(
        self, 
        prompt: str, 
        preferred: AIProvider = AIProvider.OPENAI,
        **kwargs
    ) -> AIResponse:
        """Generate with fallback to other providers if preferred fails"""
        # Try preferred first
        if preferred in self.providers:
            response = self.providers[preferred].generate(prompt, **kwargs)
            if not response.error:
                return response
        
        # Try others
        for provider, ai in self.providers.items():
            if provider != preferred:
                response = ai.generate(prompt, **kwargs)
                if not response.error:
                    return response
        
        # All failed
        return AIResponse(
            provider=preferred,
            content="",
            model="",
            error="All providers failed"
        )
    
    def compare(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate from all and compare responses"""
        responses = self.generate(prompt, **kwargs)
        
        return {
            "prompt": prompt,
            "responses": {
                p.value: {
                    "content": r.content,
                    "model": r.model,
                    "error": r.error,
                    "usage": r.usage
                }
                for p, r in responses.items()
            },
            "available": [p.value for p in self.available()]
        }
    
    def __repr__(self):
        avail = self.available()
        return f"AIOrchestrator(available={[p.value for p in avail]})"
