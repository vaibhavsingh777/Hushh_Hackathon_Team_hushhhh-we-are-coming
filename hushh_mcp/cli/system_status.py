#!/usr/bin/env python3
"""
Hushh MCP - System Status CLI
Check the status of all components and LLM providers.
"""

import os
import sys
import requests
import subprocess
from typing import Dict, Any


def check_backend_status() -> Dict[str, Any]:
    """Check if the backend server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return {"status": "✅ Running", "details": "Backend server is healthy"}
        else:
            return {"status": "⚠️ Issues", "details": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException:
        return {"status": "❌ Down", "details": "Backend server not responding"}


def check_frontend_status() -> Dict[str, Any]:
    """Check if the frontend is accessible."""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            return {"status": "✅ Running", "details": "Frontend accessible"}
        else:
            return {"status": "⚠️ Issues", "details": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException:
        return {"status": "❌ Down", "details": "Frontend not accessible"}


def check_ollama_status() -> Dict[str, Any]:
    """Check Ollama status and available models."""
    try:
        # Check if Ollama service is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name', 'Unknown') for m in models]
            
            if models:
                return {
                    "status": "✅ Running", 
                    "details": f"{len(models)} models available: {', '.join(model_names[:3])}"
                }
            else:
                return {
                    "status": "⚠️ No Models", 
                    "details": "Ollama running but no models installed. Run: ollama pull llama3.2:3b"
                }
        else:
            return {"status": "❌ Error", "details": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException:
        return {"status": "❌ Down", "details": "Ollama not running. Run: ollama serve"}


def check_api_keys() -> Dict[str, Any]:
    """Check which API keys are configured."""
    keys = {}
    
    # Check Hugging Face
    hf_key = os.getenv("HUGGINGFACE_API_KEY", "")
    if hf_key and len(hf_key) > 10 and not hf_key.startswith("your"):
        keys["Hugging Face"] = "✅ Configured"
    else:
        keys["Hugging Face"] = "❌ Not set"
    
    # Check Groq
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key and len(groq_key) > 10 and not groq_key.startswith("your"):
        keys["Groq"] = "✅ Configured"
    else:
        keys["Groq"] = "❌ Not set"
    
    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and len(openai_key) > 20 and not openai_key.startswith("your"):
        keys["OpenAI"] = "⚠️ Configured (has quota limits)"
    else:
        keys["OpenAI"] = "❌ Not set"
    
    return keys


def check_google_oauth() -> Dict[str, Any]:
    """Check Google OAuth configuration."""
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    if client_id and client_secret and not client_id.startswith("your"):
        return {"status": "✅ Configured", "details": "Google OAuth ready"}
    else:
        return {"status": "❌ Not configured", "details": "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"}


def test_categorization() -> Dict[str, Any]:
    """Test the categorization system."""
    try:
        # Import and test the categorization function
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from hushh_mcp.operons.categorize_content import categorize_with_free_llm
        
        test_content = "Team meeting about quarterly budget review and project deadlines"
        categories = categorize_with_free_llm(test_content)
        
        if categories and len(categories) > 0:
            return {
                "status": "✅ Working", 
                "details": f"Test categorization: {', '.join(categories)}"
            }
        else:
            return {"status": "❌ Failed", "details": "No categories returned"}
            
    except Exception as e:
        return {"status": "❌ Error", "details": f"Categorization test failed: {str(e)}"}


def main():
    """Main status check function."""
    print("🚀 Hushh MCP - System Status Check")
    print("=" * 50)
    
    # Load environment variables
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    checks = [
        ("Backend Server", check_backend_status),
        ("Frontend", check_frontend_status),
        ("Ollama (Local AI)", check_ollama_status),
        ("Google OAuth", check_google_oauth),
        ("Categorization Test", test_categorization),
    ]
    
    print("\n🔍 Component Status:")
    for name, check_func in checks:
        result = check_func()
        print(f"  {name:20} {result['status']}")
        if 'details' in result:
            print(f"  {' ' * 20} {result['details']}")
    
    print("\n🔑 API Keys Status:")
    api_keys = check_api_keys()
    for provider, status in api_keys.items():
        print(f"  {provider:20} {status}")
    
    print("\n💡 Recommendations:")
    
    # Check if Ollama is the best option
    ollama_status = check_ollama_status()
    if "Running" in ollama_status["status"]:
        print("  ✅ Ollama is running - you have the best setup for privacy and cost!")
    else:
        print("  💡 Install Ollama for the best experience:")
        print("     - Download from https://ollama.com/download")
        print("     - Run: ollama serve")
        print("     - Run: ollama pull llama3.2:3b")
    
    # Check if any API keys are available
    configured_keys = [k for k, v in check_api_keys().items() if "✅" in v]
    if not configured_keys and "Running" not in ollama_status["status"]:
        print("  ⚠️ No LLM providers configured!")
        print("     - Recommended: Install Ollama (completely free)")
        print("     - Alternative: Get Hugging Face API key (also free)")
        print("     - See FREE_LLM_SETUP.md for instructions")
    
    print("\n🌟 System Summary:")
    backend = check_backend_status()
    frontend = check_frontend_status()
    categorization = test_categorization()
    
    if all("✅" in result["status"] for result in [backend, frontend, categorization]):
        print("  🎉 All systems operational! Your Hushh MCP is ready to use.")
    elif "✅" in backend["status"] and "✅" in categorization["status"]:
        print("  ✅ Core functionality working. Backend and AI categorization ready.")
    else:
        print("  ⚠️ Some issues detected. Check the details above.")
    
    print("\n📚 Useful Commands:")
    print("  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("  python -m http.server 3000 --directory frontend")
    print("  python hushh_mcp/cli/setup_ollama.py")
    print("  ollama serve")
    print("  ollama pull llama3.2:3b")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Status check cancelled")
    except Exception as e:
        print(f"\n❌ Error during status check: {str(e)}")
