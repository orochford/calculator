import streamlit as st
import numpy as np
import plotly.graph_objects as go
from data import INDUSTRY_PRESETS, generate_revenue_array, CHART_COLORS
from utils import create_security_budget_chart, create_budget_table, highlight_selected_revenue

def create_budget_donut_chart(annual_revenue, it_percentage, security_percentage):
    """Create a donut chart showing budget breakdown"""
    # Calculate percentages
    revenue_percentage = 100 - it_percentage
    other_it_budget = it_percentage * (100 - security_percentage) / 100
    security_budget = it_percentage * security_percentage / 100
    
    # Create the donut chart
    fig = go.Figure(data=[go.Pie(
        labels=['Revenue', 'Other IT Budget', 'Security Budget'],
        values=[revenue_percentage, other_it_budget, security_budget],
        hole=.6,
        marker_colors=['#E8E8E8', '#008581', '#96E4B0'],
        textinfo='label+percent',
        textposition='outside',
        showlegend=True
    )])
    
    # Update layout
    fig.update_layout(
        title={
            'text': "Budget Breakdown",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        annotations=[{
            'text': f'Total Revenue<br>${annual_revenue}M<br>IT: {it_percentage}% of Revenue<br>Security: {security_percentage}% of IT',
            'x': 0.5,
            'y': 0.5,
            'font_size': 12,
            'showarrow': False
        }],
        height=400,
        margin=dict(t=60, b=60, l=30, r=30)
    )
    
    return fig

def show():
    """Display the Budget Calculator page with interactive elements"""
    
    # Hide the default menu and footer
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Budget Controls in Sidebar
    with st.sidebar:
        st.header("Budget Controls")
        
        # Industry selection - changed from selectbox to radio buttons
        selected_industry = st.radio(
            "Select Industry",
            options=list(INDUSTRY_PRESETS.keys()),
            index=list(INDUSTRY_PRESETS.keys()).index(st.session_state.selected_industry)
        )
        st.session_state.selected_industry = selected_industry
        
        # Get industry preset values
        preset = INDUSTRY_PRESETS[selected_industry]
        
        # IT Budget percentage
        it_percentage = st.slider(
            "IT Budget (% of Revenue)",
            min_value=float(preset["it_min"]),
            max_value=float(preset["it_max"]),
            value=float(st.session_state.it_percentage),
            step=0.1,
            key="it_percentage_slider"
        )
        st.session_state.it_percentage = it_percentage
        
        # Security Budget percentage
        security_percentage = st.slider(
            "Security Budget (% of IT)",
            min_value=float(preset["security_min"]),
            max_value=float(preset["security_max"]),
            value=float(st.session_state.security_percentage),
            step=0.1,
            key="security_percentage_slider"
        )
        st.session_state.security_percentage = security_percentage
        
        # Annual Revenue
        annual_revenue = st.number_input(
            "Annual Revenue (Million $)",
            min_value=1,
            max_value=1000,
            value=int(st.session_state.annual_revenue),
            step=10,
            key="annual_revenue_input"
        )
        st.session_state.annual_revenue = annual_revenue
        
        # Chart Revenue Range
        max_chart_revenue = st.slider(
            "Chart Revenue Range (Million $)",
            min_value=100,
            max_value=1000,
            value=int(st.session_state.max_chart_revenue),
            step=100,
            key="max_chart_revenue_slider"
        )
        st.session_state.max_chart_revenue = max_chart_revenue
    
    # Main content area
    st.header("Interactive Security Budget Calculator")
    
    # Calculated Budgets section at the top
    st.subheader("Calculated Budgets")
    st.markdown("Below are your calculated budgets based on the selected percentages. The delta values show the percentage relationship between each budget level.")
    
    # Calculate budgets
    it_budget = annual_revenue * (it_percentage / 100)
    security_budget = it_budget * (security_percentage / 100)
    
    # Display metrics in columns
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            "Annual Revenue",
            f"${annual_revenue:.2f}M"
        )
        
    with metric_col2:
        st.metric(
            "IT Budget",
            f"${it_budget:.2f}M",
            f"↑ {it_percentage}% of Revenue"
        )
        
    with metric_col3:
        st.metric(
            "Security Budget",
            f"${security_budget:.2f}M",
            f"↑ {security_percentage}% of IT Budget"
        )
    
    # Add donut chart
    donut_fig = create_budget_donut_chart(annual_revenue, it_percentage, security_percentage)
    st.plotly_chart(donut_fig, use_container_width=True)
    
    # Add explanation of the donut chart
    st.markdown("""
    Understanding the Budget Breakdown:
    - The outer ring shows how your total revenue is divided
    - Green section: Security budget (% of IT budget)
    - Teal section: IT budget (other than security)
    - Gray section: Revenue
    - Hover over sections to see detailed values
    """)
    
    st.divider()
    
    # Security Budget Chart section
    st.subheader("Security Budget Chart")
    st.markdown("""
    This chart visualizes security budgets across different revenue points:
    - **Grouped Bars**: Show security budgets at different percentages around your selected value
    - **Trend Lines**: Display industry typical ranges
    - **Hover**: Mouse over elements to see detailed values
    """)
    
    # Generate revenue array for the chart
    revenue_array = generate_revenue_array(max_chart_revenue)
    x_positions = np.arange(len(revenue_array))
    
    # Create the chart
    fig = create_security_budget_chart(
        revenue_array=revenue_array,
        x_positions=x_positions,
        current_it=it_percentage,
        current_security=security_percentage,
        show_ranges=True,
        min_it_percentage=float(preset["it_min"]),
        max_it_percentage=float(preset["it_max"]),
        typical_it_percentage=float(preset["it_typical"]),
        min_security_percentage=float(preset["security_min"]),
        max_security_percentage=float(preset["security_max"]),
        typical_security_percentage=float(preset["security_typical"]),
        chart_colors=CHART_COLORS
    )
    
    # Display the chart
    st.plotly_chart(
        fig, 
        use_container_width=True,
        config={
            'displayModeBar': True,
            'responsive': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {'format': 'png', 'filename': 'security_budget_chart'},
        }
    )
    
    st.divider()
    
    # Budget Table section
    st.subheader("Budget Breakdown Table")
    
    # Create a container with fixed height for the table
    table_container = st.container()
    with table_container:
        df = create_budget_table(revenue_array, it_percentage, security_percentage)
        styled_df = df.style.apply(highlight_selected_revenue, axis=1)
        st.dataframe(styled_df, hide_index=True, use_container_width=True)
    
    st.caption(f"""
    Table shows security budgets at different revenue tiers with {it_percentage}% IT budget.
    Your current revenue is highlighted. Security columns show budget at 5%, 10%, 15%, 20%, and your selected {security_percentage}% of IT budget.
    """)
    
    st.divider()
    
    # Industry Context section
    st.subheader("Industry Context")
    st.markdown("This section shows typical budget ranges for your target industry. Use this information to align your pricing with customer expectations.")
    
    st.subheader(selected_industry)
    st.markdown("Industry Budget Benchmarks")
    
    st.markdown(f"""
    - IT Budget Range: {preset["it_min"]}% to {preset["it_max"]}% of revenue
        - Typical for {selected_industry}
        - Based on industry research
    """)
    
    st.markdown(f"""
    - Security Budget Range: {preset["security_min"]}% to {preset["security_max"]}% of IT budget
        - Typical for {selected_industry}
        - Based on security maturity level
    """)
    
    st.markdown("Your Target Budgets")
    st.markdown(f"""
    - IT Budget: {it_percentage}% of revenue
        - {"Above" if it_percentage > preset["it_typical"] else "Below"} industry typical ({preset["it_typical"]}%)
    - Security Budget: {security_percentage}% of IT budget
        - {"Above" if security_percentage > preset["security_typical"] else "Below"} industry typical ({preset["security_typical"]}%)
    """)
    
    # Pricing Recommendations section
    st.markdown("### Pricing Recommendations")
    st.markdown("Based on industry benchmarks and target budgets, here are recommendations for pricing your solution:")
    
    st.markdown("✅ Budget Alignment")
    st.markdown("""
    - Your target budgets align well with industry standards
    - Consider standard market pricing based on:
        - Solution value
        - Market competition
        - Customer growth potential
    """) 