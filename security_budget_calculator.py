import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import base64
import io

# Set page layout to wide
st.set_page_config(layout="wide")

# Define industry-specific IT budget percentages based on updated industry data
INDUSTRY_IT_SPEND = {
    "Financial Services": {"min": 7, "max": 11, "typical": 9.0},
    "Healthcare": {"min": 4, "max": 6, "typical": 5.0},
    "Retail": {"min": 2, "max": 4, "typical": 3.0},
    "Technology": {"min": 8, "max": 15, "typical": 11.5},
    "Manufacturing": {"min": 2, "max": 4, "typical": 3.0},
    "Government/Public Sector": {"min": 5, "max": 8, "typical": 6.5},
    "Education": {"min": 3, "max": 6, "typical": 4.5},
    "Energy & Utilities": {"min": 3, "max": 5, "typical": 4.0},
    "Transportation & Logistics": {"min": 2, "max": 5, "typical": 3.5},
    "Weighted Average": {"min": 4, "max": 7, "typical": 5.5},
    "Custom": None  # For user-defined values
}

# Define industry-specific security budget percentages (as % of IT spend)
INDUSTRY_SECURITY_SPEND = {
    "Financial Services": {"min": 10, "max": 15, "typical": 12.5},
    "Healthcare": {"min": 7, "max": 10, "typical": 8.5},
    "Retail": {"min": 5, "max": 8, "typical": 6.5},
    "Technology": {"min": 10, "max": 20, "typical": 15.0},
    "Manufacturing": {"min": 5, "max": 10, "typical": 7.5},
    "Government/Public Sector": {"min": 8, "max": 12, "typical": 10.0},
    "Education": {"min": 5, "max": 8, "typical": 6.5},
    "Energy & Utilities": {"min": 6, "max": 10, "typical": 8.0},
    "Transportation & Logistics": {"min": 5, "max": 8, "typical": 6.5},
    "Weighted Average": {"min": 7, "max": 12, "typical": 9.5},
    "Custom": None  # For user-defined values
}

# Define NAICS revenue tiers data
NAICS_REVENUE_TIERS = {
    "Under 500,000": 13918257,
    "500,000 - 999,999": 792624,
    "1,000,000 - 2,499,999": 546969,
    "2,500,000 - 4,999,999": 222344,
    "5,000,000 - 9,999,999": 144641,
    "10,000,000 - 99,999,999": 176000,
    "100,000,000 - 499,999,999": 23670,
    "500,000,000 - 999,999,999": 4070,
    "1,000,000,000+": 5161,
    "Uncoded records": 1935963
}

# Load NAICS Data
@st.cache_data
def load_naics_data():
    # Load the correct sheet as specified by user
    df = pd.read_excel("usbusinesses.xlsx", sheet_name="AnnualSales-Jan-2024")
    
    # Columns are specified by the user:
    # - NAICS codes in column A
    # - NAICS names in column B
    # - Count of firms by revenue tier in columns C to L
    # - Total count in column M
    
    # Rename columns based on position
    columns = df.columns.tolist()
    column_rename = {}
    
    # First two columns are NAICS Code and NAICS Name
    if len(columns) >= 2:
        column_rename[columns[0]] = "NAICS Code"
        column_rename[columns[1]] = "NAICS Name"
    
    # Apply column renaming
    df = df.rename(columns=column_rename)
    
    # Create revenue tier dataframes for each range
    # Define the revenue ranges for each tier (columns C to L)
    revenue_tiers = [
        (0, 50),      # Column C: $0-50M
        (50, 100),    # Column D: $50-100M 
        (100, 250),   # Column E: $100-250M
        (250, 500),   # Column F: $250-500M
        (500, 1000),  # Column G: $500M-1B
        (1000, 2500), # Column H: $1-2.5B
        (2500, 5000), # Column I: $2.5-5B
        (5000, 10000), # Column J: $5-10B
        (10000, 50000), # Column K: $10-50B
        (50000, 100000) # Column L: $50B+
    ]
    
    # Create a list to store the expanded data
    expanded_data = []
    
    # Process each row
    for _, row in df.iterrows():
        naics_code = row["NAICS Code"]
        naics_name = row["NAICS Name"]
        
        # Columns C to L contain firm counts by revenue tier
        tier_cols = columns[2:12] if len(columns) >= 12 else columns[2:]
        
        # For each tier, create a row with the count, low and high revenue
        for i, tier_col in enumerate(tier_cols):
            if i < len(revenue_tiers):
                low, high = revenue_tiers[i]
                count = row[tier_col] if not pd.isna(row[tier_col]) else 0
                
                # Convert count to numeric before comparison
                try:
                    count = float(count) if count != '' else 0
                except (ValueError, TypeError):
                    count = 0
                    
                # Only add rows with counts > 0
                if count > 0:
                    expanded_data.append({
                        "NAICS Code": naics_code,
                        "NAICS Name": naics_name,
                        "Sales ($Mil) Low": low,
                        "Sales ($Mil) High": high,
                        "Company Count": count
                    })
    
    # Create new dataframe with the expanded data
    expanded_df = pd.DataFrame(expanded_data)
    
    # If no data was created, create a simple fallback dataframe
    if len(expanded_df) == 0:
        st.warning("No valid data found in the spreadsheet. Using default data for demonstration.")
        expanded_df = pd.DataFrame({
            "NAICS Code": ["Default"],
            "NAICS Name": ["Default Industry"],
            "Sales ($Mil) Low": [0],
            "Sales ($Mil) High": [1000],
            "Company Count": [100]
        })
    
    return expanded_df

naics_df = load_naics_data()

# Title and description
st.title('Security Budget Calculator')
st.markdown('''
This app calculates your expected IT and Security budgets based on annual revenue, IT budget percentage, and security budget percentage.

Inspired by Oliver Rochford's analysis: "Why you are probably pricing your security solution all wrong."
''')

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["Budget Calculator", "Industry Benchmarks", "NAICS Analysis", "Sector TAM Analysis"])

with tab2:
    # Display IT spend by industry chart
    st.subheader("IT Spend by Industry (% of revenue)")
    
    # Create a DataFrame for IT spend benchmarks
    it_spend_data = []
    for industry, values in INDUSTRY_IT_SPEND.items():
        if industry != "Custom":
            it_spend_data.append({
                "Industry": industry,
                "Min (%)": values["min"],
                "Typical (%)": values["typical"],
                "Max (%)": values["max"]
            })
    
    it_spend_df = pd.DataFrame(it_spend_data)
    it_spend_df = it_spend_df.sort_values("Typical (%)", ascending=True)
    
    # Create bar chart for IT spend
    fig_it_spend = go.Figure()
    
    # Add range bars
    for i, row in it_spend_df.iterrows():
        fig_it_spend.add_trace(go.Bar(
            y=[row["Industry"]],
            x=[row["Max (%)"] - row["Min (%)"]],
            base=[row["Min (%)"]],
            orientation='h',
            name=row["Industry"],
            showlegend=False,
            marker=dict(
                color='rgba(173, 216, 230, 0.7)',
                line=dict(color='rgba(73, 116, 230, 1.0)', width=1)
            ),
            hovertemplate=f"<b>{row['Industry']}</b><br>Range: {row['Min (%)']}%-{row['Max (%)']}%<br>Typical: {row['Typical (%)']}%<extra></extra>"
        ))
        
        # Add markers for typical value
        fig_it_spend.add_trace(go.Scatter(
            y=[row["Industry"]],
            x=[row["Typical (%)"]],
            mode='markers',
            marker=dict(symbol='diamond', size=10, color='rgba(55, 83, 109, 1)'),
            name=f"{row['Industry']} (Typical)",
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Update layout
    fig_it_spend.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(240, 240, 240, 0.8)',
        xaxis=dict(
            title=dict(text="IT Spend (% of Revenue)", font=dict(size=14)),
            tickfont=dict(size=12),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211, 211, 211, 0.5)',
            showline=True,
            linewidth=1,
            linecolor='rgba(211, 211, 211, 1)'
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=12),
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='rgba(211, 211, 211, 1)'
        ),
        bargap=0.3
    )
    
    # Add annotations for min, typical, max
    fig_it_spend.add_annotation(
        x=0,
        y=1.05,
        xref="paper",
        yref="paper",
        text="Range: Min-Max, Diamond: Typical Value",
        showarrow=False,
        font=dict(size=12)
    )
    
    st.plotly_chart(fig_it_spend, use_container_width=True)
    st.caption("Sources: Gartner, IDC, Deloitte, Computer Economics, Flexera, HIMSS, EDUCAUSE")
    
    # Display Security spend as % of IT budget
    st.subheader("Security Budget by Industry (% of IT Budget)")
    
    # Create a DataFrame for security spend benchmarks
    security_data = []
    for industry, values in INDUSTRY_SECURITY_SPEND.items():
        if industry != "Custom":
            security_data.append({
                "Industry": industry,
                "Min (%)": values["min"],
                "Typical (%)": values["typical"],
                "Max (%)": values["max"]
            })
    
    security_df = pd.DataFrame(security_data)
    security_df = security_df.sort_values("Typical (%)", ascending=True)
    
    # Create bar chart for security spend
    fig_security = go.Figure()
    
    # Add range bars
    for i, row in security_df.iterrows():
        fig_security.add_trace(go.Bar(
            y=[row["Industry"]],
            x=[row["Max (%)"] - row["Min (%)"]],
            base=[row["Min (%)"]],
            orientation='h',
            name=row["Industry"],
            showlegend=False,
            marker=dict(
                color='rgba(173, 216, 230, 0.7)',
                line=dict(color='rgba(73, 116, 230, 1.0)', width=1)
            ),
            hovertemplate=f"<b>{row['Industry']}</b><br>Range: {row['Min (%)']}%-{row['Max (%)']}%<br>Typical: {row['Typical (%)']}%<extra></extra>"
        ))
        
        # Add markers for typical value
        fig_security.add_trace(go.Scatter(
            y=[row["Industry"]],
            x=[row["Typical (%)"]],
            mode='markers',
            marker=dict(symbol='diamond', size=10, color='rgba(55, 83, 109, 1)'),
            name=f"{row['Industry']} (Typical)",
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Update layout
    fig_security.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(240, 240, 240, 0.8)',
        xaxis=dict(
            title=dict(text="Security Budget (% of IT Spend)", font=dict(size=14)),
            tickfont=dict(size=12),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211, 211, 211, 0.5)',
            showline=True,
            linewidth=1,
            linecolor='rgba(211, 211, 211, 1)'
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=12),
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='rgba(211, 211, 211, 1)'
        ),
        bargap=0.3
    )
    
    # Add annotations for min, typical, max
    fig_security.add_annotation(
        x=0,
        y=1.05,
        xref="paper",
        yref="paper",
        text="Range: Min-Max, Diamond: Typical Value",
        showarrow=False,
        font=dict(size=12)
    )
    
    st.plotly_chart(fig_security, use_container_width=True)
    st.caption("Sources: Gartner, IDC, Deloitte, Flexera, HIMSS, EDUCAUSE")
    
    # Data source information
    st.subheader("Data Sources")
    st.markdown("""
    The benchmarks provided are based on these authoritative sources:
    - **Gartner IT Key Metrics Data**: Annual IT and cybersecurity budget benchmarks across industries
    - **IDC Industry Spending Guides**: Industry-specific IT and cybersecurity spending percentages
    - **Computer Economics Annual IT Spending Reports**: Detailed IT spending patterns
    - **Deloitte Cybersecurity and Industry Surveys**: Industry-specific cybersecurity spend insights
    - **Flexera State of Tech Spend Annual Reports**: Granular industry breakdown of IT budgets
    - **HIMSS Cybersecurity Survey**: Healthcare sector IT and security spending benchmarks
    - **EDUCAUSE**: IT spending patterns for educational institutions
    
    These figures provide useful benchmarks for budget estimations, recognizing variations driven by regulatory demands, risk exposure, and industry-specific threats.
    """)

with tab3:
    st.header("NAICS Industry Analysis")
    st.markdown("""
    This tab shows the distribution of businesses by revenue tier based on NAICS industry codes and official business statistics.
    Select one or more NAICS codes to see how many potential customers exist in each revenue range.
    
    Note: The analysis includes 1,935,963 uncoded records which are shown in the total but excluded from revenue-based calculations.
    """)

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
        
        # Move NAICS selection to this tab
        if "NAICS Code" in naics_df.columns:
            # Create options combining code and name
            naics_options = []
            for code in naics_df["NAICS Code"].dropna().unique():
                # Get the name for this code
                name = naics_df[naics_df["NAICS Code"] == code]["NAICS Name"].iloc[0] if len(naics_df[naics_df["NAICS Code"] == code]) > 0 else ""
                # Format as "code - name"
                naics_options.append(f"{code} - {name}")
            
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
            if selected_naics != "All" and "NAICS Code" in naics_df.columns:
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
            revenue_tiers = [
                (0, 0.5),           # Under 500,000
                (0.5, 1),           # 500,000 - 999,999
                (1, 2.5),           # 1,000,000 - 2,499,999
                (2.5, 5),           # 2,500,000 - 4,999,999
                (5, 10),            # 5,000,000 - 9,999,999
                (10, 100),          # 10,000,000 - 99,999,999
                (100, 500),         # 100,000,000 - 499,999,999
                (500, 1000),        # 500,000,000 - 999,999,999
                (1000, float('inf')) # 1,000,000,000+
            ]

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

            # Map revenue tiers to actual business counts
            revenue_tier_counts = {
                (0, 0.5): 13918257,           # Under 500,000
                (0.5, 1): 792624,             # 500,000 - 999,999
                (1, 2.5): 546969,             # 1,000,000 - 2,499,999
                (2.5, 5): 222344,             # 2,500,000 - 4,999,999
                (5, 10): 144641,              # 5,000,000 - 9,999,999
                (10, 100): 176000,            # 10,000,000 - 99,999,999
                (100, 500): 23670,            # 100,000,000 - 499,999,999
                (500, 1000): 4070,            # 500,000,000 - 999,999,999
                (1000, float('inf')): 5161    # 1,000,000,000+
            }
            
            # Create dataframe for the table
            tier_analysis = []
            
            for low, high in revenue_tiers:
                # Get the actual company count for this tier
                company_count = revenue_tier_counts[(low, high)]
                
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
            st.subheader("Distribution of Companies by Revenue Tier")
            
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
            
            # Create a multi-dimensional chart with bubbles
            fig = go.Figure()
            
            # Add bar chart for number of companies
            fig.add_trace(go.Bar(
                x=chart_data["Revenue Tier"],
                y=chart_data["Number of Companies"],
                name="Number of Companies",
                marker_color="rgba(60, 120, 216, 0.7)",
                text=chart_data["Number of Companies"],
                textposition="outside",
            ))
            
            # Calculate positions for bubbles - place them above the bars
            y_offset_factor = 0.2  # Offset as a fraction of company count
            max_companies = chart_data["Number of Companies"].max()
            
            # Calculate better bubble sizes - adjust based on sqrt for more proportional appearance
            max_it_tam = chart_data["IT Budget TAM Numeric"].max()
            max_sec_tam = chart_data["Security TAM Numeric"].max()
            
            # Use logarithmic scaling for better visual representation with wide value ranges
            chart_data["IT Bubble Size"] = chart_data["IT Budget TAM Numeric"].apply(
                lambda x: 25 + (35 * np.log1p(x) / np.log1p(max_it_tam)) if x > 0 else 10
            )
            chart_data["Security Bubble Size"] = chart_data["Security TAM Numeric"].apply(
                lambda x: 20 + (25 * np.log1p(x) / np.log1p(max_sec_tam)) if x > 0 else 8
            )
            
            # Add bubble chart for IT Budget TAM - positioned above bars
            for i, row in chart_data.iterrows():
                # Calculate y position for IT bubble (above the bar)
                y_pos = row["Number of Companies"] * (1 + y_offset_factor)
                
                # Add IT TAM bubble
                fig.add_trace(go.Scatter(
                    x=[row["Revenue Tier"]],
                    y=[y_pos],
                    mode="markers+text",
                    name="IT Budget TAM" if i == 0 else None,  # Only add to legend once
                    marker=dict(
                        size=row["IT Bubble Size"],
                        color="rgba(65, 171, 93, 0.7)",
                        line=dict(width=1, color="rgba(65, 171, 93, 1)"),
                        symbol="circle",
                    ),
                    text=row["IT Budget TAM ($M)"],
                    textposition="middle center",
                    textfont=dict(
                        size=10,
                        color="black"
                    ),
                    hovertemplate="<b>%{x}</b><br>Companies: " + str(row["Number of Companies"]) + "<br>IT TAM: " + row["IT Budget TAM ($M)"] + "<extra></extra>",
                    showlegend=i == 0  # Only show in legend once
                ))
                
                # Calculate y position for Security bubble (above the IT bubble)
                y_pos_sec = row["Number of Companies"] * (1 + y_offset_factor * 2)
                
                # Add Security TAM bubble
                fig.add_trace(go.Scatter(
                    x=[row["Revenue Tier"]],
                    y=[y_pos_sec],
                    mode="markers+text",
                    name="Security TAM" if i == 0 else None,  # Only add to legend once
                    marker=dict(
                        size=row["Security Bubble Size"],
                        color="rgba(251, 180, 76, 0.7)",
                        line=dict(width=1, color="rgba(251, 180, 76, 1)"),
                        symbol="circle",
                    ),
                    text=row["Security TAM ($M)"],
                    textposition="middle center",
                    textfont=dict(
                        size=9,
                        color="black"
                    ),
                    hovertemplate="<b>%{x}</b><br>Companies: " + str(row["Number of Companies"]) + "<br>Security TAM: " + row["Security TAM ($M)"] + "<extra></extra>",
                    showlegend=i == 0  # Only show in legend once
                ))
            
            # Update layout for better readability
            fig.update_layout(
                title="Multi-dimensional Analysis by Revenue Tier",
                xaxis={"categoryorder": "array", "categoryarray": chart_data["Revenue Tier"].tolist()},
                yaxis_title="Number of Companies",
                xaxis_title="Revenue Range",
                height=600,
                font=dict(family="Arial, sans-serif", size=12),
                plot_bgcolor='rgba(240, 240, 240, 0.8)',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(t=80, b=80)
            )
            
            # Set y-axis to accommodate the bubbles above bars
            y_max = max_companies * (1 + y_offset_factor * 3)  # Extra space for bubbles and labels
            fig.update_yaxes(range=[0, y_max])
            
            # Add annotation explaining the bubbles
            fig.add_annotation(
                text="Bubble size represents TAM value",
                xref="paper",
                yref="paper",
                x=0.01,
                y=0.99,
                showarrow=False,
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="rgba(0, 0, 0, 0.5)",
                borderwidth=1,
                borderpad=4,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation
            st.markdown("""
            ### Understanding the Analysis
            
            - **Revenue Tier**: Standard NAICS revenue ranges for companies
            - **Number of Companies**: Count of companies in this revenue tier
            - **Average Revenue**: Midpoint of the revenue range (for TAM calculations)
            - **IT Budget TAM**: Total Addressable Market for IT budget (based on weighted average IT spend %)
            - **Security TAM**: Total Addressable Market for security budget (based on weighted average security spend %)
            
            TAM calculations use industry averages of:
            - IT Budget: """+str(INDUSTRY_IT_SPEND["Weighted Average"]["typical"])+"""% of revenue
            - Security Budget: """+str(INDUSTRY_SECURITY_SPEND["Weighted Average"]["typical"])+"""% of IT budget
            """)
            
        else:
            st.error("NAICS Code column not found in the dataset. Please check your Excel file structure.")

with tab4:
    st.header("Sector TAM Analysis")
    st.markdown("""
    This section analyzes the Total Addressable Market (TAM) for IT and Security budgets across different sectors.
    The analysis uses industry-standard budget percentages and revenue estimates to calculate potential market size.
    """)

    # Define sector data
    sector_data = {
        "Agriculture, Forestry, Fishing and Hunting": {"code": "11", "entities": 367959},
        "Mining": {"code": "21", "entities": 33339},
        "Utilities": {"code": "22", "entities": 52270},
        "Construction": {"code": "23", "entities": 1512763},
        "Manufacturing": {"code": "31-33", "entities": 660640},
        "Wholesale Trade": {"code": "42", "entities": 698477},
        "Retail Trade": {"code": "44-45", "entities": 1870617},
        "Transportation and Warehousing": {"code": "48-49", "entities": 711582},
        "Information": {"code": "51", "entities": 370463},
        "Finance and Insurance": {"code": "52", "entities": 771419},
        "Real Estate Rental and Leasing": {"code": "53", "entities": 926476},
        "Professional, Scientific, and Technical Services": {"code": "54", "entities": 2489746},
        "Management of Companies and Enterprises": {"code": "55", "entities": 93116},
        "Administrative and Support Services": {"code": "56", "entities": 1553879},
        "Educational Services": {"code": "61", "entities": 430343},
        "Health Care and Social Assistance": {"code": "62", "entities": 1695931},
        "Arts, Entertainment, and Recreation": {"code": "71", "entities": 385880},
        "Accommodation and Food Services": {"code": "72", "entities": 931927},
        "Other Services": {"code": "81", "entities": 1955493},
        "Public Administration": {"code": "92", "entities": 256211}
    }

    # Define revenue distribution assumptions (in millions)
    revenue_distribution = {
        "Small": {"range": (0, 10), "percentage": 0.7, "avg_revenue": 5},
        "Medium": {"range": (10, 100), "percentage": 0.2, "avg_revenue": 55},
        "Large": {"range": (100, 1000), "percentage": 0.08, "avg_revenue": 550},
        "Enterprise": {"range": (1000, float('inf')), "percentage": 0.02, "avg_revenue": 2000}
    }

    # Calculate TAM for each sector
    sector_tam = []
    for sector, data in sector_data.items():
        entities = data["entities"]
        
        # Calculate entities in each revenue tier
        small_entities = int(entities * revenue_distribution["Small"]["percentage"])
        medium_entities = int(entities * revenue_distribution["Medium"]["percentage"])
        large_entities = int(entities * revenue_distribution["Large"]["percentage"])
        enterprise_entities = entities - small_entities - medium_entities - large_entities
        
        # Calculate average revenue per tier
        small_revenue = small_entities * revenue_distribution["Small"]["avg_revenue"]
        medium_revenue = medium_entities * revenue_distribution["Medium"]["avg_revenue"]
        large_revenue = large_entities * revenue_distribution["Large"]["avg_revenue"]
        enterprise_revenue = enterprise_entities * revenue_distribution["Enterprise"]["avg_revenue"]
        
        total_revenue = small_revenue + medium_revenue + large_revenue + enterprise_revenue
        
        # Use industry-specific IT and security percentages where available
        if sector in INDUSTRY_IT_SPEND:
            it_percentage = INDUSTRY_IT_SPEND[sector]["typical"] / 100
            security_percentage = INDUSTRY_SECURITY_SPEND[sector]["typical"] / 100
        else:
            # Use weighted average for sectors not in our data
            it_percentage = INDUSTRY_IT_SPEND["Weighted Average"]["typical"] / 100
            security_percentage = INDUSTRY_SECURITY_SPEND["Weighted Average"]["typical"] / 100
        
        # Calculate TAM
        it_tam = total_revenue * it_percentage
        security_tam = it_tam * security_percentage
        
        sector_tam.append({
            "Sector": sector,
            "NAICS Code": data["code"],
            "Number of Entities": entities,
            "Total Revenue ($M)": total_revenue,
            "IT Budget TAM ($M)": it_tam,
            "Security TAM ($M)": security_tam
        })
    
    # Create DataFrame
    sector_df = pd.DataFrame(sector_tam)
    
    # Calculate totals before formatting
    total_entities = sum(data["entities"] for data in sector_data.values())
    total_revenue = sum(row["Total Revenue ($M)"] for row in sector_tam)
    total_it_tam = sum(row["IT Budget TAM ($M)"] for row in sector_tam)
    total_security_tam = sum(row["Security TAM ($M)"] for row in sector_tam)
    
    # Format numbers for display
    sector_df["Number of Entities"] = sector_df["Number of Entities"].apply(lambda x: f"{x:,.0f}")
    sector_df["Total Revenue ($M)"] = sector_df["Total Revenue ($M)"].apply(lambda x: f"${x:,.1f}M" if x < 1000 else f"${x/1000:,.1f}B")
    sector_df["IT Budget TAM ($M)"] = sector_df["IT Budget TAM ($M)"].apply(lambda x: f"${x:,.1f}M" if x < 1000 else f"${x/1000:,.1f}B")
    sector_df["Security TAM ($M)"] = sector_df["Security TAM ($M)"].apply(lambda x: f"${x:,.1f}M" if x < 1000 else f"${x/1000:,.1f}B")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total US Entities", f"{total_entities:,.0f}")
    with col2:
        st.metric("Total Revenue", f"${total_revenue:,.1f}M" if total_revenue < 1000 else f"${total_revenue/1000:,.1f}B")
    with col3:
        st.metric("Total IT TAM", f"${total_it_tam:,.1f}M" if total_it_tam < 1000 else f"${total_it_tam/1000:,.1f}B")
    with col4:
        st.metric("Total Security TAM", f"${total_security_tam:,.1f}M" if total_security_tam < 1000 else f"${total_security_tam/1000:,.1f}B")
    
    # Display the table
    st.dataframe(sector_df, use_container_width=True)
    
    # Add explanation
    st.markdown("""
    ### Understanding the TAM Analysis
    
    This analysis estimates the Total Addressable Market (TAM) for IT and Security budgets across different sectors using:
    
    1. **Revenue Distribution**:
       - Small (0-10M): 70% of entities
       - Medium (10-100M): 20% of entities
       - Large (100-1000M): 8% of entities
       - Enterprise (1000M+): 2% of entities
    
    2. **Budget Percentages**:
       - Industry-specific IT and Security budget percentages where available
       - Weighted averages for sectors not in our benchmark data
    
    3. **Data Sources**:
       - Entity counts from official business statistics
       - Budget percentages from industry benchmarks
       - Revenue distribution based on typical business size patterns
    
    Note: These are estimates based on industry averages and typical business patterns. Actual market size may vary based on specific sector characteristics and economic conditions.
    """)
    
    # Create visualization
    st.subheader("Sector TAM Distribution")
    
    # Prepare data for visualization
    viz_data = pd.DataFrame(sector_tam)
    viz_data = viz_data.sort_values("Security TAM ($M)", ascending=True)
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Add bars for Security TAM
    fig.add_trace(go.Bar(
        y=viz_data["Sector"],
        x=viz_data["Security TAM ($M)"],
        orientation='h',
        name='Security TAM',
        marker_color='rgba(65, 171, 93, 0.7)',
        text=viz_data["Security TAM ($M)"].apply(lambda x: f"${x:,.1f}M" if x < 1000 else f"${x/1000:,.1f}B"),
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Security TAM: %{text}<extra></extra>"
    ))
    
    # Update layout
    fig.update_layout(
        title="Security TAM by Sector",
        xaxis_title="Security TAM ($M)",
        yaxis_title="Sector",
        height=800,
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(240, 240, 240, 0.8)',
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)

with tab1:
    # Create columns for sidebar and main content
    main_content, sidebar = st.columns([3, 1])
    
    with sidebar:
        st.header("Budget Settings")

# NAICS Selection - Remove from sidebar since it's now in tab3
        # Get NAICS selection from session state
        if 'naics_selection' not in st.session_state:
            st.session_state.naics_selection = ["All"]
            
        selected_naics_options = st.session_state.naics_selection
        
        # Convert the selections to NAICS codes for filtering
        if "All" in selected_naics_options:
            selected_naics = "All"
        else:
            # Extract just the codes from the selections (split on first " - ")
            selected_naics = [option.split(" - ")[0] for option in selected_naics_options]
            
        # Industry Presets for IT Budget
        st.subheader("IT Budget Settings")

        # Industry preset selection
        selected_industry = st.selectbox(
            "Select Industry for Budget Presets",
            options=list(INDUSTRY_IT_SPEND.keys()),
            index=9,  # Default to Weighted Average
            help="Choose an industry to use its typical IT and security budget percentages, or select 'Custom' to define your own."
        )

        # IT Budget Percentage - conditional on industry selection
        if selected_industry == "Custom":
            it_budget_percentage = st.slider(
                "IT Budget (% of Revenue)", 
                min_value=1, 
                max_value=25, 
                value=8, 
                step=1,
                help="Typical range is 2.5% to 10%, with tech companies up to 25%"
            )
            
            security_budget_percentage = st.slider(
                "Security Budget (% of IT Budget)", 
                min_value=3, 
                max_value=20, 
                value=10, 
                step=1,
                help="Industry average is around 10% of IT budget"
            )
            
            # Custom range settings
            show_range = st.checkbox("Show Budget Ranges", value=True, key='show_range')
            
            if show_range:
                min_it_percentage = st.slider("Min IT Budget (%)", 2, 5, 4, 
                                            help="Typical minimum IT budget percentage across industries", key='min_it')
                max_it_percentage = st.slider("Max IT Budget (%)", 10, 25, 15, 
                                            help="Typical maximum IT budget percentage across industries", key='max_it')
                
                min_security_percentage = st.slider("Min Security Budget (%)", 3, 10, 5, 
                                                key='min_sec',
                                                help="Minimum security budget as % of IT budget")
                max_security_percentage = st.slider("Max Security Budget (%)", 10, 20, 15, 
                                                key='max_sec',
                                                help="Maximum security budget as % of IT budget")
        else:
            it_budget_percentage = INDUSTRY_IT_SPEND[selected_industry]["typical"]
            st.info(f"Using {selected_industry} preset: IT budget {it_budget_percentage}% of revenue (range: {INDUSTRY_IT_SPEND[selected_industry]['min']}%-{INDUSTRY_IT_SPEND[selected_industry]['max']}%)")
            
            # Use industry-specific security budget if available, otherwise default to 10%
            if selected_industry in INDUSTRY_SECURITY_SPEND:
                security_preset = INDUSTRY_SECURITY_SPEND[selected_industry]
                security_budget_percentage = security_preset["typical"]
                st.info(f"Security budget: {security_budget_percentage}% of IT budget")
                
                # Always show range for industry presets
                show_range = True
                min_it_percentage = max(2, round(it_budget_percentage * 0.7))  # 70% of typical as floor
                max_it_percentage = min(25, round(it_budget_percentage * 1.3))  # 130% of typical as ceiling
                
                min_security_percentage = security_preset["min"]
                max_security_percentage = security_preset["max"]
            else:
                security_budget_percentage = 10
                st.info("Using default security budget: 10% of IT budget")
                show_range = True
                min_it_percentage = 4
                max_it_percentage = 15
                min_security_percentage = 5
                max_security_percentage = 15

        # Add variable IT budget percentage for reference tables/charts
        st.subheader("Reference Chart Settings")
        reference_it_percentage = st.slider(
            "Reference IT Budget (% of Revenue)", 
            min_value=1, 
            max_value=15, 
            value=5, 
            step=1,
            help="IT budget percentage used in reference chart and tables (default 5%)"
        )

        # Add custom trend line option
        custom_trend = st.checkbox("Add Custom Trend Line", value=False)
        if custom_trend:
            custom_security_percentage = st.slider(
                "Custom Security Budget (% of IT Budget)",
                min_value=1,
                max_value=30,
                value=12,
                step=1,
                help="Create your own trend line with a custom security budget percentage"
            )
            custom_line_name = st.text_input("Custom Line Name", value="My Trend", 
                                           help="Give your custom trend line a name")

# Revenue Range
        st.subheader("Revenue Settings")
        # Define revenue steps with billions formatting for display
        revenue_steps = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]  # in millions
        revenue_display = [f"${r}M" if r < 1000 else f"${r/1000:.1f}B" for r in revenue_steps]
        
        # Create a mapping of display values to actual values
        revenue_map = {display: value for display, value in zip(revenue_display, revenue_steps)}
        
        selected_revenue_display = st.selectbox(
            "Max Revenue in Chart", 
            options=revenue_display,
            index=len(revenue_display)-1
        )
        selected_revenue = revenue_map[selected_revenue_display]

    # Refresh app when settings change
    if 'prev_selection' not in st.session_state:
        st.session_state.prev_selection = {
            'industry': selected_industry,
            'it_budget': it_budget_percentage,
            'security_budget': security_budget_percentage,
            'reference_it': reference_it_percentage,
            'show_range': show_range,
            'min_it': min_it_percentage if show_range else 0,
            'max_it': max_it_percentage if show_range else 0,
            'min_sec': min_security_percentage if show_range else 0,
            'max_sec': max_security_percentage if show_range else 0
        }

    # Check if any settings changed
    settings_changed = (
        st.session_state.prev_selection['industry'] != selected_industry or
        st.session_state.prev_selection['it_budget'] != it_budget_percentage or
        st.session_state.prev_selection['security_budget'] != security_budget_percentage or
        st.session_state.prev_selection['reference_it'] != reference_it_percentage or
        st.session_state.prev_selection['show_range'] != show_range or
        (show_range and st.session_state.prev_selection['min_it'] != min_it_percentage) or
        (show_range and st.session_state.prev_selection['max_it'] != max_it_percentage) or
        (show_range and st.session_state.prev_selection['min_sec'] != min_security_percentage) or
        (show_range and st.session_state.prev_selection['max_sec'] != max_security_percentage)
    )

    # Update saved selections
    st.session_state.prev_selection = {
        'industry': selected_industry,
        'it_budget': it_budget_percentage,
        'security_budget': security_budget_percentage,
        'reference_it': reference_it_percentage,
        'show_range': show_range,
        'min_it': min_it_percentage if show_range else 0,
        'max_it': max_it_percentage if show_range else 0,
        'min_sec': min_security_percentage if show_range else 0,
        'max_sec': max_security_percentage if show_range else 0
    }

    with main_content:
# Filter NAICS data if needed
        if selected_naics != "All" and "NAICS Code" in naics_df.columns:
            if isinstance(selected_naics, list):
                # Filter for multiple selected NAICS codes
                naics_df_filtered = naics_df[naics_df["NAICS Code"].isin(selected_naics)]
            else:
                # Single NAICS code (backward compatibility)
                naics_df_filtered = naics_df[naics_df["NAICS Code"] == selected_naics]
        else:
            naics_df_filtered = naics_df.copy()

# Calculations for Security Budget
        # Create a more detailed revenue array with 100M steps
        revenues = []
        for i in range(0, selected_revenue + 100, 100):
            if i <= selected_revenue:
                revenues.append(i)
        
        # Make sure we include specific points of interest
        if 50 not in revenues and selected_revenue >= 50:
            revenues.append(50)
        
        revenues.sort()
        
        it_budget_percentage_decimal = it_budget_percentage / 100
        security_budget_fraction = security_budget_percentage / 100

        budget_calc = pd.DataFrame({
            "Annual Revenue (Million $)": revenues,
            "IT Budget (Million $)": [r * it_budget_percentage_decimal for r in revenues],
            "Security Budget (Million $)": [r * it_budget_percentage_decimal * security_budget_fraction for r in revenues]
        })

        # If showing ranges, calculate the min and max values
        if show_range:
            min_it_decimal = min_it_percentage / 100
            max_it_decimal = max_it_percentage / 100
            min_security_fraction = min_security_percentage / 100
            max_security_fraction = max_security_percentage / 100
            
            # Calculate the true min and max based on both IT and security ranges
            budget_calc["Min IT Budget (Million $)"] = [r * min_it_decimal for r in revenues]
            budget_calc["Max IT Budget (Million $)"] = [r * max_it_decimal for r in revenues]
            
            budget_calc["Min Security Budget (Million $)"] = budget_calc["Min IT Budget (Million $)"] * min_security_fraction
            budget_calc["Max Security Budget (Million $)"] = budget_calc["Max IT Budget (Million $)"] * max_security_fraction

        # Merge with company count data
        def company_counts(rev):
            matching_rows = naics_df_filtered[
                (naics_df_filtered['Sales ($Mil) Low'] <= rev) &
                (naics_df_filtered['Sales ($Mil) High'] >= rev)
            ]
            return matching_rows["Company Count"].sum()

        budget_calc["Estimated Company Count"] = budget_calc["Annual Revenue (Million $)"].apply(company_counts)

        # Summary at the top for key metrics
        st.subheader("Budget Summary")
        
        # Get industry-specific context
        if selected_industry != "Custom":
            industry_context = f"Based on {selected_industry} industry benchmarks"
        else:
            industry_context = "Based on your custom settings"

        # Display the industries being analyzed
        if selected_naics == "All":
            industry_text = "all industries"
        else:
            # Get the names of selected industries for display
            selected_names = []
            for code in selected_naics:
                industry_name = naics_df[naics_df["NAICS Code"] == code]["NAICS Name"].iloc[0] if len(naics_df[naics_df["NAICS Code"] == code]) > 0 else code
                selected_names.append(f"{code} - {industry_name}")
            
            if len(selected_names) == 1:
                industry_text = f"the selected industry: **{selected_names[0]}**"
            else:
                industry_text = f"the selected industries: **{', '.join(selected_names)}**"

        # Calculate range if enabled
        selected_rev_mil = selected_revenue
        recommended_budget = selected_rev_mil * it_budget_percentage_decimal * security_budget_fraction
        
        # Format for display with B for billions
        selected_rev_display = f"${selected_rev_mil}M" if selected_rev_mil < 1000 else f"${selected_rev_mil/1000:.1f}B"
        recommended_budget_display = f"${recommended_budget:.2f}M" if recommended_budget < 1000 else f"${recommended_budget/1000:.2f}B"
        it_budget_display = f"${selected_rev_mil * it_budget_percentage_decimal:.2f}M" if (selected_rev_mil * it_budget_percentage_decimal) < 1000 else f"${(selected_rev_mil * it_budget_percentage_decimal)/1000:.2f}B"
        
        if show_range:
            min_budget = selected_rev_mil * min_it_decimal * min_security_fraction
            max_budget = selected_rev_mil * max_it_decimal * max_security_fraction
            
            min_budget_display = f"${min_budget:.2f}M" if min_budget < 1000 else f"${min_budget/1000:.2f}B"
            max_budget_display = f"${max_budget:.2f}M" if max_budget < 1000 else f"${max_budget/1000:.2f}B"
            
            range_text = f", with a possible range of {min_budget_display} to {max_budget_display} depending on budget allocation"
        else:
            range_text = ""

        # Key metrics display
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Annual Revenue", selected_rev_display)
        with col2:
            st.metric("IT Budget", it_budget_display, f"{it_budget_percentage}% of revenue")
        with col3:
            st.metric("Security Budget", recommended_budget_display, f"{security_budget_percentage}% of IT budget")
            
        # Use HTML formatting for better control
        summary_html = f"""
        <p>{industry_context}, for businesses in {industry_text} with annual revenue around 
        <span style="font-weight: normal;">{selected_rev_display}</span>, 
        a realistic security budget would typically be around 
        <span style="font-weight: normal;">{recommended_budget_display}</span>"""
        
        if show_range:
            summary_html += f""", with a possible range of 
            <span style="font-weight: normal;">{min_budget_display}</span> to 
            <span style="font-weight: normal;">{max_budget_display}</span> 
            depending on budget allocation."""
            
        summary_html += "</p>"
        
        st.markdown(summary_html, unsafe_allow_html=True)

        # Interactive Chart
        st.subheader("Security Budget Chart")

        # Create the reference dataframe with dynamic revenue tiers based on selected revenue
        # Generate revenue steps based on selected_revenue
        max_revenue = selected_revenue
        step_size = max(50, max_revenue // 10)  # Ensure at least 10 steps or minimum step of 50M
        
        revenue_tiers = []
        current = 0
        while current <= max_revenue:
            revenue_tiers.append(current)
            current += step_size
            
        # Ensure we include the max revenue exactly
        if max_revenue not in revenue_tiers:
            revenue_tiers.append(max_revenue)
            
        # Add standard revenue points for comparison
        for std_point in [50, 100, 200, 500, 1000]:
            if std_point <= max_revenue and std_point not in revenue_tiers:
                revenue_tiers.append(std_point)
                
        revenue_tiers.sort()
        security_percentages = [5, 10, 15, 20]
        
        # Define chart revenues to use in the table later
        chart_revenues = [50, 100, 200, 300, 400, 500, 750, 1000]
        chart_revenues = [r for r in chart_revenues if r <= selected_revenue]
        
        reference_data = []
        for rev in revenue_tiers:
            row_data = {"Annual Revenue (Million $)": rev}
            # Use the variable IT budget percentage instead of hardcoded 5%
            it_budget = rev * (reference_it_percentage / 100)
            
            for sec_pct in security_percentages:
                sec_budget = it_budget * (sec_pct / 100)
                row_data[f"Security Budget {sec_pct}%"] = sec_budget
                
            reference_data.append(row_data)
        
        reference_df = pd.DataFrame(reference_data)
        
        # Create reference chart similar to the image
        fig_ref = go.Figure()
        
        # Add bars for each security percentage with improved width and spacing
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for i, sec_pct in enumerate(security_percentages):
            fig_ref.add_trace(go.Bar(
                name=f'Security Budget {sec_pct}%',
                x=reference_df["Annual Revenue (Million $)"],
                y=reference_df[f"Security Budget {sec_pct}%"],
                marker_color=colors[i],
                width=step_size * 0.15,  # Adjust bar width based on step size
                text=reference_df[f"Security Budget {sec_pct}%"].apply(lambda x: f"${x:.1f}M" if x < 1000 else f"${x/1000:.1f}B"),
                textposition="outside",
                textfont=dict(size=14),  # Increased text size from 9 to 14
                showlegend=True
            ))
        
        # Add trend lines: Lower, Typical, Upper
        fig_ref.add_trace(go.Scatter(
            name='Lower',
            x=reference_df["Annual Revenue (Million $)"],
            y=reference_df["Security Budget 5%"],
            mode='lines+text',
            line=dict(color='#1f77b4', width=1.5, dash='dot'),
            marker=dict(size=5),
            text=["Lower" if i == len(reference_df)//4 else "" for i in range(len(reference_df))],
            textposition="top center",
            textfont=dict(size=16, color='#1f77b4')  # Increased text size from 10 to 16
        ))
        
        fig_ref.add_trace(go.Scatter(
            name='Typical',
            x=reference_df["Annual Revenue (Million $)"],
            y=reference_df["Security Budget 10%"],
            mode='lines+markers+text',
            line=dict(color='#ff7f0e', width=2, dash='dot'),
            marker=dict(size=8),  # Increased marker size
            text=["Typical" if i == len(reference_df)//2 else "" for i in range(len(reference_df))],
            textposition="top center",
            textfont=dict(size=16, color='#ff7f0e')  # Increased text size from 10 to 16
        ))
        
        fig_ref.add_trace(go.Scatter(
            name='Upper',
            x=reference_df["Annual Revenue (Million $)"],
            y=reference_df["Security Budget 20%"],
            mode='lines+text',
            line=dict(color='#d62728', width=1.5, dash='dot'),
            marker=dict(size=5),
            text=["Upper" if i == 3*len(reference_df)//4 else "" for i in range(len(reference_df))],
            textposition="top center",
            textfont=dict(size=16, color='#d62728')  # Increased text size from 10 to 16
        ))
        
        # Add custom trend line if enabled
        if custom_trend:
            # Calculate custom security budgets
            reference_df[f"Custom Security Budget {custom_security_percentage}%"] = reference_df["Annual Revenue (Million $)"] * (reference_it_percentage / 100) * (custom_security_percentage / 100)
            
            # Add the custom trend line
            fig_ref.add_trace(go.Scatter(
                name=custom_line_name,
                x=reference_df["Annual Revenue (Million $)"],
                y=reference_df[f"Custom Security Budget {custom_security_percentage}%"],
                mode='lines+text',
                line=dict(color='#9467bd', width=2, dash='dash'),
                marker=dict(size=8, symbol='star'),  # Increased marker size
                text=[custom_line_name if i == len(reference_df)//3 else "" for i in range(len(reference_df))],
                textposition="top center",
                textfont=dict(size=16, color='#9467bd')  # Increased text size from 10 to 16
            ))
        
        # Layout improvements
        fig_ref.update_layout(
            title="Average Security Budget based on Annual Sales in Millions",
            xaxis_title="Annual Revenue (Million $)",
            yaxis_title="Security Budget (Million $)",
            legend_title="Budget Percentages",
            barmode='group',
            bargap=0.05,     # Reduced gap between bars from 0.15 to 0.05
            bargroupgap=0.02, # Reduced gap between bar groups from 0.1 to 0.02
            height=500,
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            margin=dict(l=20, r=20, t=50, b=20),
        )
        
        # Add annotation for IT budget percentage
        fig_ref.add_annotation(
            text=f"IT Budget: {reference_it_percentage}% of Revenue",
            xref="paper",
            yref="paper",
            x=0.01,
            y=0.99,
            showarrow=False,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.5)",
            borderwidth=1,
            borderpad=4,
            font=dict(size=14)  # Increased text size from 10 to 14
        )
        
        # Improve x-axis formatting - reduce number of ticks for clarity
        fig_ref.update_xaxes(
            tickprefix="$",
            ticksuffix="M",
            title_font=dict(size=14),
            tickfont=dict(size=12),
            tickmode='array',
            tickvals=[0, 200, 400, 600, 800, 1000],  # Show fewer, more meaningful ticks
            ticktext=["$0", "$200M", "$400M", "$600M", "$800M", "$1000M"]
        )
        
        fig_ref.update_yaxes(
            tickprefix="$",
            ticksuffix="M",
            title_font=dict(size=14),
            tickfont=dict(size=12),
        )
        
        # Display chart 
        st.plotly_chart(fig_ref, use_container_width=True)
        
        # Add a data table below the chart
        st.subheader("Security Budget Table")
        
        # Create data for table using the reference IT percentage
        table_data = []
        for rev in chart_revenues:
            row = {"Annual Revenue": f"${rev}M"}
            it_budget = rev * (reference_it_percentage / 100)  # Use variable IT percentage
            
            for sec_pct in security_percentages:
                sec_budget = it_budget * (sec_pct/100)
                row[f"Security Budget {sec_pct}%"] = f"${sec_budget:.2f}M"
            
            # Add custom value to table if enabled
            if custom_trend:
                custom_budget = it_budget * (custom_security_percentage/100)
                row[f"{custom_line_name} ({custom_security_percentage}%)"] = f"${custom_budget:.2f}M"
                
            table_data.append(row)
        
        # Display as Streamlit table
        st.table(table_data)

with st.expander("📊 View Reference Table", expanded=False):
    st.markdown(f"""
    This reference table shows security budgets across different revenue tiers and security spend percentages 
    (based on {reference_it_percentage}% IT budget):
    """)
    
    # Create formatted table
    format_dict = {
        "Annual Revenue (Million $)": "${:.0f}M",
        "Security Budget 5%": "${:.3f}M",
        "Security Budget 10%": "${:.3f}M",
        "Security Budget 15%": "${:.3f}M",
        "Security Budget 20%": "${:.3f}M",
    }
    
    # Add custom column to formatting if enabled
    if custom_trend:
        format_dict[f"Custom Security Budget {custom_security_percentage}%"] = "${:.3f}M"
    
    formatted_table = reference_df.style.format(format_dict)
    
    st.dataframe(formatted_table, use_container_width=True)
    
    st.markdown(f"""
    - **Security Budget 5%**: Represents 5% of IT Budget allocation to Security
    - **Security Budget 10%**: Industry average for security spending (10% of IT Budget)
    - **Security Budget 15%**: Higher security allocation for regulated industries
    - **Security Budget 20%**: Highest security allocation for high-risk industries
    {f"- **{custom_line_name} ({custom_security_percentage}%)**: Your custom trend line" if custom_trend else ""}
    
    Assumptions:
    - IT Budget is calculated as {reference_it_percentage}% of Annual Revenue
    - Security Budget is calculated as a percentage of IT Budget
    """)

# Display unified reference table
with st.expander("View Industry Benchmark Reference Table", expanded=False):
    st.markdown("""
    ### Industry Benchmark Reference Table
    
    | Industry | IT Budget (% of Revenue) | Security Budget (% of IT Spend) |
    |----------|--------------------------|----------------------------------|
    | Financial Services | 7% - 11% | 10% - 15% |
    | Healthcare | 4% - 6% | 7% - 10% |
    | Retail | 2% - 4% | 5% - 8% |
    | Technology | 8% - 15%+ | 10% - 20% |
    | Manufacturing | 2% - 4% | 5% - 10% |
    | Government/Public Sector | 5% - 8% | 8% - 12% |
    | Education | 3% - 6% | 5% - 8% |
    | Energy & Utilities | 3% - 5% | 6% - 10% |
    | Transportation & Logistics | 2% - 5% | 5% - 8% |
    
    **Sources:** Gartner IT Key Metrics Data, IDC Industry Spending Guides, Computer Economics Annual IT Spending Reports, Deloitte, Flexera, HIMSS, EDUCAUSE
    """)

# Footer information
st.markdown("---")
st.caption("Data Sources: Gartner, IDC, Deloitte, Flexera, HIMSS, EDUCAUSE")
st.caption("Created by Oliver Rochford | [GitHub](https://github.com/RockefellerArchiveCenter/budget_calculator)")

