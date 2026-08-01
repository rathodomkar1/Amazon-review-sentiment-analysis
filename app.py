import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Amazon Review Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Advanced CSS Styling (Includes Sidebar & Interactive Element overrides)
st.markdown("""
    <style>
    /* Main Background color */
    .stApp {
        background-color: #EAEDED;
    }
    
    /* Top Header Bar Simulation */
    header[data-testid="stHeader"] {
        background-color: #131921 !important;
        height: 60px;
    }
    
    /* Custom Banner Title */
    .amazon-banner {
        background-color: #232F3E;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 25px;
        color: white;
        border-bottom: 4px solid #FF9900;
    }
    .amazon-banner h1 {
        color: white !important;
        margin: 0;
        font-family: "Amazon Ember", Arial, sans-serif;
        font-weight: 500;
        font-size: 26px;
    }
    
    /* Elegant Metric Cards Styling */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #111111 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #565959 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Target regular page columns for white background container cards */
    .stHorizontalBlock div[data-testid="column"] {
        background-color: white;
        padding: 20px !important;
        border-radius: 8px;
        border: 1px solid #D5D9D9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Style Headings */
    h3 {
        color: #0F1111 !important;
        font-family: "Amazon Ember", Arial, sans-serif;
        border-bottom: 1px solid #E7E7E7;
        padding-bottom: 8px;
        margin-top: 15px !important;
    }
    
    /* Sidebar styling override */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #D5D9D9;
    }
    
    /* Custom button styling */
    div.stButton > button {
        background-color: #FFD814 !important;
        border: 1px solid #FCD200 !important;
        color: #0F1111 !important;
        border-radius: 8px !important;
        padding: 6px 20px !important;
        box-shadow: 0 2px 5px rgba(213,217,217,.5);
    }
    div.stButton > button:hover {
        background-color: #F7CA00 !important;
        border-color: #F2C200 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Amazon Header Banner
st.markdown("""
    <div class="amazon-banner">
        <h1>📦 amazon retail analytics | review intelligence dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# 4. Load Dataset
csv_path = "Data/Reviews.csv"

if os.path.exists(csv_path):
    # Load dataset once and cache it via state if necessary, keeping it straightforward here
    raw_df = pd.read_csv(csv_path)
    raw_df = raw_df[['Score', 'Summary', 'Text']].dropna()

    # Calculate Sentiment Labels
    def sentiment_label(score):
        if score >= 4: return 'Positive'
        elif score == 3: return 'Neutral'
        else: return 'Negative'

    raw_df['Sentiment'] = raw_df['Score'].apply(sentiment_label)

    # ==========================================
    # SIDEBAR CONTROL PANEL
    # ==========================================
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=120)
    st.sidebar.markdown("### 🛠️ Control Panel")
    
    # Filter 1: Sentiment Multiselect
    selected_sentiments = st.sidebar.multiselect(
        "Filter by Sentiment Status:",
        options=['Positive', 'Neutral', 'Negative'],
        default=['Positive', 'Neutral', 'Negative']
    )
    
    # Filter 2: Star Rating Slider
    rating_range = st.sidebar.slider(
        "Select Star Rating Range:",
        min_value=1, max_value=5, value=(1, 5)
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("💡 *Tip: Filter for 'Negative' sentiment and 1-2 stars to perform root-cause complaint analysis.*")

    # Apply Filters to the Data dynamically
    df = raw_df[
        (raw_df['Sentiment'].isin(selected_sentiments)) & 
        (raw_df['Score'] >= rating_range[0]) & 
        (raw_df['Score'] <= rating_range[1])
    ]

    # Handle edge case where filters return empty rows
    if not df.empty:
        # Calculate Dynamic Metrics
        total_reviews = len(df)
        avg_rating = df['Score'].mean()
        positive_percent = (len(df[df['Sentiment'] == 'Positive']) / total_reviews) * 100 if total_reviews > 0 else 0
        negative_percent = (len(df[df['Sentiment'] == 'Negative']) / total_reviews) * 100 if total_reviews > 0 else 0

        # 5. Dashboard KPI Metric Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Selected Records", f"{total_reviews:,}")
        col2.metric("Positive Volume Ratio", f"{positive_percent:.1f}%")
        col3.metric("Negative Volume Ratio", f"{negative_percent:.1f}%")
        col4.metric("Avg Filtered Rating", f"{avg_rating:.2f} ⭐")

        # Layout splitting Chart and Data Preview
        st.write("### Sentiment Analytics Breakdown")
        chart_col, data_col = st.columns([2, 3])

        with chart_col:
            # Reindex to ensure structure consistency
            sentiment_counts = df['Sentiment'].value_counts().reindex(['Positive', 'Neutral', 'Negative']).fillna(0)
            
            # Using intuitive UX color mappings: Positive=Green, Neutral=Grey, Negative=Red
            sentiment_colors = ['#2ECC71', '#95A5A6', '#E74C3C']
            sentiment_borders = ['#27AE60', '#7F8C8D', '#C0392B']
            
            fig, ax = plt.subplots(figsize=(5, 4.2))
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            
            bars = ax.bar(sentiment_counts.index, sentiment_counts.values, color=sentiment_colors, edgecolor=sentiment_borders, width=0.5, zorder=3)
            
            # Formatted axes mapping 
            ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#D5D9D9')
            ax.spines['bottom'].set_color('#D5D9D9')
            ax.tick_params(colors='#111111', labelsize=10)
            
            # Add metric text strings above values elegantly
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{int(height):,}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, fontweight='bold', color='#111111')

            plt.title("Volume Distribution by Filtered Group", fontsize=11, color='#111111', pad=15, weight='bold')
            plt.tight_layout()
            st.pyplot(fig)

        with data_col:
            st.write("#### 📄 Document Corpus Sample")
            # Display interactive dataframe
            st.dataframe(df.head(100), height=310, use_container_width=True)
            
    else:
        st.warning("⚠️ No records match your current filter selections. Adjust your sidebar controls to display data.")
else:
    st.error(f"Could not locate target dataset file at '{csv_path}'. Please review file paths in your workspace layout.")
