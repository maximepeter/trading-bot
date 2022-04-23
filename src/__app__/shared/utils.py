import pandas as pd
import ta


def exponentialMovingAverage(df: pd.DataFrame, window: int) -> pd.DataFrame:
    ema = df.ewm(
        span=window, adjust=False, min_periods=window).mean()
    return ema


def macd(df) -> None:
    df["26DayEMA"] = exponentialMovingAverage(df["price"], 26)
    df["12DayEMA"] = exponentialMovingAverage(df["price"], 12)
    # df["macd"] = df["12DayEMA"] - df["26DayEMA"]
    macd = ta.trend.MACD(close=df['price'])
    df["macd"] = macd.macd()
    df['macdSignalLine'] = macd.macd_signal()
    df['macdHistogram'] = macd.macd_diff()


def rsi(df, window) -> pd.DataFrame:
    rsi = ta.momentum.RSIIndicator(df['price'], window=window)
    df['rsi'] = rsi.rsi()
    return df


def generateRecomendationFromMacd(df: pd.DataFrame) -> None:
    df['macdRecomendation'] = 'hold'
    df['macdChange'] = df['macdHistogram'] * df['macdHistogram'].shift() < 0
    # df.loc[(df['macdHistogram']
    #         > 0) & df['macdChange'], 'macdRecomendation'] = 'buy'
    # df.loc[(df['macdHistogram']
    #         < 0) & df['macdChange'], 'macdRecomendation'] = 'sell'
    # df.loc[((df['macdHistogram']
    #         > 0) & (df['macdHistogram'] - df['macdHistogram'].shift() > 0)) | ((df['macdHistogram']
    #                                                                             < 0) & (abs(df['macdHistogram']) - abs(df['macdHistogram'].shift()) < 0)), 'macdRecomendation'] = 'buy'
    # df.loc[((df['macdHistogram']
    #         < 0) & (abs(df['macdHistogram']) - abs(df['macdHistogram'].shift()) > 0)) | ((df['macdHistogram']
    #                                                                                       > 0) & (df['macdHistogram'] - df['macdHistogram'].shift() < 0)), 'macdRecomendation'] = 'sell'
    # df.loc[(df['macdHistogram']
    #         > 0) & (df['macdHistogram'] - df['macdHistogram'].shift() > 0), 'macdRecomendation'] = 'buy'
    # df.loc[(df['macdHistogram']
    #         < 0) & (abs(df['macdHistogram']) - abs(df['macdHistogram'].shift()) > 0), 'macdRecomendation'] = 'sell'
    df.loc[(df['macdHistogram']
            > 0) & (df['macdHistogram'] - df['macdHistogram'].shift() < 0) & (df['macdHistogram'].shift() - df['macdHistogram'].shift(periods=2) > 0), 'macdRecomendation'] = 'sell'
    df.loc[(df['macdHistogram']
            < 0) & (abs(df['macdHistogram']) - abs(df['macdHistogram'].shift()) < 0) & (abs(df['macdHistogram'].shift()) - abs(df['macdHistogram'].shift(periods=2)) > 0), 'macdRecomendation'] = 'buy'


def generateRecomendationFromRsi(df: pd.DataFrame, sellThreshold: float, buyThreshold: float) -> None:
    df.loc[df['rsi']
           <= buyThreshold, 'rsiRecomendation'] = 'buy'
    df.loc[df['rsi']
           >= sellThreshold, 'rsiRecomendation'] = 'sell'
    df.loc[(df['rsi'] > buyThreshold) & (
        df['rsi'] < sellThreshold), 'rsiRecomendation'] = 'hold'


def generateFinalRecomendation(df: pd.DataFrame) -> None:
    # df.loc[(df['rsiRecomendation'] == 'sell') &
    #        (df['macdRecomendation'] == 'sell'), 'endRecomendation'] = 'sell'
    # df.loc[(df['rsiRecomendation'] == 'buy') &
    #        (df['macdRecomendation'] == 'buy'), 'endRecomendation'] = 'buy'
    # df.loc[df['rsiRecomendation'] == 'hold', 'endRecomendation'] = 'hold'
    # df.loc[df['rsiRecomendation'] !=
    #        df['macdRecomendation'], 'endRecomendation'] = 'hold'
    df['endRecomendation'] = df['macdRecomendation']
