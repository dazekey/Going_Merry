# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: Functions_test.py
@time: 2017/9/24 21:53
"""
"""
本函数用于测试 Basic_Functions / Functions中的所有函数是否运行正常
"""

import pandas as pd
from Basic_Functions import Functions
pd.set_option('expand_frame_repr', False)

# ====1 测试个股数据导入
# 1.1 测试万得个股数据读取
# stock_data = Functions.import_stock_data_wande('000001.SZ')
# print stock_data['date']
# exit()

# 1.2 测试xbx个股数据读取
# stock_data = Functions.import_stock_data_xbx('sh600000')
# print stock_data
# exit()

# 1.3 测试money163个股数据读取
stock_data = Functions.import_stock_data_money163('000001')
# df['change'] = df['change'].astype('float')
print stock_data
# print df['change'].astype('float', inplace=True)
# print df['change'].astype('float')
exit()

# 2 测试指数数据导入
# 2.1 测试大盘数据读取 万得
# index_code='000001.SH'
# index_data = Functions.import_index_data_wande()
# print index_data['date']
# exit()

# 2.2 测试大盘数据读取 xbx
# index_code='sh000001'
# index_data = Functions.import_index_data_xbx()
# print index_data
# exit()


# ==== 3 测试计算除权股价，默认是后复权
stock_data_adjust = Functions.cal_adjust_price(stock_data, adjust_type='adjust_forth', return_type=2)
print stock_data_adjust
exit()

# ==== 4 测试从一个指定的文件夹里获得所有股票名称的列表
# 4.1 从万得的数据读取股票列表
# file_path = 'C:/all_trading_data/data/input_data/stock_data_wande'
# print Functions.get_stock_code_list_in_one_dir_wande(file_path)
# 4.2 从xbx的数据读取股票列表
file_path = 'D:/all_trading_data/data/input_data/stock_data'
# print Functions.get_stock_code_list_in_one_dir_xbx(file_path)
# exit()

# ==== 5 个股数据和指数数据合并，日周期
stock_data = Functions.merge_with_index_data(stock_data_adjust, index_data)
# print stock_data
# exit()

# ==== 6 周期转换
stock_data = Functions.transfer_to_period_data(stock_data, period_type='m')
print stock_data
exit()
# print stock_data
# 涨跌停信号添加
stock_data = Functions.limit_up_down(stock_data)

# stock_data.ix[stock_data['open'] > stock_data['close'].shift(1) * 1.097, 'limit_up'] = 1
print stock_data
exit()

# 获得所有股票数据
# df = Functions.get_all_stock_data(load_type='orginal')
# print df

import random
random = random.random()
print random