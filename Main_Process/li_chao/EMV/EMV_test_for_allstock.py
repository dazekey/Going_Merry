# encoding: utf-8


"""
@author: Ken
@file: emv_test_for_allstock.py
@time: 2017/11/30 11:28

EMV大于MAEMV时，买入，信号为1；当EMV小于MAEMV时，卖出，信号为 0
计算所有股票使用此策略在不同参数下的年化收益率，sharpe ratio, max drawdown
benchmark: 个股在同一期间内的年化收益率，sharpe ratio, max drawdown

"""

from __future__ import division
import os
import warnings
import pandas as pd
from math import sqrt
from Basic_Functions import Functions
from Basic_Functions import Data_standardize
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal

# warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)

def sharp_ratio(df, rf=0.0284):

    """
    :param df: 'date', 'equity', 'change'
    :param rf: 0.0284 无风险利率取10年期国债的到期年化收益率
    :return: 输出夏普比率
    """

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
    # print 'Sharp ratio: %f' % sharpe
    return sharpe

# 导入指数数据,作为benchmark
index_data = Functions.import_index_data_wande()

# 遍历数据文件夹中所有股票文件的文件名，得到股票代码列表
stock_code_list = Functions.get_stock_code_list_in_one_dir_wande()
# print len(stock_code_list)
# exit()

# ====数据准备

for code in stock_code_list[0:]:    # 可以适当少选一点股票
    stock_data = Functions.import_stock_data_wande(code)

    if len(stock_data) < 250:    # 剔除发行时间小于约1年的数据
        continue
    print 'The progress is in %.2f%%.' % (stock_code_list.index(code) * 1.0 / len(stock_code_list) * 100)

    stock_data = Data_standardize.data_standardize_wande(stock_data)

    re = pd.DataFrame(columns=['code', 'start', 'stock_rtn', 'stock_md', 'stock_sharpe', ' '])
    i = 0

    for p in range(16, 22, 2):
        for q in range(20, 24):

            df = TA_strategy.emv(stock_data, n=p, m=q, ph='high_adjust_back', pl='low_adjust_back', vol='volume')
            df = df[df['date'] >= pd.to_datetime('2005-01-01')]  # 采用2005年起的数据
            df.reset_index(inplace=True, drop=True)  # 在计算emv之后，最早的一部分数据没有对应的值，需要重新排index

            # EMV大于MAEMV时，买入，信号为1；当EMV小于MAEMV时，卖出，信号为 0
            # 计算EMV指标并得到信号和仓位
            df = Functions.cross_both(df, 'emv', 'maemv')
            df = equity_cal.position(df)
            df = equity_cal.equity_curve_complete(df)
            df['capital_rtn'] = df['equity'].pct_change(1)
            df.ix[0, 'capital_rtn'] = 0
            df['capital'] = (df['capital_rtn'] + 1).cumprod()

            df_stock = stock_data.copy()
            df_stock = df_stock[df_stock['date'] >= pd.to_datetime('2005-01-01')]  # 与策略开始时间一致
            df_stock.reset_index(inplace=True, drop=True)

            # 股票的年化收益
            rng_stock = pd.period_range(df_stock['date'].iloc[0], df_stock['date'].iloc[-1], freq='D')
            stock_rtn = pow(df_stock.ix[len(df_stock.index) - 1, 'close_adjust_back'] / df_stock.ix[0, 'close_adjust_back'], 250.00 / len(rng_stock)) - 1
            # 股票最大回撤
            df_stock['max2here_stock'] = df_stock['close_adjust_back'].expanding(min_periods=1).max()  # 计算当日之前的账户最大价值
            df_stock['dd2here_stock'] = df_stock['close_adjust_back'] / df_stock['max2here_stock'] - 1  # 计算当日的回撤
            temp = df_stock.sort_values(by='dd2here_stock').iloc[0][['date', 'dd2here_stock']]
            stock_md = temp['dd2here_stock']

            # 股票的sharpe ratio
            df_stock['pf_rtn'] = df_stock['change']
            df_stock['equity'] = (1 + df_stock['change']).cumprod()
            stock_sharpe = sharp_ratio(df_stock)

            # 策略的年化收益
            # 在计算指标时因参数要求，最早的一部分数据会为空值，因此在计算收益率时需要重新计算天数
            rng_strategy = pd.period_range(df['date'].iloc[0], df['date'].iloc[-1], freq='D')
            strategy_rtn = pow(df.ix[len(df.index) - 1, 'equity'] / df.ix[0, 'equity'], 250.00 / len(rng_strategy)) - 1

            # 策略最大回撤
            df['max2here'] = df['capital'].expanding(min_periods=1).max()  # 计算当日之前的账户最大价值
            df['dd2here'] = df['capital'] / df['max2here'] - 1  # 计算当日的回撤
            temp = df.sort_values(by='dd2here').iloc[0][['date', 'dd2here']]
            strategy_md = temp['dd2here']

            # 策略的sharpe ratio
            df['pf_rtn'] = df['capital_rtn']
            strategy_sharpe = sharp_ratio(df)

            re.loc[i, 'code'] = df['code'].iloc[0]
            re.loc[i, 'start'] = df.loc[0, 'date'].strftime('%Y-%m-%d')

            re.loc[i, 'stock_rtn'] = stock_rtn
            re.loc[i, 'stock_md'] = stock_md
            re.loc[i, 'stock_sharpe'] = stock_sharpe

            re.loc[i, 'strategy_rtn' + '_' + str(p) + '_' + str(q)] = strategy_rtn
            re.loc[i, 'strategy_md' + '_' + str(p) + '_' + str(q)] = strategy_md
            re.loc[i, 'strategy_sharpe' + '_' + str(p) + '_' + str(q)] = strategy_sharpe

    #         i += 1
    #
    # re.sort_values(by='excessive_rtn', ascending=False, inplace=True)
    # print re

    re.iloc[0:1, :].to_csv('d:/all_trading_data/data/output_data/emv_test_for_all_stock_20171130.csv', mode='a',header=None, index=False)














