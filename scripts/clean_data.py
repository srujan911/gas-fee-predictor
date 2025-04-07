import pandas as pd
df = pd.read_csv("data/gas_fees.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df_cleaned = df.dropna(subset=["timestamp", "block_number", "base_fee_gwei"])
df_cleaned["timestamp"] = df_cleaned["timestamp"].astype("int64") // 10**9
df_cleaned.to_csv("data/gas_fees_cleaned.csv", index=False)

print(f"✅ Cleaned data saved to 'data/gas_fees_cleaned.csv' ({len(df_cleaned)} rows)")
