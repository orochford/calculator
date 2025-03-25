import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data import INDUSTRY_IT_SPEND, INDUSTRY_SECURITY_SPEND

def show():
    st.header("Sector TAM Analysis")
    st.markdown("""
    This section analyzes the Total Addressable Market (TAM) for IT and Security budgets across different sectors.
    The analysis uses industry-standard budget percentages and revenue estimates to calculate potential market size.
    
    Data source: [NAICS Industry Search](https://www.naics.com/search/)
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