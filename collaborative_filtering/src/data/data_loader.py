import pandas as pd

import pandas as pd
import os

def load_csv(file_path):
    """
    Load a CSV file into a pandas DataFrame.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: The loaded data or None if file not found
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        absolute_path = os.path.join(base_dir, file_path)
        
        if not os.path.exists(absolute_path):
            print(f"File not found: {absolute_path}")
            return None
            
        df = pd.read_csv(absolute_path)
        print(f"Successfully loaded {file_path} with {len(df)} rows")
        return df
        
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None