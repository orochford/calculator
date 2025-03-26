# Security Budget Calculator

A Streamlit-based web application that helps security vendors understand typical IT and Security budgets across different industries to better price their solutions.

## Overview

This calculator is inspired by Oliver Rochford's analysis: "[Why you are probably pricing your security solution all wrong](https://www.linkedin.com/pulse/why-you-probably-pricing-your-security-solution-all-wrong-rochford/)."

You can use a Live version of the app here: [Security Budget Calculator](https://securitybudgets.streamlit.app/)

The application provides:
- Interactive budget visualization
- Industry-specific benchmarks
- Custom industry support
- Detailed budget breakdowns
- Pricing recommendations
- NAICS industry analysis
- Sector TAM (Total Addressable Market) analysis

## Features

- **Budget Calculator Tab**
  - Interactive charts showing security budgets across revenue points
  - Real-time budget calculations
  - Industry-specific recommendations via radio button selection
  - Visual budget breakdowns

- **Industry Benchmarks Tab**
  - Comprehensive industry data visualization
  - IT and Security budget ranges
  - Custom industry support
  - Reference tables and methodology

- **NAICS Analysis Tab**
  - Distribution of businesses by revenue tier
  - Analysis based on NAICS industry codes
  - Official business statistics integration

- **Sector TAM Analysis Tab**
  - Total Addressable Market calculations by sector
  - Company count and security budget visualizations
  - Excludes outlier categories for clearer data representation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/orochford/calculator.git
cd calculator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Data Sources

The application uses NAICS data from the included Excel file (usbusinesses.xlsx) to calculate the Total Addressable Market (TAM) for IT and security budgets across different sectors.

## Dependencies

- streamlit
- pandas
- plotly
- numpy
- Pillow
- openpyxl

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the BSD License - see the [LICENSE](LICENSE) file for details.

## Author

Created by [Oliver Rochford](https://www.linkedin.com/in/oliver-rochford/)

## Acknowledgments

- Data sources: Gartner, IDC, Deloitte, Flexera, HIMSS, EDUCAUSE
- Inspired by Oliver Rochford's analysis on security solution pricing