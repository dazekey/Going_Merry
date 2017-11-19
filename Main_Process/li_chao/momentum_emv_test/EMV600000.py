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


# 首先要获取不同EMV参数下的资金曲线，通过运行EMV_single_test，设定参数范围，生成对应的个股数据，此处以600000为案例
df = pd.read_hdf('EMV600000.h5', key='600000')

# 将资金曲线转化为收益率日数据转化为月度数据
df = df.pct_change()
df.fillna(value=0.00, inplace=True)
df_benchmark = df.resample(rule='m').last()
# 日数据转化为月度数据
df_benchmark['benchmark'] = df['benchmark'].resample(rule='m').apply(lambda x: (1.0+x).prod()-1.0)
df_benchmark.fillna(value=0.00, inplace=True)
# print df_benchmark
# exit()
monthly_df = df.resample(rule='m').last()
del monthly_df['benchmark']

# 将各类EMV参数的日收益率数据转化为月收益率
for p in range(16, 21, 2):
    for q in range(20, 23):
        monthly_df['EMV_' + str(p) + '_' + str(q)] = df['EMV_' + str(p) + '_' + str(q)].resample(rule='m').apply(lambda x: (1.0+x).prod()-1.0)

# period_df['code'] = '600000'
monthly_df.fillna(value=0.00, inplace=True)
monthly_df.reset_index(inplace=True)
# print monthly_df
# exit()


def momentum_emv(period_df, start_date, end_date, window=3):
    period_df = period_df.ix[(period_df['date'] >= start_date) & (period_df['date'] <= end_date)]
    # 转换成月度数据
    momentum_emv_equity = pd.DataFrame()

    for i in range(window, len(period_df)-1):

        start_month = period_df['date'].iloc[i - window]
        end_month = period_df['date'].iloc[i]
        stock_temp = period_df[(period_df['date'] > start_month) & (period_df['date'] <= end_month)]

        # 计算单只股票在排名期使用不同参数的累计收益率
        stock_temp.set_index('date', inplace=True)
        grouped = (stock_temp + 1.0).prod()-1.0

        # 将收益率排序并取出收益率最大的参数
        grouped.sort_values(inplace=True)
        param = grouped.index[-1]    # 在收益率相等的时候取最大的参数，以后也可以改成取最小的
        momentum = period_df.ix[(period_df['date'] > end_month) & (period_df['date'] <= period_df['date'].iloc[i + 1])]
        momentum.reset_index(drop=True, inplace=True)

        momentum_emv_equity.at[i-window, 'date'] = momentum.at[0, 'date']
        momentum_emv_equity.at[i-window, 'change'] = momentum.at[0, param]
        momentum_emv_equity.at[i-window, 'param'] = param

    return momentum_emv_equity


result = momentum_emv(monthly_df, '2005-1-31', '2017-9-30', 3)
result.set_index('date', inplace=True)
result = pd.concat([result, df_benchmark['benchmark']], axis=1, join='inner')
result['emv_equity'] = (result['change'] + 1.00).cumprod()
result['benchmark_equity'] = (result['benchmark'] + 1.00).cumprod()
print result


fig = plt.figure(figsize=(16, 5))
plt.plot(result['emv_equity'], label='emv_equity')
plt.plot(result['benchmark_equity'], label='benchmark_equity')
plt.legend(loc='best')
plt.show()

