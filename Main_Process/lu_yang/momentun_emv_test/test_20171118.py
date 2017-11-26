# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: test_20171118.py
@time: 2017/11/18 16:20
"""
import pandas as pd
from Basic_Functions import Functions
from Basic_Functions import Data_standardize
from Strategy_test import TA_strategy
from Performance_analysis import equity_cal
from Performance_analysis import pf_analysis
import tushare as ts

pd.set_option('expand_frame_repr', False)

# 读取万得的非除权数据，然后进行数据标准化
stock_data = Functions.import_stock_data_wande('600000.SH')
stock_data = Data_standardize.data_standardize_wande(stock_data, adjust_type='adjust_back', start_date='20050101')
# stock_data.to_csv(Functions.out_put_path+'/600000.SH.csv')

#读取xbx的数据
# stock_data = Functions.import_stock_data_xbx('sh600000')
# stock_data = Data_standardize.data_standardize_xbx(stock_data, adjust_type='adjust_back', start_date='20081031')
# stock_data.to_csv(Functions.out_put_path+'/sh600000.csv')

#读取tushare的股票数据
# cons = ts.get_apis()
# stock_data=ts.bar(code='600000', adj='hfq', conn=cons)
# stock_data.to_csv(Functions.out_put_path+'/600000ts.csv')
# print stock_data
# exit()

# stock_data = Data_standardize_v1_20171027.data_standardize_wande('600000.SH')
# stock_data = stock_data[stock_data['date']>=pd.to_datetime('20050101')]

# for p in range(16,18,2):
#     for q in range(20,21):
stock_data = TA_strategy.emv(stock_data, n=20, m=20, ph='high_adjust_back', pl='low_adjust_back', vol='volume')

# 计算交易信号
# 买入信号：emv上穿maemv
stock_data.ix[stock_data['emv'] >= stock_data['maemv'],'signal'] = 1
# 卖出信号：
stock_data.ix[stock_data['emv'] < stock_data['maemv'], 'signal'] = 0

# 计算仓位信号
# print stock_data
stock_data = equity_cal.position(stock_data)
# stock_data = equity_cal.equity_curve_simple(stock_data)

stock_data = equity_cal.equity_curve_complete(stock_data, slippage=0.01, c_rate=3./10000, t_rate=1./1000)
stock_data['equity'] = stock_data['equity'] / 1000000

stock_data = equity_cal.nat_equity(stock_data)

# 年化收益
# 在计算指标时因参数要求，最早的一部分数据会为空值，因此在计算收益率时需要重新计算天数
# rng_stock = pd.period_range(stock_data['date'].iloc[0], stock_data['date'].iloc[-1], freq='D')
# stock_rtn = pow(stock_data.ix[len(stock_data.index) - 1, 'close'] / stock_data.ix[0, 'close'] , 250.00 / len(rng_stock)) - 1
# print len(rng_stock)
# print stock_rtn

pf_analysis.plot_cumulative_return(stock_data)
# stock_data.to_csv('600000.csv')

print stock_data
