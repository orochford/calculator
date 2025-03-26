import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def set_custom_css():
    """Apply custom CSS for better chart rendering"""
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
        
        /* Logo container styling */
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
    """, unsafe_allow_html=True)


def display_logo():
    """Display the Cyberfuturists logo in a dark theme container"""
    st.markdown("""
    <div class="logo-container">
        <img src="https://img1.wsimg.com/isteam/ip/fc53e870-07e8-482a-a411-787d4ae0464d/Cyber%20Futurists%20LinkedIn%20Career%20Page%20Banner%20(1.png/:/rs=w:984,h:167" alt="Cyberfuturists Logo">
    </div>
    """, unsafe_allow_html=True)


def create_security_budget_chart(revenue_array, x_positions, current_it, current_security, 
                              show_ranges=False, min_it_percentage=0, max_it_percentage=0,
                              typical_it_percentage=0, min_security_percentage=0, 
                              max_security_percentage=0, typical_security_percentage=0,
                              chart_colors=None):
    """Create a scatter plot showing security budget calculations"""
    if chart_colors is None:
        chart_colors = {
            "user_selection": "#FF4B4B",
            "typical": "#1F77B4",
            "min": "#2CA02C",
            "max": "#FF7F0E",
            "range": "rgba(31, 119, 180, 0.1)"
        }
    
    fig = go.Figure()
    
    # Add range area if show_ranges is True
    if show_ranges:
        min_budget = revenue_array * (min_it_percentage / 100) * (min_security_percentage / 100)
        max_budget = revenue_array * (max_it_percentage / 100) * (max_security_percentage / 100)
        
        fig.add_trace(go.Scatter(
            x=x_positions,
            y=max_budget,
            fill=None,
            mode='lines',
            line=dict(color=chart_colors["range"], width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=x_positions,
            y=min_budget,
            fill='tonexty',
            mode='lines',
            line=dict(color=chart_colors["range"], width=0),
            name='Typical Range',
            hoverinfo='skip'
        ))
    
    # Add typical line
    typical_budget = revenue_array * (typical_it_percentage / 100) * (typical_security_percentage / 100)
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=typical_budget,
        mode='lines+text',
        name=f"Typical ({typical_security_percentage}% of {typical_it_percentage}% IT)",
        line=dict(color=chart_colors["typical"], width=2, dash='dash'),
        text=[f"${y:.2f}M" for y in typical_budget],
        textposition='middle right',
        textfont=dict(
            color=chart_colors["typical"],
            size=10,
            family="Arial"
        ),
        hovertemplate="<b>Revenue:</b> $%{customdata}M<br>" +
                    f"<b>Typical Calculation:</b><br>" +
                    f"IT Budget: {typical_it_percentage}% of Revenue<br>" +
                    f"Security Budget: {typical_security_percentage}% of IT Budget<br>" +
                    f"Final: {typical_security_percentage}% of {typical_it_percentage}% = {(typical_it_percentage * typical_security_percentage / 100):.2f}% of Revenue<br>" +
                    "<b>Result:</b> $%{y:.2f}M<extra></extra>",
        customdata=revenue_array
    ))
    
    # Add current user selection line LAST to ensure it's on top (highest z-index)
    current_security_budget = revenue_array * (current_it / 100) * (current_security / 100)
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=current_security_budget,
        mode='lines+text',
        name=f"User Selection ({current_security}% of {current_it}% IT)",
        line=dict(color=chart_colors["user_selection"], width=4, dash='solid'),  # Thicker for emphasis
        text=[f"${y:.2f}M" for y in current_security_budget],
        textposition='middle right',
        textfont=dict(
            color=chart_colors["user_selection"],
            size=12,
            family="Arial"
        ),
        hovertemplate="<b>Revenue:</b> $%{customdata}M<br>" +
                    f"<b>User Selection Calculation:</b><br>" +
                    f"IT Budget: {current_it}% of Revenue<br>" +
                    f"Security Budget: {current_security}% of IT Budget<br>" +
                    f"Final: {current_security}% of {current_it}% = {(current_it * current_security / 100):.2f}% of Revenue<br>" +
                    "<b>Result:</b> $%{y:.2f}M<extra></extra>",
        customdata=revenue_array
    ))
    
    # Update layout
    fig.update_layout(
        title="Security Budget by Revenue",
        xaxis_title="Revenue (Millions)",
        yaxis_title="Security Budget (Millions)",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        hovermode='closest'
    )
    
    return fig


def create_budget_table(revenue_array, current_it, current_security):
    """Create a budget breakdown table with standard and user-defined security percentages"""
    table_data = []
    
    # Define standard security percentages to show
    standard_security_percentages = [5, 10, 15, 20]
    
    # Use revenue array for revenue tiers
    for rev in revenue_array:
        if rev > 0:  # Prevent division by zero
            row_data = {"Annual Revenue": f"${rev:,.0f}M"}
            
            # Calculate IT budget
            it_budget = rev * (current_it / 100)
            row_data["IT Budget (%)"] = f"{current_it}%"
            
            # Add standard security percentage columns
            for sec_percent in standard_security_percentages:
                security_budget = it_budget * (sec_percent / 100)
                row_data[f"{sec_percent}% of IT"] = f"${security_budget:,.2f}M"
            
            # Add current user-defined security budget if not already in standard percentages
            if current_security not in standard_security_percentages:
                security_budget = it_budget * (current_security / 100)
                row_data[f"User ({current_security}% of IT)"] = f"${security_budget:,.2f}M"
            
            # Add user calculations in separate columns - always use the saved percentages for these
            for idx, calc in enumerate(st.session_state.user_calculations):
                user_it = calc['it_percentage']
                user_security = calc['security_percentage']
                
                # Calculate at current revenue with saved IT/Security percentages
                user_it_budget = rev * (user_it / 100)
                user_security_budget = user_it_budget * (user_security / 100)
                row_data[f"Calc #{idx+1} ({user_security}% of {user_it}% IT)"] = f"${user_security_budget:,.2f}M"
            
            table_data.append(row_data)
    
    # Convert to DataFrame
    return pd.DataFrame(table_data)


def highlight_selected_revenue(row):
    """Highlight the row closest to the selected annual revenue"""
    target_rev = float(st.session_state.annual_revenue)
    current_rev = float(row['Annual Revenue'].replace('$', '').replace('M', '').replace(',', ''))
    if abs(current_rev - target_rev) < 50:  # Within 50M of target
        return ['background-color: #e6f3ff'] * len(row)
    return [''] * len(row) 