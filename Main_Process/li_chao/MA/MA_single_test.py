# -*- encoding: utf-8 -*-

"""
计算同一支股票在MA策略选取不同参数情况下的收益情况
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
stock_data = Functions.import_stock_data_wande('000001.SZ')
stock_data = Functions.cal_adjust_price(stock_data, adjust_type='adjust_back', return_type=1)
# 和index合并
stock_data = Functions.merge_with_index_data(stock_data, index_data)
stock_data = stock_data[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume', 'open_adjust_back',
                         'high_adjust_back', 'low_adjust_back', 'close_adjust_back']]

single_stock = pd.DataFrame()

for (p, q) in ((5, 10), (5, 20), (5, 60), (5, 120), (10, 20), (20, 60), (20, 120)):
    df = TA_strategy.simple_ma(stock_data, ma_short=p, ma_long=q, price='close_adjust_back')
    df.dropna(inplace=True)
    df = df[df['date'] >= pd.to_datetime('2005-01-01')]  # 采用2005年起的数据
    df.reset_index(inplace=True, drop=True)  # 在计算ma之后，最早的一部分数据没有对应的值，需要重新排index

    # ma_short大于ma_long时，买入，信号为1；ma_short小于ma_long时，卖出，信号为 0
    # 计算EMV指标并得到信号和仓位
    df = Functions.cross_both(df, 'ma_short', 'ma_long')
    df = equity_cal.position(df)
    df = equity_cal.equity_curve_complete(df)
    # df = df[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume', 'equity']]
    df['MA_' + str(p) + '_' + str(q)] = df['equity']
    df.set_index(keys='date', inplace=True)
    single_stock = pd.concat([single_stock, df['MA_' + str(p) + '_' + str(q)]], axis=1, join='outer')



stock_data = stock_data[stock_data['date'] >= pd.to_datetime('2005-01-01')]
stock_data['benchmark'] = (stock_data['change'] + 1).cumprod() * 1000000.00
stock_data.set_index(keys='date', inplace=True)

single_stock = pd.concat([single_stock, stock_data['benchmark']], axis=1, join='inner')
print single_stock
# exit()
# single_stock.to_hdf('d:/all_trading_data/data/output_data/MA_600000.h5', key='600000', mode='w')
df = pd.DataFrame(single_stock.ix['2017-9-29'])
# print df
print df.sort_values(by='2017-9-29', ascending=0)
# exit()
fig = plt.figure(figsize=(16, 5))
for (p, q) in ((5, 10), (5, 20), (5, 60), (5, 120), (10, 20), (20, 60), (20, 120)):
    plt.plot(single_stock['MA_' + str(p) + '_' + str(q)], label='MA_' + str(p) + '_' + str(q))
#
plt.plot(single_stock['benchmark'], label='benchmark')
plt.legend(loc='best')
plt.show()


exit()






