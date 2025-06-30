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
    echo "2. Run Streamlit App (Interactive web interface)"
    echo "3. Run both Tests and then App"
    echo "4. Install/Update Dependencies"
    echo "5. Exit"
    echo ""
    read -p "Enter your choice (1-5): " choice
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
    echo "🌐 Starting Streamlit App..."
    echo "============================"
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

# Main menu loop
while true; do
    show_menu
    
    case $choice in
        1)
            run_tests
            ;;
        2)
            run_app
            ;;
        3)
            run_tests
            if [ $? -eq 0 ]; then
                echo ""
                echo "🎉 Tests completed successfully! Now starting the app..."
                sleep 3
                run_app
            else
                echo "❌ Tests failed. Check the output above for details."
            fi
            ;;
        4)
            install_dependencies
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please enter 1, 2, 3, 4, or 5."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read
done 