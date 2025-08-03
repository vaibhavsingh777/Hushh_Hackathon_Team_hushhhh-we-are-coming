#!/usr/bin/env python3
"""
Hushh MCP - Ollama Setup CLI
Helps set up and manage Ollama for local LLM processing.
"""

import os
import sys
import time
import requests
import subprocess
from typing import List, Dict, Any


def check_ollama_installation() -> bool:
    """Check if Ollama is installed and accessible."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Ollama installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama command not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama not installed or not in PATH")
        return False


def check_ollama_service() -> bool:
    """Check if Ollama service is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
        else:
            print(f"❌ Ollama service error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama service not running: {str(e)}")
        return False


def get_available_models() -> List[Dict[str, Any]]:
    """Get list of available models from Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('models', [])
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to Ollama: {str(e)}")
        return []


def pull_model(model_name: str) -> bool:
    """Pull a model from Ollama registry."""
    try:
        print(f"🔄 Pulling model '{model_name}'... This may take a few minutes.")
        
        # Use subprocess to run ollama pull command
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"✅ Successfully pulled model '{model_name}'")
            return True
        else:
            print(f"❌ Failed to pull model '{model_name}': {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout while pulling model '{model_name}'")
        return False
    except Exception as e:
        print(f"❌ Error pulling model '{model_name}': {str(e)}")
        return False


def test_model_categorization(model_name: str) -> bool:
    """Test if a model can perform categorization."""
    try:
        prompt = """You are an AI categorization assistant. Categorize the following text into 1-3 semantic categories from this list:
work, personal, finance, health, education, shopping, travel, entertainment, social, communication, scheduling, documentation, general, uncategorized.

Text to categorize: Team meeting about quarterly budget review and project deadlines

Respond ONLY with category names separated by commas. No explanations or extra text."""

        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 50
            }
        }
        
        print(f"🧪 Testing model '{model_name}' for categorization...")
        response = requests.post("http://localhost:11434/api/generate", 
                               json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            categories = result.get('response', '').strip()
            print(f"✅ Model response: {categories}")
            
            # Check if response contains valid categories
            valid_categories = ['work', 'finance', 'scheduling']
            response_lower = categories.lower()
            found_valid = any(cat in response_lower for cat in valid_categories)
            
            if found_valid:
                print(f"✅ Model '{model_name}' works well for categorization!")
                return True
            else:
                print(f"⚠️ Model '{model_name}' response needs improvement")
                return False
        else:
            print(f"❌ Test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing model '{model_name}': {str(e)}")
        return False


def setup_recommended_model():
    """Set up the recommended model for Hushh categorization."""
    recommended_models = [
        "llama3.2:3b",    # Lightweight and fast
        "llama3.2:1b",    # Even lighter
        "phi3:mini",      # Microsoft's efficient model
        "mistral:7b",     # Good balance
        "llama3.1:8b"     # Larger but more accurate
    ]
    
    print("\n🎯 Recommended models for Hushh categorization:")
    for i, model in enumerate(recommended_models, 1):
        print(f"{i}. {model}")
    
    print("\n💡 Recommendation: Start with 'llama3.2:3b' (good balance of speed and accuracy)")
    
    choice = input("\nEnter model number to install (1-5) or model name: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(recommended_models):
        model_name = recommended_models[int(choice) - 1]
    else:
        model_name = choice
    
    if model_name:
        success = pull_model(model_name)
        if success:
            print(f"\n🧪 Testing the model...")
            test_model_categorization(model_name.split(':')[0])  # Use base name for testing
        return success
    
    return False


def main():
    """Main setup function."""
    print("🚀 Hushh MCP - Ollama Setup Assistant")
    print("====================================")
    
    # Check Ollama installation
    if not check_ollama_installation():
        print("\n📥 Please install Ollama first:")
        print("   Windows: Download from https://ollama.com/download")
        print("   macOS: brew install ollama")
        print("   Linux: curl -fsSL https://ollama.com/install.sh | sh")
        return False
    
    # Check if service is running
    if not check_ollama_service():
        print("\n🔄 Starting Ollama service...")
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['ollama', 'serve'], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Unix-like
                subprocess.Popen(['ollama', 'serve'])
            
            print("⏳ Waiting for service to start...")
            time.sleep(5)
            
            if not check_ollama_service():
                print("❌ Failed to start Ollama service")
                print("💡 Try running 'ollama serve' manually in another terminal")
                return False
        except Exception as e:
            print(f"❌ Error starting Ollama: {str(e)}")
            return False
    
    # Check available models
    models = get_available_models()
    if models:
        print(f"\n📦 Available models ({len(models)}):")
        for model in models[:5]:  # Show first 5
            name = model.get('name', 'Unknown')
            size = model.get('size', 0) // (1024**3)  # Convert to GB
            print(f"   • {name} ({size}GB)")
        
        if len(models) > 5:
            print(f"   ... and {len(models) - 5} more")
    
    # Setup or verify model
    suitable_models = [m for m in models if any(x in m.get('name', '') for x in ['llama3', 'phi3', 'mistral'])]
    
    if suitable_models:
        print(f"\n✅ Found {len(suitable_models)} suitable model(s) for categorization")
        model_name = suitable_models[0].get('name', '').split(':')[0]
        test_model_categorization(model_name)
    else:
        print("\n📥 No suitable models found. Let's install one!")
        setup_recommended_model()
    
    print("\n✅ Ollama setup complete!")
    print("💡 Your Hushh system will now use local AI for categorization")
    print("🔒 All processing happens locally - no data sent to cloud!")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
