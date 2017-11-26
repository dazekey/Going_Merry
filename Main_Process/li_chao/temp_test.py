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


# 将个股数据600000转化为月度数据
df = pd.read_hdf('C:/all_trading_data/data/output_data/EMV600000.h5', key='600000')
df = df.pct_change()
df.fillna(value=0.00, inplace=True)
df_benchmark = df['benchmark'].resample(rule='m').apply(lambda x: (1.0+x).prod()-1.0)
df_benchmark.fillna(value=0.00, inplace=True)
# print df_benchmark
# exit()
period_df = df.resample(rule='m').last()
del period_df['benchmark']

for p in range(16, 21, 2):
    for q in range(20, 23):
        period_df['EMV_' + str(p) + '_' + str(q)] = df['EMV_' + str(p) + '_' + str(q)].resample(rule='m').apply(lambda x: (1.0+x).prod()-1.0)

# period_df['code'] = '600000'
period_df.fillna(value=0.00, inplace=True)
period_df.reset_index(inplace=True)
# print period_df
# exit()
start_date = '2005-1-1'
end_date = '2017-9-30'
window = 3

# 将index数据转化为月数据by_month，此处取的是SH000001
index_data = pd.read_csv('C:/all_trading_data/data/input_data/index_data_wande/000001.SH.CSV', parse_dates=True,
                         encoding='gbk')
index_data.columns = [i.encode('utf8') for i in index_data.columns]
index_data.rename(columns={'代码': 'code', '日期': 'date', '涨跌幅(%)': 'change', '收盘价': 'close'}, inplace=True)
index_data['change'] = index_data['change'] / 100
index_data['date'] = pd.to_datetime(index_data['date'])
index_data.set_index('date', inplace=True)
index_data.sort_index(inplace=True)
index_data = index_data[start_date:end_date]
# 转换成月度数据
by_month = index_data[['close']].resample('M').last()
by_month.reset_index(inplace=True)

momentum_emv_equity = pd.DataFrame()
i = 3

start_month = by_month['date'].iloc[i - window]
end_month = by_month['date'].iloc[i]
stock_temp = period_df[(period_df['date'] > start_month) & (period_df['date'] <= end_month)]

# 计算单只股票在排名期使用不同参数的累计收益率
stock_temp.set_index('date', inplace=True)
grouped = (stock_temp + 1.0).prod() - 1.0

# 将收益率排序并取出收益率最大的参数
grouped.sort_values(inplace=True)
param = grouped.index[-1]  # 在收益率相等的时候取最大的参数，以后也可以改成取最小的
momentum = period_df.ix[(period_df['date'] > end_month) & (period_df['date'] <= by_month['date'].iloc[i + 1])]
momentum.reset_index(drop =True, inplace =True)
# print momentum.at[0, 'date']
# exit()

momentum_emv_equity.at[i-window, 'date'] = momentum.at[i-window, 'date']
momentum_emv_equity.at[i-window, 'change'] = momentum.at[i-window, param]
momentum_emv_equity.at[i-window, 'param'] = param


print momentum_emv_equity