import pandas as pd
import ta


def macd(df: pd.DataFrame) -> None:
    """Calculate the MACD(signal line and histogram) for a given dataframe representing the prices of a coin. The dataframe must contain a 'price' column.

    Args:
        df (pd.DataFrame): coin's infos
    """
    macd = ta.trend.MACD(close=df['price'])
    df["macd"] = macd.macd()
    df['macdSignalLine'] = macd.macd_signal()
    df['macdHistogram'] = macd.macd_diff()


def rsi(df: pd.DataFrame, window: int) -> None:
    """Calculate the RSI for a given dataframe representing the prices of a coin. The dataframe must contain a 'price' column.

    Args:
        df (pd.DataFrame): coin's infos
        window (int): RSI rolling window
    """
    rsi = ta.momentum.RSIIndicator(df['price'], window=window)
    df['rsi'] = rsi.rsi()


def generateRecomendationFromMacd(df: pd.DataFrame) -> None:
    """Calculate the MACD's recomendations for a given dataframe representing the macd values of a coin. The dataframe must contain a 'macd' column. Generates a 'macdRecomendation' column.

    Args:
        df (pd.DataFrame): Coin's infos
    """
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
    """Calculate the RSI's recomendations for a given dataframe representing the rsi values of a coin. The dataframe must contain a 'rsi' column. Generates a 'rsiRecomendation' column.

    Args:
        df (pd.DataFrame): Coin's infos
        sellThreshold (float): RSI's selling threshold
        buyThreshold (float): RSI's buying threshold
    """
    df.loc[df['rsi']
           <= buyThreshold, 'rsiRecomendation'] = 'buy'
    df.loc[df['rsi']
           >= sellThreshold, 'rsiRecomendation'] = 'sell'
    df.loc[(df['rsi'] > buyThreshold) & (
        df['rsi'] < sellThreshold), 'rsiRecomendation'] = 'hold'


def generateFinalRecomendation(df: pd.DataFrame) -> None:
    """Generate the final recomendation if several metrics are used

    Args:
        df (pd.DataFrame): Coin's info
    """
    # df.loc[(df['rsiRecomendation'] == 'sell') &
    #        (df['macdRecomendation'] == 'sell'), 'endRecomendation'] = 'sell'
    # df.loc[(df['rsiRecomendation'] == 'buy') &
    #        (df['macdRecomendation'] == 'buy'), 'endRecomendation'] = 'buy'
    # df.loc[df['rsiRecomendation'] == 'hold', 'endRecomendation'] = 'hold'
    # df.loc[df['rsiRecomendation'] !=
    #        df['macdRecomendation'], 'endRecomendation'] = 'hold'
    df['endRecomendation'] = df['macdRecomendation']
