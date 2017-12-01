# -*- encoding: utf-8 -*-

"""
@author: Ken
@file: momentum_emv_test_for_all_stock.py
@time: 2017/11/30 11:35

计算所有股票在观察期内，使用EMV指标不同参数的情况下的收益情况，计算各类参数下收益率排名前5%的股票的平均收益率，
取平均收益最高的那组的参数作为下个策略使用期EMV指标使用的参数，进而计算以上策略下的综合收益，与index作为benchmark的收益率进行比较。
"""

from __future__ import division
import os
import warnings
import pandas as pd
from math import floor
import numpy as np

from Basic_Functions import Functions
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal
import matplotlib.pyplot as plt
import time

# warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)
# # df_stock = pd.read_hdf('d:/all_trading_data/data/output_data/momentum_emv_allstock_data.h5', key='all_stock')
df_stock = pd.read_hdf('d:/all_trading_data/data/output_data/momentum_emv_allstock_data_updated.h5', key='all_stock')


def momentum_and_emv(all_stock, start_date='2004-12-31', end_date='2017-9-30', window=3):
    index_data = Functions.import_index_data_wande(index_code='000001.SH')
    index_data.set_index('date', inplace=True)
    index_data.sort_index(inplace=True)
    index_data = index_data[start_date:end_date]
    # 转换成月度数据
    by_month = index_data[['index_close']].resample('M').last()
    by_month.reset_index(inplace=True)

    momentum_portfolio_all = pd.DataFrame()
    EMV_data = pd.DataFrame()
    EMV_list = pd.DataFrame()

    for i in range(window, len(by_month) - 1):
        print 'The progress is in %.2f%%.' % ((i-window) / len(by_month) * 100)
        start_month = by_month['date'].iloc[i - window]  # 排名期第一个月
        end_month = by_month['date'].iloc[i]  # 排名期最后一个月
        # 取出在排名期内的数据
        stock_temp = all_stock[(all_stock['date'] > start_month) & (all_stock['date'] <= end_month)]

        for p in range(16, 21, 2):
            for q in range(20, 23):
                # 计算每只股票在排名期内不同参数情况下的累计收益率
                grouped = stock_temp.groupby('code')['EMV_' + str(p) + '_' + str(q)].agg({'return': lambda x: (x + 1).prod() - 1})
                # 将累计收益率排序
                grouped.sort_values(by='return', inplace=True)
                # 取排序后前5%的股票构造反转策略的组合，后5%的股票构造动量策略的组合
                num = floor(len(grouped) * 0.05)
                momentum_code_list = grouped.index[-num:]  # 动量组合的股票代码列表
                grouped = grouped[grouped.index.isin(momentum_code_list)]
                # print grouped.mean().index
                EMV_data['EMV_' + str(p) + '_' + str(q)] = grouped.mean()
                EMV_list = pd.concat([EMV_list, EMV_data['EMV_' + str(p) + '_' + str(q)]], axis=1, join='outer')

        sort_emv = EMV_list.T
        sort_emv.sort_values(by='return', inplace=True)
        param = sort_emv.index[-1]
        grouped = stock_temp.groupby('code')[param].agg({'return': lambda x: (x + 1).prod() - 1})
        grouped.sort_values(by='return', inplace=True)
        num = floor(len(grouped) * 0.05)
        momentum_code_list = grouped.index[-num:]  # 动量组合的股票代码列表
        # print momentum_code_list
        # exit()

        # 取出排名期选中股票在持有期的表现数据
        momentum = all_stock.ix[(all_stock['code'].isin(momentum_code_list)) &
                                (all_stock['date'] > end_month) & (all_stock['date'] <= by_month['date'].iloc[i + 1])]

        momentum.reset_index(drop=True)
        # 动量组合
        momentum_portfolio = momentum.pivot('date', 'code', param).fillna(0)
        # 计算动量组合的收益率

        num = momentum_portfolio.shape[1]
        weights = num * [1. / num]
        momentum_portfolio['pf_rtn'] = np.dot(np.array(momentum_portfolio), np.array(weights))
        momentum_portfolio.reset_index(inplace=True)
        # print momentum_portfolio
        # exit()
        # 将每个月的动量组合收益数据合并
        momentum_portfolio_all = momentum_portfolio_all.append(momentum_portfolio[['date', 'pf_rtn']], ignore_index=True)
        # 计算动量策略的资金曲线
    momentum_portfolio_all['equity'] = (1 + momentum_portfolio_all['pf_rtn']).cumprod() # 是否放在window循环之外

    return momentum_portfolio_all


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
    return sharpe


me = momentum_and_emv(df_stock, '2004-12-31', '2017-09-30', window=3)
print me
date_line = list(me['date'])
capital_line = list(me['equity'])
return_line = list(me['pf_rtn'])
print '\n=====================EMV动量策略主要回测指标====================='
pf_analysis.annual_return(me)
pf_analysis.max_drawdown(me)
sharp_ratio(me)


# 同期大盘的相关指标
index = Functions.import_index_data_wande(index_code='000001.SH')
index.sort_values(by='date', inplace=True)
index['equity'] = (1.0+index['index_change']).cumprod()
index['pf_rtn'] = index['index_change']
index = index[(index['date'] >= pd.to_datetime('2005-04-30')) & (index['date'] <= pd.to_datetime('2017-09-30'))]
index.reset_index(inplace=True)
capital_line = list(index['index_close'])
return_line = list(index['index_change'])
print '\n=====================同期上证指数主要回测指标====================='
pf_analysis.annual_return(index)
pf_analysis.max_drawdown(index)
sharp_ratio(index)

plt.figure(figsize=(14, 7))
me.set_index('date', inplace=True)
index['cum_rtn'] = (index['index_change'] + 1).cumprod()
index.set_index('date', inplace=True)

plt.plot(index['cum_rtn'], label='index')
plt.plot(me['equity'], label='momentum_emv')
plt.title('Equity Curve')
plt.legend(loc='best')
plt.show()
