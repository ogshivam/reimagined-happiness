#!/usr/bin/env python3
"""
Educational demo showing correct vs incorrect session state patterns in Streamlit.
This demonstrates the fixes applied to resolve session state conflicts.
"""

import streamlit as st

st.set_page_config(page_title="Session State Best Practices", page_icon="📚")

st.title("📚 Streamlit Session State Best Practices")

st.markdown("""
This demo shows the **correct way** to handle session state with Streamlit widgets,
based on the fixes applied to the Enhanced Text-to-SQL application.
""")

# Correct Pattern Example
st.header("✅ Correct Pattern")

st.markdown("""
When using a widget with a `key` parameter, Streamlit automatically manages the session state.
**Never manually set the session state for widget-managed keys.**
""")

with st.expander("View Correct Code Example", expanded=True):
    st.code("""
# ✅ CORRECT: Let Streamlit manage the session state
option = st.selectbox(
    "Choose an option:",
    ["Option 1", "Option 2", "Option 3"],
    key="my_selection"  # This automatically sets st.session_state.my_selection
)

# Access the value through the variable or session state
st.write(f"Selected: {option}")
st.write(f"From session state: {st.session_state.my_selection}")
""")

# Live Demo
st.subheader("Live Demo:")
option = st.selectbox(
    "Choose an option:",
    ["Option 1", "Option 2", "Option 3"],
    key="demo_selection"
)

st.write(f"Selected: {option}")
st.write(f"From session state: {st.session_state.get('demo_selection', 'Not set')}")

# Incorrect Pattern Example
st.header("❌ Incorrect Pattern (Causes Errors)")

st.markdown("""
This pattern will cause a `StreamlitAPIException` because you're trying to modify
a session state key that's already managed by a widget.
""")

with st.expander("View Incorrect Code Example (DON'T DO THIS)"):
    st.code("""
# ❌ INCORRECT: This will cause an error!
option = st.selectbox(
    "Choose an option:",
    ["Option 1", "Option 2", "Option 3"],
    key="my_selection"
)

# This line will cause: StreamlitAPIException
st.session_state.my_selection = option  # DON'T DO THIS!
""")

    st.error("⚠️ The above code will throw: `StreamlitAPIException: st.session_state.my_selection cannot be modified after the widget with key my_selection is instantiated.`")

# Show current session state
st.header("🔍 Current Session State")
if st.button("Show Session State"):
    st.json(dict(st.session_state))

# Key Takeaways
st.header("🎯 Key Takeaways")

st.markdown("""
1. **Widget keys auto-manage session state** - Don't manually set them
2. **Access values through the widget variable or session state** - Both work
3. **Use unique keys** - Avoid conflicts between widgets  
4. **Check for key existence** - Use `st.session_state.get(key, default)`
5. **Initialize session state carefully** - Do it before widgets are created

**These patterns were successfully applied to fix the Enhanced Text-to-SQL application!**
""")

st.success("✅ Following these patterns will prevent session state conflicts in your Streamlit apps!") 