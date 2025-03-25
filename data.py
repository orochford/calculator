import streamlit as st
import numpy as np

# Define NAICS revenue tiers based on official business statistics
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

# Define revenue tiers for analysis
REVENUE_TIERS = [
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

# Map revenue tiers to actual business counts
REVENUE_TIER_COUNTS = {
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

# Define major NAICS sectors with codes and names
NAICS_SECTORS = [
    {"code": "11", "name": "Agriculture, Forestry, Fishing and Hunting"},
    {"code": "21", "name": "Mining, Quarrying, and Oil and Gas Extraction"},
    {"code": "22", "name": "Utilities"},
    {"code": "23", "name": "Construction"},
    {"code": "31-33", "name": "Manufacturing"},
    {"code": "42", "name": "Wholesale Trade"},
    {"code": "44-45", "name": "Retail Trade"},
    {"code": "48-49", "name": "Transportation and Warehousing"},
    {"code": "51", "name": "Information"},
    {"code": "52", "name": "Finance and Insurance"},
    {"code": "53", "name": "Real Estate and Rental and Leasing"},
    {"code": "54", "name": "Professional, Scientific, and Technical Services"},
    {"code": "55", "name": "Management of Companies and Enterprises"},
    {"code": "56", "name": "Administrative and Support Services"},
    {"code": "61", "name": "Educational Services"},
    {"code": "62", "name": "Health Care and Social Assistance"},
    {"code": "71", "name": "Arts, Entertainment, and Recreation"},
    {"code": "72", "name": "Accommodation and Food Services"},
    {"code": "81", "name": "Other Services (except Public Administration)"},
    {"code": "92", "name": "Public Administration"}
]

# Define industry-specific IT budget percentages based on updated industry data
INDUSTRY_IT_SPEND = {
    "Weighted Average": {"min": 4, "max": 7, "typical": 5.5},
    "Financial Services": {"min": 7, "max": 11, "typical": 9.0},
    "Healthcare": {"min": 4, "max": 6, "typical": 5.0},
    "Retail": {"min": 2, "max": 4, "typical": 3.0},
    "Technology": {"min": 8, "max": 15, "typical": 11.5},
    "Manufacturing": {"min": 2, "max": 4, "typical": 3.0},
    "Government/Public Sector": {"min": 5, "max": 8, "typical": 6.5},
    "Education": {"min": 3, "max": 6, "typical": 4.5},
    "Energy & Utilities": {"min": 3, "max": 5, "typical": 4.0},
    "Transportation & Logistics": {"min": 2, "max": 5, "typical": 3.5},
    "Custom": None  # For user-defined values
}

# Define industry-specific security budget percentages (as % of IT spend)
INDUSTRY_SECURITY_SPEND = {
    "Weighted Average": {"min": 7, "max": 12, "typical": 9.5},
    "Financial Services": {"min": 10, "max": 15, "typical": 12.5},
    "Healthcare": {"min": 7, "max": 10, "typical": 8.5},
    "Retail": {"min": 5, "max": 8, "typical": 6.5},
    "Technology": {"min": 10, "max": 20, "typical": 15.0},
    "Manufacturing": {"min": 5, "max": 10, "typical": 7.5},
    "Government/Public Sector": {"min": 8, "max": 12, "typical": 10.0},
    "Education": {"min": 5, "max": 8, "typical": 6.5},
    "Energy & Utilities": {"min": 6, "max": 10, "typical": 8.0},
    "Transportation & Logistics": {"min": 5, "max": 8, "typical": 6.5},
    "Custom": None  # For user-defined values
}

# Create industry presets dictionary for the UI
INDUSTRY_PRESETS = {
    "Financial Services": {
        "it_min": INDUSTRY_IT_SPEND["Financial Services"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Financial Services"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Financial Services"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Financial Services"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Financial Services"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Financial Services"]["max"],
    },
    "Healthcare": {
        "it_min": INDUSTRY_IT_SPEND["Healthcare"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Healthcare"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Healthcare"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Healthcare"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Healthcare"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Healthcare"]["max"],
    },
    "Retail": {
        "it_min": INDUSTRY_IT_SPEND["Retail"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Retail"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Retail"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Retail"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Retail"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Retail"]["max"],
    },
    "Technology": {
        "it_min": INDUSTRY_IT_SPEND["Technology"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Technology"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Technology"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Technology"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Technology"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Technology"]["max"],
    },
    "Manufacturing": {
        "it_min": INDUSTRY_IT_SPEND["Manufacturing"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Manufacturing"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Manufacturing"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Manufacturing"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Manufacturing"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Manufacturing"]["max"],
    },
    "Government/Public Sector": {
        "it_min": INDUSTRY_IT_SPEND["Government/Public Sector"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Government/Public Sector"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Government/Public Sector"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Government/Public Sector"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Government/Public Sector"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Government/Public Sector"]["max"],
    },
    "Education": {
        "it_min": INDUSTRY_IT_SPEND["Education"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Education"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Education"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Education"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Education"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Education"]["max"],
    },
    "Energy & Utilities": {
        "it_min": INDUSTRY_IT_SPEND["Energy & Utilities"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Energy & Utilities"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Energy & Utilities"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Energy & Utilities"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Energy & Utilities"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Energy & Utilities"]["max"],
    },
    "Transportation & Logistics": {
        "it_min": INDUSTRY_IT_SPEND["Transportation & Logistics"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Transportation & Logistics"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Transportation & Logistics"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Transportation & Logistics"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Transportation & Logistics"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Transportation & Logistics"]["max"],
    },
    "Weighted Average": {
        "it_min": INDUSTRY_IT_SPEND["Weighted Average"]["min"],
        "it_typical": INDUSTRY_IT_SPEND["Weighted Average"]["typical"],
        "it_max": INDUSTRY_IT_SPEND["Weighted Average"]["max"],
        "security_min": INDUSTRY_SECURITY_SPEND["Weighted Average"]["min"],
        "security_typical": INDUSTRY_SECURITY_SPEND["Weighted Average"]["typical"],
        "security_max": INDUSTRY_SECURITY_SPEND["Weighted Average"]["max"],
    },
}

# Generate revenue array for charts
def generate_revenue_array(max_chart_revenue=500):
    revenue_array = np.arange(50, max_chart_revenue + 100, 100).astype(int)
    if 50 not in revenue_array and max_chart_revenue >= 50:
        revenue_array = np.sort(np.append(revenue_array, [50]))
    return revenue_array

# Constants for chart colors
CHART_COLORS = {
    "user_selection": "#FF5733",  # Orange
    "bar_colors": ["#008581", "#4C9C8B", "#96E4B0", "#FFDAE8"],  # Teal to pink gradient
    "lower_bound": "#008581",  # Teal
    "upper_bound": "#E4509A",  # Dark pink
    "typical": "#96E4B0",  # Mint green
    "user_calculations": ['#FFC300', '#C70039', '#900C3F', '#581845', '#2874A6']  # User calc colors
}

# Initialize session state variables
def initialize_session_state():
    """Initialize all session state variables with proper types"""
    # Get default industry preset
    default_industry = "Weighted Average"
    default_preset = INDUSTRY_PRESETS[default_industry]
    
    # Initialize percentage values as floats
    if 'it_percentage' not in st.session_state:
        st.session_state.it_percentage = float(default_preset["it_typical"])
    if 'security_percentage' not in st.session_state:
        st.session_state.security_percentage = float(default_preset["security_typical"])
    
    # Initialize numeric values as integers
    if 'annual_revenue' not in st.session_state:
        st.session_state.annual_revenue = 100
    if 'max_chart_revenue' not in st.session_state:
        st.session_state.max_chart_revenue = 500
    
    # Initialize industry selection
    if 'selected_industry' not in st.session_state:
        st.session_state.selected_industry = default_industry
    
    # Initialize calculation history
    if 'user_calculations' not in st.session_state:
        st.session_state.user_calculations = []
    if 'custom_industries' not in st.session_state:
        st.session_state.custom_industries = {} 