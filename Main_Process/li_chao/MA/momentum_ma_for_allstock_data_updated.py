# encoding: utf-8

"""
为momentum emv strategy 准备全量股票数据

"""

import os
import warnings
import pandas as pd
from Basic_Functions import Functions
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal

warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)

# 导入指数数据,作为benchmark
index_data = Functions.import_index_data_wande()

# 遍历数据文件夹中所有股票文件的文件名，得到股票代码列表
stock_code_list = Functions.get_stock_code_list_in_one_dir_wande(input_data_path='d:/all_trading_data/data/input_data/stock_data_wande/')
# print len(stock_code_list)
# exit()

# ====数据准备
all_stock = pd.DataFrame()

for code in stock_code_list[0:]:    # 可以适当少选一点股票

    stock_data = Functions.import_stock_data_wande(code)

    if len(stock_data) < 250:    # 剔除发行时间小于约1年的数据
        continue
    print 'The progress is in %.2f%%.' % (stock_code_list.index(code) * 1.0 / len(stock_code_list) * 100)
    stock_data = Functions.cal_adjust_price(stock_data, adjust_type='adjust_back', return_type=1)
    # 和index合并
    stock_data = Functions.merge_with_index_data(stock_data, index_data)
    stock_data = stock_data[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume', 'open_adjust_back',
                             'high_adjust_back', 'low_adjust_back', 'close_adjust_back']]

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
        # df = df[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume', 'equity']]
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

    # 将各类EMV参数的日收益率数据转化为月收益率
    for (p, q) in ((5, 20), (10, 20), (20, 60), (20, 120)):
        monthly_single_stock['MA_' + str(p) + '_' + str(q)] = single_stock['MA_' + str(p) + '_' + str(q)].\
            resample(rule='m').apply(lambda x: (1.0 + x).prod() - 1.0)

    monthly_single_stock.fillna(value=0.00, inplace=True)
    monthly_single_stock.reset_index(inplace=True)

    all_stock = all_stock.append(monthly_single_stock, ignore_index=True)

# print all_stock

# all_stock.to_csv('D:/all_trading_data/data/output_data/test171118.csv', encoding='gbk')
all_stock.to_hdf('d:/all_trading_data/data/output_data/momentum_ma_allstock_data_20171124.h5', key='all_stock', mode='w')
