import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import os
import json

OUTPUT_FILE = "02b_sp500_matrix_output.csv"
START_DATE = (pd.Timestamp.now() - pd.DateOffset(weeks=1)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")
MAX_TICKER_SLOTS = 500

def get_current_tickers():
    """Scrape current S&P 500 tickers from Wikipedia."""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {'User-Agent': 'QuantProject/1.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        html = response.text
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        table_match = re.search(r'<table[^>]*id="constituents"[^>]*>(.*?)</table>', html, re.DOTALL)
        if not table_match:
            table_match = re.search(r'<table[^>]*class="wikitable sortable"[^>]*>(.*?)</table>', html, re.DOTALL)
        
        if table_match:
            tickers = set()
            rows = re.findall(r'<tr>(.*?)</tr>', table_match.group(1), re.DOTALL)
            for row in rows:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if cells:
                    link_match = re.search(r'<a[^>]*>([A-Z]{1,5}(?:-[A-Z]{1,3})?)</a>', cells[0])
                    if link_match:
                        t = link_match.group(1)
                        if t not in ['A', 'THE', 'NYSE', 'NASDAQ', 'S&P', 'SPX']:
                            tickers.add(t)
            
            if len(tickers) >= 400:
                return sorted(list(tickers))
    except Exception as e:
        print(f"    Error: {e}")
    
    return None

def generate_sp500_matrix():
    """Generate S&P 500 matrix for the date range."""
    
    print(f"\n{'='*60}")
    print(f"S&P 500 Matrix Generator")
    print(f"{'='*60}")
    print(f"Date Range: {START_DATE} to {END_DATE}")
    
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    # Get current tickers
    print("\n1. Getting current S&P 500 tickers...")
    current_tickers = get_current_tickers()
    if not current_tickers:
        print("   ✗ Failed. Aborting.")
        return False
    print(f"   ✓ {len(current_tickers)} current tickers")
    
    # For 1 week, just use current tickers for all days (no historical changes needed)
    forward_dates = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
    
    print(f"\n2. Writing {OUTPUT_FILE}...")
    DATE_WIDTH = 14
    TICKER_WIDTH = 14
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write(f"{'index'.ljust(DATE_WIDTH)}")
        for i in range(MAX_TICKER_SLOTS):
            f.write(f", {f'ticker_{i+1}'.ljust(TICKER_WIDTH)}")
        f.write("\n")
        
        f.write(f"{'-' * (DATE_WIDTH - 1)}")
        for i in range(MAX_TICKER_SLOTS):
            f.write(f", {'-' * (TICKER_WIDTH - 1)}")
        f.write("\n")
        
        for d in forward_dates:
            date_str = d.strftime("%Y-%m-%d")
            padded = list(current_tickers[:MAX_TICKER_SLOTS])
            while len(padded) < MAX_TICKER_SLOTS:
                padded.append('EMPTY')
            
            f.write(f"{date_str.ljust(DATE_WIDTH)}")
            for t in padded:
                f.write(f", {str(t).ljust(TICKER_WIDTH)}")
            f.write("\n")
    
    file_size = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"\n{'='*60}")
    print(f"✓ Generated! {file_size:.1f} KB, {len(current_tickers)} tickers, {len(forward_dates)} days")
    print(f"{'='*60}")
    
    return True

if __name__ == "__main__":
    generate_sp500_matrix()