"""
Setup script for Together AI configuration and model management.
"""

import os
import requests
import json
from config import TOGETHER_MODELS

def check_api_key():
    """Check if Together AI API key is configured."""
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        print("✅ Together AI API key found")
        print(f"   Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}")
        return api_key
    else:
        print("❌ Together AI API key not found")
        return None

def test_api_connection(api_key: str):
    """Test connection to Together AI API."""
    print("\n🔗 Testing API connection...")
    
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://api.together.xyz/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Together AI API connection successful")
            return True, response.json()
        elif response.status_code == 401:
            print("❌ API key is invalid or expired")
            return False, None
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False, None

def list_available_models(api_key: str):
    """List available models from Together AI."""
    print("\n📋 Checking available models...")
    
    success, models_data = test_api_connection(api_key)
    if not success or not models_data:
        return []
    
    # Filter for Llama models
    llama_models = []
    for model in models_data:
        model_id = model.get("id", "")
        if "llama" in model_id.lower():
            llama_models.append({
                "id": model_id,
                "name": model.get("display_name", model_id),
                "context_length": model.get("context_length", "Unknown"),
                "pricing": model.get("pricing", {})
            })
    
    if llama_models:
        print(f"✅ Found {len(llama_models)} Llama models")
        print("\nTop Llama models available:")
        
        # Show our recommended models first
        for model_id, description in list(TOGETHER_MODELS.items())[:5]:
            matching_model = next((m for m in llama_models if m["id"] == model_id), None)
            if matching_model:
                context = matching_model["context_length"]
                print(f"   🦙 {description}")
                print(f"      Model ID: {model_id}")
                print(f"      Context: {context} tokens")
                print()
    else:
        print("❌ No Llama models found")
    
    return llama_models

def show_model_recommendations():
    """Show model recommendations for different use cases."""
    print("\n💡 Model Recommendations:")
    print("=" * 50)
    
    recommendations = [
        {
            "use_case": "🚀 Best Overall Performance",
            "model": "meta-llama/Llama-3-70b-chat-hf",
            "description": "Most capable model, best for complex SQL queries"
        },
        {
            "use_case": "⚡ Fastest Response",
            "model": "meta-llama/Llama-3-8b-chat-hf", 
            "description": "Smaller model, faster responses, good for simple queries"
        },
        {
            "use_case": "🆕 Latest Model",
            "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "description": "Latest Llama 3.1 with improved reasoning"
        },
        {
            "use_case": "💻 Code-Specialized",
            "model": "meta-llama/CodeLlama-34b-Instruct-hf",
            "description": "Specialized for code generation and SQL"
        }
    ]
    
    for rec in recommendations:
        print(f"{rec['use_case']}")
        print(f"   Model: {rec['model']}")
        print(f"   {rec['description']}")
        print()

def setup_environment_file():
    """Create environment configuration."""
    env_content = """# Together AI Configuration
TOGETHER_API_KEY=your_together_ai_api_key
TOGETHER_MODEL=meta-llama/Llama-3-70b-chat-hf

# LangSmith (optional)
# LANGCHAIN_API_KEY=your_langsmith_api_key
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_PROJECT=text-to-sql-tool
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created .env file with default Together AI settings")
        print("   Remember to add your actual API key!")
    else:
        print("ℹ️  .env file already exists")

def estimate_costs():
    """Show cost estimates for different models."""
    print("\n💰 Cost Estimates (approximate):")
    print("=" * 40)
    
    # These are example rates - actual rates may vary
    cost_info = [
        ("Llama-3-8b", "$0.20 per 1M tokens", "~$0.002 per 100 queries"),
        ("Llama-3-70b", "$0.90 per 1M tokens", "~$0.009 per 100 queries"),
        ("CodeLlama-34b", "$0.80 per 1M tokens", "~$0.008 per 100 queries"),
    ]
    
    for model, rate, estimate in cost_info:
        print(f"   {model}: {rate} ({estimate})")
    
    print("\n   Note: Costs depend on query complexity and response length")
    print("   Check https://api.together.xyz/pricing for current rates")

def main():
    """Main setup function."""
    print("🤝 Together AI Setup for Text-to-SQL Tool")
    print("=" * 50)
    
    # Check API key
    api_key = check_api_key()
    
    if not api_key:
        print("\n📋 To get your API key:")
        print("1. Visit: https://api.together.xyz/settings/api-keys")
        print("2. Sign up or log in")
        print("3. Create a new API key")
        print("4. Set it as environment variable:")
        print("   export TOGETHER_API_KEY=your_key_here")
        
        setup_environment_file()
        return 1
    
    # Test connection and list models
    available_models = list_available_models(api_key)
    
    if available_models:
        # Show recommendations
        show_model_recommendations()
        
        # Show cost estimates
        estimate_costs()
        
        # Setup environment file
        setup_environment_file()
        
        print("\n🎉 Setup complete!")
        print("\nNext steps:")
        print("1. Make sure your API key is set correctly")
        print("2. Run: python test_tool.py")
        print("3. Run: streamlit run app.py")
        
        print(f"\n📊 You have access to {len(available_models)} Llama models")
        print("   Use the Streamlit app to easily switch between models!")
        
    else:
        print("\n❌ Could not access models. Please check your API key.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 