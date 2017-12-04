# encoding: utf-8


"""
@author: Ocean
@file: MA_test_for_allstock_v1.py
@time: 2017/11/30 11:28
"""
from __future__ import division
"""
批量计算所有股票的emv结果

EMV大于MAEMV时，买入，信号为1；当EMV小于MAEMV时，卖出，信号为 0
计算所有股票使用此策略在不同参数下的年化收益率，sharpe ratio, max drawdown
benchmark: 个股在同一期间内的年化收益率，sharpe ratio, max drawdown

"""

import os
import warnings
import pandas as pd
from math import sqrt
from Basic_Functions import Functions
from Basic_Functions import Data_standardize
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal, pf_analysis
import time

start= time.time()
# warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)

# 导入指数数据,作为benchmark
index_data = Functions.import_index_data_wande()

# 遍历数据文件夹中所有股票文件的文件名，得到股票代码列表
stock_code_list = Functions.get_stock_code_list_in_one_dir_wande()
# print stock_code_list
# print len(stock_code_list)
# exit()

# 设置存储和读取路径
dir = '/Going_Merry/MA'
file = '/MA_test_for_all_stock_test_20171204.csv'
data_path = Functions.out_put_path + dir + file
# print data_path
# exit()

# 读取文件中已经有的股票代码，为了断点续传

if os.path.exists(data_path):
    exist_list = pd.read_csv(data_path)
    exist_list = list(exist_list['code'])
else: exist_list = []
stock_list = [i for i in stock_code_list if i not in exist_list]
# print len(exist_list)
# exit()

# ====数据准备
i = 0  # 行计数器
re = pd.DataFrame(columns=['code', 'start'])  # 建立空表re
for code in stock_list[0:2]:    # 可以适当少选一点股票
    stock_data = Functions.import_stock_data_wande(code)
    print i, code
    if len(stock_data) < 250:    # 剔除发行时间小于约1年的数据
        continue
    print 'The progress is in %.2f%%.' % (stock_code_list.index(code) * 1.0 / len(stock_code_list) * 100)

    stock_data = Data_standardize.data_standardize_wande(stock_data)

    # for p in range(5, 20, 5):
    #     for q in range(20, 130, 10):
    for (p, q) in ((5, 20), (10, 20), (20, 60), (20, 120)):
            df = stock_data.copy()
            df = TA_strategy.simple_ma(stock_data, ma_short=p, ma_long=q, price='close_adjust_back')
            df = df[df['date'] >= pd.to_datetime('2005-01-01')]  # 采用2005年起的数据
            df.reset_index(inplace=True, drop=True)  # 在计算emv之后，最早的一部分数据没有对应的值，需要重新排index

            # EMV大于MAEMV时，买入，信号为1；当EMV小于MAEMV时，卖出，信号为 0
            # 计算EMV指标并得到信号和仓位
            df = Functions.cross_both(df, 'ma_short', 'ma_long')

            df = equity_cal.position(df)
            df = equity_cal.equity_curve_complete(df)

            # 增加自然的年化收益
            df = equity_cal.nat_equity(df)

            # 股票的自然年化收益
            nat_rtn = pf_analysis.annual_return(df, columns='nat_equity')

            # 股票自身的最大回撤
            nat_md = pf_analysis.max_drawdown(df, columns='nat_equity')

            # 股票的sharpe ratio
            nat_sharpe = pf_analysis.sharp_ratio(df, equity='nat_equity', type=1)

            # 策略的年化收益
            strategy_rtn = pf_analysis.annual_return(df)

            # 策略最大回撤
            strategy_md = pf_analysis.max_drawdown(df)

            # 策略的sharpe ratio
            strategy_sharpe = pf_analysis.sharp_ratio(df, equity='equity', type=0)

            re.loc[i, 'code'] = df['code'].iloc[0]
            re.loc[i, 'start'] = df.loc[0, 'date'].strftime('%Y-%m-%d')
            re.loc[i, 'nat_rtn'] = nat_rtn
            re.loc[i, 'nat_md'] = nat_md[0]
            re.loc[i, 'nat_sharpe'] = nat_sharpe
            re.loc[i, 'MA_' + str(p) + '_' + str(q)] = 'MA_' + str(p) + '_' + str(q)
            re.loc[i, 'strategy_rtn' + '_' + str(p) + '_' + str(q)] = strategy_rtn
            re.loc[i, 'strategy_md' + '_' + str(p) + '_' + str(q)] = strategy_md[0]
            re.loc[i, 'strategy_sharpe' + '_' + str(p) + '_' + str(q)] = strategy_sharpe
            re.loc[i, 'excess_rtn' + '_' + str(p) + '_' + str(q)] = strategy_rtn - nat_rtn

    if len(exist_list) > 0 or os.path.exists(data_path):
        # re.sort_values(by='excessive_rtn', ascending=False, inplace=True)
        pd.DataFrame(re.iloc[i, :]).T.to_csv(data_path, mode='a',header=None, index=False)
        # print pd.DataFrame(re.iloc[i, :]).T
    i += 1
# print re

if len(exist_list) == 0:
    re.to_csv(data_path, mode='w', index=False)
    # re.iloc[0:1, :].to_csv('d:/all_trading_data/data/output_data/emv_test_for_all_stock_20171203.csv', mode='a',header=None, index=False)

end = time.time()
used = str(end - start)

print 'Time used: ' + used












