# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: TA_strategy.py
@time: 2017/10/3 23:53
"""
"""
1. simple_ma(df, ma_short=5, ma_long=20, price='close')  # 简单均线策略
2. kdj(df, n=9)
3. macd(df, m=12, n=26, p=9)
4.
"""

# 简单均线策略
def simple_ma(df, ma_short=5, ma_long=20, price='close'):
    """

    :param df: 输入对的个股数据
    :param ma_short: 短期均线
    :param ma_long: 长期均线
    :return: 有'signal'，’hold'列的df
    """
    df = df.copy()
    # ===计算均线
    df['ma_short'] = df[price].rolling(ma_short, min_periods=1).mean()
    df['ma_long'] = df[price].rolling(ma_long, min_periods=1).mean()

    return df

# KDJ策略
def kdj(df, n=9):
    df['max'] = df['high'].rolling(window=n).max()
    df['min'] = df['low'].rolling(window=n).min()
    df['rsv'] = (df['close'] - df['min']) / (df['max'] - df['min']) * 100

    # df.dropna(inplace=True)

    df['K'] = df['rsv'].ewm(com=2, adjust=False).mean()
    df['D'] = df['K'].ewm(com=2, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']

    df.drop(['max', 'min', 'rsv'], axis=1, inplace=True)

    return df

# MACD
def macd(df, m=12, n=26, p=9):

    df = df.copy()
    df['EMA_s'] = df['close'].ewm(span=m, adjust=False).mean()
    df['EMA_l'] = df['close'].ewm(span=n, adjust=False).mean()

    df['DIF'] = df['EMA_s'] - df['EMA_l']
    df['DEA'] = df['DIF'].ewm(span=p, adjust=False).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2

    df.drop(['EMA_s', 'EMA_l'], axis=1, inplace=True)

    return df

# 海龟交易法则
def turtle(stock_data, window=20):
    """
    按照海龟交易法则的买卖策略，对stock_data添加买，卖，持仓列，收益率列
    :param stock_data: 经处理过的stock_data
    :param window: 海龟交易法则的参数
    :return: 返回带有买，卖，持仓，收益率列的stock_data
    """

    # stock_data.reset_index(inplace=True)
    stock_data = stock_data.copy()  # 复制原来的df 不改变原来的df

    stock_data['turtle_high'] = stock_data['high'].rolling(window=window).max()
    # stock_data['20_high'].fillna(stock_data['high'].expanding().max(), inplace=True)
    stock_data['turtle_low'] = stock_data['low'].rolling(window=window).min()

    # # 设置买卖点
    # stock_data.loc[(stock_data['close'] > stock_data['turtle_high'].shift()), 'signal'] = 1
    # stock_data.loc[(stock_data['close'] < stock_data['turtle_low'].shift()), 'signal'] = 0

    return stock_data