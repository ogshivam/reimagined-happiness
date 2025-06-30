#!/bin/bash

# Enhanced Text-to-SQL Application - Test Runner Script
# This script sets up the environment and runs comprehensive tests

echo "🚀 Enhanced Text-to-SQL Application - Test Runner"
echo "=================================================="

# Set the API key
export TOGETHER_API_KEY="tgp_v1_XELYRCJuDTY69-ICL7OBEONSAYquezhyLAMfyi5-Cgc"
echo "✅ API Key configured"

# Check if we're in the right directory
if [ ! -f "chinook.db" ]; then
    echo "❌ Error: chinook.db not found in current directory"
    echo "Please run this script from the directory containing chinook.db"
    exit 1
fi

if [ ! -f "app_enhanced.py" ]; then
    echo "❌ Error: app_enhanced.py not found in current directory"
    echo "Please run this script from the directory containing the app files"
    exit 1
fi

echo "✅ Database and app files found"

# Function to show menu
show_menu() {
    echo ""
    echo "🎯 What would you like to do?"
    echo "1. Run Comprehensive Tests (Python script)"
    echo "2. Run Compatibility Tests (validate fixes)"
    echo "3. Run Streamlit App (Multi-approach interface)"
    echo "4. Run Chat App (Conversational SQL assistant)"  
    echo "5. View Session State Demo (educational)"
    echo "6. Run both Tests and then Apps"
    echo "7. Install/Update Dependencies"
    echo "8. Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice
}

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing/Updating dependencies..."
    
    if command -v pip &> /dev/null; then
        pip install -r requirements.txt
        echo "✅ Dependencies installed via pip"
    elif command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
        echo "✅ Dependencies installed via pip3"
    else
        echo "❌ Neither pip nor pip3 found. Please install Python and pip first."
        return 1
    fi
}

# Function to run comprehensive tests
run_tests() {
    echo ""
    echo "🧪 Running Comprehensive Test Suite..."
    echo "======================================"
    
    if command -v python &> /dev/null; then
        python test_comprehensive.py
    elif command -v python3 &> /dev/null; then
        python3 test_comprehensive.py
    else
        echo "❌ Python not found. Please install Python first."
        return 1
    fi
    
    echo ""
    echo "🎯 Tests completed! Check the generated JSON report for detailed results."
}

# Function to run Streamlit app
run_app() {
    echo ""
    echo "🌐 Starting Multi-Approach Streamlit App..."
    echo "============================================="
    echo "The app will open in your default browser."
    echo "If it doesn't open automatically, go to: http://localhost:8501"
    echo ""
    echo "Press Ctrl+C to stop the app when you're done testing."
    echo ""
    
    if command -v streamlit &> /dev/null; then
        streamlit run app_enhanced.py
    else
        echo "❌ Streamlit not found. Installing..."
        if command -v pip &> /dev/null; then
            pip install streamlit
            streamlit run app_enhanced.py
        elif command -v pip3 &> /dev/null; then
            pip3 install streamlit
            streamlit run app_enhanced.py
        else
            echo "❌ Cannot install Streamlit. Please install pip first."
            return 1
        fi
    fi
}

# Function to run Chat app
run_chat_app() {
    echo ""
    echo "💬 Starting SQL Chat Assistant..."
    echo "=================================="
    echo "The chat app will open in your default browser."
    echo "If it doesn't open automatically, go to: http://localhost:8501"
    echo ""
    echo "Press Ctrl+C to stop the chat app when you're done."
    echo ""
    
    if command -v streamlit &> /dev/null; then
        streamlit run app_chat.py
    else
        echo "❌ Streamlit not found. Installing..."
        if command -v pip &> /dev/null; then
            pip install streamlit
            streamlit run app_chat.py
        elif command -v pip3 &> /dev/null; then
            pip3 install streamlit
            streamlit run app_chat.py
        else
            echo "❌ Cannot install Streamlit. Please install pip first."
            return 1
        fi
    fi
}

# Main menu loop
while true; do
    show_menu
    
    case $choice in
        1)
            run_tests
            ;;
        2)
            echo ""
            echo "🔍 Running Compatibility Tests..."
            echo "=================================="
            if command -v python &> /dev/null; then
                python test_fixes.py
            elif command -v python3 &> /dev/null; then
                python3 test_fixes.py
            else
                echo "❌ Python not found. Please install Python first."
            fi
            ;;
        3)
            run_app
            ;;
        4)
            run_chat_app
            ;;
        5)
            echo ""
            echo "📚 Starting Session State Educational Demo..."
            echo "============================================="
            echo "This demo shows correct vs incorrect session state patterns."
            echo ""
            if command -v streamlit &> /dev/null; then
                streamlit run streamlit_session_state_demo.py
            else
                echo "❌ Streamlit not found. Installing..."
                if command -v pip &> /dev/null; then
                    pip install streamlit
                    streamlit run streamlit_session_state_demo.py
                else
                    echo "❌ Cannot install Streamlit. Please install pip first."
                fi
            fi
            ;;
        6)
            run_tests
            if [ $? -eq 0 ]; then
                echo ""
                echo "🎉 Tests completed successfully! Choose which app to start:"
                echo "1. Multi-approach App (app_enhanced.py)"
                echo "2. Chat App (app_chat.py)"
                read -p "Enter choice (1-2): " app_choice
                
                case $app_choice in
                    1)
                        echo "Starting Multi-approach App..."
                        sleep 2
                        run_app
                        ;;
                    2)
                        echo "Starting Chat App..."
                        sleep 2
                        run_chat_app
                        ;;
                    *)
                        echo "Invalid choice. Starting Multi-approach App by default..."
                        sleep 2
                        run_app
                        ;;
                esac
            else
                echo "❌ Tests failed. Check the output above for details."
            fi
            ;;
        7)
            install_dependencies
            ;;
        8)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, or 8."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read
done 