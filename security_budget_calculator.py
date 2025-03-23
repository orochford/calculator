import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import base64
import io
import plotly.io as pio
import math

# Set page layout to wide
st.set_page_config(layout="wide", menu_items=None)

# Initialize session state for syncing values between sidebar and main column
if 'it_percentage' not in st.session_state:
    st.session_state.it_percentage = 5.5
if 'security_percentage' not in st.session_state:
    st.session_state.security_percentage = 9.5
# Initialize session state for custom industries
if 'custom_industries' not in st.session_state:
    st.session_state.custom_industries = {}

# Configure plotly to use a higher renderer
pio.templates.default = "plotly_white"

# Apply custom CSS for better chart rendering
st.markdown("""
<style>
    .stPlotlyChart {
        max-width: 100% !important;
    }
    .js-plotly-plot .plotly {
        width: 100%;
    }
    iframe {
        width: 100%;
    }
    
    /* Ensure tooltips are visible */
    .plotly-graph-div .hoverlayer {
        z-index: 1000;
    }
    
    /* Increase spacing for text */
    .plotly-graph-div text {
        font-weight: bold !important;
    }

    /* Custom styling for the cyberfuturists link */
    .cyberfuturists-link {
        background-color: #1E1E1E;
        padding: 15px 25px;
        border-radius: 8px;
        color: #ffffff !important;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 20px;
        transition: all 0.3s ease;
    }
    .cyberfuturists-link:hover {
        background-color: #2E2E2E;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Define industry-specific IT budget percentages based on updated industry data
INDUSTRY_IT_SPEND = {
    "Weighted Average": {"min": 4, "max": 7, "typical": 5.5},
    "Financial Services": {"min": 7, "max": 11, "typical": 9.0},
    "Healthcare": {"min": 4, "max": 6, "typical": 5.0},
    "Retail": {"min": 2, "max": 4, "typical": 3.0},
    "Technology": {"min": 8, "max": 15, "typical": 11.5},
    "Manufacturing": {"min": 2, "max": 4, "typical": 3.0},
    "Government/Public Sector": {"min": 5, "max": 8, "typical": 6.5},
    "Education": {"min": 3, "max": 6, "typical": 4.5},
    "Energy & Utilities": {"min": 3, "max": 5, "typical": 4.0},
    "Transportation & Logistics": {"min": 2, "max": 5, "typical": 3.5},
    "Custom": None  # For user-defined values
}

# Define industry-specific security budget percentages (as % of IT spend)
INDUSTRY_SECURITY_SPEND = {
    "Weighted Average": {"min": 7, "max": 12, "typical": 9.5},
    "Financial Services": {"min": 10, "max": 15, "typical": 12.5},
    "Healthcare": {"min": 7, "max": 10, "typical": 8.5},
    "Retail": {"min": 5, "max": 8, "typical": 6.5},
    "Technology": {"min": 10, "max": 20, "typical": 15.0},
    "Manufacturing": {"min": 5, "max": 10, "typical": 7.5},
    "Government/Public Sector": {"min": 8, "max": 12, "typical": 10.0},
    "Education": {"min": 5, "max": 8, "typical": 6.5},
    "Energy & Utilities": {"min": 6, "max": 10, "typical": 8.0},
    "Transportation & Logistics": {"min": 5, "max": 8, "typical": 6.5},
    "Custom": None  # For user-defined values
}

# Create industry presets dictionary for the new UI
industry_presets = {
    "Financial Services": {
        "it_min": INDUSTRY_IT_SPEND["Financial Services"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Financial Services"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Financial Services"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Financial Services"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Financial Services"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Financial Services"]["max"],
    },
    "Healthcare": {
        "it_min": INDUSTRY_IT_SPEND["Healthcare"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Healthcare"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Healthcare"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Healthcare"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Healthcare"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Healthcare"]["max"],
    },
    "Retail": {
        "it_min": INDUSTRY_IT_SPEND["Retail"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Retail"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Retail"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Retail"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Retail"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Retail"]["max"],
    },
    "Technology": {
        "it_min": INDUSTRY_IT_SPEND["Technology"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Technology"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Technology"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Technology"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Technology"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Technology"]["max"],
    },
    "Manufacturing": {
        "it_min": INDUSTRY_IT_SPEND["Manufacturing"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Manufacturing"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Manufacturing"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Manufacturing"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Manufacturing"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Manufacturing"]["max"],
    },
    "Government/Public Sector": {
        "it_min": INDUSTRY_IT_SPEND["Government/Public Sector"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Government/Public Sector"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Government/Public Sector"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Government/Public Sector"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Government/Public Sector"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Government/Public Sector"]["max"],
    },
    "Education": {
        "it_min": INDUSTRY_IT_SPEND["Education"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Education"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Education"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Education"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Education"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Education"]["max"],
    },
    "Energy & Utilities": {
        "it_min": INDUSTRY_IT_SPEND["Energy & Utilities"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Energy & Utilities"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Energy & Utilities"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Energy & Utilities"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Energy & Utilities"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Energy & Utilities"]["max"],
    },
    "Transportation & Logistics": {
        "it_min": INDUSTRY_IT_SPEND["Transportation & Logistics"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Transportation & Logistics"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Transportation & Logistics"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Transportation & Logistics"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Transportation & Logistics"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Transportation & Logistics"]["max"],
    },
    "Weighted Average": {
        "it_min": INDUSTRY_IT_SPEND["Weighted Average"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Weighted Average"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Weighted Average"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Weighted Average"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Weighted Average"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Weighted Average"]["max"],
    },
}

# Title and description


# Add dark theme container for logo
st.markdown("""
<style>
.logo-container {
    background-color: #1E1E1E;
    padding: 40px;
    border-radius: 10px;
    margin-bottom: 30px;
    text-align: center;
    width: 100%;
}
.logo-container img {
    width: 100%;
    max-width: 600px;
    height: auto;
    margin: 0 auto;
}
</style>
<div class="logo-container">
    <img src="https://img1.wsimg.com/isteam/ip/fc53e870-07e8-482a-a411-787d4ae0464d/Cyber%20Futurists%20LinkedIn%20Career%20Page%20Banner%20(1.png/:/rs=w:984,h:167" alt="Cyberfuturists Logo">
</div>
""", unsafe_allow_html=True)
st.title('Security Budget Calculator')
st.markdown('''
This app helps security vendors understand typical IT and Security budgets across different industries to better price their solutions.

Inspired by [Oliver Rochford's](https://www.linkedin.com/in/oliver-rochford/) analysis: "[Why you are probably pricing your security solution all wrong](https://www.linkedin.com/pulse/why-you-probably-pricing-your-security-solution-all-wrong-rochford/)."

Brought to you by [Cyberfuturists](https://www.cyberfuturists.com).
''')

# Create tabs for different views
tab1, tab2 = st.tabs(["Budget Calculator", "Industry Benchmarks"])

# Tab 1: Budget Calculator
with tab1:
    # Create sidebar for settings
    with st.sidebar:
        st.header("Calculator Settings")
        st.markdown("""
        Configure the calculator to understand typical budget ranges for your target industry.
        Use this information to better align your pricing with customer budgets.
        """)
        
        # Industry selection with help text
        industry_help = """
        Select your target industry to understand typical budget ranges:
        - Financial Services: Higher IT/Security spend due to regulations
        - Healthcare: Moderate IT spend with focus on security
        - Technology: Highest IT spend across sectors
        - Manufacturing: Generally lower IT spend
        - Custom: Define your own industry benchmarks
        """
        selected_industry = st.radio(
            "Select Industry",
            options=list(industry_presets.keys()) + ["Custom"],
            index=9,  # Default to Weighted Average
            key="industry_selector",
            help=industry_help
        )
        
        # Initialize show_ranges and range variables
        show_ranges = False
        min_it_percentage = 0
        max_it_percentage = 0
        typical_it_percentage = 0
        min_security_percentage = 0
        max_security_percentage = 0
        typical_security_percentage = 0
        
        # Budget percentage settings with enhanced help
        if selected_industry == "Custom":
            st.markdown("""
            #### Custom Budget Settings
            Set your own budget ranges for scenario planning.
            """)
            
            # Option to show ranges with help text
            ranges_help = """
            Enable this to set and display custom budget ranges.
            Useful for:
            - Planning different scenarios
            - Setting budget boundaries
            - Comparing multiple options
            """
            show_ranges = st.checkbox("Show Budget Ranges", value=True, help=ranges_help)
            
            if show_ranges:
                st.markdown("#### Custom Range Settings")
                
                min_it_help = "Minimum IT budget percentage for conservative scenario"
                max_it_help = "Maximum IT budget percentage for aggressive scenario"
                typical_it_help = "Most likely IT budget percentage based on your assessment"
                
                min_it_percentage = st.slider("Min IT Budget (%)", 
                    min_value=0.1, 
                    max_value=10.0, 
                    value=3.0, 
                    step=0.1, 
                    help=min_it_help
                )
                max_it_percentage = st.slider("Max IT Budget (%)", 
                    min_value=min_it_percentage, 
                    max_value=30.0, 
                    value=8.0, 
                    step=0.1, 
                    help=max_it_help
                )
                typical_it_percentage = st.slider("Typical IT Budget (%)", 
                    min_value=min_it_percentage, 
                    max_value=max_it_percentage, 
                    value=(min_it_percentage + max_it_percentage) / 2,
                    step=0.1,
                    help=typical_it_help
                )
                
                min_security_help = "Minimum security budget percentage for conservative scenario"
                max_security_help = "Maximum security budget percentage for aggressive scenario"
                typical_security_help = "Most likely security budget percentage based on your assessment"
                
                min_security_percentage = st.slider("Min Security Budget (%)", 
                    min_value=0.1, 
                    max_value=15.0, 
                    value=5.0, 
                    step=0.1, 
                    help=min_security_help
                )
                max_security_percentage = st.slider("Max Security Budget (%)", 
                    min_value=min_security_percentage, 
                    max_value=40.0, 
                    value=15.0, 
                    step=0.1, 
                    help=max_security_help
                )
                typical_security_percentage = st.slider("Typical Security Budget (%)", 
                    min_value=min_security_percentage, 
                    max_value=max_security_percentage,
                    value=(min_security_percentage + max_security_percentage) / 2,
                    step=0.1,
                    help=typical_security_help
                )
        else:
            # Use industry preset values
            preset = industry_presets[selected_industry]
            st.session_state.it_percentage = preset["it_typical"]
            st.session_state.security_percentage = preset["security_typical"]
            
            # Show ranges by default for industry presets
            show_ranges = True
            min_it_percentage = preset["it_min"]
            max_it_percentage = preset["it_max"]
            typical_it_percentage = preset["it_typical"]
            min_security_percentage = preset["security_min"]
            max_security_percentage = preset["security_max"]
            typical_security_percentage = preset["security_typical"]
        
        # Chart settings
        st.markdown("#### Chart Settings")
        chart_revenue_help = """
        Set the maximum revenue point shown in the chart.
        This affects:
        - The range of revenue points displayed
        - The scale of the visualization
        - The detail level of budget breakdowns
        """
        max_chart_revenue = st.slider(
            "Max Revenue in Chart (Million $)",
            min_value=100,
            max_value=1000,
            value=500,
            step=100,
            help=chart_revenue_help
        )
        
        # Add information about chart customization
        st.markdown("""
        💡 **Chart Customization Tips**:
        - Adjust max revenue to zoom in/out
        - Toggle ranges to compare scenarios
        - Use custom ranges for detailed planning
        - Industry presets provide standard benchmarks
        """)
        
        # Generate revenue array - use consistent 100M increments
        revenue_array = np.arange(0, max_chart_revenue + 100, 100).astype(int)
        # Make sure we include starting points for better visualization
        if 50 not in revenue_array and max_chart_revenue >= 50:
            revenue_array = np.sort(np.append(revenue_array, [50]))
        
    st.header("Interactive Security Budget Calculator")
    
    # Layout for main content
    main_col1, main_col2 = st.columns([2, 1])
    
    # First column - Chart and Budget Controls
    with main_col1:
        # Create the chart with enhanced description
        st.subheader("Security Budget Chart")
        st.markdown("""
        This chart visualizes security budgets across different revenue points:
        - **Grouped Bars**: Show security budgets at different percentages around your selected value
        - **Trend Lines**: Display industry typical ranges (if enabled)
        - **Hover**: Mouse over elements to see detailed values
        """)
        
        # Get the current values from session state
        current_security = st.session_state.security_percentage
        current_it = st.session_state.it_percentage
        
        # Create the chart
        fig = go.Figure()
        
        # Add bar traces for percentages around the selected security percentage
        bar_colors = ["#008581", "#4C9C8B", "#96E4B0", "#FFDAE8"]  # New teal-to-pink gradient
        # Create percentages centered around the selected value
        security_percentages = [
            max(1, current_security - 6),
            max(1, current_security - 3),
            current_security,
            min(25, current_security + 3)
        ]
        
        # Bar width configuration for clearer grouping
        bar_width = 0.15
        
        # Revenue array for bars placement
        x_positions = np.arange(len(revenue_array))
        
        # Always use current_it for bars
        display_it_percentage = current_it
        
        for idx, percent in enumerate(security_percentages):
            # Use the same IT percentage as trend lines for consistency
            security_budget = revenue_array * (display_it_percentage / 100) * (percent / 100)
            
            # Highlight the selected percentage
            is_selected = percent == current_security
            marker_color = bar_colors[idx]
            marker_line_width = 3 if is_selected else 2
            
            fig.add_trace(go.Bar(
                x=x_positions + (idx - 1.5) * bar_width,  # grouped bars
                y=security_budget,
                name=f"{percent}% of IT Budget ({display_it_percentage}% IT){' (Selected)' if is_selected else ''}",
                marker_color=marker_color,
                marker_line_width=marker_line_width,  # Thicker border for selected
                marker_line_color='rgba(0,0,0,0.7)',  # Darker border
                width=bar_width,
                text=[f"${val:.2f}M" for val in security_budget],
                textposition='outside',
                textfont=dict(
                    size=11,  # Larger text
                    family="Arial",
                    color="rgba(0,0,0,0.9)"  # Darker text
                ),
                hovertemplate="<b>Revenue:</b> $%{customdata}M<br>" +
                            "<b>Calculation:</b><br>" +
                            f"IT Budget: {display_it_percentage}% of Revenue<br>" +
                            f"Security Budget: {percent}% of IT Budget<br>" +
                            f"Final: {percent}% of {display_it_percentage}% = {(display_it_percentage * percent / 100):.2f}% of Revenue<br>" +
                            "<b>Result:</b> $%{y:.2f}M<extra></extra>",
                customdata=revenue_array
            ))

        # Add trend lines for industry standard scenarios if ranges are enabled
        if show_ranges:
            # Lower bound trend line
            lower_security_budget = revenue_array * (min_it_percentage / 100) * (min_security_percentage / 100)
            fig.add_trace(go.Scatter(
                x=x_positions,  # Use x_positions for consistency
                y=lower_security_budget,
                mode='lines+text',
                name=f"Lower Bound ({min_security_percentage}% of {min_it_percentage}% IT)",
                line=dict(color='#008581', width=2, dash='dot'),  # Teal
                text=[f"${y:.2f}M" for y in lower_security_budget],
                textposition='bottom right',
                textfont=dict(
                    color='#008581',
                    size=10,
                    family="Arial",
                ),
                hovertemplate="<b>Revenue:</b> $%{customdata}M<br>" +
                            f"<b>Lower Bound Calculation:</b><br>" +
                            f"IT Budget: {min_it_percentage}% of Revenue<br>" +
                            f"Security Budget: {min_security_percentage}% of IT Budget<br>" +
                            f"Final: {min_security_percentage}% of {min_it_percentage}% = {(min_it_percentage * min_security_percentage / 100):.2f}% of Revenue<br>" +
                            "<b>Result:</b> $%{y:.2f}M<extra></extra>",
                customdata=revenue_array
            ))
            
            # Upper bound trend line
            upper_security_budget = revenue_array * (max_it_percentage / 100) * (max_security_percentage / 100)
            fig.add_trace(go.Scatter(
                x=x_positions,  # Use x_positions for consistency
                y=upper_security_budget,
                mode='lines+text',
                name=f"Upper Bound ({max_security_percentage}% of {max_it_percentage}% IT)",
                line=dict(color='#E4509A', width=2, dash='dot'),  # Dark pink
                text=[f"${y:.2f}M" for y in upper_security_budget],
                textposition='top right',
                textfont=dict(
                    color='#E4509A',
                    size=10,
                    family="Arial",
                ),
                hovertemplate="<b>Revenue:</b> $%{customdata}M<br>" +
                            f"<b>Upper Bound Calculation:</b><br>" +
                            f"IT Budget: {max_it_percentage}% of Revenue<br>" +
                            f"Security Budget: {max_security_percentage}% of IT Budget<br>" +
                            f"Final: {max_security_percentage}% of {max_it_percentage}% = {(max_it_percentage * max_security_percentage / 100):.2f}% of Revenue<br>" +
                            "<b>Result:</b> $%{y:.2f}M<extra></extra>",
                customdata=revenue_array
            ))
            
            # Typical range trend line
            typical_security_budget = revenue_array * (typical_it_percentage / 100) * (typical_security_percentage / 100)
            fig.add_trace(go.Scatter(
                x=x_positions,  # Use x_positions for consistency
                y=typical_security_budget,
                mode='lines+text',
                name=f"Typical ({typical_security_percentage}% of {typical_it_percentage}% IT)",
                line=dict(color='#96E4B0', width=3),  # Mint green
                text=[f"${y:.2f}M" for y in typical_security_budget],
                textposition='middle right',
                textfont=dict(
                    color='#96E4B0',
                    size=10,
                    family="Arial",
                ),
                hovertemplate="<b>Revenue:</b> $%{customdata}M<br>" +
                            f"<b>Typical Calculation:</b><br>" +
                            f"IT Budget: {typical_it_percentage}% of Revenue<br>" +
                            f"Security Budget: {typical_security_percentage}% of IT Budget<br>" +
                            f"Final: {typical_security_percentage}% of {typical_it_percentage}% = {(typical_it_percentage * typical_security_percentage / 100):.2f}% of Revenue<br>" +
                            "<b>Result:</b> $%{y:.2f}M<extra></extra>",
                customdata=revenue_array
            ))

        # Update layout for better chart presentation with thicker bars
        fig.update_layout(
            title=dict(
                text=f"Security Budget by Annual Revenue",
                y=0.99,  # Move title higher but keep within 0-1 range
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=16)
            ),
            xaxis_title="Annual Revenue (Million $)",
            yaxis_title="Security Budget (Million $)",
            barmode='group',
            bargap=0.15,    # Slightly reduced gap between grouped bars
            bargroupgap=0.02,  # Tighter grouping
            height=700,  # Taller chart
            width=None,  # Allow auto-width
            autosize=True,
            font=dict(family="Arial", size=11),
            plot_bgcolor='white',
            margin=dict(l=80, r=80, t=150, b=100),  # Increased top margin for title and subtitle
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.98,  # Keep legend within 0-1 range
                xanchor="center",
                x=0.5,
                bgcolor='rgba(255, 255, 255, 0.8)',
                font=dict(size=10)
            ),
            uniformtext=dict(mode='hide', minsize=8),
            showlegend=True,
        )

        # Add subtitle for current settings
        fig.add_annotation(
            text=f"IT Budget: {current_it}% of Revenue | Security Budget: {current_security}% of IT Budget",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.95,  # Keep subtitle within 0-1 range
            showarrow=False,
            font=dict(size=12),
            yshift=0
        )

        # Configure axis formatting with better spacing and consistent grid
        fig.update_xaxes(
            showgrid=True,
            gridcolor='lightgray',
            tickmode='array',
            tickvals=x_positions,
            ticktext=[f"${rev}M" for rev in revenue_array],
            tickangle=45,  # Angled labels to prevent overlap
            tickfont=dict(size=10),
            minor_showgrid=False,
            dtick=1,  # Force spacing between ticks
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridcolor='lightgray',
            tickprefix='$',
            ticksuffix='M',
            rangemode='tozero',
            tickfont=dict(size=10),
            minor_showgrid=False,
            dtick='auto',  # Automatic tick spacing
        )
        
        # Display the chart with full-width and enhanced configuration
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
        
        # Add helper text about chart sizing with more detail
        st.info("""
        💡 **Chart Tips**: 
        - Click the fullscreen button (↗️) for a larger view
        - Use the legend to toggle different elements
        - Double-click legend items to isolate them
        - Drag to zoom, double-click to reset
        """)

        st.divider()

        # Add budget table
        st.subheader("Budget Breakdown Table")
        
        # Create table data
        table_data = []
        for rev in revenue_array:
            it_budget = rev * (current_it / 100)
            security_budget = it_budget * (current_security / 100)
            
            # Format numbers for table
            rev_fmt = f"${rev:,.0f}M"
            it_fmt = f"${it_budget:,.2f}M"
            sec_fmt = f"${security_budget:,.2f}M"
            
            table_data.append({
                "Annual Revenue": rev_fmt,
                "IT Budget": it_fmt,
                f"Security Budget ({current_security}% of IT)": sec_fmt
            })
        
        # Convert to DataFrame and display
        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True
        )

    # Second column - Budget Controls and Analysis
    with main_col2:
        st.subheader("Budget Controls")
        st.markdown("""
        Adjust the values below to explore different budget scenarios. 
        Use this to understand how your solution's pricing aligns with typical customer budgets.
        """)
        
        # Get annual revenue input with help text
        revenue_help = """
        Enter the target customer's annual revenue in millions of dollars. 
        For example:
        - Enter 100 for $100 million
        - Enter 1000 for $1 billion
        """
        annual_revenue = st.number_input(
            "Annual Revenue (Million $)",
            min_value=1,
            max_value=10000,
            value=100,
            step=50,
            help=revenue_help
        )
        
        # IT Budget slider with help text
        it_help = """
        Set the percentage of annual revenue allocated to IT budget.
        Industry averages typically range from 2% to 15% depending on sector.
        Higher percentages are common in technology-focused industries.
        """
        new_it_percentage = st.slider(
            "IT Budget (% of Revenue)", 
            min_value=1.0,
            max_value=20.0,
            value=float(st.session_state.it_percentage),
            step=0.1,
            help=it_help,
            key="it_percentage_control"
        )
        
        # Security Budget slider with help text
        security_help = """
        Set the percentage of IT budget allocated to security.
        Industry averages typically range from 5% to 20% of IT budget.
        Consider factors like:
        - Regulatory requirements
        - Industry threat landscape
        - Data sensitivity
        - Compliance needs
        """
        new_security_percentage = st.slider(
            "Security Budget (% of IT Budget)", 
            min_value=1.0,
            max_value=25.0,
            value=float(st.session_state.security_percentage),
            step=0.1,
            help=security_help,
            key="security_percentage_control"
        )

        # Update session state values
        st.session_state.it_percentage = new_it_percentage
        st.session_state.security_percentage = new_security_percentage

        st.divider()

        # Display calculated budgets
        st.subheader("Calculated Budgets")
        st.markdown("""
        Below are your calculated budgets based on the selected percentages. 
        The delta values show the percentage relationship between each budget level.
        """)

        # Calculate and format budgets
        annual_revenue_formatted = f"${annual_revenue:,.2f}M" if annual_revenue < 1000 else f"${annual_revenue/1000:,.2f}B"
        it_budget = annual_revenue * (new_it_percentage / 100)
        security_budget = it_budget * (new_security_percentage / 100)
        it_budget_formatted = f"${it_budget:,.2f}M" if it_budget < 1000 else f"${it_budget/1000:,.2f}B"
        security_budget_formatted = f"${security_budget:,.2f}M" if security_budget < 1000 else f"${security_budget/1000:,.2f}B"

        # Display metrics in a more compact way
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Annual Revenue", annual_revenue_formatted)
        with col2:
            st.metric("IT Budget", it_budget_formatted, f"{new_it_percentage}% of Revenue")
        with col3:
            st.metric("Security Budget", security_budget_formatted, f"{new_security_percentage}% of IT Budget")

        st.divider()

        # Industry Context
        st.subheader("Industry Context")
        st.markdown("""
        This section shows typical budget ranges for your target industry.
        Use this information to align your pricing with customer expectations.
        """)
        
        # Add contextual information with enhanced formatting
        if selected_industry != "Custom":
            st.markdown(f"""
            ### {selected_industry}
            
            #### Industry Budget Benchmarks
            - **IT Budget Range**: {min_it_percentage}% to {max_it_percentage}% of revenue
                - Typical for {selected_industry}
                - Based on industry research
            
            - **Security Budget Range**: {min_security_percentage}% to {max_security_percentage}% of IT budget
                - Typical for {selected_industry}
                - Based on security maturity level
            
            #### Your Target Budgets
            - IT Budget: **{new_it_percentage:.1f}%** of revenue
                - {" Above" if new_it_percentage > typical_it_percentage else " Below"} industry typical ({typical_it_percentage}%)
            
            - Security Budget: **{new_security_percentage:.1f}%** of IT budget
                - {" Above" if new_security_percentage > typical_security_percentage else " Below"} industry typical ({typical_security_percentage}%)
            """)
        else:
            st.markdown(f"""
            ### Custom Industry Settings
            
            You have defined custom budget ranges for your target industry.
            Consider these factors when setting custom budgets:
            - Industry-specific requirements
            - Regulatory environment
            - Technology adoption rates
            - Market maturity
            
            #### Your Target Budgets
            - IT Budget: **{new_it_percentage:.1f}%** of revenue
            - Security Budget: **{new_security_percentage:.1f}%** of IT budget
            
            {"#### Custom Ranges" if show_ranges else ""}
            {f"- IT Budget: **{min_it_percentage}% to {max_it_percentage}%**" if show_ranges else ""}
            {f"- Security Budget: **{min_security_percentage}% to {max_security_percentage}%**" if show_ranges else ""}
            """)

        st.divider()

        # Budget Recommendations
        st.subheader("Pricing Recommendations")
        st.markdown("""
        Based on industry benchmarks and target budgets, here are recommendations for pricing your solution:
        """)

        # Calculate percentage differences from typical values
        it_diff = new_it_percentage - typical_it_percentage
        security_diff = new_security_percentage - typical_security_percentage

        # Generate recommendations
        recommendations = []
        
        # IT Budget recommendations
        if abs(it_diff) > 2:
            if it_diff > 0:
                recommendations.append(f"""
                ⚠️ **High IT Budget Target**
                - Target IT budget is {it_diff:.1f}% above industry typical
                - Consider premium pricing if your solution addresses:
                    - Digital transformation needs
                    - Regulatory requirements
                    - Competitive advantage
                """)
            else:
                recommendations.append(f"""
                ⚠️ **Low IT Budget Target**
                - Target IT budget is {abs(it_diff):.1f}% below industry typical
                - Consider value-based pricing if your solution helps with:
                    - Infrastructure modernization
                    - Security improvements
                    - Digital transformation
                """)
        
        # Security Budget recommendations
        if abs(security_diff) > 2:
            if security_diff > 0:
                recommendations.append(f"""
                ⚠️ **High Security Budget Target**
                - Target security budget is {security_diff:.1f}% above industry typical
                - Premium pricing may be justified if your solution addresses:
                    - Regulatory compliance
                    - Security incidents
                    - Complex threats
                """)
            else:
                recommendations.append(f"""
                ⚠️ **Low Security Budget Target**
                - Target security budget is {abs(security_diff):.1f}% below industry typical
                - Consider value-based pricing if your solution helps with:
                    - Compliance needs
                    - Threat management
                    - Digital transformation security
                """)
        
        # Add positive recommendations if within range
        if abs(it_diff) <= 2 and abs(security_diff) <= 2:
            recommendations.append("""
            ✅ **Budget Alignment**
            - Your target budgets align well with industry standards
            - Consider standard market pricing based on:
                - Solution value
                - Market competition
                - Customer growth potential
            """)
        
        # Display recommendations
        for rec in recommendations:
            st.markdown(rec)

        st.divider()

        # Create donut chart
        donut_fig = go.Figure()

        # Calculate budget values
        it_budget = annual_revenue * (new_it_percentage / 100)
        security_budget = it_budget * (new_security_percentage / 100)
        non_it_budget = annual_revenue - it_budget
        non_security_it = it_budget - security_budget

        # Add donut trace
        donut_fig.add_trace(go.Pie(
            values=[security_budget, non_security_it, non_it_budget],
            labels=['Security Budget', 'Other IT Budget', 'Revenue'],
            hole=0.6,
            marker_colors=['#96E4B0', '#008581', 'rgba(200, 200, 200, 0.7)'],  # Mint green, Teal, Light gray
            textinfo='label+percent',
            hovertemplate="<b>%{label}</b><br>" +
                        "$%{value:.2f}M<br>" +
                        "%{percent}<extra></extra>",
            textfont=dict(size=14),
            insidetextorientation='horizontal'
        ))

        # Update layout
        donut_fig.update_layout(
            title={
                'text': "Budget Breakdown",
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=16)
            },
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            ),
            annotations=[
                dict(
                    text=f"Total Revenue<br>${annual_revenue:.2f}M",
                    x=0.5,
                    y=0.5,
                    font=dict(size=14),
                    showarrow=False
                ),
                dict(
                    text=f"IT: {new_it_percentage}% of Revenue<br>Security: {new_security_percentage}% of IT",
                    x=0.5,
                    y=0.4,
                    font=dict(size=12),
                    showarrow=False
                )
            ]
        )

        # Display the donut chart
        st.plotly_chart(donut_fig, use_container_width=True)

        # Add explanation of the chart
        st.markdown("""
        **Understanding the Budget Breakdown:**
        - The outer ring shows how your total revenue is divided
        - Green section: Security budget (% of IT budget)
        - Teal section: IT budget (other than security)
        - Gray section: Revenue
        - Hover over sections to see detailed values
        """)

# Tab 2: Industry Benchmarks
with tab2:
    st.header("Industry Budget Benchmarks")
    
    st.markdown("""
    This tab provides benchmark data on IT and security spending across different industries. 
    Use this information to understand typical customer budgets and align your pricing strategy.
    """)
    
    # Display industry benchmarks
    st.subheader("IT Budget as Percentage of Revenue")
    
    # Combine standard and custom industries for charts
    all_industries = {**industry_presets}
    for name, data in st.session_state.custom_industries.items():
        all_industries[name] = {
            "it_min": data["it_min"],
            "it_typical": data["it_typical"],
            "it_max": data["it_max"],
            "security_min": data["security_min"],
            "security_typical": data["security_typical"],
            "security_max": data["security_max"]
        }
    
    industry_it_chart_data = pd.DataFrame({
        'Industry': list(all_industries.keys()),
        'Min IT %': [all_industries[ind]['it_min'] for ind in all_industries],
        'Typical IT %': [all_industries[ind]['it_typical'] for ind in all_industries],
        'Max IT %': [all_industries[ind]['it_max'] for ind in all_industries],
    })
    
    # Create horizontal bar chart for IT budget percentages
    it_fig = go.Figure()
    
    it_fig.add_trace(go.Bar(
        y=industry_it_chart_data['Industry'],
        x=industry_it_chart_data['Max IT %'] - industry_it_chart_data['Min IT %'],
        base=industry_it_chart_data['Min IT %'],
        name='IT Budget Range',
        marker_color='#96E4B0',  # Mint green
        orientation='h',
        text=[f"{min_val}% - {max_val}%" for min_val, max_val in 
              zip(industry_it_chart_data['Min IT %'], industry_it_chart_data['Max IT %'])],
        textposition='auto',
        hovertemplate='%{y}: %{text}<extra></extra>'
    ))
    
    it_fig.add_trace(go.Scatter(
        y=industry_it_chart_data['Industry'],
        x=industry_it_chart_data['Typical IT %'],
        mode='markers',
        name='Typical Value',
        marker=dict(color='#008581', size=12, symbol='diamond'),  # Teal
        hovertemplate='%{y}: %{x}%<extra>Typical</extra>'
    ))
    
    it_fig.update_layout(
        title='IT Budget Range by Industry (% of Revenue)',
        xaxis_title='Percentage of Revenue',
        yaxis=dict(
            title='Industry',
            categoryorder='total ascending'
        ),
        height=500,
        margin=dict(l=10, r=10, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            ticksuffix='%',
        )
    )
    
    # Display the IT budget chart
    st.plotly_chart(
        it_fig, 
        use_container_width=True,
        config={
            'displayModeBar': True,
            'responsive': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {'format': 'png', 'filename': 'it_budget_benchmarks'},
        }
    )
    
    # Create a similar chart for security budget percentages
    st.subheader("Security Budget as Percentage of IT Spend")
    industry_sec_chart_data = pd.DataFrame({
        'Industry': list(all_industries.keys()),  # Use all_industries instead of industry_presets
        'Min Security %': [all_industries[ind]['security_min'] for ind in all_industries],
        'Typical Security %': [all_industries[ind]['security_typical'] for ind in all_industries],
        'Max Security %': [all_industries[ind]['security_max'] for ind in all_industries],
    })
    
    # Create horizontal bar chart for security budget percentages
    sec_fig = go.Figure()
    
    sec_fig.add_trace(go.Bar(
        y=industry_sec_chart_data['Industry'],
        x=industry_sec_chart_data['Max Security %'] - industry_sec_chart_data['Min Security %'],
        base=industry_sec_chart_data['Min Security %'],
        name='Security Budget Range',
        marker_color='#FFDAE8',  # Light pink
        orientation='h',
        text=[f"{min_val}% - {max_val}%" for min_val, max_val in 
              zip(industry_sec_chart_data['Min Security %'], industry_sec_chart_data['Max Security %'])],
        textposition='auto',
        hovertemplate='%{y}: %{text}<extra></extra>'
    ))
    
    sec_fig.add_trace(go.Scatter(
        y=industry_sec_chart_data['Industry'],
        x=industry_sec_chart_data['Typical Security %'],
        mode='markers',
        name='Typical Value',
        marker=dict(color='#E4509A', size=12, symbol='diamond'),  # Dark pink
        hovertemplate='%{y}: %{x}%<extra>Typical</extra>'
    ))
    
    sec_fig.update_layout(
        title='Security Budget Range by Industry (% of IT Budget)',
        xaxis_title='Percentage of IT Budget',
        yaxis=dict(
            title='Industry',
            categoryorder='total ascending'
        ),
        height=500,
        margin=dict(l=10, r=10, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            ticksuffix='%',
        )
    )
    
    # Display the security budget chart
    st.plotly_chart(
        sec_fig, 
        use_container_width=True,
        config={
            'displayModeBar': True,
            'responsive': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
            'toImageButtonOptions': {'format': 'png', 'filename': 'security_budget_benchmarks'},
        }
    )
    
    # Add bubble chart for industry benchmarks
    st.subheader("Industry Budget Distribution")
    st.markdown("""
    This bubble chart shows the relationship between industries and their budget allocations.
    - Bubble size represents the combined IT and security budget
    - Larger bubbles indicate higher total investment in technology
    """)
    
    # Create data for bubble chart
    bubble_data = []
    
    # Define industries in desired order
    industries = [
        'Retail',
        'Manufacturing',
        'Transportation',  # Shortened for better display
        'Energy',  # Shortened for better display
        'Education',
        'Healthcare',
        'Weighted Avg',  # Shortened for better display
        'Government',  # Shortened for better display
        'Financial',  # Shortened for better display
        'Technology'
    ]
    
    # Add custom industries to the list
    industries.extend(list(st.session_state.custom_industries.keys()))
    
    for industry in industries:
        base_industry = industry
        if industry == 'Transportation':
            base_industry = 'Transportation & Logistics'
        elif industry == 'Energy':
            base_industry = 'Energy & Utilities'
        elif industry == 'Weighted Avg':
            base_industry = 'Weighted Average'
        elif industry == 'Government':
            base_industry = 'Government/Public Sector'
        elif industry == 'Financial':
            base_industry = 'Financial Services'
            
        # Check if it's a custom industry
        if industry in st.session_state.custom_industries:
            custom_data = st.session_state.custom_industries[industry]
            bubble_data.append({
                'Industry': industry,
                'Full Industry': industry,
                'IT Budget': custom_data['it_typical'],
                'Security Budget': custom_data['security_typical']
            })
        elif base_industry in industry_presets:
            it_typical = industry_presets[base_industry]['it_typical']
            security_typical = industry_presets[base_industry]['security_typical']
            
            bubble_data.append({
                'Industry': industry,
                'Full Industry': base_industry,
                'IT Budget': it_typical,
                'Security Budget': security_typical
            })
    
    # Convert to DataFrame
    bubble_df = pd.DataFrame(bubble_data)
    
    # Create evenly spaced x-coordinates
    x_positions = np.arange(len(bubble_df))
    
    # Create bubble chart
    bubble_fig = go.Figure()
    
    # Add bubble trace
    bubble_fig.add_trace(go.Scatter(
        x=x_positions,
        y=bubble_df['IT Budget'],
        mode='markers',  # Removed text mode since we'll add industry names as annotations
        marker=dict(
            size=bubble_df['Security Budget'] * 5,  # Size based on security budget
            color='rgba(147, 224, 220, 0.8)',  # Lighter turquoise with more opacity
            line=dict(color='rgba(147, 224, 220, 0.9)', width=1)
        ),
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                     "IT Budget: %{y:.1f}%<br>" +
                     "Security Budget: %{marker.size/5:.1f}%<extra></extra>",
        customdata=bubble_df[['Full Industry']].values,
        name=''
    ))
    
    # Add annotations for IT budget values above bubbles
    for idx, row in bubble_df.iterrows():
        # Add IT Budget percentage above bubble
        bubble_fig.add_annotation(
            x=x_positions[idx],
            y=row['IT Budget'],
            text=f"{row['IT Budget']:.1f}%",
            yshift=35,
            showarrow=False,
            font=dict(
                size=14,
                color='rgba(0, 0, 0, 0.7)',
                family='Arial'
            )
        )
        # Add industry name below bubble
        bubble_fig.add_annotation(
            x=x_positions[idx],
            y=row['IT Budget'],
            text=row['Industry'],
            yshift=-35,  # Position below bubble
            showarrow=False,
            font=dict(
                size=12,
                color='rgba(0, 0, 0, 0.7)',
                family='Arial'
            ),
            textangle=-45  # Angle the text for better readability
        )
    
    # Calculate y-axis range with nice intervals
    max_y = 15  # Fixed max for better visualization
    
    # Update layout for minimalist design
    bubble_fig.update_layout(
        title=dict(
            text='',  # Ensure empty title
            x=0.5,
            y=0.95
        ),
        xaxis_title=None,
        yaxis_title=dict(
            text='IT Budget %',
            standoff=10  # Add some padding between axis and title
        ),
        height=600,
        margin=dict(l=60, r=40, t=40, b=100),  # Reduced top margin
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='black',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                size=12,
                family='Arial'
            ),
            showticklabels=False,
            range=[-0.5, len(bubble_df) - 0.5]
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.15)',
            gridwidth=1,
            griddash='dash',
            showline=True,
            linecolor='black',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                size=12,
                family='Arial'
            ),
            range=[0, max_y],
            ticksuffix='%',
            dtick=5,
            tickmode='array',
            ticktext=['0%', '5%', '10%', '15%'],
            tickvals=[0, 5, 10, 15]
        ),
        showlegend=False,
        font=dict(
            family='Arial',
            size=14
        )
    )
    
    # Add a note about bubble sizes in a more subtle way
    bubble_fig.add_annotation(
        x=0.02,
        y=1.02,  # Lowered position
        xref='paper',
        yref='paper',
        text='Bubble size represents Security Budget %',
        showarrow=False,
        font=dict(
            size=12,
            color='rgba(0, 0, 0, 0.6)',
            family='Arial'
        ),
        align='left'
    )
    
    # Display the bubble chart
    st.plotly_chart(
        bubble_fig, 
        use_container_width=True,
        config={
            'displayModeBar': False,
            'responsive': True
        }
    )
    
    # Remove the legend since we now have labels on the chart
    st.markdown("---")
    
    # Display industry benchmark reference table
    st.subheader("Industry Benchmark Reference Table")
    
    # Create DataFrame for the table
    table_data = []
    
    # Add standard industries
    for industry in all_industries.keys():  # Use all_industries instead of industry_presets
        if industry != "Custom":  # Skip the "Custom" placeholder
            table_data.append({
                'Industry': industry,
                'IT Budget (% of Revenue)': f"{all_industries[industry]['it_min']}-{all_industries[industry]['it_max']}%",
                'Security Budget (% of IT)': f"{all_industries[industry]['security_min']}-{all_industries[industry]['security_max']}%"
            })
    
    # Create and display DataFrame
    table_df = pd.DataFrame(table_data)
    st.dataframe(
        table_df,
        hide_index=True,
        use_container_width=True
    )
    
    st.caption("*Source: Compiled from industry data from Gartner, IDC, Deloitte, Flexera and custom inputs*")
    
    # Move custom industry section to bottom as expandable
    with st.expander("➕ Add Custom Industry"):
        st.markdown("""
        Add your own industry benchmarks to compare with standard industries.
        Custom industries will be included in all charts and tables above.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Form for adding custom industry
            with st.form("add_custom_industry"):
                st.markdown("##### Industry Information")
                custom_industry_name = st.text_input("Industry Name", placeholder="Enter industry name")
                
                st.markdown("##### IT Budget (% of Revenue)")
                it_min = st.number_input("Minimum IT %", 0.1, 30.0, 2.0, 0.1)
                it_typical = st.number_input("Typical IT %", it_min, 30.0, (it_min + 2), 0.1)
                it_max = st.number_input("Maximum IT %", it_typical, 30.0, (it_typical + 2), 0.1)
                
                st.markdown("##### Security Budget (% of IT)")
                sec_min = st.number_input("Minimum Security %", 0.1, 40.0, 5.0, 0.1)
                sec_typical = st.number_input("Typical Security %", sec_min, 40.0, (sec_min + 2), 0.1)
                sec_max = st.number_input("Maximum Security %", sec_typical, 40.0, (sec_typical + 2), 0.1)
                
                submitted = st.form_submit_button("Add Industry")
                
                if submitted and custom_industry_name:
                    # Add new industry to session state
                    st.session_state.custom_industries[custom_industry_name] = {
                        "it_min": it_min,
                        "it_typical": it_typical,
                        "it_max": it_max,
                        "security_min": sec_min,
                        "security_typical": sec_typical,
                        "security_max": sec_max
                    }
                    st.success(f"Added custom industry: {custom_industry_name}")
                    st.rerun()
        
        with col2:
            # Display custom industries
            if st.session_state.custom_industries:
                st.markdown("##### Your Custom Industries")
                for name, data in st.session_state.custom_industries.items():
                    st.markdown(f"""
                    **{name}**
                    - IT Budget Range: {int(data['it_min'])}% - {int(data['it_max'])}%
                    - Typical IT: {int(data['it_typical'])}%
                    - Security Budget Range: {int(data['security_min'])}% - {int(data['security_max'])}%
                    - Typical Security: {int(data['security_typical'])}%
                    ---
                    """)
                
                if st.button("Clear All Custom Industries"):
                    st.session_state.custom_industries = {}
                    st.rerun()
            else:
                st.info("No custom industries added yet. Use the form on the left to add your first industry.")
    
    # References and methodology
    with st.expander("Methodology and References", expanded=False):
        st.markdown("""
        ### Methodology
        
        The benchmark data presented here is compiled from multiple industry sources including Gartner, IDC, Deloitte, 
        Flexera, HIMSS, and EDUCAUSE. The ranges represent typical spending patterns observed across organizations 
        of various sizes within each industry.
        
        ### Key Considerations for Budget Planning
        
        When planning your security budget, consider these factors beyond the benchmarks:
        
        1. **Regulatory Requirements**: Industries with strict compliance needs (e.g., healthcare, financial services) 
           typically require higher security investments.
        
        2. **Threat Landscape**: Organizations facing higher threats may need to invest more regardless of industry averages.
        
        3. **Digital Transformation**: Companies undergoing significant digital transformation often need to allocate 
           more resources to security during the transition.
        
        4. **Risk Appetite**: Your organization's risk tolerance should inform budget decisions.
        
        5. **Maturity Level**: Less mature security programs may initially require higher investment to establish 
           fundamental capabilities.
        
        ### References
        
        - Gartner IT Key Metrics Data
        - IDC Industry Spending Guides
        - Computer Economics Annual IT Spending Reports
        - Deloitte Global Security Surveys
        - Flexera State of Tech Spend Reports
        - HIMSS Healthcare Security Forum
        - EDUCAUSE Core Data Service
        """)
    
    # Footer with citation
    st.markdown("""
    ---
    **Created by Oliver Rochford** | Data Sources: Gartner, IDC, Deloitte, Flexera, HIMSS, EDUCAUSE | Last Updated: 2024
    """)

