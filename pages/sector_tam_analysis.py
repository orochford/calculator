import streamlit as st
import pandas as pd
import data
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show():
    """Show the sector TAM analysis page"""
    st.title("Sector TAM Analysis")
    
    # Load NAICS data
    naics_data = data.load_naics_revenue_data()
    
    if naics_data is None:
        st.error("Failed to load NAICS data. Please check the console for errors.")
        return
    
    # Add title for the section
    st.write("### Total Addressable Market (TAM) by Sector")
    
    # Calculate TAM for each sector
    sector_tam = []
    total_it_budget = 0
    total_security_budget = 0
    total_revenue = 0
    total_companies = 0
    
    for _, row in naics_data.iterrows():
        sector = row['sector_name']
        companies = row['Companies']
        coded_companies = row['CodedCompanies']
        uncoded_companies = row['UncodedCompanies']
        revenue = row['Revenue']  # in millions
        
        # Apply industry-specific IT and security percentages
        it_percent = data.get_industry_it_percent(sector)
        security_percent = data.get_industry_security_percent(sector)
        
        # Calculate IT and security budgets
        it_budget = revenue * it_percent / 100
        security_budget = it_budget * security_percent / 100
        
        # Add to totals
        total_revenue += revenue
        total_companies += companies
        total_it_budget += it_budget
        total_security_budget += security_budget
        
        # Add to sector TAM list
        sector_tam.append({
            'Sector': sector,
            'Coded Companies': f"{coded_companies:,.0f}",
            'Uncoded Companies': f"{uncoded_companies:,.0f}",
            'Total Companies': f"{companies:,.0f}",
            'Revenue ($M)': f"${revenue:,.0f}",
            'IT Budget ($M)': f"${it_budget:,.0f}",
            'Security Budget ($M)': f"${security_budget:,.0f}"
        })
    
    # Calculate scaling factor to match target TAM of $180B
    target_security_tam = 180000  # $180B in millions
    scaling_factor = 1.0
    
    if total_security_budget > 0:
        scaling_factor = target_security_tam / total_security_budget
    
    # Apply scaling factor if needed
    if abs(scaling_factor - 1.0) > 0.01:  # If scaling factor is significantly different from 1.0
        for item in sector_tam:
            # Extract numeric values from formatted strings
            it_budget = float(item['IT Budget ($M)'].replace('$', '').replace(',', ''))
            security_budget = float(item['Security Budget ($M)'].replace('$', '').replace(',', ''))
            
            # Apply scaling factor to security budget
            adjusted_security_budget = security_budget * scaling_factor
            
            # Update the item with scaled security budget
            item['Security Budget ($M)'] = f"${adjusted_security_budget:,.0f}"
    
    # Display the TAM table
    st.dataframe(sector_tam)
    
    # Create visualization data
    viz_data = pd.DataFrame(sector_tam)
    
    # Convert string columns to numeric for plotting
    viz_data['Coded Companies'] = viz_data['Coded Companies'].str.replace(',', '').astype(float)
    viz_data['Uncoded Companies'] = viz_data['Uncoded Companies'].str.replace(',', '').astype(float)
    viz_data['Revenue ($M)'] = viz_data['Revenue ($M)'].str.replace('$', '').str.replace(',', '').astype(float)
    viz_data['Security Budget ($M)'] = viz_data['Security Budget ($M)'].str.replace('$', '').str.replace(',', '').astype(float)
    
    # Sort by Security Budget for better visualization
    viz_data = viz_data.sort_values('Security Budget ($M)', ascending=False)
    
    # Create a mixed chart (bar for companies, line for security budget)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bar chart for coded companies
    fig.add_trace(
        go.Bar(
            x=viz_data['Sector'],
            y=viz_data['Coded Companies'],
            name="Coded Companies",
            marker_color='rgba(55, 83, 109, 0.7)',
            offsetgroup=0
        ),
        secondary_y=False,
    )
    
    # Add bar chart for uncoded companies
    fig.add_trace(
        go.Bar(
            x=viz_data['Sector'],
            y=viz_data['Uncoded Companies'],
            name="Uncoded Companies",
            marker_color='rgba(26, 118, 255, 0.7)',
            offsetgroup=0
        ),
        secondary_y=False,
    )
    
    # Add line chart for security budget
    fig.add_trace(
        go.Scatter(
            x=viz_data['Sector'],
            y=viz_data['Security Budget ($M)'],
            name="Security Budget ($M)",
            line=dict(color='rgba(219, 64, 82, 0.7)', width=3)
        ),
        secondary_y=True,
    )
    
    # Update layout
    fig.update_layout(
        title_text="Companies and Security Budget by Sector",
        barmode='stack',
        xaxis=dict(
            title="Sector",
            tickangle=45,
            tickfont=dict(size=10),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        margin=dict(l=50, r=50, t=80, b=150)
    )
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Number of Companies", secondary_y=False)
    fig.update_yaxes(title_text="Security Budget ($M)", secondary_y=True)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Add note about uncoded records
    st.write("### Data Processing Notes")
    st.write("""
    **Note on Business Counts:**
    
    The business counts in this analysis include both coded and uncoded records from the NAICS data source:
    
    - **Coded Companies**: Businesses with specific revenue information categorized in revenue tiers
    - **Uncoded Companies**: Businesses that don't have specific revenue information but are still counted in the industry totals
    
    For revenue calculations, we've made the conservative assumption that uncoded records represent small businesses 
    with annual revenue under $500,000 (using a multiplier of $250,000 per business).
    
    This approach ensures we're accounting for all businesses in each sector, including government entities, 
    non-profits, and other organizations that may not report detailed revenue information but are still potential 
    customers for security products and services.
    """)