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
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal



# # 同期大盘的相关指标
# test = Functions.import_index_data_wande(index_code='000001.SH')
# test.sort_values(by='date', inplace=True)
# # print index
# # exit()
# test = test[(test['date'] >= pd.to_datetime('2005-04-01')) & (test['date'] <= pd.to_datetime('2017-09-30'))]
# test.set_index('date', inplace=True)
#
# me = test.resample('M').last()
# me.reset_index(inplace=True)
# # print me
# # exit()
# abc = pd.DataFrame()
# abc['list'] = [1, 2, 3]
# abc['test'] = [4, 5, 6]
# date_line = list(me['date'])[0:3]
# abc.iloc[1,1] = date_line
# # print date_line
# # for i in date_line:
# #     print i
# print abc.iloc[1, 1]
all_stock = pd.read_hdf('d:/all_trading_data/data/output_data/momentum_ma_for_allstock_data_20171128.h5', key='all_stock')

# 取出在排名期内的数据
stock_temp = all_stock[(all_stock['date'] > pd.to_datetime('2005-01-01')) & (all_stock['date'] <= pd.to_datetime('2017-09-30'))]
p = 5
q = 10
# for (p, q) in ((5, 10), (5, 20), (5, 60), (10, 20), (10, 30), (10, 60), (20, 40), (20, 60), (20, 120)):
    # 计算每只股票在排名期的累计收益率
grouped = stock_temp.groupby('code')['MA_' + str(p) + '_' + str(q)].agg({'return': lambda x: (x + 1).prod() - 1})
# 将累计收益率排序
grouped.sort_values(by='return', inplace=True)
# 取排序后前5%的股票构造反转策略的组合，后5%的股票构造动量策略的组合
num = floor(len(grouped) * 0.001)
momentum_code_list = grouped.index[-num:]  # 动量组合的股票代码列表
# print momentum_code_list
# grouped = grouped[grouped.index.isin(momentum_code_list)]
abc = pd.DataFrame()
abc['list'] = [1, 2, 3]
abc['test'] = [4, 5, 6]
test1 = list(momentum_code_list)
# print test1
# for i in test1:
#     print i
abc.ix[1, 'test'] = test1
print abc.ix[1, 'test']
# print abc
# abc['test'] = abc['test'].astype(object)
# abc['list'] = abc['list'].astype(object)
# abc.set_value(1, 'test', test1)
# print abc.loc[1, 'test']
# grouped = grouped[grouped.index.isin(abc.loc[1, 'test'])]
print abc
# print grouped
exit()




