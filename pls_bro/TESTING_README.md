# 🧪 Testing Guide for Enhanced Text-to-SQL Application

This guide explains how to test all functionalities of the Enhanced Text-to-SQL application.

## 🚀 Quick Start

### Option 1: Interactive Menu (Recommended)
```bash
./run_tests.sh
```
This will show you a menu with options to:
- Run comprehensive tests
- Launch the Streamlit app
- Install dependencies
- Do both tests and app

### Option 2: Quick Basic Test
```bash
python quick_test.py
```
Tests basic functionality of all three approaches with a simple query.

### Option 3: Comprehensive Test Suite
```bash
python test_comprehensive.py
```
Runs extensive tests covering all features and generates a detailed JSON report.

### Option 4: Test Chat App
```bash
python test_chat_app.py
```
Tests the conversational SQL assistant with context management and follow-up questions.

### Option 5: Run Apps Directly
```bash
# Multi-approach App
export TOGETHER_API_KEY="tgp_v1_XELYRCJuDTY69-ICL7OBEONSAYquezhyLAMfyi5-Cgc"
streamlit run app_enhanced.py

# Chat App
streamlit run app_chat.py
```

## 🔧 System Compatibility & Fixes

### Recent Fixes Applied
The system has been updated for modern Streamlit compatibility:

- **✅ Deprecated Functions Fixed**: Replaced `st.experimental_rerun()` with `st.rerun()`
- **✅ Model Selection Enhanced**: Added proper session state management for model selection
- **✅ API Key Integration**: Embedded API key for seamless testing
- **✅ Import Validation**: All modules properly import without errors
- **✅ Streamlit 1.45.1 Compatible**: Tested with latest Streamlit version

### Compatibility Test (`test_fixes.py`)
Run this test to validate all fixes are working:
```bash
python test_fixes.py
```

Expected output:
- ✅ All imports successful
- ✅ API key configured  
- ✅ No deprecated functions
- ✅ Model selection working
- 🎉 All fixes validated

You can also run this test via the interactive menu:
```bash
./run_tests.sh
# Choose option 2: Run Compatibility Tests
```

## 📋 What Gets Tested

### 🔍 Test Coverage

#### **1. Database Connection Test**
- ✅ Database file accessibility
- ✅ Table structure validation
- ✅ Basic connectivity

#### **2. SQL Chain Approach** 
- ✅ Basic queries (counts, simple selects)
- ✅ Aggregation queries (SUM, AVG, GROUP BY)
- ✅ Complex joins and analytics
- ✅ SQL query generation accuracy
- ✅ Execution time measurement

#### **3. Simple Agent Approach**
- ✅ Reasoning workflow (Think → Act → Observe)
- ✅ Error recovery and retry logic
- ✅ Tool usage and SQL execution
- ✅ Natural language answer generation

#### **4. Enhanced Agent Approach**
- ✅ Advanced workflow with 10+ processing steps
- ✅ Automatic chart generation (bar, pie, line, scatter)
- ✅ Data insights and pattern detection
- ✅ Dashboard creation and layout
- ✅ Export functionality (PNG, PDF, HTML, JSON)
- ✅ Visualization recommendations

#### **5. Visualization Features**
- ✅ Chart type detection algorithms
- ✅ Data analysis (column types, cardinality)
- ✅ Business intelligence insights
- ✅ Interactive dashboard generation

#### **6. Chat Application Features**
- ✅ Conversational context management
- ✅ Follow-up question detection
- ✅ Multi-turn conversation handling
- ✅ Context-aware SQL generation
- ✅ Chat interface and styling

## 📊 Test Query Types

The tests use these query categories to validate different capabilities:

| Query Type | Example | Tests |
|------------|---------|-------|
| **Basic Count** | "How many artists are in the database?" | Simple SQL generation |
| **Aggregation** | "Top 5 selling artists by total sales" | GROUP BY, ORDER BY, LIMIT |
| **Grouping** | "Revenue by country" | Data grouping for charts |
| **Time Series** | "Sales trends by year" | Date handling, line charts |
| **Comparison** | "Sales by media type" | Categorical comparisons |
| **Distribution** | "Track length distribution" | Histogram generation |
| **Complex Join** | "Customer spending + genre preferences" | Multi-table joins |
| **Analytical** | "Popular genres + avg duration" | Advanced analytics |

## 🎯 Expected Results

### ✅ **Successful Test Run Should Show:**

#### **SQL Chain:**
- ✅ Fast execution (2-5 seconds)
- ✅ Accurate SQL generation
- ✅ Natural language answers
- ✅ Intermediate results (SQL query, execution details)

#### **Simple Agent:**
- ✅ Reasoning steps visible
- ✅ Error recovery if SQL fails
- ✅ Tool-based approach working
- ✅ Medium execution time (5-10 seconds)

#### **Enhanced Agent:**
- ✅ Comprehensive analysis (10-15 seconds)
- ✅ Multiple charts generated (2-4 typically)
- ✅ Business insights provided (3-5 insights)
- ✅ Dashboard layout created
- ✅ Export options available
- ✅ Raw data preserved

### 📈 **Visualization Results:**
- **Bar Charts**: For categorical comparisons (sales by artist)
- **Pie Charts**: For proportional breakdowns (revenue distribution)
- **Line Charts**: For time series data (trends over time)
- **Scatter Plots**: For correlation analysis
- **Histograms**: For distribution analysis

## 🔧 Troubleshooting

### Common Issues:

#### **❌ Import Errors**
```bash
pip install -r requirements.txt
```

#### **❌ API Key Issues**
The API key is pre-configured in the test scripts. If you get authentication errors:
1. Check your internet connection
2. Verify the API key is still valid
3. Try running tests one at a time

#### **❌ Database Not Found**
Make sure you're running tests from the directory containing `chinook.db`.

#### **❌ Streamlit Issues**
```bash
pip install streamlit
# or
pip3 install streamlit
```

#### **❌ Model Loading Failures**
This usually indicates:
- Network connectivity issues
- API rate limiting (wait a minute and retry)
- Invalid API key

## 📁 Generated Files

After running tests, you'll find:

- **`test_report_YYYYMMDD_HHMMSS.json`** - Detailed test results
- **Charts and exports** (if Enhanced Agent tests pass)
- **Streamlit cache files** (in `.streamlit/` directory)

## 🎨 UI Testing Guide

### **Multi-Approach App Testing:**

1. **Start the app**: `streamlit run app_enhanced.py`
2. **Test each approach** with sample queries:
   - Try "What are the top 5 selling artists?"
   - Test "Show me revenue by country"
   - Try "What is the distribution of track lengths?"

3. **Verify features**:
   - ✅ Intermediate results always shown
   - ✅ Enhanced Agent generates charts
   - ✅ Export buttons work
   - ✅ Insights are displayed
   - ✅ Dashboard combines multiple charts

4. **Test sample queries** from the sidebar

5. **Check responsiveness** on different screen sizes

### **Chat App Testing:**

1. **Start the chat app**: `streamlit run app_chat.py`
2. **Test conversational flow**:
   - Start: "What are the top 5 selling artists?"
   - Follow-up: "Tell me more about the top artist"
   - Continue: "What about their albums?"

3. **Verify chat features**:
   - ✅ Message bubbles display correctly
   - ✅ Charts appear inline with messages
   - ✅ Context detection works
   - ✅ Follow-up questions are understood
   - ✅ Conversation history is maintained

4. **Test different conversation patterns**:
   - Comparisons: "Compare this with last month"
   - Refinements: "Filter that by country = USA"
   - References: "Show more details about those results"

5. **Check conversation sidebar**:
   - ✅ Recent topics displayed
   - ✅ Conversation statistics
   - ✅ Clear conversation button works

## 🚀 Performance Expectations

| Approach | Typical Time | What It Does |
|----------|-------------|--------------|
| **SQL Chain** | 2-5 seconds | SQL generation + execution |
| **Simple Agent** | 5-10 seconds | Reasoning + tools + SQL |
| **Enhanced Agent** | 10-15 seconds | Full AI pipeline + visualizations |
| **Chat App** | 10-15 seconds | Conversational Enhanced Agent + context |

## 🎯 Success Criteria

A successful test run should achieve:
- **✅ 80%+ overall pass rate**
- **✅ All three approaches functional**
- **✅ Enhanced Agent generates charts**
- **✅ Chat app handles conversations correctly**
- **✅ Follow-up detection works (80%+ accuracy)**
- **✅ No critical errors in core functionality**
- **✅ Both Streamlit apps load and respond**

---

## 📞 Need Help?

If tests are failing consistently:
1. Check the detailed error messages
2. Verify all dependencies are installed
3. Ensure you have a stable internet connection
4. Try the quick test first before comprehensive tests
5. Check the generated JSON report for specific failure details

## 📚 Educational Resources

### Session State Demo (`streamlit_session_state_demo.py`)
An educational demo showing correct vs incorrect session state patterns:
```bash
streamlit run streamlit_session_state_demo.py
```

This demo illustrates the fixes applied to resolve session state conflicts and teaches best practices for Streamlit development.

**Happy Testing! 🎉** 