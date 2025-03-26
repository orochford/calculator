import pandas as pd
import sys

def examine_excel_file(file_path):
    """Examine the structure of an Excel file and print detailed information"""
    try:
        # Get all sheet names
        xls = pd.ExcelFile(file_path)
        print(f"Excel file: {file_path}")
        print(f"Available sheets: {xls.sheet_names}")
        
        # Examine the target sheet
        sheet_name = 'AnnualSales-Jan-2024'
        print(f"\nExamining sheet: {sheet_name}")
        
        # Try different skiprows values
        for skip_rows in [0, 1, 2, 3, 4]:
            print(f"\nReading with skiprows={skip_rows}:")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)
                print(f"  Shape: {df.shape}")
                print(f"  Columns: {df.columns.tolist()}")
                print(f"  First few rows:")
                print(df.head(3).to_string())
            except Exception as e:
                print(f"  Error: {str(e)}")
        
    except Exception as e:
        print(f"Failed to examine Excel file: {str(e)}")

if __name__ == "__main__":
    file_path = "usbusinesses.xlsx"
    examine_excel_file(file_path)
