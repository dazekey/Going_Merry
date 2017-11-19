# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: TA_strategy_v1.1_2017119.py
@time: 2017/11/19 23:53
"""
import pandas as pd
"""
更新：
by lichao:
    添加了ADX和EMV
by luyang:
    所有指标添加price参数，可选择对列进行运算
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
def kdj(df, n=9, ph='high', pl='low', pc='close'):
    df['max'] = df[ph].rolling(window=n).max()
    df['min'] = df[pl].rolling(window=n).min()
    df['rsv'] = (df[pc] - df['min']) / (df['max'] - df['min']) * 100

    # df.dropna(inplace=True)

    df['K'] = df['rsv'].ewm(com=2, adjust=False).mean()
    df['D'] = df['K'].ewm(com=2, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']

    df.drop(['max', 'min', 'rsv'], axis=1, inplace=True)

    return df

# MACD
def macd(df, m=12, n=26, p=9, pc='close'):

    df = df.copy()
    df['EMA_s'] = df[pc].ewm(span=m, adjust=False).mean()
    df['EMA_l'] = df[pc].ewm(span=n, adjust=False).mean()

    df['DIF'] = df['EMA_s'] - df['EMA_l']
    df['DEA'] = df['DIF'].ewm(span=p, adjust=False).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2

    df.drop(['EMA_s', 'EMA_l'], axis=1, inplace=True)

    return df

# 海龟交易法则
def turtle(stock_data, window=20, ph='high', pl='low'):
    """
    按照海龟交易法则的买卖策略，对stock_data添加买，卖，持仓列，收益率列
    :param stock_data: 经处理过的stock_data
    :param window: 海龟交易法则的参数
    :return: 返回带有买，卖，持仓，收益率列的stock_data
    """

    # stock_data.reset_index(inplace=True)
    stock_data = stock_data.copy()  # 复制原来的df 不改变原来的df

    stock_data['turtle_high'] = stock_data[ph].rolling(window=window).max()
    # stock_data['20_high'].fillna(stock_data['high'].expanding().max(), inplace=True)
    stock_data['turtle_low'] = stock_data[pl].rolling(window=window).min()

    # # 设置买卖点
    # stock_data.loc[(stock_data['close'] > stock_data['turtle_high'].shift()), 'signal'] = 1
    # stock_data.loc[(stock_data['close'] < stock_data['turtle_low'].shift()), 'signal'] = 0

    return stock_data

# 简易波动指标（EMV）


"""
EMV 指标的上升下降意味着市场的强弱变化，可以以此作为择时的判断依据。
    EMV大于MAEMV时，买入，信号为1；当EMV小于MAEMV时，卖出，信号为-1

    :param stock_data: 输入包含volume, high, low 的股票数据
    :param n: 计算EMV = EM的n日简单移动平均
           m: 计算MAEMV = EMV的m日简单移动平均

    :return: 返回转换好的df, 增加列em, emv, maemv
"""


def emv(stock_data, n=14, m=9, ph='high', pl='low', vol='volume'):    # 查了下市场默认参数是14，9，可以通过策略进行测试
    df = stock_data.copy()

    # 计算每天的em值
    df['em'] = ((df[ph] + df[pl]) / 2 - (df[ph].shift(1) + df[pl].shift(1)) / 2) * \
               (df[ph] - df[pl]) / df[vol]
    df.dropna(inplace=True)

    # emv等于em的n日简单移动平均
    # df['emv'] = pd.rolling_mean(df['em'], n)
    df['emv'] = df['em'].rolling(n).mean()

    # maemv等于emv的m日简单移动平均
    # df['maemv'] = pd.rolling_mean(df['emv'], m)
    df['maemv'] = df['emv'].rolling(m).mean()
    df.dropna(inplace=True)

    return df


# 计算+DI和-DI指标

"""
平均趋向指标(ADX)是由美国技术分析大师威尔斯•威尔德（Wells Wilder）所创造的，是一种中长期股市技术分析方法。
ADX属于趋向指标DMI指标的一种，而DMI主要是通过分析股票价格在涨跌过程中买卖双方力量均衡点的变化情况，即多空双
方的力量的变化受价格波动的影响而发生由均衡到失衡的循环过程，从而提供对趋势判断依据的一种技术指标。

    :param stock_data: 输入包含 high, low, close 的股票数据
    :param n: 计算tr,dmp和dmm需要用到，默认为14
           

    :return: 返回转换好的df, 需要根据pdi, mdi的数值大小关系生成买入卖出信号。
"""


def adx(stock_data, n=14, ph='high', pl='low', pc='close'):

    df = stock_data.copy()

    # 计算HD和LD值
    df['hd'] = df[ph] - df[ph].shift(1)  # 若股票当日相对前日重心上移并且创新高，将最高点的价差记为hd
    df['ld'] = df[pl].shift(1) - df[pl]  # 若重心下移并且创新低，将最低价的价差记为ld

    # 计算真实涨跌幅TR值，为t1,t2, t3中绝对值的数值最大者
    df['t1'] = df[ph] - df[pl]  # t1为当日的最高价减去当日的最低价。
    df['t2'] = abs(df[ph] - df[pc].shift(1))  # t2为当日的最高价减去前一日的收盘价
    df['t3'] = abs(df[pl] - df[pc].shift(1))

    for i in range(0, df.shape[0]):
        df.loc[i, 'temp'] = max(df.loc[i, 't1'], df.loc[i, 't2'], df.loc[i, 't3'])

    df.dropna(inplace=True)

    df['tr'] = pd.rolling_sum(df['temp'], n)

    df.ix[(df['hd'] > 0) & (df['hd'] > df['ld']), 'hd1'] = df['hd']  # 如果hd>0并且hd>ld，则hd=hd,否则hd取0
    df['hd1'].fillna(0, inplace=True)

    df.ix[(df['ld'] > 0) & (df['ld'] > df['hd']), 'ld1'] = df['ld']  # 如果ld>0并且ld>hd，则ld=ld,否则ld取0
    df['ld1'].fillna(0, inplace=True)

    df['dmp'] = pd.rolling_sum(df['hd1'], n)
    df['dmm'] = pd.rolling_sum(df['ld1'], n)

    df['pdi'] = df['dmp'] / df['tr'] * 100  # pdi(+DI)为一段时间内hd的和/真实涨跌的和
    df['mdi'] = df['dmm'] / df['tr'] * 100
    df.dropna(inplace=True)

    return df


















