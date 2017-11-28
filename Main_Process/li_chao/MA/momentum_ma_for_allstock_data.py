# encoding: utf-8

"""

@author: Ken
@file: momentum_ma_for_allstock.py
@time: 2017/11/28 15:40

为momentum_ma_test_for_allstock.py准备全量股票数据。
在MA策略下，将不同参数情况下的个股日收益率转化为月度收益率，然后将所有股票数据拼成一张表。
cost time: 10374.21秒

"""

from __future__ import division  # 不引入这个的话，除法结果小于1的都是0
import os
import warnings
import time
import pandas as pd
from Basic_Functions import Functions
from Basic_Functions import Data_standardize
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal

# warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)

# 导入指数数据,作为benchmark
index_data = Functions.import_index_data_wande()

# 遍历数据文件夹中所有股票文件的文件名，得到股票代码列表
stock_code_list = Functions.get_stock_code_list_in_one_dir_wande(input_data_path='d:/all_trading_data/data/input_data/stock_data_wande/')
# print len(stock_code_list)
# exit()

start_time = time.time()

# ====数据准备
all_stock = pd.DataFrame()

for code in stock_code_list[0:]:    # 可以适当少选一点股票

    stock_data = Functions.import_stock_data_wande(code)

    if len(stock_data) < 250:    # 剔除发行时间小于约1年的数据
        continue
    print 'The progress is in %.2f%%.' % (stock_code_list.index(code) * 1.0 / len(stock_code_list) * 100)
    stock_data = Data_standardize.data_standardize_wande(df=stock_data, index_code='000001.SH',
                                                         adjust_type='adjust_back', return_type=1)

    single_stock = pd.DataFrame()
    monthly_single_stock = pd.DataFrame()

    for (p, q) in ((5, 10), (5, 20), (5, 60), (10, 20), (10, 30), (10, 60), (20, 40), (20, 60), (20, 120)):
        df = TA_strategy.simple_ma(stock_data, ma_short=p, ma_long=q, price='close_adjust_back')
        df.dropna(inplace=True)
        df = df[df['date'] >= pd.to_datetime('2005-01-01')]  # 采用2005年起的数据
        df.reset_index(inplace=True, drop=True)  # 在计算ma之后，最早的一部分数据没有对应的值，需要重新排index

        # ma_short大于ma_long时，买入，信号为1；ma_short小于ma_long时，卖出，信号为 0
        # 计算MA指标并得到信号和仓位
        df = Functions.cross_both(df, 'ma_short', 'ma_long')
        df = equity_cal.position(df)
        df = equity_cal.equity_curve_complete(df)
        df['MA_' + str(p) + '_' + str(q)] = df['equity']
        df.set_index(keys='date', inplace=True)
        single_stock = pd.concat([single_stock, df['MA_' + str(p) + '_' + str(q)]], axis=1, join='outer')

    stock_data = stock_data[stock_data['date'] >= pd.to_datetime('2005-01-01')]
    stock_data.set_index(keys='date', inplace=True)

    # 从资金曲线转化为日收益率
    single_stock = single_stock.pct_change()
    single_stock.fillna(value=0.00, inplace=True)
    single_stock = pd.concat([single_stock, stock_data['code']], axis=1, join='outer')

    monthly_single_stock = single_stock.resample(rule='m').last()

    # 将各类MA参数的日收益率数据转化为月收益率
    for (p, q) in ((5, 10), (5, 20), (5, 60), (10, 20), (10, 30), (10, 60), (20, 40), (20, 60), (20, 120)):
        monthly_single_stock['MA_' + str(p) + '_' + str(q)] = single_stock['MA_' + str(p) + '_' + str(q)].\
            resample(rule='m').apply(lambda x: (1.0 + x).prod() - 1.0)

    monthly_single_stock.fillna(value=0.00, inplace=True)
    monthly_single_stock.reset_index(inplace=True)

    all_stock = all_stock.append(monthly_single_stock, ignore_index=True)

end_time = time.time()
cost_time = end_time - start_time

# print all_stock
print 'cost time: ' + str(cost_time)

# all_stock.to_csv('D:/all_trading_data/data/output_data/test171118.csv', encoding='gbk')
all_stock.to_hdf('d:/all_trading_data/data/output_data/momentum_ma_for_allstock_data_20171128.h5', key='all_stock', mode='w')
