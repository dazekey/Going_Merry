# -*- coding: utf-8 -*-

from __future__ import division
from math import floor
import os
import pandas as pd
from pandas_datareader import data, wb
import pandas_datareader as pdr
import pandas_datareader.data as web
import datetime
import os
import matplotlib.pyplot as plt
import pandas as pd
from Basic_Functions import Functions
from Basic_Functions import Data_standardize
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal


# momentum list test

# all_stock = pd.read_hdf('d:/all_trading_data/data/output_data/momentum_ma_for_allstock_data_20171128.h5', key='all_stock')
#
# # 取出在排名期内的数据
# stock_temp = all_stock[(all_stock['date'] > pd.to_datetime('2005-01-01')) & (all_stock['date'] <= pd.to_datetime('2017-09-30'))]
# p = 5
# q = 10
# # for (p, q) in ((5, 10), (5, 20), (5, 60), (10, 20), (10, 30), (10, 60), (20, 40), (20, 60), (20, 120)):
#     # 计算每只股票在排名期的累计收益率
# grouped = stock_temp.groupby('code')['MA_' + str(p) + '_' + str(q)].agg({'return': lambda x: (x + 1).prod() - 1})
# # 将累计收益率排序
# grouped.sort_values(by='return', inplace=True)
# # 取排序后前5%的股票构造反转策略的组合，后5%的股票构造动量策略的组合
# num = floor(len(grouped) * 0.001)
# momentum_code_list = grouped.index[-num:]  # 动量组合的股票代码列表
# # print momentum_code_list
# # grouped = grouped[grouped.index.isin(momentum_code_list)]
# abc = pd.DataFrame()
# abc['list'] = [1, 2, 3]
# abc['test'] = [4, 5, 6]
# # print abc
# test1 = list(momentum_code_list)
# # print test1
# # for i in test1:
# #     print i
# abc.ix[1, 'list'] = test1
# print abc
# # print grouped
# exit()
p = 5
q = 10
start_date = '1989-01-01'
stock_data = Functions.import_stock_data_wande('000001.SZ')
stock_data = Data_standardize.data_standardize_wande(df=stock_data, index_code='000001.SH', adjust_type='adjust_back',
                                                     return_type=1)
# df = stock_data.copy()
# df = TA_strategy.emv(stock_data, n=14, m=9, ph='high_adjust_back', pl='low_adjust_back', vol='volume')
# df = TA_strategy.simple_ma(stock_data, ma_short=p, ma_long=q, price='close_adjust_back')
# df = df[['date', 'close', 'close_adjust_back', 'ma_short', 'ma_long','trade']]
# print df
# df.to_csv('test_ma.csv', encoding='gbk')
# exit()




# df.dropna(inplace=True)
# df = df[df['date'] >= pd.to_datetime(start_date)]  # 一般采用2005年起的数据
# df.reset_index(inplace=True, drop=True)  # 在计算ma之后，最早的一部分数据没有对应的值，需要重新排index

# ma_short大于ma_long时，买入，信号为1；ma_short小于ma_long时，卖出，信号为 0
# 计算EMV指标并得到信号和仓位
# df = Functions.cross_both(df, 'ma_short', 'ma_long')
# n=14
# m=9
# ph='high_adjust_back'
# pl='low_adjust_back'
# vol='volume'
# # 计算每天的em值
# df['em'] = ((df[ph] + df[pl]) / 2 - (df[ph].shift(1) + df[pl].shift(1)) / 2) * \
#            (df[ph] - df[pl]) / df[vol]
#
#
# # emv等于em的n日简单移动平均
# df['emv'] = df['em'].rolling(n).mean()
#
# # maemv等于emv的m日简单移动平均
# df['maemv'] = df['emv'].rolling(m).mean()
# df = TA_strategy.macd(stock_data, m=12, n=26, p=9, pc='close_adjust_back')
# df = TA_strategy.kdj(stock_data, n=9, ph='high_adjust_back', pl='low_adjust_back', pc='close_adjust_back')
# df = TA_strategy.emv(stock_data, n=14, m=9, ph='high_adjust_back', pl='low_adjust_back', vol='volume')
df = TA_strategy.bolling(stock_data, m=26, n=2, ph='high_adjust_back', pl='low_adjust_back', pc='close_adjust_back')

# df = Functions.cross_both(df, 'DIF', 'DEA')
df = df[['date', 'close_adjust_back', 'middle', 'upper', 'lower','signal']]
df = df[df['signal'] == 1]
# df.to_csv('test_bolling_from_functions.csv', encoding='gbk')
print df







