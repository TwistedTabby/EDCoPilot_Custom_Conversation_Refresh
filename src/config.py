"""
Configuration module for EDCopilot Chit Chat Updater
Handles environment variables and application settings
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the EDCopilot Chit Chat Updater"""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv('KEY_OPENAI', '')
    ANTHROPIC_API_KEY: str = os.getenv('KEY_ANTHROPIC', '')
    
    # Model Configuration
    OPENAI_MODEL: str = os.getenv('MODEL_OPENAI', 'gpt-4')
    ANTHROPIC_MODEL: str = os.getenv('MODEL_ANTHROPIC', 'claude-3-sonnet-20240229')
    
    # Provider Configuration
    PREFERRED_PROVIDER: str = os.getenv('PROVIDER_PREFERRED', 'OPENAI').upper()
    
    # Directory Configuration
    CUSTOM_DIR: str = os.getenv('DIR_CUSTOM', '')
    
    # Optional Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    CONTENT_LENGTH: int = int(os.getenv('CONTENT_LENGTH', '50'))
    CONVERSATIONS_COUNT: int = int(os.getenv('CONVERSATIONS_COUNT', '30'))
    CONVERSATIONS_CHANCE_PERSONALIZATION: int = int(os.getenv('CONVERSATIONS_CHANCE_PERSONALIZATION', '25'))
    CONVERSATIONS_CHANCE_RSS: int = int(os.getenv('CONVERSATIONS_CHANCE_RSS', '15'))
    CONVERSATIONS_CHANCE_CONDITIONALS: int = int(os.getenv('CONVERSATIONS_CHANCE_CONDITIONALS', '10').replace('%', ''))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            ('KEY_OPENAI', cls.OPENAI_API_KEY),
            ('KEY_ANTHROPIC', cls.ANTHROPIC_API_KEY),
            ('DIR_CUSTOM', cls.CUSTOM_DIR)
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please check your .env file or environment variables.")
            return False
        
        if cls.PREFERRED_PROVIDER not in ['OPENAI', 'ANTHROPIC']:
            print(f"❌ Invalid PROVIDER_PREFERRED: {cls.PREFERRED_PROVIDER}")
            print("Must be either 'OPENAI' or 'ANTHROPIC'")
            return False
        
        if not os.path.exists(cls.CUSTOM_DIR):
            print(f"❌ Custom directory does not exist: {cls.CUSTOM_DIR}")
            return False
        
        print("✅ Configuration validation passed")
        return True
    
    @classmethod
    def get_provider_order(cls) -> list:
        """Get the order of providers to try (preferred first, then fallback)"""
        if cls.PREFERRED_PROVIDER == 'OPENAI':
            return ['OPENAI', 'ANTHROPIC']
        else:
            return ['ANTHROPIC', 'OPENAI']
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)"""
        print("📋 Current Configuration:")
        print(f"  Preferred Provider: {cls.PREFERRED_PROVIDER}")
        print(f"  OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"  Anthropic Model: {cls.ANTHROPIC_MODEL}")
        print(f"  Custom Directory: {cls.CUSTOM_DIR}")
        print(f"  Log Level: {cls.LOG_LEVEL}")
        print(f"  Max Retries: {cls.MAX_RETRIES}")
        print(f"  Content Length: {cls.CONTENT_LENGTH}")
        print(f"  Conversations Count: {cls.CONVERSATIONS_COUNT}")
        print(f"  Personalization Chance: {cls.CONVERSATIONS_CHANCE_PERSONALIZATION}%")
        print(f"  RSS Feed Chance: {cls.CONVERSATIONS_CHANCE_RSS}%")
        print(f"  Conditionals Chance: {cls.CONVERSATIONS_CHANCE_CONDITIONALS}%")
        print(f"  OpenAI API Key: {'✅ Set' if cls.OPENAI_API_KEY else '❌ Missing'}")
        print(f"  Anthropic API Key: {'✅ Set' if cls.ANTHROPIC_API_KEY else '❌ Missing'}")
