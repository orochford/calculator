import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from data import INDUSTRY_PRESETS

def show():
    """Display the Industry Benchmarks page with comparative charts and data"""
    
    st.header("Industry Budget Benchmarks")
    
    st.markdown("""
    This tab provides benchmark data on IT and security spending across different industries. 
    Use this information to understand typical customer budgets and align your pricing strategy.
    """)
    
    # Display industry benchmarks
    st.subheader("IT Budget as Percentage of Revenue")
    
    # Combine standard and custom industries for charts
    all_industries = {**INDUSTRY_PRESETS}
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
        'Industry': list(all_industries.keys()),
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
        elif base_industry in INDUSTRY_PRESETS:
            it_typical = INDUSTRY_PRESETS[base_industry]['it_typical']
            security_typical = INDUSTRY_PRESETS[base_industry]['security_typical']
            
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
    
    # Display industry benchmark reference table
    st.subheader("Industry Benchmark Reference Table")
    
    # Create DataFrame for the table
    table_data = []
    
    # Add standard industries
    for industry in all_industries.keys():
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
                    - IT Budget Range: {data['it_min']}% - {data['it_max']}%
                    - Typical IT: {data['it_typical']}%
                    - Security Budget Range: {data['security_min']}% - {data['security_max']}%
                    - Typical Security: {data['security_typical']}%
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