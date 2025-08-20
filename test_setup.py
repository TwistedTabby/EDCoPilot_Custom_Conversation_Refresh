"""
Test script for EDCopilot Chit Chat Updater
Validates setup and configuration
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from src.config import Config
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Config: {e}")
        return False
    
    try:
        from src.utils.api_client import APIClient
        print("✅ API Client module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import API Client: {e}")
        return False
    
    try:
        from src.utils.file_manager import FileManager
        print("✅ File Manager module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import File Manager: {e}")
        return False
    
    try:
        from src.generators.chit_chat_generator import ChitChatGenerator
        print("✅ ChitChat Generator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ChitChat Generator: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        from src.config import Config
        
        # Test basic configuration loading
        print(f"  Preferred Provider: {Config.PREFERRED_PROVIDER}")
        print(f"  OpenAI Model: {Config.OPENAI_MODEL}")
        print(f"  Anthropic Model: {Config.ANTHROPIC_MODEL}")
        print(f"  Log Level: {Config.LOG_LEVEL}")
        print(f"  Max Retries: {Config.MAX_RETRIES}")
        
        # Test API key presence (without revealing keys)
        openai_key_set = bool(Config.OPENAI_API_KEY)
        anthropic_key_set = bool(Config.ANTHROPIC_API_KEY)
        
        print(f"  OpenAI API Key: {'✅ Set' if openai_key_set else '❌ Missing'}")
        print(f"  Anthropic API Key: {'✅ Set' if anthropic_key_set else '❌ Missing'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_file_structure():
    """Test that required files and directories exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "requirements.txt",
        "env.example",
        "src/main.py",
        "src/config.py",
        "src/utils/api_client.py",
        "src/utils/file_manager.py",
        "src/generators/base_generator.py",
        "src/generators/chit_chat_generator.py",
        "src/generators/space_chatter_generator.py",
        "src/generators/crew_chatter_generator.py",
        "src/generators/deep_space_chatter_generator.py",
        "scheduler.py",
        "README.md"
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            all_files_exist = False
    
    return all_files_exist

def test_dependencies():
    """Test that required dependencies are available"""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        "openai",
        "anthropic", 
        "dotenv",
        "requests",
        "schedule",
        "colorama",
        "tqdm",
        "feedparser"
    ]
    
    all_deps_available = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            all_deps_available = False
    
    return all_deps_available

def test_generators():
    """Test that generators can be instantiated"""
    print("\n🔍 Testing generators...")
    
    try:
        from src.generators.chit_chat_generator import ChitChatGenerator
        from src.generators.space_chatter_generator import SpaceChatterGenerator
        from src.generators.crew_chatter_generator import CrewChatterGenerator
        from src.generators.deep_space_chatter_generator import DeepSpaceChatterGenerator
        
        generators = [
            ("ChitChat", ChitChatGenerator()),
            ("SpaceChatter", SpaceChatterGenerator()),
            ("CrewChatter", CrewChatterGenerator()),
            ("DeepSpaceChatter", DeepSpaceChatterGenerator())
        ]
        
        for name, generator in generators:
            chatter_type = generator.get_chatter_type()
            prompt_template = generator.get_prompt_template()
            
            if chatter_type and prompt_template:
                print(f"✅ {name} Generator: {chatter_type}")
            else:
                print(f"❌ {name} Generator: Invalid configuration")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Generator test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 EDCopilot Chit Chat Updater - Setup Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Generators", test_generators)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
