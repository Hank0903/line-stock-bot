import mplfinance as mpf
import pandas as pd

def plot_kline(df: pd.DataFrame, stock_no: str, filepath: str, show_sma=False):
    df = df.copy()
    df.set_index('日期', inplace=True)

    df.rename(columns={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '收盤價': 'Close',
        '成交量': 'Volume'
    }, inplace=True)

    mc = mpf.make_marketcolors(
        up='red', down='green', edge='inherit', wick='inherit', volume='inherit')
    s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc)

    mpf.plot(
        df,
        type='candle',
        mav=(10, 30) if show_sma else (),
        volume=True,
        title=f"{stock_no} K 線圖 (近 {len(df)} 日)",
        style=s,
        savefig=filepath
    )
