import streamlit as st
from services.usage_logger import UsageLogger
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_logs_page():
    usage_logger = UsageLogger()
    stats = usage_logger.get_usage_stats()
    
    # Add references section at the bottom
    st.markdown("---")
    st.subheader("מקורות")
    
    with st.expander("מחירי מודלים"):
        st.code("""
        Claude 3 Sonnet: $3/MTok (input), $15/MTok (output)
        Claude 3 Haiku: $1/MTok (input), $5/MTok (output)
        Claude 3 Opus: $15/MTok (input), $75/MTok (output)
        """)
    
    # Display total stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("עלות כוללת", f"${stats['total_cost']:.4f}")
    with col2:
        st.metric("מספר קריאות", stats["calls_count"])
    with col3:
        st.metric("סה״כ טוקנים", f"{stats['total_tokens']:,}")
    
    # Display per-model stats
    if "per_model" in stats:
        st.subheader("שימוש לפי מודל")
        
        # Create pie charts for costs
        costs = [model_stats['cost'] for model_stats in stats['per_model'].values()]
        labels = list(stats['per_model'].keys())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=costs,
            hole=.3,
            textinfo='label+percent',
            textposition='inside'
        )])
        
        fig.update_layout(
            title="התפלגות עלויות לפי מודל",
            height=400,
            margin=dict(t=50, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed stats per model
        for model, model_stats in stats["per_model"].items():
            with st.expander(f"מודל: {model}"):
                cols = st.columns(3)
                with cols[0]:
                    st.metric("קריאות", model_stats['calls'])
                with cols[1]:
                    st.metric("טוקנים", f"{model_stats['total_tokens']:,}")
                with cols[2]:
                    st.metric("עלות", f"${model_stats['cost']:.4f}")