import pandas as pd
import os
import sqlite3

# Define File Paths
INPUT_FILE = 'data_cleaning/politics/combined_politics_results.csv'
OUTPUT_DIR = 'analysis/politics/table'
OUTPUT_FILE = 'model_language_reliability.csv'

def get_language(row_id):
    """
    Extract language code from the question ID.
    Format: 'PQ_01_Econ' -> 'ENG' (3 parts)
            'PQ_01_Econ_KOR' -> 'KOR' (4 parts)
    """
    parts = str(row_id).split('_')
    if len(parts) == 3:
        return 'ENG'
    elif len(parts) > 3:
        return parts[-1]  # Returns KOR, CHN, ARAB, etc.
    return 'Unknown'

def main():
    # 1. Create Output Directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 2. Check Input File
    if not os.path.exists(INPUT_FILE):
        print(f"[Error] Input file not found: {INPUT_FILE}")
        return

    # 3. Load Data using SQLite (Database Requirement)
    print("Loading data into SQLite database for aggregation...")
    conn = sqlite3.connect(':memory:')
    
    # Load CSV to SQLite Table
    df_raw = pd.read_csv(INPUT_FILE)
    df_raw.to_sql('raw_data', conn, index=False, if_exists='replace')

    # Register Python function to use in SQL
    conn.create_function("get_language", 1, get_language)

    # 4. Execute SQL Query
    # Calculate Average Variance grouped by Model and Language
    query = """
    SELECT 
        Model, 
        get_language(id) as Language, 
        AVG(Variance) as Mean_Variance
    FROM raw_data
    GROUP BY Model, Language
    """
    
    df_agg = pd.read_sql(query, conn)
    conn.close()

    # 5. Pivot Data for Visualization
    # Row (Index) = Language
    # Column = Model
    # Value = Mean_Variance
    df_pivot = df_agg.pivot(index='Language', columns='Model', values='Mean_Variance')

    # Optional: Clean up formatting (round to 3 decimal places)
    df_pivot = df_pivot.round(3)

    # 6. Save Results
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    df_pivot.to_csv(output_path)

    print(f"\n[Success] Reliability analysis completed.")
    print(f" - Aggregated results saved to: {output_path}")
    
    # Display preview
    print("\n[Preview of Reliability Table (Lower Value = More Reliable)]")
    print(df_pivot)

if __name__ == "__main__":
    main()