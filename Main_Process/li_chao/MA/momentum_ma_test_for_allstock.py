# -*- encoding: utf-8 -*-

"""
@author: Ken
@file: momentum_ma_test_for_allstock.py
@time: 2017/11/28 15:18

计算所有股票在观察期内，使用不同参数计算的MA指标下的月度累计收益情况，对不同参数下收益率排名前5%的股票的平均收益率进行排名
取平均收益率最高的那组参数作为下个策略使用期的参数，股票取收益率排名前5%的，进而计算该参数对应的股票池在下个持有期的收益率，画出收益率曲线
benchmark： index(000001.SH)的收益率曲线
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

# warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)
# df_stock = pd.read_hdf('d:/all_trading_data/data/output_data/momentum_emv_allstock_data.h5', key='all_stock')
df_stock = pd.read_hdf('d:/all_trading_data/data/output_data/momentum_ma_for_allstock_data_20171128.h5', key='all_stock')
# print df_stock
# exit()


def momentum_and_ma(all_stock, start_date='2004-12-31', end_date='2017-9-30', window=3):

    index_data = Functions.import_index_data_wande(index_code='000001.SH')
    index_data.set_index('date', inplace=True)
    index_data.sort_index(inplace=True)
    index_data = index_data[start_date:end_date]
    # 转换成月度数据
    by_month = index_data[['index_close']].resample('M').last()
    by_month.reset_index(inplace=True)

    momentum_portfolio_all = pd.DataFrame()
    ma_data = pd.DataFrame()
    ma_list = pd.DataFrame()

    for i in range(window, len(by_month) - 1):
        print 'The progress is in %.2f%%.' % ((i-window) / len(by_month) * 100)
        start_month = by_month['date'].iloc[i - window]  # 排名期第一个月
        end_month = by_month['date'].iloc[i]  # 排名期最后一个月
        # 取出在排名期内的数据
        stock_temp = all_stock[(all_stock['date'] > start_month) & (all_stock['date'] <= end_month)]

        for (p, q) in ((5, 10), (5, 20), (5, 60), (10, 20), (10, 30), (10, 60), (20, 40), (20, 60), (20, 120)):
            # 计算每只股票在排名期的累计收益率
            grouped = stock_temp.groupby('code')['MA_' + str(p) + '_' + str(q)].agg(
                {'return': lambda x: (x + 1).prod() - 1})
            # 将累计收益率排序
            grouped.sort_values(by='return', inplace=True)
            # 取排序后前5%的股票构造反转策略的组合，后5%的股票构造动量策略的组合
            num = floor(len(grouped) * 0.05)
            momentum_code_list = grouped.index[-num:]  # 动量组合的股票代码列表
            grouped = grouped[grouped.index.isin(momentum_code_list)]
            # print grouped.mean().index
            ma_data['MA_' + str(p) + '_' + str(q)] = grouped.mean()
            ma_list = pd.concat([ma_list, ma_data['MA_' + str(p) + '_' + str(q)]], axis=1, join='outer')

        sort_ma = ma_list.T
        sort_ma.sort_values(by='return', inplace=True)
        param = sort_ma.index[-1]
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
    momentum_portfolio_all['equity'] = (1 + momentum_portfolio_all['pf_rtn']).cumprod()

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
    print 'Sharp ratio: %f' % sharpe
    return sharpe


mm = momentum_and_ma(df_stock, '2004-12-31', '2017-09-30', window=3)
print mm
date_line = list(mm['date'])
capital_line = list(mm['equity'])
return_line = list(mm['pf_rtn'])
print '\n=====================MA动量策略主要回测指标====================='
pf_analysis.annual_return(mm)
pf_analysis.max_drawdown(mm)
sharp_ratio(mm)


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

# 作图
plt.figure(figsize=(14, 7))
mm.set_index('date', inplace=True)
index['cum_rtn'] = (index['index_change'] + 1).cumprod()
index.set_index('date', inplace=True)

plt.plot(mm['equity'], label='momentum_ma_equity')
plt.plot(index['cum_rtn'], label='index')
plt.legend(loc='best')
plt.show()

