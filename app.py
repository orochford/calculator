import streamlit as st
import plotly.io as pio
import pages.budget_calculator as budget_calculator
import pages.industry_benchmarks as industry_benchmarks
import pages.naics_analysis as naics_analysis
import pages.sector_tam_analysis as sector_tam_analysis
from data import initialize_session_state
from utils import set_custom_css, display_logo

# Set page layout to wide
st.set_page_config(layout="wide", menu_items=None)

# Initialize session state variables
initialize_session_state()

# Configure plotly to use a higher renderer
pio.templates.default = "plotly_white"

# Apply custom CSS
set_custom_css()

# Display logo
display_logo()

# Title and description
st.title('Security Budget Calculator')
st.markdown('''
This app helps security vendors understand typical IT and Security budgets across different industries to better price their solutions.

Inspired by [Oliver Rochford's](https://www.linkedin.com/in/oliver-rochford/) analysis: "[Why you are probably pricing your security solution all wrong](https://www.linkedin.com/pulse/why-you-probably-pricing-your-security-solution-all-wrong-rochford/)."

Brought to you by [Cyberfuturists](https://www.cyberfuturists.com).

The code is open-source under the BSD license at [github](https://github.com/orochford/calculator/).
''')

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["Budget Calculator", "Industry Benchmarks", "NAICS Analysis", "Sector TAM Analysis"])

# Tab 1: Budget Calculator
with tab1:
    budget_calculator.show()

# Tab 2: Industry Benchmarks
with tab2:
    industry_benchmarks.show()

# Tab 3: NAICS Analysis
with tab3:
    naics_analysis.show()

# Tab 4: Sector TAM Analysis
with tab4:
    sector_tam_analysis.show() 