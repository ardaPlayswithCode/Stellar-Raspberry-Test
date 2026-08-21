import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
import time

FILE_1_PATH = "01b_market_calendar_output.csv"
FILE_2_PATH = "02b_sp500_matrix_output.csv"
OUTPUT_PARQUET = "03b_output.parquet"

def generate_file_3():
    t0 = time.time()
    print("=" * 60)
    print("File 3: Parquet Generator (1 Week)")
    print("=" * 60)
    
    print("\n1. Loading calendar...")
    df1 = pd.read_csv(FILE_1_PATH, engine='python')
    df1.columns = [c.strip() for c in df1.columns]
    df1['index'] = df1['index'].astype(str).str.strip()
    df1 = df1[df1['index'].str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)]
    print(f"   ✓ {len(df1)} rows")
    
    print("2. Loading S&P 500 matrix...")
    df2 = pd.read_csv(FILE_2_PATH, engine='python', dtype=str, keep_default_na=False)
    df2.columns = [c.strip() for c in df2.columns]
    df2['index'] = df2['index'].str.strip()
    df2 = df2[df2['index'].str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)]
    print(f"   ✓ {len(df2)} rows × {len(df2.columns)-1} cols")
    
    print("3. Merging...")
    merged = df1.merge(df2, on='index', how='inner')
    print(f"   ✓ {len(merged)} days")
    
    meta_cols = ['index', 'premarket_start', 'regular_start', 'post_start', 'post_end']
    ticker_cols = [c for c in merged.columns if c not in meta_cols]
    
    print("4. Building ticker universe...")
    all_tickers = set()
    for col in ticker_cols:
        for v in merged[col].unique():
            v = str(v).strip()
            if v and v not in ['EMPTY', 'nan', '']:
                all_tickers.add(v)
    
    universe = sorted(list(all_tickers))
    print(f"   ✓ {len(universe)} unique tickers")
    
    ohlcv = ['open', 'high', 'low', 'close', 'vol']
    flat_cols = [f"{t}_{f}" for t in universe for f in ohlcv]
    ticker_to_idx = {t: i for i, t in enumerate(universe)}
    
    trading = merged[merged['premarket_start'].str.strip().str.isnumeric()].copy()
    print(f"\n5. Processing {len(trading)} trading days...")
    
    writer = None
    total_rows = 0
    np.random.seed(42)
    BATCH = 2  # Small batch for 1 week
    
    for batch_start in range(0, len(trading), BATCH):
        batch_end = min(batch_start + BATCH, len(trading))
        batch = trading.iloc[batch_start:batch_end]
        frames = []
        
        for _, row in batch.iterrows():
            date_str = row['index']
            p_start = int(float(row['premarket_start']))
            r_start = int(float(row['regular_start']))
            po_start = int(float(row['post_start']))
            po_end = int(float(row['post_end']))
            
            seconds = np.arange(p_start, po_end + 1, dtype=np.int32)
            n_sec = len(seconds)
            
            active = set()
            for col in ticker_cols:
                v = str(row[col]).strip()
                if v and v not in ['EMPTY', 'nan']:
                    active.add(v)
            
            n_active = len(active)
            if n_active == 0:
                continue
                
            prices = 100 * np.exp(np.cumsum(np.random.normal(0, 0.001, (n_active, n_sec)), axis=1))
            vols = np.random.randint(1000, 5000000, (n_active, n_sec)).astype(np.float32)
            
            data = np.full((n_sec, len(flat_cols)), np.nan, dtype=np.float32)
            for t_idx, ticker in enumerate(active):
                if ticker in ticker_to_idx:
                    c = ticker_to_idx[ticker] * 5
                    p = prices[t_idx]
                    data[:, c] = p
                    data[:, c+1] = p * np.random.uniform(1.0, 1.02, n_sec)
                    data[:, c+2] = p * np.random.uniform(0.98, 1.0, n_sec)
                    data[:, c+3] = p
                    data[:, c+4] = vols[t_idx]
            
            df_day = pd.DataFrame(data, columns=flat_cols)
            df_day['timestamp'] = pd.Timestamp(date_str, tz="America/New_York") + pd.to_timedelta(seconds, unit='s')
            df_day['premarket_start'] = np.uint32(p_start)
            df_day['regular_start'] = np.uint32(r_start)
            df_day['post_start'] = np.uint32(po_start)
            df_day['post_end'] = np.uint32(po_end)
            
            frames.append(df_day)
            total_rows += n_sec
        
        if frames:
            batch_df = pd.concat(frames, ignore_index=True)
            table = pa.Table.from_pandas(batch_df)
            
            if writer is None:
                writer = pq.ParquetWriter(OUTPUT_PARQUET, table.schema, compression='snappy')
            
            writer.write_table(table)
        
        elapsed = time.time() - t0
        print(f"   Days {batch_start+1}-{batch_end} | {total_rows:,} rows | {elapsed:.0f}s")
    
    if writer:
        writer.close()
        size_mb = Path(OUTPUT_PARQUET).stat().st_size / (1024*1024)
        print(f"\n{'='*60}")
        print(f"✓ DONE in {time.time()-t0:.0f}s")
        print(f"  {len(trading)} days, {total_rows:,} rows, {size_mb:.1f} MB")
        print(f"  {len(universe)} tickers, {len(flat_cols)} OHLCV columns")
        print(f"{'='*60}")

if __name__ == "__main__":
    generate_file_3()