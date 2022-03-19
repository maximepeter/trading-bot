import pandas as pd


def exponentialMovingAverage(df: pd.DataFrame, window: int) -> pd.DataFrame:
    ema = df.ewm(
        span=window, adjust=False, min_periods=window).mean()
    return ema


def macd(df) -> pd.DataFrame:
    df["26DayEMA"] = exponentialMovingAverage(df["price"], 26)
    df["12DayEMA"] = exponentialMovingAverage(df["price"], 12)
    df["macd"] = df["12DayEMA"] - df["26DayEMA"]
    return df["macd"]


def macdSignalLine(df) -> None:
    df['macdSignalLine'] = exponentialMovingAverage(df["macd"], 9)


def macdHistogram(df) -> None:
    df['macdHistogram'] = df['macd'] - df['macdSignalLine']


def rsi(df, window) -> pd.DataFrame:
    df['diff'] = df['price'].diff(1)

    # Calculate Avg. Gains/Losses
    df['gain'] = df['diff'].clip(lower=0).round(2)
    df['loss'] = df['diff'].clip(upper=0).abs().round(2)

    # Get initial Averages
    df['avg_gain'] = df['gain'].rolling(
        window=window, min_periods=window).mean()[:window+1]
    df['avg_loss'] = df['loss'].rolling(
        window=window, min_periods=window).mean()[:window+1]

    # Get WMS averages
    # Average Gains
    for i, row in enumerate(df['avg_gain'].iloc[window+1:]):
        df['avg_gain'].iloc[i + window + 1] = (df['avg_gain'].iloc[i + window] *
                                               (window - 1) +
                                               df['gain'].iloc[i + window + 1])\
            / window
    # Average Losses
    for i, row in enumerate(df['avg_loss'].iloc[window+1:]):
        df['avg_loss'].iloc[i + window + 1] = (df['avg_loss'].iloc[i + window] *
                                               (window - 1) +
                                               df['loss'].iloc[i + window + 1])\
            / window

        # Calculate RS Values
    df['rs'] = df['avg_gain'] / df['avg_loss']
    df['rsi'] = 100 - (100 / (1.0 + df['rs']))
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
            < 0) & (abs(df['macdHistogram']) - abs(df['macdHistogram'].shift()) > 0) & (abs(df['macdHistogram'].shift()) - abs(df['macdHistogram'].shift(periods=2)) > 0), 'macdRecomendation'] = 'buy'


def generateRecomendationFromRsi(df: pd.DataFrame, sellThreshold: float, buyThreshold: float) -> None:
    df.loc[df['rsi']
           <= buyThreshold, 'rsiRecomendation'] = 'buy'
    df.loc[df['rsi']
           >= sellThreshold, 'rsiRecomendation'] = 'sell'
    df.loc[(df['rsi'] > buyThreshold) & (
        df['rsi'] < sellThreshold), 'rsiRecomendation'] = 'hold'


def generateFinalRecomendation(df: pd.DataFrame) -> None:
    df.loc[(df['rsiRecomendation'] == 'sell') &
           (df['macdRecomendation'] == 'sell'), 'endRecomendation'] = 'sell'
    df.loc[(df['rsiRecomendation'] == 'buy') &
           (df['macdRecomendation'] == 'buy'), 'endRecomendation'] = 'buy'
    df.loc[df['rsiRecomendation'] == 'hold', 'endRecomendation'] = 'hold'
    df.loc[df['rsiRecomendation'] !=
           df['macdRecomendation'], 'endRecomendation'] = 'hold'
