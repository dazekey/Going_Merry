# -*- encoding: utf-8 -*-

"""
@author: Ken
@file: ADX_single_test.py
@time: 2017/11/30 11:28

计算同一支股票在ADX指标参数不同情况下的收益情况
benchmark:个股累计收益曲线
"""

import os
import warnings
import pandas as pd
from Basic_Functions import Functions
from Basic_Functions import Data_standardize
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal
import matplotlib.pyplot as plt

# warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)

# 导入指数数据,作为benchmark
index_data = Functions.import_index_data_wande()

# 此处可以填入对应的code进行单个股票测试
stock_data = Functions.import_stock_data_wande('600000.SH')
stock_data = Data_standardize.data_standardize_wande(stock_data)
# print stock_data
# exit()

concat = pd.DataFrame()

for i in range(14, 19):
    df = TA_strategy.adx(stock_data, n=i, ph='high_adjust_back', pl='low_adjust_back', pc='close_adjust_back')
    df = df[df['date'] >= pd.to_datetime('2005-01-01')]  # 采用2005年起的数据
    df.reset_index(inplace=True, drop=True)  # 在计算ADX之后，最早的一部分数据没有对应的值，需要重新排index

    # 当pdi上穿mdi，买入，信号为1；当pdi下穿mdi，卖空，信号为0
    # 计算ADX指标并得到信号和仓位
    df = Functions.cross_both(df, 'pdi', 'mdi')
    df = equity_cal.position(df)
    df = equity_cal.equity_curve_complete(df)
    # df = df[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume', 'equity']]
    df['ADX_' + str(i)] = df['equity']
    df.set_index(keys='date', inplace=True)
    concat = pd.concat([concat, df['ADX_' + str(i)]], axis=1, join='outer')


stock_data = stock_data[stock_data['date'] >= pd.to_datetime('2005-01-01')]
stock_data['benchmark'] = (stock_data['change'] + 1).cumprod() * 1000000.00
stock_data.set_index(keys='date', inplace=True)
concat = pd.concat([concat, stock_data['benchmark']], axis=1, join='inner')


fig = plt.figure(figsize=(16, 5))
for i in range(14, 19):
    plt.plot(concat['ADX_' + str(i)], label='ADX_' + str(i))

plt.plot(concat['benchmark'], label='benchmark')
plt.legend(loc='best')
plt.show()

print concat
