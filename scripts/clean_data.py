import pandas as pd

def clean_gas_data(input_path="data/gas_fees.csv", output_path="data/gas_fees_cleaned.csv"):
    try:
        print(f"Reading data from: {input_path}")
        df = pd.read_csv(input_path)
        print("Initial DataFrame shape:", df.shape)
        df.dropna(inplace=True)
        print("After dropna, shape:", df.shape)
        df.drop_duplicates(inplace=True)
        print("After dropping duplicates, shape:", df.shape)
        print("Converting timestamp column...")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')  
        print("Timestamp conversion preview:", df["timestamp"].head())
        df.dropna(subset=["timestamp"], inplace=True)
        print("After removing invalid timestamps, shape:", df.shape)
        print("Sorting data by block_number...")
        df.sort_values("block_number", inplace=True)

        if df.empty:
            print("❌ No data to save after cleaning.")
            return
        print(f"Saving cleaned data to: {output_path}")
        df.to_csv(output_path, index=False)
        print("✅ Cleaned data saved successfully.")

    except Exception as e:
        print("❌ Error cleaning data:", e)
        print("Full error details:", str(e))

clean_gas_data()