import streamlit as st
import numpy as np
from data import INDUSTRY_PRESETS, generate_revenue_array, CHART_COLORS
from utils import create_security_budget_chart, create_budget_table, highlight_selected_revenue

def show():
    """Display the Budget Calculator page with interactive elements"""
    
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
            options=list(INDUSTRY_PRESETS.keys()) + ["Custom"],
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
            preset = INDUSTRY_PRESETS[selected_industry]
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
    
    st.header("Interactive Security Budget Calculator")
    
    # Generate revenue array for the chart
    revenue_array = generate_revenue_array(max_chart_revenue)
    
    # Layout for main content - use a 2-column layout
    main_col1, main_col2 = st.columns([2, 1])
    
    # First column - Chart and Budget Table
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
        
        # Use the updated values from session state
        # This ensures the latest values are used when the user clicks "Apply Changes"
        current_security = float(current_security)
        current_it = float(current_it)
        
        # Revenue array for bars placement
        x_positions = np.arange(len(revenue_array))
        
        # Create the chart
        fig = create_security_budget_chart(
            revenue_array=revenue_array,
            x_positions=x_positions,
            current_it=current_it,
            current_security=current_security,
            show_ranges=show_ranges,
            min_it_percentage=min_it_percentage,
            max_it_percentage=max_it_percentage,
            typical_it_percentage=typical_it_percentage,
            min_security_percentage=min_security_percentage,
            max_security_percentage=max_security_percentage,
            typical_security_percentage=typical_security_percentage,
            chart_colors=CHART_COLORS
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
        
        # Create budget table
        df = create_budget_table(revenue_array, current_it, current_security)
        
        # Apply highlight styling to the DataFrame
        styled_df = df.style.apply(highlight_selected_revenue, axis=1)
        
        # Display the styled DataFrame
        st.dataframe(
            styled_df,
            hide_index=True,
            use_container_width=True
        )
        
        # Add explanation of the table
        st.caption(f"""
        Table shows security budgets at different revenue tiers with {current_it}% IT budget.
        Your current revenue is highlighted. Security columns show budget at 5%, 10%, 15%, 20%, and your selected {current_security}% of IT budget.
        """)
        
    # Second column - Budget Controls and Analysis
    with main_col2:
        st.subheader("Budget Controls")
        st.markdown("""
        Adjust the values below to explore different budget scenarios. 
        Use this to understand how your solution's pricing aligns with typical customer budgets.
        """)
        
        # Use a form to collect all inputs before updating
        with st.form(key="budget_controls_form"):
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
                value=st.session_state.annual_revenue,
                step=50,
                help=revenue_help,
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
            )
            
            # Submit button for the form - adds a calculation
            submit_button = st.form_submit_button(label="Add Calculation")
            
            if submit_button:
                # Add the current values as a new calculation before updating current values
                st.session_state.user_calculations.append({
                    "it_percentage": st.session_state.it_percentage,
                    "security_percentage": st.session_state.security_percentage
                })
                
                # Update session state values for current selection
                st.session_state.annual_revenue = annual_revenue
                st.session_state.it_percentage = new_it_percentage
                st.session_state.security_percentage = new_security_percentage
                
                # Rerun the app to update all components
                st.rerun()

        # Create columns for the buttons to appear side by side
        button_col1, button_col2 = st.columns(2)
        
        with button_col1:
            # Add an Apply button outside the form to just update values without adding calculation
            if st.button("Apply Changes", key="apply_changes"):
                # First update the values in session state
                st.session_state.annual_revenue = annual_revenue
                st.session_state.it_percentage = new_it_percentage
                st.session_state.security_percentage = new_security_percentage
                
                # Force a complete rerun of the app to update all charts and tables
                st.rerun()
        
        with button_col2:
            # Add a button to clear all calculations
            if st.session_state.user_calculations and st.button("Clear All Calculations", key="clear_calculations"):
                st.session_state.user_calculations = []
                st.rerun()

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