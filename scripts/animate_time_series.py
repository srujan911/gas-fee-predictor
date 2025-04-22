import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pytz

df = pd.read_csv("data/gas_fees_with_predictions.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
ist = pytz.timezone("Asia/Kolkata")
df["timestamp_local"] = df["timestamp"].dt.tz_convert(ist)

fig, ax = plt.subplots(figsize=(14, 6))
line_real, = ax.plot([], [], color='#2a9d8f', label='Real Fee', linewidth=2)
line_pred, = ax.plot([], [], color='#e76f51', linestyle='--', label='Predicted Fee', linewidth=2)
ax.set_xlim(df["timestamp_local"].min(), df["timestamp_local"].max())
ax.set_ylim(0, max(df["base_fee_gwei"].max(), df["predicted_fee"].max()) * 1.1)

ax.set_title("Ethereum Gas Fee Over Time ", fontsize=20, fontweight='bold')
ax.set_xlabel("Time")
ax.set_ylabel("Base Fee (GWEI)")
ax.legend()
ax.grid(True, linestyle='--', alpha=0.5)

def update(frame):
    x = df["timestamp_local"][:frame]
    y_real = df["base_fee_gwei"][:frame]
    y_pred = df["predicted_fee"][:frame]
    line_real.set_data(x, y_real)
    line_pred.set_data(x, y_pred)
    return line_real, line_pred

ani = animation.FuncAnimation(fig, update, frames=len(df), interval=100, blit=True)
plt.tight_layout()
plt.show()
