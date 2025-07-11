#!/usr/bin/env python3
"""
Generate sample Iris dataset CSV file for testing
"""

import pandas as pd
import numpy as np
from pathlib import Path

def generate_iris_csv(filename="iris.csv"):
    """Generate a sample Iris dataset"""
    
    # Define the full sample data
    data = {
        'sepal_length': [
            # Setosa
            5.1, 4.9, 4.7, 4.6, 5.0, 5.4, 4.6, 5.0, 4.4, 4.9,
            5.4, 4.8, 4.8, 4.3, 5.8, 5.7, 5.4, 5.1, 5.7, 5.1,
            # Versicolor
            7.0, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2,
            5.0, 5.9, 6.0, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6,
            # Virginica
            6.3, 5.8, 7.1, 6.3, 6.5, 7.6, 4.9, 7.3, 6.7, 7.2,
            6.5, 6.4, 6.8, 5.7, 5.8, 6.4, 6.5, 7.7, 7.7, 6.0
        ],
        'sepal_width': [
            # Setosa
            3.5, 3.0, 3.2, 3.1, 3.6, 3.9, 3.4, 3.4, 2.9, 3.1,
            3.7, 3.4, 3.0, 3.0, 4.0, 4.4, 3.9, 3.5, 3.8, 3.8,
            # Versicolor
            3.2, 3.2, 3.1, 2.3, 2.8, 2.8, 3.3, 2.4, 2.9, 2.7,
            2.0, 3.0, 2.2, 2.9, 2.9, 3.1, 3.0, 2.7, 2.2, 2.5,
            # Virginica
            3.3, 2.7, 3.0, 2.9, 3.0, 3.0, 2.5, 2.9, 2.5, 3.6,
            3.2, 2.7, 3.0, 2.5, 2.8, 3.2, 3.0, 3.8, 2.6, 2.2
        ],
        'petal_length': [
            # Setosa
            1.4, 1.4, 1.3, 1.5, 1.4, 1.7, 1.4, 1.5, 1.4, 1.5,
            1.5, 1.6, 1.4, 1.1, 1.2, 1.5, 1.3, 1.4, 1.7, 1.5,
            # Versicolor
            4.7, 4.5, 4.9, 4.0, 4.6, 4.5, 4.7, 3.3, 4.6, 3.9,
            3.5, 4.2, 4.0, 4.7, 3.6, 4.4, 4.5, 4.1, 4.5, 3.9,
            # Virginica
            6.0, 5.1, 5.9, 5.6, 5.8, 6.6, 4.5, 6.3, 5.8, 6.1,
            5.1, 5.3, 5.5, 5.0, 5.1, 5.3, 5.5, 6.7, 6.9, 5.0
        ],
        'petal_width': [
            # Setosa
            0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.3, 0.2, 0.2, 0.1,
            0.2, 0.2, 0.1, 0.1, 0.2, 0.4, 0.4, 0.3, 0.3, 0.3,
            # Versicolor
            1.4, 1.5, 1.5, 1.3, 1.5, 1.3, 1.6, 1.0, 1.3, 1.4,
            1.0, 1.5, 1.2, 1.4, 1.3, 1.4, 1.5, 1.0, 1.5, 1.1,
            # Virginica
            2.5, 1.9, 2.1, 1.8, 2.2, 2.1, 1.7, 1.8, 1.8, 2.5,
            2.0, 1.9, 2.1, 2.0, 2.4, 2.3, 1.8, 2.2, 2.3, 1.5
        ],
        'species': (
            ['setosa'] * 20 +
            ['versicolor'] * 20 +
            ['virginica'] * 20
        )
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle the data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Generated {filename} with {len(df)} samples")
    print(f"Species distribution: {df['species'].value_counts().to_dict()}")
    
    return df

if __name__ == "__main__":
    # Generate the CSV file
    df = generate_iris_csv()
    
    # Show sample data
    print("\nSample data:")
    print(df.head(10))
    
    # Show data info
    print("\nDataset info:")
    print(df.info())
    
    print("\nStatistics by species:")
    print(df.groupby('species').describe())