import pandas_market_calendars as mcal
import pandas as pd
import numpy as np
from datetime import datetime

OUTPUT_FILE = "01b_market_calendar_output.csv"
START_DATE = (pd.Timestamp.now() - pd.DateOffset(years=1)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")
W = 25

def generate_schedule():
    nyse = mcal.get_calendar("NYSE")
    all_days = pd.DataFrame({"index": pd.date_range(start=START_DATE, end=END_DATE, freq="D")})
    schedule = nyse.schedule(start_date=START_DATE, end_date=END_DATE).reset_index()
    schedule.columns = ["index", "market_open", "market_close"]
    full_df = pd.merge(all_days, schedule, on="index", how="left")
    full_df["market_open"] = pd.to_datetime(full_df["market_open"], utc=True).dt.tz_convert("America/New_York")
    full_df["market_close"] = pd.to_datetime(full_df["market_close"], utc=True).dt.tz_convert("America/New_York")

    reg_start = full_df["market_open"].dt.hour * 3600 + full_df["market_open"].dt.minute * 60 + full_df["market_open"].dt.second
    post_start = full_df["market_close"].dt.hour * 3600 + full_df["market_close"].dt.minute * 60 + full_df["market_close"].dt.second
    is_open = full_df["market_open"].notna()
    pre_start = np.where(is_open, 14400, -1)
    post_end = np.where(is_open, np.where(post_start < 57600, 61200, 72000), -1)

    def format_col(s): return pd.Series(s).fillna(-1).astype(int).astype(str).replace("-1", "not_applicable")
    full_df["premarket_start"], full_df["regular_start"] = format_col(pre_start), format_col(reg_start)
    full_df["post_start"], full_df["post_end"] = format_col(post_start), format_col(post_end)
    full_df["index"] = full_df["index"].dt.strftime("%Y-%m-%d")

    with open(OUTPUT_FILE, "w") as f:
        f.write(f"{'index'.ljust(W)}, {'premarket_start'.ljust(W)}, {'regular_start'.ljust(W)}, {'post_start'.ljust(W)}, {'post_end'.ljust(W)}\n")
        f.write(f"{('-' * (W - 1)).ljust(W)}, " * 4 + f"{('-' * (W - 1)).ljust(W)}\n")
        for row in full_df.itertuples(index=False):
            f.write(f"{str(row.index).ljust(W)}, {str(row.premarket_start).ljust(W)}, {str(row.regular_start).ljust(W)}, {str(row.post_start).ljust(W)}, {str(row.post_end).ljust(W)}\n")
    print(f"File 1 Sync: {START_DATE} to {END_DATE}")

if __name__ == "__main__": generate_schedule()