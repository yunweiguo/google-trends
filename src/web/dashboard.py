"""
Streamlit web dashboard entry point
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from ..config import config


def main():
    """Main dashboard application"""
    st.set_page_config(
        page_title="Google Trends Website Builder",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 Google Trends Website Builder")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Keyword Explorer", "Analysis Results", "Settings"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Keyword Explorer":
        show_keyword_explorer()
    elif page == "Analysis Results":
        show_analysis_results()
    elif page == "Settings":
        show_settings()


def show_dashboard():
    """Show main dashboard"""
    st.header("Trends Dashboard")
    st.info("Dashboard functionality will be implemented in later tasks")
    
    # Placeholder content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Keywords", "0", "0")
    
    with col2:
        st.metric("Active Analyses", "0", "0")
    
    with col3:
        st.metric("Generated Reports", "0", "0")


def show_keyword_explorer():
    """Show keyword explorer"""
    st.header("Keyword Explorer")
    st.info("Keyword exploration functionality will be implemented in later tasks")


def show_analysis_results():
    """Show analysis results"""
    st.header("Analysis Results")
    st.info("Analysis results functionality will be implemented in later tasks")


def show_settings():
    """Show settings page"""
    st.header("Settings")
    
    st.subheader("Configuration")
    st.text(f"Database: {config.database.host}:{config.database.port}")
    st.text(f"Redis: {config.redis.host}:{config.redis.port}")
    st.text(f"API: {config.api.host}:{config.api.port}")


if __name__ == "__main__":
    main()