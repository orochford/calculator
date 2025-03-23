import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import base64
import io
import plotly.io as pio

# Set page layout to wide
st.set_page_config(layout="wide", menu_items=None)

# Initialize session state for syncing values between sidebar and main column
if 'it_percentage' not in st.session_state:
    st.session_state.it_percentage = 5.5
if 'security_percentage' not in st.session_state:
    st.session_state.security_percentage = 9.5

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
This app calculates your expected IT and Security budgets based on annual revenue, IT budget percentage, and security budget percentage.

Inspired by [Oliver Rochford's](https://www.linkedin.com/in/oliver-rochford/) analysis: "[Why you are probably pricing your security solution all wrong](https://www.linkedin.com/pulse/why-you-probably-pricing-your-security-solution-all-wrong-rochford/)."
''')

# Create tabs for different views
tab1, tab2 = st.tabs(["Budget Calculator", "Industry Benchmarks"])

# Tab 1: Budget Calculator
with tab1:
    # Create sidebar for settings
    with st.sidebar:
        st.header("Calculator Settings")
        st.markdown("""
        Configure your calculator settings here. Select your industry for automatic benchmarks,
        or choose 'Custom' to set your own ranges.
        """)
        
        # Industry selection with help text
        industry_help = """
        Choose your industry to automatically set typical budget ranges:
        - Financial Services: Higher IT/Security spend due to regulations
        - Healthcare: Moderate IT spend with focus on security
        - Technology: Highest IT spend across sectors
        - Manufacturing: Generally lower IT spend
        - Custom: Set your own budget ranges
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
            Set your own budget percentages based on your organization's needs.
            """)
            
            custom_it_help = """
            Set your custom IT budget percentage.
            Consider:
            - Digital transformation needs
            - Technology dependencies
            - Operational requirements
            - Industry competition
            """
            st.session_state.it_percentage = st.slider(
                "IT Budget (% of Revenue)",
                min_value=1,
                max_value=20,
                value=st.session_state.it_percentage,
                step=1,
                key="sidebar_it_slider",
                help=custom_it_help
            )
            
            custom_security_help = """
            Set your custom security budget percentage.
            Consider:
            - Threat landscape
            - Compliance requirements
            - Data sensitivity
            - Risk appetite
            - Security maturity
            """
            st.session_state.security_percentage = st.slider(
                "Security Budget (% of IT Budget)",
                min_value=1,
                max_value=25,
                value=st.session_state.security_percentage,
                step=1,
                key="sidebar_security_slider",
                help=custom_security_help
            )
            
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
                
                min_it_percentage = st.slider("Min IT Budget (%)", 1, 5, 3, help=min_it_help)
                max_it_percentage = st.slider("Max IT Budget (%)", 6, 20, 8, help=max_it_help)
                typical_it_percentage = st.slider("Typical IT Budget (%)", 
                    min_it_percentage, max_it_percentage, 
                    (min_it_percentage + max_it_percentage) // 2,
                    help=typical_it_help
                )
                
                min_security_help = "Minimum security budget percentage for conservative scenario"
                max_security_help = "Maximum security budget percentage for aggressive scenario"
                typical_security_help = "Most likely security budget percentage based on your assessment"
                
                min_security_percentage = st.slider("Min Security Budget (%)", 1, 8, 5, help=min_security_help)
                max_security_percentage = st.slider("Max Security Budget (%)", 11, 25, 15, help=max_security_help)
                typical_security_percentage = st.slider("Typical Security Budget (%)", 
                    min_security_percentage, max_security_percentage,
                    (min_security_percentage + max_security_percentage) // 2,
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
    
    # Second column - Budget Controls FIRST
    with main_col2:
        st.subheader("Budget Controls")
        st.markdown("""
        Adjust the values below to calculate IT and security budgets. 
        The chart and calculations will automatically update based on your inputs.
        """)
        
        # Get annual revenue input with help text
        revenue_help = """
        Enter your organization's annual revenue in millions of dollars. 
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

        # Display metrics
        st.metric("Annual Revenue", annual_revenue_formatted)
        st.metric("IT Budget", it_budget_formatted, f"{new_it_percentage}% of Revenue")
        st.metric("Security Budget", security_budget_formatted, f"{new_security_percentage}% of IT Budget")

        st.divider()

        # Add custom trend line control
        st.subheader("Additional Controls")
        custom_trend = st.checkbox("Add Custom Trend Line", value=False, key="custom_trend_checkbox")
        if custom_trend:
            custom_security_percentage = st.slider(
                "Custom Security Budget (%)",
                min_value=1,
                max_value=30,
                value=12,
                step=1,
                key="custom_security_percentage_slider"
            )
            custom_line_name = st.text_input("Custom Line Name", value="My Custom Budget", key="custom_line_name_input")

        st.divider()

        # Industry Context
        st.subheader("Industry Context")
        st.markdown("""
        This section shows how your selected budget percentages compare to industry standards.
        Use this information to benchmark your budget allocations against industry peers.
        """)
        
        # Add contextual information with enhanced formatting
        if selected_industry != "Custom":
            st.markdown(f"""
            ### {selected_industry}
            
            #### Industry Research Benchmarks
            - **IT Budget Range**: {min_it_percentage}% to {max_it_percentage}% of revenue
                - Typical for {selected_industry}
                - Based on industry research
            
            - **Security Budget Range**: {min_security_percentage}% to {max_security_percentage}% of IT budget
                - Typical for {selected_industry}
                - Based on security maturity level
            
            #### Your Current Settings
            - IT Budget: **{new_it_percentage:.1f}%** of revenue
                - {" Above" if new_it_percentage > typical_it_percentage else " Below"} industry typical ({typical_it_percentage}%)
            
            - Security Budget: **{new_security_percentage:.1f}%** of IT budget
                - {" Above" if new_security_percentage > typical_security_percentage else " Below"} industry typical ({typical_security_percentage}%)
            """)
        else:
            st.markdown(f"""
            ### Custom Budget Settings
            
            You have selected custom budget percentages outside of predefined industry ranges.
            Consider these factors when setting custom budgets:
            - Business objectives
            - Risk tolerance
            - Regulatory requirements
            - Technology dependencies
            
            #### Your Settings
            - IT Budget: **{new_it_percentage:.1f}%** of revenue
            - Security Budget: **{new_security_percentage:.1f}%** of IT budget
            
            {"#### Custom Ranges" if show_ranges else ""}
            {f"- IT Budget: **{min_it_percentage}% to {max_it_percentage}%**" if show_ranges else ""}
            {f"- Security Budget: **{min_security_percentage}% to {max_security_percentage}%**" if show_ranges else ""}
            """)

    # First column - Chart
    with main_col1:
        # Create the chart with enhanced description
        st.subheader("Security Budget Chart")
        st.markdown("""
        This chart visualizes security budgets across different revenue points:
        - **Grouped Bars**: Show security budgets at different percentages around your selected value
        - **Trend Lines**: Display industry typical ranges (if enabled)
        - **Hover**: Mouse over elements to see detailed values
        """)
        
        # Create the chart
        fig = go.Figure()
        
        # Add bar traces for percentages around the selected security percentage
        bar_colors = ["#008581", "#4C9C8B", "#96E4B0", "#FFDAE8"]  # New teal-to-pink gradient
        selected_security = new_security_percentage  # Use the new value
        # Create percentages centered around the selected value
        security_percentages = [
            max(1, selected_security - 6),
            max(1, selected_security - 3),
            selected_security,
            min(25, selected_security + 3)
        ]
        
        # Bar width configuration for clearer grouping
        bar_width = 0.15
        
        # Revenue array for bars placement
        x_positions = np.arange(len(revenue_array))
        
        # Always use new_it_percentage for bars
        display_it_percentage = new_it_percentage
        
        for idx, percent in enumerate(security_percentages):
            # Use the same IT percentage as trend lines for consistency
            security_budget = revenue_array * (display_it_percentage / 100) * (percent / 100)
            
            # Highlight the selected percentage
            is_selected = percent == selected_security
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

        # Add custom trend line if enabled
        if custom_trend:
            custom_security_budget = revenue_array * (new_it_percentage / 100) * (custom_security_percentage / 100)
            fig.add_trace(go.Scatter(
                x=x_positions,
                y=custom_security_budget,
                mode='lines+markers+text',
                name=custom_line_name,
                line=dict(color='rgba(128, 0, 128, 1)', width=4, dash='dot'),
                marker=dict(size=8, symbol='circle', color='rgba(128, 0, 128, 1)'),
                text=[f"${y:.2f}M" for y in custom_security_budget],
                textposition='top center',
                textfont=dict(
                    color='rgba(128, 0, 128, 1)',
                    size=11,
                    family="Arial",
                ),
                hovertemplate="<b>Revenue:</b> $%{customdata}M<br>" +
                            f"<b>Custom Security Budget ({custom_security_percentage}%):</b> $%{{y:.2f}}M<extra></extra>",
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
            text=f"IT Budget: {new_it_percentage}% of Revenue | Security Budget: {new_security_percentage}% of IT Budget",
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
            it_budget = rev * (new_it_percentage / 100)
            security_budget = it_budget * (new_security_percentage / 100)
            
            # Format numbers for table
            rev_fmt = f"${rev:,.0f}M"
            it_fmt = f"${it_budget:,.2f}M"
            sec_fmt = f"${security_budget:,.2f}M"
            
            table_data.append({
                "Annual Revenue": rev_fmt,
                "IT Budget": it_fmt,
                f"Security Budget ({new_security_percentage}% of IT)": sec_fmt
            })
        
        # Convert to DataFrame and display
        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True
        )

        st.divider()

    # Add spacer and Cyberfuturists link at the bottom
    st.markdown("""
    <br><br>
    <div style='text-align: center; padding: 20px 0;'>
        <a href='https://cyberfuturists.com' target='_blank' class='cyberfuturists-link'>
            Visit The Cyberfuturists →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Tab 2: Industry Benchmarks
with tab2:
    st.header("Industry Benchmarks")
    
    st.markdown("""
    This tab provides benchmark data on IT and security spending across different industries. 
    Use this information to compare your organization's budget allocations with industry standards.
    """)
    
    # Display industry benchmarks
    st.subheader("IT Budget as Percentage of Revenue")
    industry_it_chart_data = pd.DataFrame({
        'Industry': list(industry_presets.keys()),
        'Min IT %': [industry_presets[ind]['it_min'] for ind in industry_presets],
        'Typical IT %': [industry_presets[ind]['it_typical'] for ind in industry_presets],
        'Max IT %': [industry_presets[ind]['it_max'] for ind in industry_presets],
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
        'Industry': list(industry_presets.keys()),
        'Min Security %': [industry_presets[ind]['security_min'] for ind in industry_presets],
        'Typical Security %': [industry_presets[ind]['security_typical'] for ind in industry_presets],
        'Max Security %': [industry_presets[ind]['security_max'] for ind in industry_presets],
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
    
    # Add helpful information
    st.info("💡 **Tip**: Click the fullscreen button in the top-right corner of any chart for better viewing.")
    
    # Display industry benchmark reference table
    st.subheader("Industry Benchmark Reference Table")
    
    st.markdown("""
    | Industry | IT Budget (% of Revenue) | Security Budget (% of IT) |
    |----------|--------------------------|---------------------------|
    | Financial Services | 7-11% | 10-15% |
    | Healthcare | 4-6% | 7-10% |
    | Retail | 2-4% | 5-8% |
    | Technology | 8-15% | 10-20% |
    | Manufacturing | 2-4% | 5-10% |
    | Government/Public Sector | 5-8% | 8-12% |
    | Education | 3-6% | 5-8% |
    | Energy & Utilities | 3-5% | 6-10% |
    | Transportation & Logistics | 2-5% | 5-8% |
    | Weighted Average | 4-7% | 7-12% |
    
    *Source: Compiled from industry data from Gartner, IDC, Deloitte, Flexera*
    """)
    
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

