# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: KDJ_0.01.py
@time: 2017/10/4 13:37
"""
"""
买入 KDJ J反转, 指数大于ma20
卖出 涨幅大于1%, 指数小于ma20
"""
import pandas as pd
from Basic_Functions import Functions
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal
from Strategy_test import TA_strategy

pd.set_option('expand_frame_repr', False)

# ====数据准备
stock_code = '600000.SH'
# 导入指定的股票数据,从20050101开始
stock_data = Functions.import_stock_data(stock_code, startdate='20050101')
# 导入指数数据,作为benchmark
index_data = Functions.import_index_data()
# 和index合并
stock_data = Functions.merge_with_index_data(stock_data, index_data)
# 添加kdj指标
stock_data= TA_strategy.kdj(stock_data)
# 添加指数指标
stock_data = TA_strategy.simple_ma(stock_data, price='index_close')


# ====设置交易信号
# 买入点
# stock_data = Functions.cross_signle(stock_data, 'J', 'D', trade_type='buy')

# 卖出点1
# stock_data = Functions.cross_signle(stock_data, 'ma_long', 'close', trade_type='sell')
# print stock_data[stock_data['signal'] == 1].shape, stock_data.shape
# cost_price = 0
# for i in range(0, stock_data.shape[0]):
#     if stock_data.loc[i-1, 'signal'] == 1:
#         cost_price = stock_data.loc[i, 'open']
#     elif cost_price >0 and stock_data.loc[i, 'open'] >= (cost_price * 1.01):
#         stock_data.loc[i, 'singal'] = 0
#         cost_price = 0
#     elif stock_data.loc[i-1, 'signal'] == 0:
#         cost_price = 0

# print stock_data[stock_data['signal'] == 0].shape
# cost = 0
stock_data['cost']=0
for i in range(2, stock_data.shape[0]):
    #买入条件: 1 index_close >= index_ma_long
    condition1 = stock_data.loc[i, 'index_close'] >= stock_data.loc[i, 'ma_long']
    condition2_1 = stock_data.loc[i, 'J'] > stock_data.loc[i-1, 'J']  # J反转
    condition2_2 = stock_data.loc[i - 1, 'J'] < stock_data.loc[i - 2, 'J']
    if stock_data.loc[i-1, 'cost'] > 0:
       stock_data.loc[i, 'cost'] = stock_data.loc[i - 1, 'cost']
    elif condition1 and condition2_1 and condition2_2:
        stock_data.loc[i, 'signal'] = 1
        stock_data.loc[i, 'cost'] = stock_data.loc[i + 1, 'open']
    else:
        stock_data.loc[i, 'cost'] = stock_data.loc[i - 1, 'cost']

    #卖出条件: 1 index_close < index_ma_long
    condition1 = stock_data.loc[i, 'index_close'] < stock_data.loc[i, 'ma_long']
    # 开盘价高于cost 1%
    condition2 = stock_data.loc[i, 'open'] >= (stock_data.loc[i, 'cost'] * 1.01)
    if condition1 or condition2:
        stock_data.loc[i - 1, 'signal'] = 0
        stock_data.loc[i, 'cost'] = 0



print stock_data[stock_data['signal'] == 0].shape
stock_data = equity_cal.position(stock_data)
stock_data = equity_cal.equity_curve_complete(stock_data, slippage=0)
stock_data = equity_cal.nat_equity(stock_data, type=1)
stock_data.to_csv('test_20171004.csv')
print stock_data
pf_analysis.annual_return(stock_data)
pf_analysis.sharp_ratio(stock_data)
pf_analysis.prob_up(stock_data)
pf_analysis.volatility(stock_data)
pf_analysis.max_successive_up(stock_data)
pf_analysis.plot_cumulative_return(stock_data, index=False, nat_rtn=False)