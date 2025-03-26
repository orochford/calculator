import streamlit as st
import numpy as np
import pandas as pd

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

# Function to map sector names to industry categories for IT percentages
def get_industry_it_percent(sector_name):
    """Get the IT budget percentage for a given sector"""
    # Map sector names to industry categories
    sector_to_industry = {
        "Agriculture, Forestry, Fishing and Hunting": "Weighted Average",
        "Mining": "Energy & Utilities",
        "Utilities": "Energy & Utilities",
        "Construction": "Weighted Average",
        "Manufacturing": "Manufacturing",
        "Wholesale Trade": "Retail",
        "Retail Trade": "Retail",
        "Transportation and Warehousing": "Transportation & Logistics",
        "Information": "Technology",
        "Finance and Insurance": "Financial Services",
        "Real Estate Rental and Leasing": "Weighted Average",
        "Professional, Scientific, and Technical Services": "Technology",
        "Management of Companies and Enterprises": "Weighted Average",
        "Administrative and Support Services": "Weighted Average",
        "Educational Services": "Education",
        "Health Care and Social Assistance": "Healthcare",
        "Arts, Entertainment, and Recreation": "Weighted Average",
        "Accommodation and Food Services": "Weighted Average",
        "Other Services": "Weighted Average",
        "Public Administration": "Government/Public Sector"
    }
    
    # Get the industry category for the sector
    industry = sector_to_industry.get(sector_name, "Weighted Average")
    
    # Return the typical IT percentage for the industry
    return INDUSTRY_IT_SPEND[industry]["typical"]

# Function to map sector names to industry categories for security percentages
def get_industry_security_percent(sector_name):
    """Get the security budget percentage for a given sector"""
    # Map sector names to industry categories
    sector_to_industry = {
        "Agriculture, Forestry, Fishing and Hunting": "Weighted Average",
        "Mining": "Energy & Utilities",
        "Utilities": "Energy & Utilities",
        "Construction": "Weighted Average",
        "Manufacturing": "Manufacturing",
        "Wholesale Trade": "Retail",
        "Retail Trade": "Retail",
        "Transportation and Warehousing": "Transportation & Logistics",
        "Information": "Technology",
        "Finance and Insurance": "Financial Services",
        "Real Estate Rental and Leasing": "Weighted Average",
        "Professional, Scientific, and Technical Services": "Technology",
        "Management of Companies and Enterprises": "Weighted Average",
        "Administrative and Support Services": "Weighted Average",
        "Educational Services": "Education",
        "Health Care and Social Assistance": "Healthcare",
        "Arts, Entertainment, and Recreation": "Weighted Average",
        "Accommodation and Food Services": "Weighted Average",
        "Other Services": "Weighted Average",
        "Public Administration": "Government/Public Sector"
    }
    
    # Get the industry category for the sector
    industry = sector_to_industry.get(sector_name, "Weighted Average")
    
    # Return the typical security percentage for the industry
    return INDUSTRY_SECURITY_SPEND[industry]["typical"]

# Constants for chart colors
CHART_COLORS = {
    "user_selection": "#FF5733",  # Orange
    "bar_colors": ["#008581", "#4C9C8B", "#96E4B0", "#FFDAE8"],  # Teal to pink gradient
    "lower_bound": "#008581",  # Teal
    "upper_bound": "#E4509A",  # Dark pink
    "typical": "#96E4B0",  # Mint green
    "user_calculations": ['#FFC300', '#C70039', '#900C3F', '#581845', '#2874A6'],  # User calc colors
    "range": "rgba(31, 119, 180, 0.1)"  # Light blue with transparency for range area
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

def load_naics_revenue_data():
    """Load and process NAICS revenue data from Excel file"""
    try:
        # Read the Excel file with the correct sheet name, skipping header rows
        df = pd.read_excel('usbusinesses.xlsx', sheet_name='AnnualSales-Jan-2024', skiprows=2)
        
        # Extract NAICS codes (first column)
        naics_codes = df.iloc[:, 0].astype(str)
        
        # Clean NAICS codes: remove whitespace and non-numeric characters
        naics_codes = naics_codes.str.strip().str.replace(r'[^0-9]', '', regex=True)
        
        # Get the top-level NAICS code (first 2 digits)
        # Make sure to handle any non-numeric values
        df['top_naics'] = naics_codes.str.extract(r'^(\d{2})').fillna('00')
        
        # Define the revenue tier columns (columns 3-11)
        # Note: Column 2 is "Uncoded records" which we need to include
        revenue_columns = [
            'uncoded_records',  # Uncoded records (column 2)
            'under_500k',       # Under 500,000
            '500k_1m',          # 500,000 - 999,999
            '1m_2.5m',          # 1,000,000 - 2,499,999
            '2.5m_5m',          # 2,500,000 - 4,999,999
            '5m_10m',           # 5,000,000 - 9,999,999
            '10m_100m',         # 10,000,000 - 99,999,999
            '100m_500m',        # 100,000,000 - 499,999,999
            '500m_1b',          # 500,000,000 - 999,999,999
            '1b_plus'           # 1,000,000,000+
        ]
        
        # Map the revenue columns from the Excel file to our defined columns
        excel_columns = [
            'Uncoded records',
            'Under 500,000',
            '500,000 - 999,999',
            '1,000,000 - 2,499,999',
            '2,500,000 - 4,999,999',
            '5,000,000 - 9,999,999',
            '10,000,000 - 99,999,999',
            '100,000,000 - 499,999,999',
            '500,000,000 - 999,999,999',
            '1,000,000,000+'
        ]
        
        # Map Excel columns to our defined columns
        for i, (col_name, excel_col) in enumerate(zip(revenue_columns, excel_columns)):
            if excel_col in df.columns:
                # Convert to numeric, replacing any non-numeric values with 0
                df[col_name] = pd.to_numeric(df[excel_col], errors='coerce').fillna(0)
            else:
                df[col_name] = 0
        
        # Calculate revenue multipliers (in millions of dollars)
        revenue_multipliers = {
            'uncoded_records': 0.25,  # Assume uncoded records are small businesses (under 500k)
            'under_500k': 0.25,       # midpoint of 0-500k (in millions)
            '500k_1m': 0.75,          # midpoint of 500k-1m (in millions)
            '1m_2.5m': 1.75,          # midpoint of 1m-2.5m (in millions)
            '2.5m_5m': 3.75,          # midpoint of 2.5m-5m (in millions)
            '5m_10m': 7.5,            # midpoint of 5m-10m (in millions)
            '10m_100m': 55,           # midpoint of 10m-100m (in millions)
            '100m_500m': 300,         # midpoint of 100m-500m (in millions)
            '500m_1b': 750,           # midpoint of 500m-1b (in millions)
            '1b_plus': 1500           # conservative estimate for 1b+ (in millions)
        }
        
        # Sum all businesses by NAICS code (first 2 digits)
        # This uses the raw data directly without any aggregation steps
        sector_data = {}
        
        # Process each row in the dataframe
        for idx, row in df.iterrows():
            naics = row['top_naics']
            if naics not in sector_data:
                sector_data[naics] = {
                    'Companies': 0, 
                    'CodedCompanies': 0,
                    'UncodedCompanies': 0,
                    'Revenue': 0.0
                }
            
            # Sum the companies across all revenue tiers
            for col in revenue_columns:
                if col in df.columns:
                    companies = row[col]
                    
                    # Track coded vs uncoded companies separately
                    if col == 'uncoded_records':
                        sector_data[naics]['UncodedCompanies'] += companies
                    else:
                        sector_data[naics]['CodedCompanies'] += companies
                    
                    # Add to total companies
                    sector_data[naics]['Companies'] += companies
                    
                    # Calculate revenue contribution
                    sector_data[naics]['Revenue'] += companies * revenue_multipliers[col]
        
        # Convert the dictionary to a DataFrame
        naics_summary = pd.DataFrame([
            {
                'top_naics': k, 
                'Companies': v['Companies'], 
                'CodedCompanies': v['CodedCompanies'],
                'UncodedCompanies': v['UncodedCompanies'],
                'Revenue': v['Revenue']
            }
            for k, v in sector_data.items()
        ])
        
        # Map to sector names
        naics_to_sector = {
            "11": "Agriculture, Forestry, Fishing and Hunting",
            "21": "Mining",
            "22": "Utilities",
            "23": "Construction",
            "31": "Manufacturing",
            "32": "Manufacturing",
            "33": "Manufacturing",
            "42": "Wholesale Trade",
            "44": "Retail Trade",
            "45": "Retail Trade",
            "48": "Transportation and Warehousing",
            "49": "Transportation and Warehousing",
            "51": "Information",
            "52": "Finance and Insurance",
            "53": "Real Estate Rental and Leasing",
            "54": "Professional, Scientific, and Technical Services",
            "55": "Management of Companies and Enterprises",
            "56": "Administrative and Support Services",
            "61": "Educational Services",
            "62": "Health Care and Social Assistance",
            "71": "Arts, Entertainment, and Recreation",
            "72": "Accommodation and Food Services",
            "81": "Other Services",
            "92": "Public Administration"
        }
        
        # Add sector names
        naics_summary['sector_name'] = naics_summary['top_naics'].map(naics_to_sector)
        
        # Fill any missing sector names with "Other"
        naics_summary['sector_name'] = naics_summary['sector_name'].fillna("Other")
        
        # Combine rows with the same sector name (e.g., Manufacturing for 31, 32, 33)
        sector_summary = naics_summary.groupby('sector_name').agg({
            'Companies': 'sum',
            'CodedCompanies': 'sum',
            'UncodedCompanies': 'sum',
            'Revenue': 'sum'
        }).reset_index()
        
        # Add the top_naics column back for reference
        sector_summary['top_naics'] = sector_summary['sector_name'].map({v: k for k, v in naics_to_sector.items()})
        
        # For sectors with multiple NAICS codes (like Manufacturing), use the first one
        for sector in sector_summary['sector_name']:
            if sector_summary[sector_summary['sector_name'] == sector].shape[0] > 0 and pd.isna(sector_summary.loc[sector_summary['sector_name'] == sector, 'top_naics'].iloc[0]):
                for code, name in naics_to_sector.items():
                    if name == sector:
                        sector_summary.loc[sector_summary['sector_name'] == sector, 'top_naics'] = code
                        break
        
        return sector_summary
    except Exception as e:
        st.error(f"Error loading NAICS data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# Generate revenue array for charts
def generate_revenue_array(max_chart_revenue=500):
    revenue_array = np.arange(50, max_chart_revenue + 100, 100).astype(int)
    if 50 not in revenue_array and max_chart_revenue >= 50:
        revenue_array = np.sort(np.append(revenue_array, [50]))
    return revenue_array