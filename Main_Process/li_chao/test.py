# -*- coding: utf-8 -*-

import os
import pandas as pd
from pandas_datareader import data, wb
import pandas_datareader as pdr
import pandas_datareader.data as web
import datetime
import os
import warnings
import pandas as pd
from Basic_Functions import Functions
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal

pd.set_option('expand_frame_repr', False)
# start = datetime.datetime(2010, 1, 1)
# end = datetime.datetime(2013, 1, 27)
# yahoo = web.DataReader('F', 'yahoo', start, end)    # Historical stock prices from Yahoo! Finance
# google = web.DataReader("F", 'google', start, end)    # connection aborted 无法读取
# df = pdr.get_data_enigma('enigma.trade.ams.toxic.2015', os.getenv('TJA4dC0LZ3w4fHwRIJuCEhqZWP7nw1oj7qWE6jOVFrraBvvLi0nBu'))    # 无法读取
# symbol = 'WIKI/AAPL'  # or 'AAPL.US'
# df = web.DataReader(symbol, 'quandl', "2015-01-01", "2015-01-05")

# print df
#
# print wb.search('gdp.*capita.*const').iloc[:, :2]

re = pd.DataFrame()
re.loc[1, 'stock_md'] = [1, 2, 3]
print re
exit()


stock_data = Functions.import_stock_data_wande(stock_code='600000.SH')
index_data = Functions.import_index_data_wande()
# stock_data = Functions.cal_adjust_price(stock_data, adjust_type='adjust_back', return_type=1)
#
# print stock_data
p = 5
q = 10
stock_data = Functions.cal_adjust_price(stock_data, adjust_type='adjust_back', return_type=1)
# 和index合并
stock_data = Functions.merge_with_index_data(stock_data, index_data)
stock_data = stock_data[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume', 'open_adjust_back',
                         'high_adjust_back', 'low_adjust_back', 'close_adjust_back']]

re = pd.DataFrame(columns=['code', 'start', 'param', 'stock_rtn',  'stock_md', 'stock_sharpe', 'strategy_rtn',
                           'strategy_md', 'strategy_sharpe', 'excessive_rtn'])

df = TA_strategy.simple_ma(stock_data, ma_short=p, ma_long=q, price='close_adjust_back')
df.dropna(inplace=True)
df = df[df['date'] >= pd.to_datetime('2005-01-01')]  # 采用2005年起的数据
df.reset_index(inplace=True, drop=True)  # 在计算ma之后，最早的一部分数据没有对应的值，需要重新排index

# ma_short大于ma_long时，买入，信号为1；ma_short小于ma_long时，卖出，信号为 0
# 计算MA指标并得到信号和仓位
df = Functions.cross_both(df, 'ma_short', 'ma_long')
df = equity_cal.position(df)
df = equity_cal.equity_curve_complete(df)
df['pf_rtn'] = df['equity'].pct_change()
df['pf_rtn'].fillna(value=0.00, inplace=True)
print df['equity']


def sharp_ratio(df, rf=0.0284):
    """

    :param df: 'date', 'equity', 'change'
    :param rf: 0.0284 无风险利率取10年期国债的到期年化收益率
    :return: 输出夏普比率
    """

    from math import sqrt
    # 将数据序列合并为一个dataframe并按日期排序
    df = df.copy()
    rng = pd.period_range(df['date'].iloc[0], df['date'].iloc[-1], freq='D')

    # 账户年化收益率
    annual_stock = pow(df.ix[len(df.index) - 1, 'equity'] / df.ix[0, 'equity'], 250/len(rng)) - 1
    # 计算收益波动率
    df['rtn'] = df['pf_rtn']
    volatility = df['rtn'].std() * sqrt(250)
    # 计算夏普比率
    sharpe = (annual_stock - rf) / volatility
    print 'Sharp raio: %f' % sharpe
    return sharpe


# sharp_ratio(df)
exit()