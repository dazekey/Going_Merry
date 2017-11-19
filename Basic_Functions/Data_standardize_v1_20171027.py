# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: Data_standardize_v1_20171027.py
@time: 2017/10/27 0:02
"""
"""
1. 利用Funcitons 里的函数对股票数据标准化处理
    1.1 对万得的数据进行处理，读取个股、指数、除权、合并、涨跌停信号添加
        data_standardize_wande(code)
    1.2 对xbx的数据进行数据处理，读取个股、指数、除权、合并、涨跌停信号添加
        data_standardize_xbx(code)

"""
from Basic_Functions import Functions
import pandas as pd
pd.set_option('expand_frame_repr', False)

code_wande = '000001.SZ'
code_xbx='sh600000'

# ==== 1 对股票数据标准化处理
# 1.1 对万得的数据进行处理，读取个股、指数、除权、合并、涨跌停信号添加
def data_standardize_wande(code):
    # 1.读取万得的股票数据
    stock_data = Functions.import_stock_data_wande(code)
    # 2.读取指数数据
    index_data = Functions.import_index_data_wande()
    # 3.个股数据除权处理, 默认前复权，直接替换OLHC列
    stock_data = Functions.cal_adjust_price(stock_data, adjust_type=1)
    # 3.合并个股数据和指数数据
    stock_data = Functions.merge_with_index_data(stock_data, index_data)
    # 4.添加涨跌停列
    stock_data = Functions.limit_up_down(stock_data)
    return stock_data
# print stock_data
# print data_standardize_wande(code_wande)

# 对xbx的数据进行数据处理，读取个股、指数、除权、合并、涨跌停信号添加
def data_standardize_xbx(code):
    # 1.读取万得的股票数据
    stock_data = Functions.import_stock_data_xbx(code)
    # 2.读取指数数据
    index_data = Functions.import_index_data_xbx()
    # 3.个股数据除权处理, 默认后复权，直接替换OLHC列
    stock_data = Functions.cal_adjust_price(stock_data)
    # 3.合并个股数据和指数数据
    stock_data = Functions.merge_with_index_data(stock_data, index_data)
    # 4.添加涨跌停列
    stock_data = Functions.limit_up_down(stock_data)
    return stock_data

# print data_standardize_xbx(code_xbx)

# 对xbx的数据进行数据处理，读取个股、指数、除权、合并、涨跌停信号添加
def data_standardize_money163(stock_code,index_code='000001.SH'):
    # 1.读取万得的股票数据
    stock_data = Functions.import_stock_data_money163(stock_code)
    # 2.读取指数数据
    index_data = Functions.import_index_data_wande(index_code=index_code)
    # 3.个股数据除权处理, 默认后复权，直接替换OLHC列
    stock_data = Functions.cal_adjust_price(stock_data)
    # 3.合并个股数据和指数数据
    stock_data = Functions.merge_with_index_data(stock_data, index_data)
    # 4.添加涨跌停列
    stock_data = Functions.limit_up_down(stock_data)
    return stock_data

