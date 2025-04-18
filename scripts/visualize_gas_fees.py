import pandas as pd
import pytz
import plotly.express as px
import plotly.graph_objects as go


df = pd.read_csv("data/gas_fees_cleaned.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
df = df.dropna(subset=["timestamp"])
ist = pytz.timezone("Asia/Kolkata")
df["timestamp_local"] = df["timestamp"].dt.tz_convert(ist)
fig1 = px.line(
    df,
    x="timestamp_local",
    y="base_fee_gwei",
    title="📈 Ethereum Base Fee Over Time (IST)",
    labels={"timestamp_local": "Time (IST)", "base_fee_gwei": "Base Fee (GWEI)"},
    template="plotly_dark",
)

fig1.update_traces(line=dict(color="#00CC96", width=2), hovertemplate="Time: %{x}<br>Fee: %{y:.2f} GWEI")
fig1.update_layout(title_font_size=20, xaxis_title_font_size=16, yaxis_title_font_size=16)

fig1.show()

df["hour_of_day_local"] = df["timestamp_local"].dt.hour
hourly_fee = df.groupby("hour_of_day_local")["base_fee_gwei"].mean().reindex(range(24), fill_value=0).reset_index()

fig2 = px.bar(
    hourly_fee,
    x="hour_of_day_local",
    y="base_fee_gwei",
    title="🕒 Average Ethereum Gas Fee by Hour (IST)",
    labels={"hour_of_day_local": "Hour (IST)", "base_fee_gwei": "Average Base Fee (GWEI)"},
    color="base_fee_gwei",
    color_continuous_scale="Viridis",
    template="plotly_dark",
)

fig2.update_traces(hovertemplate="Hour: %{x}h<br>Fee: %{y:.2f} GWEI")
fig2.update_layout(title_font_size=20, xaxis_title_font_size=16, yaxis_title_font_size=16)

fig2.show()
