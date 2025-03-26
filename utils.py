import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np


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
    """Create a mixed bar and line chart showing security budget calculations"""
    if chart_colors is None:
        chart_colors = {
            "user_selection": "#FF5733",
            "bar_colors": ["#008581", "#4C9C8B", "#96E4B0", "#FFDAE8"],
            "lower_bound": "#008581",
            "upper_bound": "#E4509A",
            "typical": "#96E4B0",
            "range": "rgba(31, 119, 180, 0.1)"
        }
    
    fig = go.Figure()
    
    # Use the typical IT percentage for all security budget tiers
    it_percentage = typical_it_percentage
    
    # Calculate security budget values for different tiers (5%, 10%, 15%, 20%)
    security_5pct = revenue_array * (it_percentage / 100) * (5 / 100)
    security_10pct = revenue_array * (it_percentage / 100) * (10 / 100)
    security_15pct = revenue_array * (it_percentage / 100) * (15 / 100)
    security_20pct = revenue_array * (it_percentage / 100) * (20 / 100)
    
    # User selection
    user_budget = revenue_array * (current_it / 100) * (current_security / 100)
    
    # Calculate lower and upper bounds for trend lines
    lower_bound = revenue_array * (min_it_percentage / 100) * (min_security_percentage / 100)
    upper_bound = revenue_array * (max_it_percentage / 100) * (max_security_percentage / 100)
    typical_line = revenue_array * (typical_it_percentage / 100) * (typical_security_percentage / 100)
    
    # Add bars for different security budget tiers using go.Bar directly
    fig.add_trace(go.Bar(
        name=f"5% of IT Budget ({it_percentage}% IT)",
        x=revenue_array,
        y=security_5pct,
        marker_color=chart_colors["bar_colors"][0],
        hovertemplate="<b>Revenue:</b> $%{x}M<br>" +
                    f"<b>IT:</b> {it_percentage}%<br>" +
                    "<b>Security:</b> 5% of IT<br>" +
                    "<b>Budget:</b> $%{y:.2f}M<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        name=f"10% of IT Budget ({it_percentage}% IT)",
        x=revenue_array,
        y=security_10pct,
        marker_color=chart_colors["bar_colors"][1],
        hovertemplate="<b>Revenue:</b> $%{x}M<br>" +
                    f"<b>IT:</b> {it_percentage}%<br>" +
                    "<b>Security:</b> 10% of IT<br>" +
                    "<b>Budget:</b> $%{y:.2f}M<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        name=f"15% of IT Budget ({it_percentage}% IT)",
        x=revenue_array,
        y=security_15pct,
        marker_color=chart_colors["bar_colors"][2],
        hovertemplate="<b>Revenue:</b> $%{x}M<br>" +
                    f"<b>IT:</b> {it_percentage}%<br>" +
                    "<b>Security:</b> 15% of IT<br>" +
                    "<b>Budget:</b> $%{y:.2f}M<extra></extra>"
    ))
    
    fig.add_trace(go.Bar(
        name=f"20% of IT Budget ({it_percentage}% IT)",
        x=revenue_array,
        y=security_20pct,
        marker_color=chart_colors["bar_colors"][3],
        hovertemplate="<b>Revenue:</b> $%{x}M<br>" +
                    f"<b>IT:</b> {it_percentage}%<br>" +
                    "<b>Security:</b> 20% of IT<br>" +
                    "<b>Budget:</b> $%{y:.2f}M<extra></extra>"
    ))
    
    # Add trend lines
    if show_ranges:
        # Lower bound line
        fig.add_trace(go.Scatter(
            x=revenue_array,
            y=lower_bound,
            mode='lines',
            line=dict(color=chart_colors["lower_bound"], width=2, dash='dot'),
            name=f'Lower Bound ({min_security_percentage}% of {min_it_percentage}% IT)',
            hovertemplate="<b>Revenue:</b> $%{x}M<br>" +
                        "<b>Lower Bound:</b> $%{y:.2f}M<extra></extra>"
        ))
        
        # Upper bound line
        fig.add_trace(go.Scatter(
            x=revenue_array,
            y=upper_bound,
            mode='lines',
            line=dict(color=chart_colors["upper_bound"], width=2, dash='dot'),
            name=f'Upper Bound ({max_security_percentage}% of {max_it_percentage}% IT)',
            hovertemplate="<b>Revenue:</b> $%{x}M<br>" +
                        "<b>Upper Bound:</b> $%{y:.2f}M<extra></extra>"
        ))
    
    # Add typical line
    fig.add_trace(go.Scatter(
        x=revenue_array,
        y=typical_line,
        mode='lines',
        name=f"Typical ({typical_security_percentage}% of {typical_it_percentage}% IT)",
        line=dict(color=chart_colors["typical"], width=2),
        hovertemplate="<b>Revenue:</b> $%{x}M<br>" +
                    "<b>Typical:</b> $%{y:.2f}M<extra></extra>"
    ))
    
    # Add current user selection line
    fig.add_trace(go.Scatter(
        x=revenue_array,
        y=user_budget,
        mode='lines+markers',
        name=f"Your Selection ({current_security}% of {current_it}% IT)",
        line=dict(color=chart_colors["user_selection"], width=3),
        marker=dict(size=8, symbol='circle'),
        hovertemplate="<b>Revenue:</b> $%{x}M<br>" +
                    "<b>Your Selection:</b> $%{y:.2f}M<br>" +
                    f"IT Budget: {current_it}% of Revenue<br>" +
                    f"Security Budget: {current_security}% of IT Budget<extra></extra>"
    ))
    
    # Update layout with proper bar settings
    fig.update_layout(
        title="Security Budget by Annual Revenue",
        xaxis_title="Annual Revenue (Million $)",
        yaxis_title="Security Budget (Million $)",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font=dict(size=10)
        ),
        hovermode='closest',
        height=500,
        margin=dict(l=60, r=40, t=80, b=60),
        barmode='group',  # Use group mode for side-by-side bars
        bargap=0.15,      # Gap between bars of adjacent location coordinates
        bargroupgap=0.1   # Gap between bars of the same location coordinates
    )
    
    # Make the bars wider by reducing the number of bar groups
    fig.update_layout(
        bargap=0.05,      # Reduce gap between bar groups
        bargroupgap=0.05  # Reduce gap within bar groups
    )
    
    # Add a subtitle with the current settings
    fig.add_annotation(
        text=f"IT Budget: {current_it}% of Revenue | Security Budget: {current_security}% of IT Budget",
        xref="paper", yref="paper",
        x=0.5, y=1.05,
        showarrow=False,
        font=dict(size=12)
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