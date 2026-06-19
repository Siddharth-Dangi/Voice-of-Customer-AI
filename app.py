import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Import database and LLM helper modules
import database as db
import llm
import utils
import report_generator

# Load environment variables
load_dotenv()

# App Page Configurations
st.set_page_config(
    page_title="Voice of Customer AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design Aesthetics
st.markdown("""
<style>
    /* Global Styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
        border-left: 6px solid #6366f1;
        margin-bottom: 15px;
    }
    .metric-card-positive {
        border-left-color: #0d9488 !important;
    }
    .metric-card-negative {
        border-left-color: #f43f5e !important;
    }
    .metric-title {
        font-size: 13px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #f8fafc;
    }
    .metric-desc {
        font-size: 11px;
        color: #64748b;
        margin-top: 5px;
    }
    
    /* Persona Card */
    .persona-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -4px rgba(0, 0, 0, 0.2);
        border-left: 6px solid #0d9488;
    }
    .persona-title {
        font-size: 20px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
    }
    .persona-desc {
        font-size: 13px;
        color: #cbd5e1;
        font-style: italic;
        margin-bottom: 15px;
    }
    .persona-bullet {
        font-size: 13px;
        color: #e2e8f0;
        margin-bottom: 5px;
    }
    
    /* Custom Sections */
    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #f8fafc;
        border-bottom: 2px solid #334155;
        padding-bottom: 8px;
        margin-bottom: 20px;
    }

    /* Segmented Control Styling */
    div[data-testid="stSegmentedControl"] {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        padding-top: 10px;
    }
    
    div[data-testid="stSegmentedControl"] button {
        background: #192231 !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 6px 16px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
    }
    
    div[data-testid="stSegmentedControl"] button:hover {
        background: #243042 !important;
        color: #f8fafc !important;
        border-color: #475569 !important;
    }
    
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%) !important;
        color: white !important;
        border-color: #6366f1 !important;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3), 0 2px 4px -2px rgba(99, 102, 241, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- TOP NAVIGATION & HEADER -----------------
# Create horizontal layout for title and navigation
col_title, col_nav = st.columns([1, 2], vertical_alignment="center")

with col_title:
    st.markdown("""
        <div style="padding-top: 10px;">
            <h1 style="color: #6366f1; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2;">Voice of Customer AI</h1>
            <p style="font-size: 11px; color: #64748b; margin: 2px 0 0 0; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">AI-Powered Feedback Intelligence</p>
        </div>
    """, unsafe_allow_html=True)

with col_nav:
    # Top navigation options
    nav_options = [
        "Upload Dataset", 
        "Analytics Dashboard", 
        "Customer Personas", 
        "Feedback Explorer", 
        "Executive Report"
    ]
    
    # Track selection in session state
    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = nav_options[0]
        st.session_state["prev_nav_page"] = nav_options[0]

    # Callback to prevent deselection of active tab
    def on_nav_change():
        if st.session_state["nav_page"] is None:
            st.session_state["nav_page"] = st.session_state["prev_nav_page"]
        else:
            st.session_state["prev_nav_page"] = st.session_state["nav_page"]

    nav_page_val = st.segmented_control(
        label="Navigation Menu",
        options=nav_options,
        key="nav_page",
        selection_mode="single",
        label_visibility="collapsed",
        on_change=on_nav_change
    )
    nav_page = st.session_state["nav_page"]

# Add a divider under the navigation
st.markdown("<hr style='margin: 15px 0 25px 0; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# ----------------- SIDEBAR CONFIGURATION -----------------
st.sidebar.markdown("<h3 style='margin-top: 0px;'>Settings</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Groq API Configuration
st.sidebar.subheader("Groq API Settings")
env_key = os.getenv("GROQ_API_KEY", "")
api_key_input = st.sidebar.text_input(
    "Groq API Key", 
    value=env_key if env_key else st.session_state.get("api_key", ""), 
    type="password",
    help="Provide your Groq API Key. If set in .env, it is pre-loaded."
)

# Set API key in session state
if api_key_input:
    st.session_state["api_key"] = api_key_input

# Key Status indicator
if st.session_state.get("api_key"):
    st.sidebar.success("Groq Connected")
else:
    st.sidebar.warning("Groq API Key Required")

# Model selection
model_selection = st.sidebar.selectbox(
    "AI Model",
    options=["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
    index=0
)

# ----------------- PAGE 1: UPLOAD DATASET -----------------
if nav_page == "Upload Dataset":
    st.markdown("<div class='section-title'>Upload Customer Feedback Dataset</div>", unsafe_allow_html=True)
    
    st.write(
        "Upload your customer feedback dataset to trigger the AI analysis pipeline. "
        "The system accepts CSV, Excel (XLSX), and Plain Text (TXT) files."
    )
    
    # Upload widget
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls", "txt"])
    
    if uploaded_file is not None:
        # Reset analysis state if a new file is uploaded
        if st.session_state.get("last_uploaded_filename") != uploaded_file.name:
            st.session_state["last_uploaded_filename"] = uploaded_file.name
            st.session_state["analysis_completed"] = False
            
        filename = uploaded_file.name
        
        try:
            # Parse file
            df = utils.parse_uploaded_file(uploaded_file, filename)
            
            st.success(f"Successfully loaded '{filename}' ({len(df)} rows)")
            
            # Preview Data
            st.subheader("Dataset Preview")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Column Mapping
            st.subheader("Match Dataset Columns")
            cols = list(df.columns)
            
            # Guessing columns based on common names
            def guess_col(choices, keywords, default_idx=0):
                for idx, col in enumerate(choices):
                    if any(kw in col.lower() for kw in keywords):
                        return idx
                return default_idx
                
            feedback_col_idx = guess_col(cols, ["feedback", "text", "comment", "review", "msg"])
            cust_col_idx = guess_col(cols, ["customer", "cust", "user", "id", "email"])
            date_col_idx = guess_col(cols, ["date", "time", "created", "timestamp"])
            
            feedback_col = st.selectbox("Feedback Text Column (Required)", options=cols, index=feedback_col_idx)
            cust_col = st.selectbox("Customer ID Column (Optional)", options=["None"] + cols, index=cust_col_idx + 1)
            date_col = st.selectbox("Date / Timestamp Column (Optional)", options=["None"] + cols, index=date_col_idx + 1)
            
            st.markdown("---")
            
            # Persistent success message and CTA redirect button
            if st.session_state.get("analysis_completed"):
                st.markdown("""
                    <div style="background: rgba(13, 148, 136, 0.1); border: 1px solid #0d9488; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
                        <h4 style="color: #0d9488; margin-top: 0px; margin-bottom: 8px; font-weight: 700; font-size: 16px;">Analysis Completed Successfully!</h4>
                        <p style="color: #cbd5e1; font-size: 13px; margin-bottom: 0px;">
                            The customer feedback dataset has been fully processed and stats compiled. Click the button below to view the results.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("View Insights Dashboard", type="primary", use_container_width=True):
                    st.session_state["analysis_completed"] = False
                    st.session_state["nav_page"] = "Analytics Dashboard"
                    st.session_state["prev_nav_page"] = "Analytics Dashboard"
                    st.rerun()
                st.markdown("---")
            
            # Trigger analysis
            if st.button("Run AI Analysis Pipeline", type="primary"):
                # Validate inputs
                if not st.session_state.get("api_key"):
                    st.error("Please provide a Groq API Key in the sidebar to run the analysis.")
                else:
                    progress_bar = st.progress(0.0)
                    status_text = st.empty()
                    
                    status_text.text("Ingesting feedback entries and creating project report...")
                    
                    # 1. Create Upload Report in DB
                    report_id = db.create_uploaded_report(filename)
                    
                    # 2. Insert customer feedback items to SQLite
                    feedback_batch_data = []
                    for idx, row in df.iterrows():
                        text = str(row[feedback_col])
                        cleaned_text = utils.clean_text(text)
                        
                        cust_id = str(row[cust_col]) if cust_col != "None" else f"ANON-{idx+1}"
                        created_date = str(row[date_col]) if date_col != "None" else None
                        
                        fb_id = db.insert_customer_feedback(report_id, cleaned_text, cust_id, created_date)
                        feedback_batch_data.append({"id": fb_id, "text": cleaned_text})
                    
                    # 3. Analyze feedback concurrently
                    status_text.text(f"Running LLM analysis on {len(feedback_batch_data)} feedback items in concurrent batches...")
                    
                    def progress_cb(completed, total):
                        pct = completed / total
                        progress_bar.progress(pct)
                        status_text.text(f"Analyzing feedback: {completed}/{total} items processed ({pct * 100:.0f}%)")
                        
                    analyses = llm.analyze_feedback_dataset(
                        api_key=st.session_state["api_key"],
                        model=model_selection,
                        feedback_list=feedback_batch_data,
                        progress_callback=progress_cb
                    )
                    
                    # 4. Save analysis results to database
                    status_text.text("Saving analysis classifications to the database...")
                    for idx, analysis in enumerate(analyses):
                        db.insert_analysis_result(analysis.id, analysis)
                        
                    # 5. Calculate stats and run overall summary
                    status_text.text("Compiling statistical dashboard & generating executive summary...")
                    df_results = db.get_feedback_and_analysis(report_id)
                    stats = utils.calculate_aggregate_statistics(df_results)
                    
                    summary_result = llm.generate_executive_summary(
                        api_key=st.session_state["api_key"],
                        model=model_selection,
                        stats=stats
                    )
                    
                    # 6. Update database record with summary
                    db.update_report_status(report_id, "completed", summary_result.model_dump())
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    # Save currently selected report ID and mark completed in session state
                    st.session_state["current_report_id"] = report_id
                    st.session_state["analysis_completed"] = True
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Error parsing file: {e}")

# ----------------- PAGE 2: ANALYTICS DASHBOARD -----------------
elif nav_page == "Analytics Dashboard":
    st.markdown("<div class='section-title'>Customer Insights Dashboard</div>", unsafe_allow_html=True)
    
    # Report selector
    reports_df = db.get_uploaded_reports()
    
    if reports_df.empty:
        st.warning("No feedback reports found in the database. Please go to the 'Upload Dataset' tab and upload your customer reviews.")
    else:
        # Pre-select report if set in session state
        selected_idx = 0
        if "current_report_id" in st.session_state:
            matching_rows = reports_df[reports_df["id"] == st.session_state["current_report_id"]]
            if not matching_rows.empty:
                selected_idx = int(matching_rows.index[0])
                
        selected_report_label = st.selectbox(
            "Select Feedback Analysis Run:",
            options=reports_df.index,
            format_func=lambda idx: f"{reports_df.loc[idx, 'filename']} (ID: {reports_df.loc[idx, 'id']} | {reports_df.loc[idx, 'uploaded_at'][:16]})",
            index=selected_idx
        )
        
        report_id = int(reports_df.loc[selected_report_label, "id"])
        st.session_state["current_report_id"] = report_id
        
        # Load details
        report_details = db.get_report_details(report_id)
        df_results = db.get_feedback_and_analysis(report_id)
        stats = utils.calculate_aggregate_statistics(df_results)
        
        if report_details["status"] == "processing":
            st.info("This report is still being processed. Please refresh in a moment.")
        elif df_results.empty:
            st.error("No feedback data found for this report.")
        else:
            # Main Stats Panel
            # Calculate Avg Sentiment Score
            avg_sentiment = df_results["sentiment_score"].mean()
            net_sentiment_pct = (df_results["sentiment"].value_counts(normalize=True).get("Positive", 0) - 
                                 df_results["sentiment"].value_counts(normalize=True).get("Negative", 0)) * 100
            
            top_category = df_results["category"].mode()[0] if not df_results["category"].empty else "N/A"
            top_pain_point = stats["top_pain_points"][0][0] if stats["top_pain_points"] else "None"
            
            # Metrics Cards Row
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Feedback Analyzed</div>
                    <div class="metric-value">{stats['total_feedback']:,}</div>
                    <div class="metric-desc">Total uploaded items</div>
                </div>
                """, unsafe_allow_html=True)
            with m_col2:
                sentiment_class = "metric-card-positive" if avg_sentiment > 0.1 else "metric-card-negative" if avg_sentiment < -0.1 else ""
                st.markdown(f"""
                <div class="metric-card {sentiment_class}">
                    <div class="metric-title">Net Sentiment Index</div>
                    <div class="metric-value">{net_sentiment_pct:+.1f}%</div>
                    <div class="metric-desc">Avg Sentiment Score: {avg_sentiment:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with m_col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Primary Driver</div>
                    <div class="metric-value" style="font-size: 22px; padding-top: 5px;">{top_category}</div>
                    <div class="metric-desc">Highest volume category</div>
                </div>
                """, unsafe_allow_html=True)
            with m_col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Top Complaint</div>
                    <div class="metric-value" style="font-size: 16px; padding-top: 8px;" title="{top_pain_point}">{top_pain_point[:35]}...</div>
                    <div class="metric-desc">Most recurring issue</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("---")
            
            # Charts Row 1: Sentiment and Categories
            c1_col1, c1_col2 = st.columns(2)
            
            with c1_col1:
                st.subheader("Sentiment Distribution")
                sent_data = pd.DataFrame([
                    {"Sentiment": k, "Count": v} for k, v in stats["sentiment_distribution"].items()
                ])
                # Custom premium colors: Teal (Pos), Gray (Neu), Rose (Neg)
                color_map = {"Positive": "#0d9488", "Neutral": "#94a3b8", "Negative": "#f43f5e"}
                
                fig_sent = px.pie(
                    sent_data, 
                    values="Count", 
                    names="Sentiment", 
                    hole=0.5,
                    color="Sentiment",
                    color_discrete_map=color_map,
                )
                fig_sent.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
                st.plotly_chart(fig_sent, use_container_width=True)
                
            with c1_col2:
                st.subheader("Feedback Category Breakdown")
                cat_data = pd.DataFrame([
                    {"Category": k, "Count": v} for k, v in stats["category_distribution"].items()
                ]).sort_values("Count", ascending=True)
                
                fig_cat = px.bar(
                    cat_data,
                    x="Count",
                    y="Category",
                    orientation="h",
                    color_discrete_sequence=["#4f46e5"] # Indigo
                )
                fig_cat.update_layout(
                    xaxis_title="Number of Mentions",
                    yaxis_title=None,
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=300
                )
                st.plotly_chart(fig_cat, use_container_width=True)
                
            st.markdown("---")
            
            # Charts Row 2: Pain Points and Feature Requests
            c2_col1, c2_col2 = st.columns(2)
            
            with c2_col1:
                st.subheader("Top Complaints & Pain Points")
                if not stats["top_pain_points"]:
                    st.info("No specific complaints identified.")
                else:
                    pain_df = pd.DataFrame(stats["top_pain_points"][:8], columns=["Pain Point", "Frequency"]).sort_values("Frequency", ascending=True)
                    fig_pain = px.bar(
                        pain_df,
                        x="Frequency",
                        y="Pain Point",
                        orientation="h",
                        color_discrete_sequence=["#f43f5e"] # Rose
                    )
                    fig_pain.update_layout(
                        xaxis_title="Occurrences",
                        yaxis_title=None,
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=300
                    )
                    st.plotly_chart(fig_pain, use_container_width=True)
                    
            with c2_col2:
                st.subheader("Feature Requests Rank")
                if not stats["top_feature_requests"]:
                    st.info("No specific feature requests identified.")
                else:
                    feat_df = pd.DataFrame(stats["top_feature_requests"][:8], columns=["Feature Request", "Demand Count"]).sort_values("Demand Count", ascending=True)
                    fig_feat = px.bar(
                        feat_df,
                        x="Demand Count",
                        y="Feature Request",
                        orientation="h",
                        color_discrete_sequence=["#0d9488"] # Teal
                    )
                    fig_feat.update_layout(
                        xaxis_title="Demand Level",
                        yaxis_title=None,
                        margin=dict(t=10, b=10, l=10, r=10),
                        height=300
                    )
                    st.plotly_chart(fig_feat, use_container_width=True)
                    
            st.markdown("---")
            
            # Opportunity Discovery Scatter Matrix
            st.subheader("Opportunity Discovery Engine")
            st.write(
                "Compare issues by **Opportunity Score** (unmet demand/blockers) "
                "against their estimated **Business Impact Score** (churn reduction, user retention)."
            )
            
            # Average score per category
            opp_matrix = df_results.groupby("category")[["opportunity_score", "business_impact_score", "sentiment_score"]].mean().reset_index()
            # Map sentiment back to label
            opp_matrix["avg_sentiment"] = opp_matrix["sentiment_score"].apply(lambda x: "Positive" if x > 0.1 else "Negative" if x < -0.1 else "Neutral")
            
            fig_opp = px.scatter(
                opp_matrix,
                x="opportunity_score",
                y="business_impact_score",
                size="opportunity_score",
                color="category",
                hover_name="category",
                text="category",
                labels={
                    "opportunity_score": "Opportunity Score (0-100)",
                    "business_impact_score": "Business Impact Score (0-100)"
                },
                range_x=[0, 100],
                range_y=[0, 100]
            )
            
            fig_opp.update_traces(textposition='top center')
            fig_opp.update_layout(height=450)
            
            # Add quadrant lines
            fig_opp.add_vline(x=50, line_dash="dash", line_color="#cbd5e1", line_width=1)
            fig_opp.add_hline(y=50, line_dash="dash", line_color="#cbd5e1", line_width=1)
            
            st.plotly_chart(fig_opp, use_container_width=True)

# ----------------- PAGE 3: CUSTOMER PERSONAS -----------------
elif nav_page == "Customer Personas":
    st.markdown("<div class='section-title'>Customer Personas Insights</div>", unsafe_allow_html=True)
    
    # Selector
    reports_df = db.get_uploaded_reports()
    if reports_df.empty:
        st.warning("Please upload a dataset first.")
    else:
        # Pre-select report
        selected_idx = 0
        if "current_report_id" in st.session_state:
            matching_rows = reports_df[reports_df["id"] == st.session_state["current_report_id"]]
            if not matching_rows.empty:
                selected_idx = int(matching_rows.index[0])
                
        selected_report_label = st.selectbox(
            "Select Feedback Analysis Run:",
            options=reports_df.index,
            format_func=lambda idx: f"{reports_df.loc[idx, 'filename']} (ID: {reports_df.loc[idx, 'id']})",
            index=selected_idx,
            key="personas_selector"
        )
        
        report_id = int(reports_df.loc[selected_report_label, "id"])
        st.session_state["current_report_id"] = report_id
        
        report_details = db.get_report_details(report_id)
        
        if report_details and report_details["summary_json"]:
            summary_dict = report_details["summary_json"]
            personas = summary_dict.get("personas", [])
            
            st.write("Based on recurring patterns in the text, the AI has generated these target user profiles:")
            
            if not personas:
                st.info("No personas generated for this report.")
            else:
                p_cols = st.columns(len(personas))
                for i, persona in enumerate(personas):
                    with p_cols[i]:
                        pains_list = "".join([f"<li class='persona-bullet'>{p}</li>" for p in persona.get("pain_points", [])])
                        needs_list = "".join([f"<li class='persona-bullet'>{n}</li>" for n in persona.get("needs", [])])
                        
                        st.markdown(f"""
                        <div class="persona-card">
                            <div class="persona-title">{persona.get('name', 'Customer Profile')}</div>
                            <div class="persona-desc">"{persona.get('description', '')}"</div>
                            <h4 style="color: #f43f5e; margin-top: 15px; margin-bottom: 5px; font-size: 14px; font-weight:600;">Key Pain Points</h4>
                            <ul style="padding-left: 15px; margin-bottom: 15px;">
                                {pains_list}
                            </ul>
                            <h4 style="color: #0d9488; margin-top: 15px; margin-bottom: 5px; font-size: 14px; font-weight:600;">Core Needs</h4>
                            <ul style="padding-left: 15px; margin-bottom: 0px;">
                                {needs_list}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.error("No summary details found for this run. Run the analysis first.")
 
# ----------------- PAGE 4: FEEDBACK EXPLORER -----------------
elif nav_page == "Feedback Explorer":
    st.markdown("<div class='section-title'>Customer Feedback Explorer</div>", unsafe_allow_html=True)
    
    # Selector
    reports_df = db.get_uploaded_reports()
    if reports_df.empty:
        st.warning("Please upload a dataset first.")
    else:
        # Pre-select report
        selected_idx = 0
        if "current_report_id" in st.session_state:
            matching_rows = reports_df[reports_df["id"] == st.session_state["current_report_id"]]
            if not matching_rows.empty:
                selected_idx = int(matching_rows.index[0])
                
        selected_report_label = st.selectbox(
            "Select Feedback Analysis Run:",
            options=reports_df.index,
            format_func=lambda idx: f"{reports_df.loc[idx, 'filename']} (ID: {reports_df.loc[idx, 'id']})",
            index=selected_idx,
            key="explorer_selector"
        )
        
        report_id = int(reports_df.loc[selected_report_label, "id"])
        st.session_state["current_report_id"] = report_id
        
        # Load feedback and classifications
        df_results = db.get_feedback_and_analysis(report_id)
        
        if df_results.empty:
            st.info("No feedback entries found.")
        else:
            # Filters
            f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
            with f_col1:
                filter_sentiment = st.multiselect(
                    "Filter Sentiment:",
                    options=["Positive", "Neutral", "Negative"],
                    default=["Positive", "Neutral", "Negative"]
                )
            with f_col2:
                categories = list(df_results["category"].unique())
                filter_category = st.multiselect(
                    "Filter Category:",
                    options=categories,
                    default=categories
                )
            with f_col3:
                search_query = st.text_input("Search Feedback Text:", "")
                
            # Apply filters
            filtered_df = df_results[
                (df_results["sentiment"].isin(filter_sentiment)) & 
                (df_results["category"].isin(filter_category))
            ]
            
            if search_query:
                filtered_df = filtered_df[filtered_df["feedback_text"].str.contains(search_query, case=False, na=False)]
                
            st.write(f"Showing {len(filtered_df)} of {len(df_results)} feedback records.")
            
            # Format display
            display_df = filtered_df[[
                "feedback_id", "customer_id", "feedback_date", "feedback_text", 
                "sentiment", "sentiment_score", "category", "opportunity_score", "business_impact_score"
            ]].copy()
            
            st.dataframe(display_df, use_container_width=True)
 
# ----------------- PAGE 5: EXECUTIVE REPORT -----------------
elif nav_page == "Executive Report":
    st.markdown("<div class='section-title'>Executive Summary Report</div>", unsafe_allow_html=True)
    
    # Selector
    reports_df = db.get_uploaded_reports()
    if reports_df.empty:
        st.warning("Please upload a dataset first.")
    else:
        # Pre-select report
        selected_idx = 0
        if "current_report_id" in st.session_state:
            matching_rows = reports_df[reports_df["id"] == st.session_state["current_report_id"]]
            if not matching_rows.empty:
                selected_idx = int(matching_rows.index[0])
                
        selected_report_label = st.selectbox(
            "Select Feedback Analysis Run:",
            options=reports_df.index,
            format_func=lambda idx: f"{reports_df.loc[idx, 'filename']} (ID: {reports_df.loc[idx, 'id']})",
            index=selected_idx,
            key="report_selector"
        )
        
        report_id = int(reports_df.loc[selected_report_label, "id"])
        st.session_state["current_report_id"] = report_id
        
        # Load details
        report_details = db.get_report_details(report_id)
        df_results = db.get_feedback_and_analysis(report_id)
        stats = utils.calculate_aggregate_statistics(df_results)
        
        if report_details and report_details["summary_json"]:
            summary_dict = report_details["summary_json"]
            
            st.write("Review and edit the AI-generated Executive Summary sections before exporting to PDF.")
            
            # Create a form to edit summary details
            with st.form("edit_report_form"):
                col_left, col_right = st.columns(2)
                
                with col_left:
                    overall_sentiment_summary = st.text_area(
                        "Overall Sentiment Summary", 
                        value=summary_dict.get("overall_sentiment_summary", ""), 
                        height=150
                    )
                    top_complaints_summary = st.text_area(
                        "Top Complaints Summary", 
                        value=summary_dict.get("top_complaints_summary", ""), 
                        height=150
                    )
                    
                with col_right:
                    # Represent lists as string lines for easy editing
                    key_findings_str = "\n".join(summary_dict.get("key_findings", []))
                    key_findings_text = st.text_area(
                        "Key Findings (One per line)", 
                        value=key_findings_str, 
                        height=150
                    )
                    
                    product_recs_str = "\n".join(summary_dict.get("product_recommendations", []))
                    product_recs_text = st.text_area(
                        "Product Recommendations (One per line)", 
                        value=product_recs_str, 
                        height=150
                    )
                
                st.markdown("---")
                
                # Checkbox / submit
                save_changes = st.form_submit_button("Save Report Edits")
                
                if save_changes:
                    # Re-compile lists
                    summary_dict["overall_sentiment_summary"] = overall_sentiment_summary
                    summary_dict["top_complaints_summary"] = top_complaints_summary
                    summary_dict["key_findings"] = [line.strip() for line in key_findings_text.split("\n") if line.strip()]
                    summary_dict["product_recommendations"] = [line.strip() for line in product_recs_text.split("\n") if line.strip()]
                    
                    db.update_report_status(report_id, "completed", summary_dict)
                    st.success("Executive summary updates saved to the database!")
                    
            st.markdown("---")
            
            # PDF Generation
            st.subheader("Export PDF Executive Report")
            
            # Create a temp path in reports folder
            reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
            pdf_filename = f"VOC_Executive_Report_{report_id}.pdf"
            pdf_path = os.path.join(reports_dir, pdf_filename)
            
            if st.button("Generate & Download PDF Report", type="primary"):
                with st.spinner("Generating ReportLab PDF Document..."):
                    report_generator.generate_pdf_report(
                        report_id=report_id,
                        filename=report_details["filename"],
                        stats=stats,
                        summary_data=summary_dict,
                        df_feedback=df_results,
                        output_path=pdf_path
                    )
                    
                    # Save generated report details in database
                    db.save_generated_report(report_id, pdf_path)
                    st.success("PDF Executive Report generated successfully!")
            
            # If report file exists, show download button
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    
                st.download_button(
                    label="Download Executive Report (PDF)",
                    data=pdf_bytes,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
        else:
            st.error("No summary details found for this run. Generate statistics first.")
