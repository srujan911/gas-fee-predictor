import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pytz

sns.set_theme(style="whitegrid")
df = pd.read_csv("data/gas_fees_with_predictions.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
ist = pytz.timezone("Asia/Kolkata")
df["timestamp_local"] = df["timestamp"].dt.tz_convert(ist)
plt.figure(figsize=(14, 6))
plt.plot(df["timestamp_local"], df["base_fee_gwei"], label="Real Base Fee (GWEI)", color="#2a9d8f", linewidth=2)
plt.plot(df["timestamp_local"], df["predicted_fee"], label="Predicted Base Fee (GWEI)", color="#e76f51", linewidth=2, linestyle="--")

plt.title("🎯 Real vs Predicted Ethereum Gas Fee (IST)", fontsize=16, fontweight="bold")
plt.xlabel("Time (IST)", fontsize=12)
plt.ylabel("Base Fee (GWEI)", fontsize=12)
plt.xticks(rotation=30)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b %H:%M'))
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
