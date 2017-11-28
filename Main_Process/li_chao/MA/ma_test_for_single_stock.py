# -*- encoding: utf-8 -*-

"""
@author: Ken
@file: ma_test_for_single_stock.py
@time: 2017/11/28 15:18

ma_short大于ma_long时，买入，信号为1；当ma_short小于ma_long时，卖出，信号为0
计算同一支股票在MA策略选取不同参数情况下的收益率曲线
benchmark:个股在同一期间内的累计收益率曲线
"""

import os
import warnings
import pandas as pd
import time
from Basic_Functions import Functions
from Basic_Functions import Data_standardize
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal
import matplotlib.pyplot as plt

# warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)
end_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))


def ma_single_test(code='000001.SZ', start_date='19890101'):

    # 此处可以填入对应的code进行单个股票测试
    stock_data = Functions.import_stock_data_wande(code)
    stock_data = Data_standardize.data_standardize_wande(df=stock_data, index_code='000001.SH', adjust_type='adjust_back',
                                                         return_type=1)

    single_stock = pd.DataFrame()

    for (p, q) in ((5, 10), (5, 20), (5, 60), (5, 120), (10, 20), (20, 60), (20, 120)):    # 以后考虑修改参数范围
        df = TA_strategy.simple_ma(stock_data, ma_short=p, ma_long=q, price='close_adjust_back')
        df.dropna(inplace=True)
        df = df[df['date'] >= pd.to_datetime(start_date)]  # 一般采用2005年起的数据
        df.reset_index(inplace=True, drop=True)  # 在计算ma之后，最早的一部分数据没有对应的值，需要重新排index

        # ma_short大于ma_long时，买入，信号为1；ma_short小于ma_long时，卖出，信号为 0
        # 计算EMV指标并得到信号和仓位
        df = Functions.cross_both(df, 'ma_short', 'ma_long')
        df = equity_cal.position(df)
        df = equity_cal.equity_curve_complete(df)
        df['MA_' + str(p) + '_' + str(q)] = df['equity']
        df.set_index(keys='date', inplace=True)
        single_stock = pd.concat([single_stock, df['MA_' + str(p) + '_' + str(q)]], axis=1, join='outer')

    stock_data = stock_data[stock_data['date'] >= pd.to_datetime(start_date)]
    stock_data['benchmark'] = (stock_data['change'] + 1).cumprod() * 1000000.00
    stock_data.set_index(keys='date', inplace=True)

    single_stock = pd.concat([single_stock, stock_data['benchmark']], axis=1, join='inner')
    # print single_stock
    return single_stock


# stock_ma = ma_single_test(code='000001.SZ', start_date='20050101')
# # print stock_ma
# # exit()
# # stock_ma.to_hdf('d:/all_trading_data/data/output_data/MA_000001.h5', key='000001.SZ', mode='w')
# df = pd.DataFrame(stock_ma.ix[-1])
# print df.sort_values(by=df.columns[0], ascending=0)
#
# # 作图，比较不同参数下的资金收益情况
# fig = plt.figure(figsize=(16, 5))
# for (m, n) in ((5, 10), (5, 20), (5, 60), (5, 120), (10, 20), (20, 60), (20, 120)):
#     plt.plot(stock_ma['MA_' + str(m) + '_' + str(n)], label='MA_' + str(m) + '_' + str(n))
#
# plt.plot(stock_ma['benchmark'], label='benchmark')
# plt.legend(loc='best')
# plt.show()







