import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data import (
    INDUSTRY_IT_SPEND,
    INDUSTRY_SECURITY_SPEND,
    NAICS_REVENUE_TIERS,
    NAICS_SECTORS,
    REVENUE_TIERS,
    REVENUE_TIER_COUNTS
)

# Load NAICS Data
@st.cache_data
def load_naics_data():
    """Create a DataFrame from the NAICS sectors and revenue tiers"""
    # Create expanded data for each NAICS sector across revenue tiers
    expanded_data = []
    
    for sector in NAICS_SECTORS:
        # Distribute the companies across revenue tiers based on overall distribution
        total_companies = sum(REVENUE_TIER_COUNTS.values())
        
        for low, high in REVENUE_TIERS:
            # Get the count for this tier
            tier_count = REVENUE_TIER_COUNTS[(low, high)]
            # Calculate the sector's proportion of companies in this tier
            sector_count = round(tier_count / len(NAICS_SECTORS))  # Evenly distribute across sectors
            
            if sector_count > 0:
                expanded_data.append({
                    "NAICS Code": sector["code"],
                    "NAICS Name": sector["name"],
                    "Sales ($Mil) Low": low,
                    "Sales ($Mil) High": high if high != float('inf') else 100000,
                    "Company Count": sector_count
                })
    
    # Create DataFrame
    df = pd.DataFrame(expanded_data)
    return df

def show():
    st.header("NAICS Industry Analysis")
    st.markdown("""
    This tab shows the distribution of businesses by revenue tier based on NAICS industry codes and official business statistics.
    Select one or more NAICS codes to see how many potential customers exist in each revenue range.
    
    Note: The analysis includes 1,935,963 uncoded records which are shown in the total but excluded from revenue-based calculations.
    
    Data source: [NAICS Business Counts by Company Size](https://www.naics.com/business-lists/counts-by-company-size/)
    """)

    # Load NAICS data
    naics_df = load_naics_data()

    # Create columns for the two analyses
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("NAICS Revenue Distribution")
        # Create a DataFrame from the NAICS revenue tiers
        naics_tiers_df = pd.DataFrame({
            "Revenue Range": NAICS_REVENUE_TIERS.keys(),
            "Number of Businesses": NAICS_REVENUE_TIERS.values()
        })

        # Calculate total businesses
        total_businesses = naics_tiers_df["Number of Businesses"].sum()
        coded_businesses = total_businesses - NAICS_REVENUE_TIERS["Uncoded records"]
        
        # Add percentage column (excluding uncoded records from percentage calculation)
        naics_tiers_df["Percentage"] = naics_tiers_df.apply(
            lambda row: (row["Number of Businesses"] / coded_businesses * 100).round(2) 
            if row["Revenue Range"] != "Uncoded records" else 0, 
            axis=1
        )
        
        # Display metrics
        col1_metrics, col2_metrics = st.columns(2)
        with col1_metrics:
            st.metric("Total U.S. Businesses", f"{total_businesses:,.0f}")
        with col2_metrics:
            st.metric("Coded Businesses", f"{coded_businesses:,.0f}")
        
        # Create bar chart (excluding uncoded records)
        fig_naics = go.Figure()
        
        # Filter out uncoded records for the chart
        chart_df = naics_tiers_df[naics_tiers_df["Revenue Range"] != "Uncoded records"]
        
        # Add bars
        fig_naics.add_trace(go.Bar(
            x=chart_df["Revenue Range"],
            y=chart_df["Number of Businesses"],
            text=chart_df["Number of Businesses"].apply(lambda x: f"{x:,.0f}"),
            textposition="outside",
            marker_color="rgba(60, 120, 216, 0.7)",
            name="Number of Businesses"
        ))
        
        # Update layout
        fig_naics.update_layout(
            title="U.S. Business Distribution by Revenue Tier",
            xaxis_title="Annual Revenue Range",
            yaxis_title="Number of Businesses",
            height=500,
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            showlegend=False,
            margin=dict(t=50, b=100)  # Increase bottom margin for rotated labels
        )
        
        # Rotate x-axis labels for better readability
        fig_naics.update_xaxes(
            tickangle=45,
            tickfont=dict(size=10)
        )
        
        # Use log scale for y-axis due to large range
        fig_naics.update_yaxes(type="log")
        
        st.plotly_chart(fig_naics, use_container_width=True)
        
        # Display the data table
        st.dataframe(
            naics_tiers_df.style.format({
                "Number of Businesses": "{:,.0f}",
                "Percentage": "{:.2f}%"
            }),
            use_container_width=True
        )

    with col2:
        st.subheader("Industry-Specific Analysis")
        
        # Create options combining code and name
        naics_options = [f"{sector['code']} - {sector['name']}" for sector in NAICS_SECTORS]
        
        # Store current selection in session state to handle the logic
        if 'naics_selection' not in st.session_state:
            st.session_state.naics_selection = ["All"]
        
        # Use multiselect instead of selectbox
        selected_naics_options = st.multiselect(
            "Select NAICS Industry Code(s)",
            options=["All"] + sorted(naics_options),
            default=st.session_state.naics_selection,
            help="Select 'All' to include all industries, or select specific industries."
        )
        
        # Update the session state
        st.session_state.naics_selection = selected_naics_options
        
        # Handle the multiselect logic
        if "All" in selected_naics_options and len(selected_naics_options) > 1:
            # If All is selected along with other options, prioritize the specific selections
            selected_naics_options.remove("All")
            st.session_state.naics_selection = selected_naics_options
        
        # Handle empty selection (fallback to All)
        if not selected_naics_options:
            selected_naics_options = ["All"]
            st.session_state.naics_selection = ["All"]
        
        # Convert the selections to NAICS codes for filtering
        if "All" in selected_naics_options:
            selected_naics = "All"
        else:
            # Extract just the codes from the selections (split on first " - ")
            selected_naics = [option.split(" - ")[0] for option in selected_naics_options]
            
        # Filter NAICS data based on selection
        if selected_naics != "All":
            if isinstance(selected_naics, list):
                # Filter for multiple selected NAICS codes
                naics_df_filtered = naics_df[naics_df["NAICS Code"].isin(selected_naics)]
            else:
                # Single NAICS code
                naics_df_filtered = naics_df[naics_df["NAICS Code"] == selected_naics]
        else:
            naics_df_filtered = naics_df.copy()
        
        # Display industry names for selected NAICS codes
        if selected_naics == "All":
            st.subheader("Analysis for all industries")
        else:
            industry_names = []
            for code in selected_naics:
                name_matches = naics_df[naics_df["NAICS Code"] == code]["NAICS Name"]
                if len(name_matches) > 0:
                    industry_names.append(f"{code} - {name_matches.iloc[0]}")
                else:
                    industry_names.append(code)
            
            st.subheader(f"Analysis for selected industries: {', '.join(industry_names)}")
        
        # Group by revenue tiers and calculate totals
        revenue_tiers = REVENUE_TIERS

        # Format revenue range for display
        def format_revenue_range(low, high):
            if low >= 1000:
                low_str = f"${low/1000:.1f}B"
            else:
                low_str = f"${low}M"
                
            if high == float('inf'):
                high_str = "+"
            elif high >= 1000:
                high_str = f"${high/1000:.1f}B"
            else:
                high_str = f"${high}M"
                
            return f"{low_str} - {high_str}"
            
        # Create dataframe for the table
        tier_analysis = []
        
        for low, high in revenue_tiers:
            # Get the actual company count for this tier
            company_count = REVENUE_TIER_COUNTS[(low, high)]
            
            # Calculate average revenue for TAM estimation
            if high == float('inf'):
                # For 1B+ companies, use a conservative estimate of 1.5B average
                avg_revenue = 1500  # $1.5B in millions
            else:
                avg_revenue = (low + high) / 2
            
            # Calculate IT budget based on weighted average
            avg_it_budget_pct = INDUSTRY_IT_SPEND["Weighted Average"]["typical"] / 100
            avg_security_pct = INDUSTRY_SECURITY_SPEND["Weighted Average"]["typical"] / 100
            
            # Calculate TAM for this tier
            it_budget_tam = avg_revenue * avg_it_budget_pct * company_count
            security_tam = it_budget_tam * avg_security_pct
            
            tier_analysis.append({
                "Revenue Tier": format_revenue_range(low, high),
                "Number of Companies": int(company_count),
                "Average Revenue ($M)": avg_revenue,
                "IT Budget TAM ($M)": it_budget_tam,
                "Security TAM ($M)": security_tam
            })
        
        # Create the DataFrame
        tier_df = pd.DataFrame(tier_analysis)
        
        # Calculate totals
        total_companies = tier_df["Number of Companies"].sum()
        total_it_tam = tier_df["IT Budget TAM ($M)"].sum()
        total_security_tam = tier_df["Security TAM ($M)"].sum()
        
        # Format values for display
        tier_df["Average Revenue ($M)"] = tier_df["Average Revenue ($M)"].apply(
            lambda x: f"${x:.1f}M" if x < 1000 else f"${x/1000:.1f}B"
        )
        tier_df["IT Budget TAM ($M)"] = tier_df["IT Budget TAM ($M)"].apply(
            lambda x: f"${x:.1f}M" if x < 1000 else f"${x/1000:.1f}B"
        )
        tier_df["Security TAM ($M)"] = tier_df["Security TAM ($M)"].apply(
            lambda x: f"${x:.1f}M" if x < 1000 else f"${x/1000:.1f}B"
        )
        
        # Add TAM metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Companies", f"{total_companies:,.0f}")
        with col2:
            it_tam_display = f"${total_it_tam:.1f}M" if total_it_tam < 1000 else f"${total_it_tam/1000:.1f}B"
            st.metric("Total IT Budget TAM", it_tam_display)
        with col3:
            security_tam_display = f"${total_security_tam:.1f}M" if total_security_tam < 1000 else f"${total_security_tam/1000:.1f}B"
            st.metric("Total Security TAM", security_tam_display)
        
        # Show the table
        st.subheader("Business Count by Revenue Tier (NAICS Standard Ranges)")
        st.dataframe(tier_df, use_container_width=True)
        
        # Create chart for visualization
        st.subheader("Distribution of Companies and TAM by Revenue Tier")
        
        # Prepare data for chart
        chart_data = tier_df.copy()
        chart_data["Revenue Tier"] = pd.Categorical(chart_data["Revenue Tier"], categories=chart_data["Revenue Tier"].tolist())
        
        # Convert formatted budget strings back to numeric for bubble sizing
        chart_data["IT Budget TAM Numeric"] = chart_data["IT Budget TAM ($M)"].apply(
            lambda x: float(x.replace("$", "").replace("M", "")) if "M" in x 
            else float(x.replace("$", "").replace("B", "")) * 1000
        )
        
        chart_data["Security TAM Numeric"] = chart_data["Security TAM ($M)"].apply(
            lambda x: float(x.replace("$", "").replace("M", "")) if "M" in x 
            else float(x.replace("$", "").replace("B", "")) * 1000
        )
        
        # Create scatter plot with bubbles
        fig = go.Figure()

        # Calculate bubble sizes using sqrt scale for better visual representation
        max_it_tam = chart_data["IT Budget TAM Numeric"].max()
        max_sec_tam = chart_data["Security TAM Numeric"].max()
        
        chart_data["IT Bubble Size"] = chart_data["IT Budget TAM Numeric"].apply(
            lambda x: 40 + (60 * np.sqrt(x) / np.sqrt(max_it_tam)) if x > 0 else 20
        )
        chart_data["Security Bubble Size"] = chart_data["Security TAM Numeric"].apply(
            lambda x: 30 + (50 * np.sqrt(x) / np.sqrt(max_sec_tam)) if x > 0 else 15
        )

        # Create y-axis positions for staggered layout
        y_positions = np.arange(len(chart_data)) * 2  # Multiply by 2 for more spacing

        # Add IT TAM bubbles
        fig.add_trace(go.Scatter(
            x=chart_data["Revenue Tier"],
            y=y_positions,
            mode="markers+text",
            name="IT Budget TAM",
            marker=dict(
                size=chart_data["IT Bubble Size"],
                color="rgba(65, 171, 93, 0.8)",
                line=dict(width=2, color="rgba(65, 171, 93, 1)"),
                symbol="circle",
            ),
            text=chart_data["IT Budget TAM ($M)"],
            textposition="middle center",
            textfont=dict(
                size=11,
                color="black",
                family="Arial"
            ),
            hovertemplate="<b>%{x}</b><br>" +
                         "IT TAM: %{text}<br>" +
                         "Companies: %{customdata:,.0f}<extra></extra>",
            customdata=chart_data["Number of Companies"]
        ))

        # Add Security TAM bubbles
        fig.add_trace(go.Scatter(
            x=chart_data["Revenue Tier"],
            y=y_positions + 0.7,  # Offset for staggered appearance
            mode="markers+text",
            name="Security TAM",
            marker=dict(
                size=chart_data["Security Bubble Size"],
                color="rgba(251, 180, 76, 0.8)",
                line=dict(width=2, color="rgba(251, 180, 76, 1)"),
                symbol="circle",
            ),
            text=chart_data["Security TAM ($M)"],
            textposition="middle center",
            textfont=dict(
                size=10,
                color="black",
                family="Arial"
            ),
            hovertemplate="<b>%{x}</b><br>" +
                         "Security TAM: %{text}<br>" +
                         "Companies: %{customdata:,.0f}<extra></extra>",
            customdata=chart_data["Number of Companies"]
        ))

        # Add company count as text
        fig.add_trace(go.Scatter(
            x=chart_data["Revenue Tier"],
            y=y_positions + 0.35,  # Center between bubbles
            mode="text",
            text=chart_data["Number of Companies"].apply(lambda x: f"{x:,.0f} companies"),
            textposition="middle right",
            textfont=dict(
                size=10,
                color="rgba(0,0,0,0.6)",
                family="Arial"
            ),
            showlegend=False,
            hoverinfo="skip"
        ))
        
        # Update layout for better readability
        fig.update_layout(
            title=dict(
                text="TAM Analysis by Revenue Tier",
                font=dict(size=16, family="Arial")
            ),
            xaxis=dict(
                title="Revenue Range",
                showgrid=True,
                gridcolor="rgba(0,0,0,0.1)"
            ),
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False
            ),
            height=700,
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor="white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12)
            ),
            margin=dict(t=80, b=60, l=40, r=40)
        )

        # Add annotation explaining the bubbles
        fig.add_annotation(
            text="Bubble size represents relative TAM value",
            xref="paper",
            yref="paper",
            x=0.01,
            y=0.99,
            showarrow=False,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="rgba(0, 0, 0, 0.5)",
            borderwidth=1,
            borderpad=4,
            font=dict(size=12, family="Arial")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.markdown(f"""
        ### Understanding the Analysis
        
        - **Revenue Tier**: Standard NAICS revenue ranges for companies
        - **Number of Companies**: Count of companies in this revenue tier
        - **Average Revenue**: Midpoint of the revenue range (for TAM calculations)
        - **IT Budget TAM**: Total Addressable Market for IT budget (based on weighted average IT spend %)
        - **Security TAM**: Total Addressable Market for security budget (based on weighted average security spend %)
        
        TAM calculations use industry averages of:
        - IT Budget: {INDUSTRY_IT_SPEND["Weighted Average"]["typical"]}% of revenue
        - Security Budget: {INDUSTRY_SECURITY_SPEND["Weighted Average"]["typical"]}% of IT budget
        """) 