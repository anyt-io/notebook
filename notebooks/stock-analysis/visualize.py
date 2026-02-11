import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

df = pd.read_csv("stocks.csv", parse_dates=["Date"])
stock_name = df["Stock"].iloc[0]
ticker = df["Ticker"].iloc[0]

fig, axes = plt.subplots(3, 1, figsize=(12, 14), sharex=True)
fig.suptitle(f"{stock_name} ({ticker}) — 30-Day Stock Analysis", fontsize=16, fontweight="bold", y=0.98)

# --- Price chart with high/low range ---
ax1 = axes[0]
ax1.fill_between(df["Date"], df["Low"], df["High"], alpha=0.2, color="steelblue", label="High–Low Range")
ax1.plot(df["Date"], df["Close"], color="steelblue", linewidth=2, label="Close Price")
ax1.plot(df["Date"], df["Open"], color="darkorange", linewidth=1, linestyle="--", alpha=0.7, label="Open Price")
ax1.set_ylabel("Price (USD)", fontsize=12)
ax1.set_title("Price Movement", fontsize=13)
ax1.legend(loc="upper right")
ax1.grid(True, alpha=0.3)

# Annotate start and end close prices
for idx in [0, len(df) - 1]:
    ax1.annotate(
        f"${df['Close'].iloc[idx]:.2f}",
        xy=(df["Date"].iloc[idx], df["Close"].iloc[idx]),
        textcoords="offset points",
        xytext=(0, 12),
        fontsize=9,
        fontweight="bold",
        ha="center",
        color="steelblue",
    )

# --- Daily price change ---
ax2 = axes[1]
df["Daily Change"] = df["Close"].diff()
colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in df["Daily Change"]]
ax2.bar(df["Date"], df["Daily Change"], color=colors, width=0.8)
ax2.axhline(y=0, color="gray", linewidth=0.8)
ax2.set_ylabel("Daily Change (USD)", fontsize=12)
ax2.set_title("Daily Price Change", fontsize=13)
ax2.grid(True, alpha=0.3)

# --- Volume ---
ax3 = axes[2]
vol_colors = ["#2ecc71" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#e74c3c" for i in range(len(df))]
ax3.bar(df["Date"], df["Volume"] / 1e6, color=vol_colors, width=0.8, alpha=0.8)
ax3.set_ylabel("Volume (Millions)", fontsize=12)
ax3.set_title("Trading Volume", fontsize=13)
ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax3.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha="right")

# Summary stats annotation
total_change = df["Close"].iloc[-1] - df["Close"].iloc[0]
pct_change = (total_change / df["Close"].iloc[0]) * 100
avg_volume = df["Volume"].mean()
high_max = df["High"].max()
low_min = df["Low"].min()

summary = (
    f"Period: {df['Date'].iloc[0].strftime('%b %d')} – {df['Date'].iloc[-1].strftime('%b %d, %Y')}\n"
    f"Change: ${total_change:+.2f} ({pct_change:+.1f}%)\n"
    f"Range: ${low_min:.2f} – ${high_max:.2f}\n"
    f"Avg Volume: {avg_volume/1e6:.1f}M"
)
fig.text(0.13, 0.01, summary, fontsize=10, family="monospace",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))

plt.tight_layout(rect=[0, 0.06, 1, 0.96])

output_path = output_dir / "stock_visualization.png"
fig.savefig(output_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {output_path}")
