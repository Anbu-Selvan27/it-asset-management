# save as excel_to_db.py
import sqlite3
import pandas as pd
from pathlib import Path

EXCEL_PATH = r"C:\Users\Anbuselvan\Desktop\Book1.xlsx"
DB_PATH = "assets.db"

def import_excel_to_db():
    print(f"Importing {EXCEL_PATH} to {DB_PATH}")
    
    try:
        # Read Excel file
        df = pd.read_excel(EXCEL_PATH, sheet_name='employees')
        print(f"Found {len(df)} rows in 'employees' sheet")
        
        # Clean column names (critical step)
        df.columns = [str(col).strip().lower().replace(' ', '_').replace('-', '_') 
                     for col in df.columns]
        print("Cleaned column names:", df.columns.tolist())
        
        # Connect to SQLite
        with sqlite3.connect(DB_PATH) as conn:
            # Import to SQLite
            df.to_sql(
                name='employees',
                con=conn,
                if_exists='replace',  # Overwrites if table exists
                index=False
            )
            
            # Verify
            imported = pd.read_sql('SELECT * FROM employees', conn)
            print(f"Successfully imported {len(imported)} rows to 'employees' table")
            
            # Print sample
            print("\nFirst 2 rows in database:")
            print(imported.head(2))
            
    except Exception as e:
        print(f"\nError during import: {str(e)}")

if __name__ == "__main__":
    import_excel_to_db()
    input("\nPress Enter to exit...")