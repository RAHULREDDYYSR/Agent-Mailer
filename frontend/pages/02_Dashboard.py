import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import api
from auth_utils import restore_session
import pandas as pd

restore_session()

# Page Header
st.markdown("""
<div style="margin-bottom: 24px;">
    <h1>📊 Dashboard</h1>
    <p style="opacity: 0.6; margin-top: -8px;">Manage your job contexts and view analytics</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("access_token"):
    st.warning("⚠️ Please login to access the dashboard.")
    st.stop()

# Fetch jobs and contents for both tabs
jobs = api.get_jobs()
contents = api.get_all_generated_contents()

# Navigation Tabs
tab_jobs, tab_analytics = st.tabs(["📋 Jobs", "📈 Analytics"])

# ──────────────────────────────────────────────────────────────────────────────
# JOBS TAB
# ──────────────────────────────────────────────────────────────────────────────
with tab_jobs:
    if jobs:
        st.markdown(f"**{len(jobs)} job contexts saved**")
        st.markdown("---")
        
        for job in jobs:
            with st.container():
                st.markdown(f"""
                <div class="premium-card" style="margin-bottom: -65px; padding-bottom: 85px; position: relative; z-index: 0;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="margin: 0 0 4px 0;">{job.get('title', 'Untitled')}</h3>
                            <p style="margin: 0; opacity: 0.6;">{job.get('company', 'Unknown Company')}</p>
                        </div>
                        <span style="background: rgba(99, 102, 241, 0.1); color: #6366f1; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 500;">
                            ID: {job.get('id')}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([0.03, 0.94, 0.03])
                with c2:
                    if st.button("👁️ View Details & Actions", key=f"view_{job['id']}", use_container_width=True):
                        st.session_state.selected_job_id = job['id']
                        st.switch_page("pages/05_Job_Details.py")
                
                st.markdown("<br><br>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="premium-card" style="text-align: center; padding: 48px;">
            <div style="font-size: 3rem; margin-bottom: 16px;">📭</div>
            <h3>No Jobs Yet</h3>
            <p style="opacity: 0.6;">Go to Generator to analyze your first job description.</p>
        </div>
        """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# ANALYTICS TAB
# ──────────────────────────────────────────────────────────────────────────────
with tab_analytics:
    all_companies = list(set([j.get('company', 'Unknown') for j in jobs])) if jobs else []
    
    if contents or jobs:
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="premium-card stat-card">
                <div class="stat-value">{len(contents) if contents else 0}</div>
                <div class="stat-label">Documents Generated</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="premium-card stat-card">
                <div class="stat-value">{len(jobs) if jobs else 0}</div>
                <div class="stat-label">Jobs Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="premium-card stat-card">
                <div class="stat-value">{len(all_companies)}</div>
                <div class="stat-label">Companies</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if contents:
            df = pd.DataFrame(contents)
            
            # Chart
            if 'content_type' in df.columns:
                st.markdown("### Content Distribution")
                type_counts = df['content_type'].value_counts()
                st.bar_chart(type_counts)
            
            # Filters
            st.markdown("### Recent Generations")
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                type_options = df['content_type'].unique().tolist() if 'content_type' in df.columns else []
                type_filter = st.multiselect("Filter by Type", options=type_options)
            with col_f2:
                company_filter = st.multiselect("Filter by Company", options=all_companies)
            
            filtered_df = df.copy()
            if type_filter:
                filtered_df = filtered_df[filtered_df['content_type'].isin(type_filter)]
            if company_filter and 'company_name' in df.columns:
                filtered_df = filtered_df[filtered_df['company_name'].isin(company_filter)]
            
            # Display Table
            display_cols = []
            for col in ['company_name', 'job_title', 'content_type', 'to_address', 'subject']:
                if col in filtered_df.columns:
                    display_cols.append(col)
            
            if display_cols:
                st.dataframe(
                    filtered_df[display_cols],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("No generated content yet. Use the Generator to create your first draft!")
    else:
        st.markdown("""
        <div class="premium-card" style="text-align: center; padding: 48px;">
            <div style="font-size: 3rem; margin-bottom: 16px;">📊</div>
            <h3>No Data Available</h3>
            <p style="opacity: 0.6;">Analytics will appear once you start generating content.</p>
        </div>
        """, unsafe_allow_html=True)
