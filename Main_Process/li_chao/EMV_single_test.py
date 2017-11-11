# -*- encoding: utf-8 -*-

"""
计算同一支股票在EMV指标参数不同情况下的收益情况
"""

import os
import warnings
import pandas as pd
from Basic_Functions import Functions
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)

# 导入指数数据,作为benchmark
index_data = Functions.import_index_data_wande()

# 此处可以填入对应的code进行单个股票测试
stock_data = Functions.import_stock_data_wande('600000.SH', other_columns=['成交量(股)'])
stock_data.rename(columns={'成交量(股)': 'volume'}, inplace=True)
stock_data = Functions.cal_adjust_price(stock_data, adjust_type='adjust_back', return_type=2)
# 和index合并
stock_data = Functions.merge_with_index_data(stock_data, index_data)
stock_data = stock_data[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume']]


concat = pd.DataFrame()

for p in range(16, 27, 2):
    for q in range(20, 26):
        df = TA_strategy.emv(stock_data, n=p, m=q)
        df = df[df['date'] >= pd.to_datetime('2005-01-01')]  # 采用2005年起的数据
        df.reset_index(inplace=True, drop=True)  # 在计算emv之后，最早的一部分数据没有对应的值，需要重新排index

        # EMV大于MAEMV时，买入，信号为1；当EMV小于MAEMV时，卖出，信号为 0
        # 计算EMV指标并得到信号和仓位
        df = Functions.cross_both(df, 'emv', 'maemv')
        df = equity_cal.position(df)
        df = equity_cal.equity_curve_complete(df)
        # df = df[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume', 'equity']]
        df['EMV_' + str(p) + '_' + str(q)] = df['equity']
        df.set_index(keys='date', inplace=True)
        concat = pd.concat([concat, df['EMV_' + str(p) + '_' + str(q)]], axis=1, join='outer')
        concat['date'] = df['date']


stock_data = stock_data[stock_data['date'] >= pd.to_datetime('2005-01-01')]
stock_data['benchmark'] = (stock_data['change'] + 1).cumprod() * 1000000.00
stock_data.set_index(keys='date', inplace=True)

concat = pd.concat([concat, stock_data['benchmark']], axis=1, join='inner')


# fig = plt.figure(figsize=(16, 5))
# for p in range(16, 19, 2):
#     for q in range(20, 22):
#         plt.plot(concat['EMV_' + str(p) + '_' + str(q)], label='EMV_' + str(p) + '_' + str(q))
#
# plt.plot(concat['benchmark'], label='benchmark')
# plt.legend(loc='best')
# plt.show()

df = pd.DataFrame(concat.iloc[-1, :].T)

df = df.astype('float64')
df.reset_index(inplace=True)
# print df.dtypes
# df = pd.DataFrame(concat.ix['2017-9-29'])
# print df.columns

print df.sort_values(by=['2017-9-29'], ascending=1, inplace=True)
exit()






