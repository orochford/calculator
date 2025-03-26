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
    """
    Create the security budget chart with clear separation of trend lines.
    This function ensures proper z-index and drawing order to prevent overlap.
    """
    # Default colors if not provided
    if chart_colors is None:
        chart_colors = {
            "user_selection": "#FF5733",  # Orange
            "bar_colors": ["#008581", "#4C9C8B", "#96E4B0", "#FFDAE8"],  # Teal to pink gradient
            "lower_bound": "#008581",  # Teal
            "upper_bound": "#E4509A",  # Dark pink
            "typical": "#96E4B0",  # Mint green
            "user_calculations": ['#FFC300', '#C70039', '#900C3F', '#581845', '#2874A6']  # User calc colors
        }
    
    fig = go.Figure()
    
    # Add bar traces for percentages around the selected security percentage
    display_it_percentage = current_it
    
    # Create percentages centered around the selected value
    security_percentages = [
        max(1, current_security - 6),
        max(1, current_security - 3),
        current_security,
        min(25, current_security + 3)
    ]
    
    # Bar width configuration for clearer grouping
    bar_width = 0.15
    
    # Add the bar graphs first (lower z-index)
    for idx, percent in enumerate(security_percentages):
        # Use the same IT percentage as trend lines for consistency
        security_budget = revenue_array * (display_it_percentage / 100) * (percent / 100)
        
        # Highlight the selected percentage
        is_selected = percent == current_security
        marker_color = chart_colors["bar_colors"][idx]
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
    
    # Add trend lines in a specific order, starting with industry standards (if enabled)
    if show_ranges:
        # Lower bound trend line (lowest visual priority)
        lower_security_budget = revenue_array * (min_it_percentage / 100) * (min_security_percentage / 100)
        fig.add_trace(go.Scatter(
            x=x_positions,
            y=lower_security_budget,
            mode='lines+text',
            name=f"Lower Bound ({min_security_percentage}% of {min_it_percentage}% IT)",
            line=dict(color=chart_colors["lower_bound"], width=2, dash='dot'),
            text=[f"${y:.2f}M" for y in lower_security_budget],
            textposition='bottom right',
            textfont=dict(
                color=chart_colors["lower_bound"],
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
            x=x_positions,
            y=upper_security_budget,
            mode='lines+text',
            name=f"Upper Bound ({max_security_percentage}% of {max_it_percentage}% IT)",
            line=dict(color=chart_colors["upper_bound"], width=2, dash='dot'),
            text=[f"${y:.2f}M" for y in upper_security_budget],
            textposition='top right',
            textfont=dict(
                color=chart_colors["upper_bound"],
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
            x=x_positions,
            y=typical_security_budget,
            mode='lines+text',
            name=f"Typical ({typical_security_percentage}% of {typical_it_percentage}% IT)",
            line=dict(color=chart_colors["typical"], width=3),
            text=[f"${y:.2f}M" for y in typical_security_budget],
            textposition='middle right',
            textfont=dict(
                color=chart_colors["typical"],
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
    
    # Add saved user calculations trend lines (higher z-index than industry standards)
    for idx, calc in enumerate(st.session_state.user_calculations):
        user_it = calc['it_percentage']
        user_security = calc['security_percentage']
        color_idx = idx % len(chart_colors["user_calculations"])
        
        user_calc_budget = revenue_array * (user_it / 100) * (user_security / 100)
        fig.add_trace(go.Scatter(
            x=x_positions,
            y=user_calc_budget,
            mode='lines+text',
            name=f"User Calc #{idx+1} ({user_security}% of {user_it}% IT)",
            line=dict(
                color=chart_colors["user_calculations"][color_idx], 
                width=2.5, 
                dash='dash'
            ),
            text=[f"${y:.2f}M" for y in user_calc_budget],
            textposition='middle right',
            textfont=dict(
                color=chart_colors["user_calculations"][color_idx],
                size=10,
                family="Arial",
            ),
            hovertemplate="<b>Revenue:</b> $%{customdata}M<br>" +
                        f"<b>User Calculation #{idx+1}:</b><br>" +
                        f"IT Budget: {user_it}% of Revenue<br>" +
                        f"Security Budget: {user_security}% of IT Budget<br>" +
                        f"Final: {user_security}% of {user_it}% = {(user_it * user_security / 100):.2f}% of Revenue<br>" +
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
            size=12,  # Slightly larger font
            family="Arial",
            weight="bold",
        ),
        hovertemplate="<b>Revenue:</b> $%{customdata}M<br>" +
                    f"<b>User Selection Calculation:</b><br>" +
                    f"IT Budget: {current_it}% of Revenue<br>" +
                    f"Security Budget: {current_security}% of IT Budget<br>" +
                    f"Final: {current_security}% of {current_it}% = {(current_it * current_security / 100):.2f}% of Revenue<br>" +
                    "<b>Result:</b> $%{y:.2f}M<extra></extra>",
        customdata=revenue_array
    ))
    
    # Update layout with improved visual styling
    fig.update_layout(
        title=dict(
            text=f"Security Budget by Annual Revenue",
            y=0.99,
            x=0.5,
            xanchor='center',
            yanchor='top',
            font=dict(size=16)
        ),
        xaxis_title="Annual Revenue (Million $)",
        yaxis_title="Security Budget (Million $)",
        barmode='group',
        bargap=0.15,
        bargroupgap=0.02,
        height=700,
        width=None,
        autosize=True,
        font=dict(family="Arial", size=11),
        plot_bgcolor='white',
        margin=dict(l=80, r=80, t=150, b=100),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.98,
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
        y=0.95,
        showarrow=False,
        font=dict(size=12),
        yshift=0
    )
    
    # Configure axis formatting
    fig.update_xaxes(
        showgrid=True,
        gridcolor='lightgray',
        tickmode='array',
        tickvals=x_positions,
        ticktext=[f"${rev}M" for rev in revenue_array],
        tickangle=45,
        tickfont=dict(size=10),
        minor_showgrid=False,
        dtick=1,
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridcolor='lightgray',
        tickprefix='$',
        ticksuffix='M',
        rangemode='tozero',
        tickfont=dict(size=10),
        minor_showgrid=False,
        dtick='auto',
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