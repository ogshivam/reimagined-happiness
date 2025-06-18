"""
Quick test script for Together AI API key validation.
"""

import requests
import json

def test_together_api_key(api_key: str):
    """Test the Together AI API key and list available models."""
    
    print("🔑 Testing Together AI API Key...")
    print(f"Key: {api_key[:12]}...{api_key[-8:]}")
    print("=" * 50)
    
    try:
        # Test basic API connection - try different endpoints
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Try the correct API endpoint
        endpoints_to_try = [
            "https://api.together.xyz/v1/models",
            "https://api.together.ai/v1/models", 
            "https://api.together.xyz/models"
        ]
        
        response = None
        working_endpoint = None
        
        for endpoint in endpoints_to_try:
            try:
                print(f"🔍 Trying endpoint: {endpoint}")
                response = requests.get(endpoint, headers=headers, timeout=15)
                if response.status_code == 200 and 'application/json' in response.headers.get('content-type', ''):
                    working_endpoint = endpoint
                    break
                else:
                    print(f"   ❌ Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'unknown')}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        if not working_endpoint:
            print("❌ Could not find working API endpoint")
            return False, []
        
        print(f"✅ Found working endpoint: {working_endpoint}")
        
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Key is VALID and working!")
            
            # Debug: print response content
            print(f"📄 Response content type: {response.headers.get('content-type', 'unknown')}")
            print(f"📄 Response length: {len(response.text)} characters")
            
            try:
                models_data = response.json()
                print(f"📊 Total models available: {len(models_data)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"📄 Raw response: {response.text[:500]}...")
                return False, []
            
            # Filter for Llama models
            llama_models = []
            for model in models_data:
                model_id = model.get("id", "")
                if "llama" in model_id.lower():
                    llama_models.append({
                        "id": model_id,
                        "display_name": model.get("display_name", model_id),
                        "context_length": model.get("context_length", "Unknown"),
                        "type": model.get("type", "Unknown")
                    })
            
            print(f"🦙 Llama models found: {len(llama_models)}")
            print("\nAvailable Llama Models:")
            print("-" * 40)
            
            # Look specifically for Llama 4 models
            llama4_models = []
            llama3_models = []
            other_llama_models = []
            
            for model in llama_models:
                model_id = model["id"].lower()
                if "llama-4" in model_id or "llama4" in model_id:
                    llama4_models.append(model)
                elif "llama-3" in model_id or "llama3" in model_id:
                    llama3_models.append(model)
                else:
                    other_llama_models.append(model)
            
            # Display Llama 4 models first
            if llama4_models:
                print("🚀 LLAMA 4 MODELS:")
                for model in llama4_models:
                    print(f"   ✨ {model['id']}")
                    print(f"      Display Name: {model['display_name']}")
                    print(f"      Context: {model['context_length']} tokens")
                    print()
            else:
                print("❌ No Llama 4 models found")
            
            # Display Llama 3 models
            if llama3_models:
                print("🦙 LLAMA 3 MODELS:")
                for model in llama3_models[:5]:  # Show top 5
                    print(f"   🔥 {model['id']}")
                    print(f"      Context: {model['context_length']} tokens")
                if len(llama3_models) > 5:
                    print(f"   ... and {len(llama3_models) - 5} more Llama 3 models")
                print()
            
            # Display other Llama models
            if other_llama_models:
                print("📚 OTHER LLAMA MODELS:")
                for model in other_llama_models[:3]:  # Show top 3
                    print(f"   📖 {model['id']}")
                if len(other_llama_models) > 3:
                    print(f"   ... and {len(other_llama_models) - 3} more")
                print()
            
            return True, llama_models
            
        elif response.status_code == 401:
            print("❌ API Key is INVALID or EXPIRED")
            print("   Please check your API key")
            return False, []
            
        elif response.status_code == 403:
            print("❌ API Key is valid but ACCESS DENIED")
            print("   Your account may not have access to the API")
            return False, []
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, []
            
    except requests.exceptions.Timeout:
        print("❌ Request TIMEOUT - API server may be slow")
        return False, []
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Check your internet connection")
        return False, []
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, []

def test_model_inference(api_key: str, model_id: str):
    """Test actual model inference with a simple query."""
    
    print(f"\n🧪 Testing model inference: {model_id}")
    print("-" * 50)
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_id,
            "messages": [
                {
                    "role": "user", 
                    "content": "Generate a simple SQL query to count all records in a table called 'users'. Just respond with the SQL query only."
                }
            ],
            "max_tokens": 100,
            "temperature": 0
        }
        
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            print(f"✅ Model response:")
            print(f"   {message.strip()}")
            return True
        else:
            print(f"❌ Inference failed: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Inference error: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the provided API key
    api_key = "tgp_v1_XELYRCJuDTY69-ICL7OBEONSAYquezhyLAMfyi5-Cgc"
    
    success, models = test_together_api_key(api_key)
    
    if success and models:
        print("\n" + "=" * 50)
        print("🎉 API KEY TEST SUCCESSFUL!")
        
        # Test inference with the first available Llama model
        if models:
            test_model = models[0]["id"]
            print(f"\n🔬 Testing inference with: {test_model}")
            inference_success = test_model_inference(api_key, test_model)
            
            if inference_success:
                print("\n✅ Ready to integrate into the project!")
                print("\nNext steps:")
                print("1. Set environment variable: export TOGETHER_API_KEY=tgp_v1_XELYRCJuDTY69-ICL7OBEONSAYquezhyLAMfyi5-Cgc")
                print("2. Run: python test_tool.py")
                print("3. Run: streamlit run app.py")
            else:
                print("\n⚠️  API key works but inference failed - may need debugging")
        
    else:
        print("\n❌ API KEY TEST FAILED")
        print("Please check the API key and try again") 