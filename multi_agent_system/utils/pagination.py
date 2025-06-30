"""
Pagination utilities for handling large datasets in Streamlit
"""
import pandas as pd
import streamlit as st
from typing import Tuple, Dict, Any
import math

class DataPaginator:
    """Handles pagination for large datasets"""
    
    def __init__(self, page_size: int = 100):
        self.page_size = page_size
    
    def paginate_dataframe(self, df: pd.DataFrame, page_key: str = "page") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Paginate a DataFrame and return the current page with pagination info
        
        Args:
            df: DataFrame to paginate
            page_key: Unique key for this pagination (to handle multiple tables)
            
        Returns:
            Tuple of (paginated_df, pagination_info)
        """
        if df.empty:
            return df, {"total_rows": 0, "total_pages": 0, "current_page": 1, "page_size": self.page_size}
        
        total_rows = len(df)
        total_pages = max(1, math.ceil(total_rows / self.page_size))
        
        # Get current page from session state
        session_key = f"pagination_{page_key}"
        if session_key not in st.session_state:
            st.session_state[session_key] = 1
        
        current_page = st.session_state[session_key]
        current_page = max(1, min(current_page, total_pages))  # Clamp to valid range
        
        # Calculate start and end indices
        start_idx = (current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total_rows)
        
        # Get the page data
        page_df = df.iloc[start_idx:end_idx].copy()
        
        pagination_info = {
            "total_rows": total_rows,
            "total_pages": total_pages,
            "current_page": current_page,
            "page_size": self.page_size,
            "start_row": start_idx + 1,
            "end_row": end_idx,
            "showing_rows": len(page_df)
        }
        
        return page_df, pagination_info
    
    def render_pagination_controls(self, pagination_info: Dict[str, Any], page_key: str = "page"):
        """
        Render pagination controls in Streamlit
        
        Args:
            pagination_info: Information from paginate_dataframe
            page_key: Unique key for this pagination
        """
        if pagination_info["total_pages"] <= 1:
            return  # No pagination needed
        
        session_key = f"pagination_{page_key}"
        current_page = pagination_info["current_page"]
        total_pages = pagination_info["total_pages"]
        
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("⏮️ First", disabled=(current_page == 1), key=f"first_{page_key}"):
                st.session_state[session_key] = 1
                st.rerun()
        
        with col2:
            if st.button("⬅️ Prev", disabled=(current_page == 1), key=f"prev_{page_key}"):
                st.session_state[session_key] = max(1, current_page - 1)
                st.rerun()
        
        with col3:
            # Page selector
            new_page = st.selectbox(
                "Page", 
                range(1, total_pages + 1), 
                index=current_page - 1,
                key=f"page_select_{page_key}"
            )
            if new_page != current_page:
                st.session_state[session_key] = new_page
                st.rerun()
        
        with col4:
            if st.button("➡️ Next", disabled=(current_page == total_pages), key=f"next_{page_key}"):
                st.session_state[session_key] = min(total_pages, current_page + 1)
                st.rerun()
        
        with col5:
            if st.button("⏭️ Last", disabled=(current_page == total_pages), key=f"last_{page_key}"):
                st.session_state[session_key] = total_pages
                st.rerun()
    
    def render_pagination_info(self, pagination_info: Dict[str, Any]):
        """Render pagination information"""
        st.caption(
            f"Showing rows {pagination_info['start_row']}-{pagination_info['end_row']} "
            f"of {pagination_info['total_rows']} total rows "
            f"(Page {pagination_info['current_page']} of {pagination_info['total_pages']})"
        )
    
    def render_page_size_selector(self, page_key: str = "page"):
        """Render page size selector"""
        session_key = f"pagination_{page_key}_size"
        
        if session_key not in st.session_state:
            st.session_state[session_key] = self.page_size
        
        new_size = st.selectbox(
            "Rows per page:",
            [25, 50, 100, 200, 500],
            index=[25, 50, 100, 200, 500].index(st.session_state[session_key]) if st.session_state[session_key] in [25, 50, 100, 200, 500] else 2,
            key=f"page_size_{page_key}"
        )
        
        if new_size != self.page_size:
            self.page_size = new_size
            st.session_state[session_key] = new_size
            # Reset to first page when changing page size
            reset_key = f"pagination_{page_key}"
            if reset_key in st.session_state:
                st.session_state[reset_key] = 1
            st.rerun()

def render_large_dataframe(df: pd.DataFrame, title: str = "Data Results", 
                          page_key: str = "main", show_controls: bool = True):
    """
    Render a large DataFrame with pagination controls
    
    Args:
        df: DataFrame to display
        title: Title for the data display
        page_key: Unique key for pagination
        show_controls: Whether to show pagination controls
    """
    if df.empty:
        st.info("No data to display")
        return
    
    # Initialize paginator
    paginator = DataPaginator()
    
    # Add page size selector if showing controls
    if show_controls and len(df) > 25:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(title)
        with col2:
            paginator.render_page_size_selector(page_key)
    else:
        st.subheader(title)
    
    # Paginate the data
    page_df, pagination_info = paginator.paginate_dataframe(df, page_key)
    
    # Show pagination info
    if show_controls and pagination_info["total_pages"] > 1:
        paginator.render_pagination_info(pagination_info)
    
    # Display the data
    st.dataframe(page_df, use_container_width=True)
    
    # Show pagination controls
    if show_controls and pagination_info["total_pages"] > 1:
        paginator.render_pagination_controls(pagination_info, page_key)
        
        # Show export options for large datasets
        if pagination_info["total_rows"] > 1000:
            st.warning(f"⚠️ Large dataset ({pagination_info['total_rows']} rows). Consider using filters or exporting for full analysis.")
        
        # Export buttons
        if pagination_info["total_rows"] > 25:
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Export Current Page", key=f"export_page_{page_key}"):
                    st.session_state[f"export_mode_{page_key}"] = "current_page"
                    st.session_state[f"export_data_{page_key}"] = page_df
            
            with col2:
                if st.button("📊 Export All Data", key=f"export_all_{page_key}"):
                    st.session_state[f"export_mode_{page_key}"] = "all_data"
                    st.session_state[f"export_data_{page_key}"] = df
            
            with col3:
                if pagination_info["total_rows"] > 10000:
                    if st.button("📋 Export Sample", key=f"export_sample_{page_key}"):
                        st.session_state[f"export_mode_{page_key}"] = "sample"
                        st.session_state[f"export_data_{page_key}"] = df.head(1000)
            
            # Show export dialog if mode is set
            export_mode = st.session_state.get(f"export_mode_{page_key}")
            if export_mode:
                with st.expander("📥 Export Options", expanded=True):
                    export_format = st.selectbox(
                        "Format:",
                        ["csv", "json", "html"],
                        key=f"export_format_{page_key}"
                    )
                    
                    export_data = st.session_state.get(f"export_data_{page_key}")
                    if export_data is not None:
                        # Generate export
                        from agents.export_agent import ExportAgent
                        exporter = ExportAgent()
                        
                        if export_mode == "current_page":
                            result = exporter.export_data(
                                df, export_format, 
                                current_page_only=True, 
                                page_data=export_data
                            )
                            export_desc = f"Current page ({len(export_data)} rows)"
                        elif export_mode == "sample":
                            result = exporter.export_data(
                                df, export_format, 
                                max_rows=1000
                            )
                            export_desc = f"Sample data (first 1000 of {len(df)} rows)"
                        else:
                            result = exporter.export_data(df, export_format)
                            export_desc = f"All data ({len(df)} rows)"
                        
                        if result["success"]:
                            st.success(f"✅ Ready to download: {export_desc}")
                            st.download_button(
                                label=f"💾 Download {export_format.upper()}",
                                data=result["content"],
                                file_name=result["filename"],
                                mime=result["content_type"],
                                key=f"download_{page_key}"
                            )
                        else:
                            st.error(f"❌ Export failed: {result['error']}")
                    
                    if st.button("❌ Cancel", key=f"cancel_export_{page_key}"):
                        st.session_state[f"export_mode_{page_key}"] = None
                        st.session_state[f"export_data_{page_key}"] = None
                        st.rerun()

# Global paginator instance
default_paginator = DataPaginator() 