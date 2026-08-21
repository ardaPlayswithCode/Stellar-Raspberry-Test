import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

PARQUET_FILE = "data_onboarding/03b_output.parquet"

def generate_4hour_chart():
    print("=" * 60)
    print("AAPL 4-Hour Candlestick Chart (CNN-Ready)")
    print("=" * 60)
    
    # Read only AAPL
    cols = ['timestamp', 'AAPL_open', 'AAPL_high', 'AAPL_low', 'AAPL_close']
    df = pd.read_parquet(PARQUET_FILE, columns=cols)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    df = df.rename(columns={
        'AAPL_open': 'open', 'AAPL_high': 'high', 
        'AAPL_low': 'low', 'AAPL_close': 'close'
    }).set_index('timestamp')
    
    # Resample to 4-hour
    bars = df.resample('4h').agg({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'
    }).dropna()
    
    print(f"   {len(bars)} 4-hour bars")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Use numeric x-axis for proper bar widths
    x = np.arange(len(bars))
    
    up = bars['close'].values >= bars['open'].values
    down = ~up
    
    # Wicks
    ax.vlines(x[up], bars['low'].values[up], bars['high'].values[up], 
              color='#26a69a', linewidth=1)
    ax.vlines(x[down], bars['low'].values[down], bars['high'].values[down], 
              color='#ef5350', linewidth=1)
    
    # Bodies - wider bars
    body_width = 0.8
    ax.bar(x[up], bars['close'].values[up] - bars['open'].values[up], 
           body_width, bottom=bars['open'].values[up], 
           color='#26a69a', edgecolor='#26a69a')
    ax.bar(x[down], bars['open'].values[down] - bars['close'].values[down], 
           body_width, bottom=bars['close'].values[down], 
           color='#ef5350', edgecolor='#ef5350')
    
    # Auto-scale with small margin
    ax.autoscale()
    y_margin = (bars['high'].max() - bars['low'].min()) * 0.02
    ax.set_ylim(bars['low'].min() - y_margin, bars['high'].max() + y_margin)
    
    # Remove everything
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout(pad=0)
    plt.savefig('aapl_4hour_cnn.png', dpi=100, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"\n✓ Saved as aapl_4hour_cnn.png")
    plt.close()

if __name__ == "__main__":
    generate_4hour_chart()