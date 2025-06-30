#!/usr/bin/env python3
"""
Demo Script: Chat App vs Multi-Approach App
Demonstrates the differences and use cases for both applications
"""

import os
import time
from datetime import datetime

# Set API key
os.environ["TOGETHER_API_KEY"] = "tgp_v1_XELYRCJuDTY69-ICL7OBEONSAYquezhyLAMfyi5-Cgc"

def main():
    """Main demo function."""
    print("🎯 Enhanced Text-to-SQL Applications Demo")
    print("=" * 50)
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("You now have TWO powerful applications to choose from:")
    print()
    
    print("📊 1. MULTI-APPROACH APP (app_enhanced.py)")
    print("=" * 45)
    print("🎯 **Best for**: Testing different AI approaches")
    print("⚡ **Features:**")
    print("   • Three different approaches side-by-side")
    print("   • SQL Chain (fast, simple)")
    print("   • Simple Agent (reasoning, retry)")
    print("   • Enhanced Agent (full visualization pipeline)")
    print("   • Compare performance and results")
    print("   • Single-query interface")
    print("   • Intermediate results always shown")
    print()
    print("🔥 **Use Cases:**")
    print("   • Development and testing")
    print("   • Comparing AI approaches")
    print("   • One-off data analysis queries")
    print("   • Learning how different methods work")
    print()
    
    print("💬 2. CHAT APP (app_chat.py)")
    print("=" * 30)
    print("🎯 **Best for**: Natural conversations about data")
    print("⚡ **Features:**")
    print("   • Conversational interface like ChatGPT")
    print("   • Follow-up question detection")
    print("   • Context awareness (remembers previous queries)")
    print("   • Enhanced Agent only (most advanced)")
    print("   • Multi-turn conversations")
    print("   • Chat history and context display")
    print()
    print("🔥 **Use Cases:**")
    print("   • Business intelligence conversations")
    print("   • Exploratory data analysis")
    print("   • Follow-up questions and refinements")
    print("   • Natural, ChatGPT-like experience")
    print()
    
    print("🤔 **WHICH ONE TO CHOOSE?**")
    print("=" * 30)
    print()
    
    print("Choose **MULTI-APPROACH APP** if you want to:")
    print("  ✅ Test different AI approaches")
    print("  ✅ See intermediate steps (SQL queries, debug info)")
    print("  ✅ Compare performance and accuracy")
    print("  ✅ One-time queries")
    print("  ✅ Development and testing")
    print()
    
    print("Choose **CHAT APP** if you want to:")
    print("  ✅ Natural conversation about your data")
    print("  ✅ Ask follow-up questions")
    print("  ✅ Refine and explore results")
    print("  ✅ ChatGPT-like experience")
    print("  ✅ Business intelligence conversations")
    print()
    
    print("💡 **CONVERSATION EXAMPLES**")
    print("=" * 30)
    print()
    print("**Multi-Approach App style:**")
    print("❓ User enters: 'What are the top 5 selling artists?'")
    print("🔄 User clicks 'Enhanced Agent'")
    print("📊 Gets answer + charts + insights")
    print("❓ User enters new question: 'Show me revenue by country'")
    print("🔄 User clicks 'Enhanced Agent' again")
    print("📊 Gets completely new analysis")
    print()
    
    print("**Chat App style:**")
    print("❓ User: 'What are the top 5 selling artists?'")
    print("🤖 Assistant: [Answer + charts + insights]")
    print("❓ User: 'Tell me more about the top artist'")
    print("🤖 Assistant: [Understands 'top artist' refers to previous result]")
    print("❓ User: 'What about their albums?'")
    print("🤖 Assistant: [Knows we're still talking about the same artist]")
    print("❓ User: 'Compare this with other genres'")
    print("🤖 Assistant: [Uses context to make relevant comparison]")
    print()
    
    print("🚀 **QUICK START COMMANDS**")
    print("=" * 30)
    print()
    print("🎮 Interactive Menu (Recommended):")
    print("   ./run_tests.sh")
    print()
    print("⚡ Quick Tests:")
    print("   python quick_test.py          # Test both apps quickly")
    print("   python test_chat_app.py       # Test chat functionality")
    print()
    print("🌐 Direct App Launch:")
    print("   streamlit run app_enhanced.py # Multi-approach app")
    print("   streamlit run app_chat.py     # Chat app")
    print()
    
    print("💡 **TECHNICAL DETAILS**")
    print("=" * 30)
    print()
    print("**Both apps use:**")
    print("  • Same Enhanced Agent underneath")
    print("  • Same visualization capabilities")
    print("  • Same AI models (Llama 4, Llama 3.3, etc.)")
    print("  • Same database (Chinook music store)")
    print("  • Same chart generation (Plotly)")
    print()
    print("**Key differences:**")
    print("  • Multi-approach: Single queries, multiple methods")
    print("  • Chat: Conversational flow, context awareness")
    print()
    
    # Interactive choice
    print("🎯 **WHAT WOULD YOU LIKE TO DO?**")
    print("-" * 40)
    
    try:
        while True:
            print("\n1. 🧪 Run quick tests for both apps")
            print("2. 📊 Start Multi-Approach App")
            print("3. 💬 Start Chat App")
            print("4. 🎮 Open Interactive Menu")
            print("5. 👋 Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\n🧪 Running quick tests...")
                print("This will test basic functionality of both apps.\n")
                os.system("python quick_test.py")
                
            elif choice == "2":
                print("\n📊 Starting Multi-Approach App...")
                print("🌐 Opening at: http://localhost:8501")
                print("Press Ctrl+C to stop when done.\n")
                time.sleep(2)
                os.system("streamlit run app_enhanced.py")
                
            elif choice == "3":
                print("\n💬 Starting Chat App...")
                print("🌐 Opening at: http://localhost:8501")
                print("Press Ctrl+C to stop when done.\n")
                time.sleep(2)
                os.system("streamlit run app_chat.py")
                
            elif choice == "4":
                print("\n🎮 Opening Interactive Menu...")
                os.system("./run_tests.sh")
                
            elif choice == "5":
                print("\n👋 Thanks for trying our Enhanced Text-to-SQL applications!")
                print("💡 Remember:")
                print("   📊 Multi-approach for testing and comparison")
                print("   💬 Chat for natural conversations")
                break
                
            else:
                print("\n❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 