"""
API Client module for EDCopilot Chit Chat Updater
Handles OpenAI and Anthropic API interactions with failover capabilities
"""

import time
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
from src.config import Config
from src.utils.personalization import PersonalizationManager

logger = logging.getLogger(__name__)

class APIClient:
    """API Client for handling OpenAI and Anthropic interactions"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.personalization_manager = PersonalizationManager()
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API clients if keys are available"""
        if Config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        if Config.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    
    def generate_content(self, prompt: str, chatter_type: str, max_retries: int = None, 
                        include_personalization: bool = True, include_rss: bool = True, include_web: bool = True) -> Optional[str]:
        """
        Generate content using the preferred provider with automatic failover
        
        Args:
            prompt: The prompt to send to the AI model
            chatter_type: Type of chatter (for logging purposes)
            max_retries: Maximum number of retries per provider
            include_personalization: Whether to include personalization context
            include_rss: Whether to include RSS feed content
            include_web: Whether to include web content
            
        Returns:
            Generated content string or None if all providers fail
        """
        if max_retries is None:
            max_retries = Config.MAX_RETRIES
        
        # If personalization is already included in the prompt, use it as-is
        if not include_personalization:
            enhanced_prompt = prompt
        else:
            # Legacy method - add personalization context to the top
            personalization_context = self.personalization_manager.get_personalization_context(
                include_rss=include_rss, include_web=include_web)
            if personalization_context:
                enhanced_prompt = f"{personalization_context}\n\n{prompt}"
                logger.info(f"🎯 Enhanced prompt with personalization context for {chatter_type}")
            else:
                enhanced_prompt = prompt
        
        provider_order = Config.get_provider_order()
        
        for provider in provider_order:
            logger.info(f"🔄 Trying {provider} for {chatter_type}")
            
            try:
                if provider == 'OPENAI' and self.openai_client:
                    content = self._generate_openai(enhanced_prompt, max_retries)
                    if content:
                        logger.info(f"✅ Successfully generated {chatter_type} content using OpenAI")
                        return content
                
                elif provider == 'ANTHROPIC' and self.anthropic_client:
                    content = self._generate_anthropic(enhanced_prompt, max_retries)
                    if content:
                        logger.info(f"✅ Successfully generated {chatter_type} content using Anthropic")
                        return content
                
            except Exception as e:
                logger.error(f"❌ {provider} failed for {chatter_type}: {str(e)}")
                continue
        
        logger.error(f"❌ All providers failed for {chatter_type}")
        return None
    
    def _generate_openai(self, prompt: str, max_retries: int) -> Optional[str]:
        """Generate content using OpenAI API with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates engaging conversation content for a space-themed game."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.8
                )
                
                content = response.choices[0].message.content.strip()
                if content:
                    return content
                    
            except Exception as e:
                logger.warning(f"OpenAI attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def _generate_anthropic(self, prompt: str, max_retries: int) -> Optional[str]:
        """Generate content using Anthropic API with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.anthropic_client.messages.create(
                    model=Config.ANTHROPIC_MODEL,
                    max_tokens=1000,
                    temperature=0.8,
                    system="You are a helpful assistant that generates engaging conversation content for a space-themed game.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                content = response.content[0].text.strip()
                if content:
                    return content
                    
            except Exception as e:
                logger.warning(f"Anthropic attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def test_connectivity(self) -> Dict[str, bool]:
        """Test connectivity to both API providers"""
        results = {}
        
        # Test OpenAI
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=Config.OPENAI_MODEL,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                results['OPENAI'] = True
                logger.info("✅ OpenAI connectivity test passed")
            except Exception as e:
                results['OPENAI'] = False
                logger.error(f"❌ OpenAI connectivity test failed: {str(e)}")
        else:
            results['OPENAI'] = False
            logger.warning("⚠️ OpenAI client not initialized (missing API key)")
        
        # Test Anthropic
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model=Config.ANTHROPIC_MODEL,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}]
                )
                results['ANTHROPIC'] = True
                logger.info("✅ Anthropic connectivity test passed")
            except Exception as e:
                results['ANTHROPIC'] = False
                logger.error(f"❌ Anthropic connectivity test failed: {str(e)}")
        else:
            results['ANTHROPIC'] = False
            logger.warning("⚠️ Anthropic client not initialized (missing API key)")
        
        return results
