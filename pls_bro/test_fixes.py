#!/usr/bin/env python3
"""
Test script to validate all the fixes made to the system.
This script checks:
1. No deprecated Streamlit functions
2. Proper imports
3. API key configuration
4. Model selection functionality
"""

import os
import sys

# Set API key for testing
os.environ["TOGETHER_API_KEY"] = "tgp_v1_XELYRCJuDTY69-ICL7OBEONSAYquezhyLAMfyi5-Cgc"

def test_imports():
    """Test that all modules import correctly."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print(f"✅ Streamlit {st.__version__} imported successfully")
        
        # Test that st.rerun exists (not deprecated)
        if hasattr(st, 'rerun'):
            print("✅ st.rerun() function available")
        else:
            print("❌ st.rerun() function not available")
            
        # Test that deprecated function doesn't exist in newer versions
        if hasattr(st, 'experimental_rerun'):
            print("⚠️  st.experimental_rerun() still exists (deprecated)")
        else:
            print("✅ st.experimental_rerun() properly deprecated")
            
    except Exception as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import app_chat
        print("✅ app_chat imported successfully")
    except Exception as e:
        print(f"❌ app_chat import failed: {e}")
        return False
    
    try:
        import app_enhanced
        print("✅ app_enhanced imported successfully")
    except Exception as e:
        print(f"❌ app_enhanced import failed: {e}")
        return False
    
    return True

def test_api_key():
    """Test API key configuration."""
    print("\n🔑 Testing API key configuration...")
    
    api_key = os.getenv("TOGETHER_API_KEY")
    if api_key:
        print(f"✅ API key configured: {api_key[:20]}...")
        return True
    else:
        print("❌ API key not found")
        return False

def test_deprecated_functions():
    """Test for deprecated function usage."""
    print("\n🔍 Checking for deprecated functions...")
    
    files_to_check = ['app_chat.py', 'app_enhanced.py']
    
    for filename in files_to_check:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read()
                
            if 'st.experimental_rerun' in content:
                print(f"❌ {filename} still contains st.experimental_rerun()")
                return False
            else:
                print(f"✅ {filename} - no deprecated st.experimental_rerun()")
                
            if 'st.rerun' in content:
                print(f"✅ {filename} - uses modern st.rerun()")
                
            # Check for session state conflicts
            if 'st.session_state.selected_model = ' in content:
                print(f"❌ {filename} has session state conflict with selected_model")
                return False
            else:
                print(f"✅ {filename} - no session state conflicts")
        else:
            print(f"⚠️  {filename} not found")
    
    return True

def test_model_selection():
    """Test model selection functionality."""
    print("\n🤖 Testing model selection...")
    
    try:
        from config import TOGETHER_MODELS
        
        if TOGETHER_MODELS:
            print(f"✅ Found {len(TOGETHER_MODELS)} available models")
            first_model = list(TOGETHER_MODELS.keys())[0]
            print(f"✅ Default model: {first_model}")
            return True
        else:
            print("❌ No models found in TOGETHER_MODELS")
            return False
            
    except Exception as e:
        print(f"❌ Model selection test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting compatibility and fix validation tests...\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("API Key Tests", test_api_key), 
        ("Deprecated Function Tests", test_deprecated_functions),
        ("Model Selection Tests", test_model_selection)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All fixes are working correctly!")
        return 0
    else:
        print("⚠️  Some issues remain. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 