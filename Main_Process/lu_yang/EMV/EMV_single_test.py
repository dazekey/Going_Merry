# -*- encoding: utf-8 -*-

"""
@author: Ken
@file: emv_single_test.py
@time: 2017/11/30 11:33

计算同一支股票在EMV指标参数不同情况下的收益情况
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
stock_data = Functions.import_stock_data_wande('000001.SZ')
stock_data = Data_standardize.data_standardize_wande(stock_data)
# print stock_data
# exit()

single_stock = pd.DataFrame()

for p in range(16, 21, 2):
    for q in range(20, 23):
        df = TA_strategy.emv(stock_data, n=p, m=q, ph='high_adjust_back', pl='low_adjust_back', vol='volume')
        df = df[df['date'] >= pd.to_datetime('2005-01-01')]  # 采用2005年起的数据，写在前面可以提高计算效率
        df.reset_index(inplace=True, drop=True)  # 在计算emv之后，最早的一部分数据没有对应的值，需要重新排index

        # EMV大于MAEMV时，买入，信号为1；当EMV小于MAEMV时，卖出，信号为 0
        # 计算EMV指标并得到信号和仓位
        df = Functions.cross_both(df, 'emv', 'maemv')
        df = equity_cal.position(df)
        df = equity_cal.equity_curve_complete(df)
        df['EMV_' + str(p) + '_' + str(q)] = df['equity']
        df.set_index(keys='date', inplace=True)
        single_stock = pd.concat([single_stock, df['EMV_' + str(p) + '_' + str(q)]], axis=1, join='outer')    # 看下merge怎么做


stock_data = stock_data[stock_data['date'] >= pd.to_datetime('2005-01-01')]
stock_data['benchmark'] = (stock_data['change'] + 1).cumprod() * 1000000.00
stock_data.set_index(keys='date', inplace=True)

single_stock = pd.concat([single_stock, stock_data['benchmark']], axis=1, join='inner')
print single_stock
single_stock.to_csv('emv_single_test_000001.csv')
# exit()
# concat.to_hdf('C:/all_trading_data/data/output_data/EMV600000.h5', key='600000', mode='w')
# df = pd.DataFrame(concat.ix['2017-9-29'])
# print df
# print df.sort_values(by='2017-9-29', ascending=0)
fig = plt.figure(figsize=(16, 5))
for p in range(16, 19, 2):
    for q in range(20, 22):
        plt.plot(single_stock['EMV_' + str(p) + '_' + str(q)], label='EMV_' + str(p) + '_' + str(q))


plt.plot(single_stock['benchmark'], label='benchmark')
plt.legend(loc='best')
plt.show()
exit()






