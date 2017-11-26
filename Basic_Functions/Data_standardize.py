# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: Data_standardize_v1.1_20171119.py
@time: 2017/11/19 15:11
"""

"""
v1.1 更新：
1.data_standardize系列函数（万得，预测者，网易），读取的是数据，不再是代码。
2.计算除权价时候使用return_type=1，返回的是在原df上增加四列
"""
"""
1. 利用Functions 里的函数对股票数据标准化处理
    1.1 对万得的数据进行处理，读取个股、指数、除权、合并、涨跌停信号添加
        data_standardize_wande(code)
    1.2 对xbx的数据进行数据处理，读取个股、指数、除权、合并、涨跌停信号添加
        data_standardize_xbx(code)

"""
from Basic_Functions import Functions
import pandas as pd
import time
pd.set_option('expand_frame_repr', False)

code_wande = '000001.SZ'
code_xbx='sh600000'
end_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
# print end_date

# ==== 1 对股票数据标准化处理
# 1.1 对万得的数据进行处理，读取个股、指数、除权、合并、涨跌停信号添加
def data_standardize_wande(df, index_code='000001.SH', adjust_type='adjust_back', return_type=1, start_date='19890101', end_date=str(end_date)):
    # 1.读取万得的股票数据
    # stock_data = Functions.import_stock_data_wande(code)
    stock_data = df.copy()
    # 2.读取指数数据
    index_data = Functions.import_index_data_wande(index_code=index_code)
    # 3.个股数据除权处理, 默认前复权，直接替换OLHC列
    stock_data = Functions.cal_adjust_price(stock_data, adjust_type=adjust_type,return_type=return_type)
    # 3.合并个股数据和指数数据
    stock_data = Functions.merge_with_index_data(stock_data, index_data)
    # 4.添加涨跌停列
    stock_data = Functions.limit_up_down(stock_data)
    # 取得指定时间范围的数据
    stock_data = stock_data[(stock_data['date'] >= pd.to_datetime(start_date)) & (stock_data['date'] <= pd.to_datetime(end_date))]

    return stock_data
# print stock_data
# print data_standardize_wande(code_wande)

# 对xbx的数据进行数据处理，读取个股、指数、除权、合并、涨跌停信号添加
def data_standardize_xbx(df, index_code='sh000001', adjust_type='adjust_back', return_type=1, start_date='19890101'):
    # 1.读取万得的股票数据
    # stock_data = Functions.import_stock_data_xbx(code)
    stock_data = df.copy()
    # 2.读取指数数据
    index_data = Functions.import_index_data_xbx(index_code=index_code)
    # 3.个股数据除权处理, 默认后复权，直接替换OLHC列
    stock_data = Functions.cal_adjust_price(stock_data, adjust_type=adjust_type, return_type=return_type)
    # 3.合并个股数据和指数数据
    stock_data = Functions.merge_with_index_data(stock_data, index_data)
    # 4.添加涨跌停列
    stock_data = Functions.limit_up_down(stock_data)
    # 取得指定时间范围的数据
    stock_data = stock_data[stock_data['date'] >= pd.to_datetime(start_date)]

    return stock_data

# print data_standardize_xbx(code_xbx)

# 对xbx的数据进行数据处理，读取个股、指数、除权、合并、涨跌停信号添加
def data_standardize_money163(df,index_code='000001.SH', return_type=1, start_date='19890101'):
    # 1.读取万得的股票数据
    # stock_data = Functions.import_stock_data_money163(stock_code)
    stock_data = df.copy()
        # 2.读取指数数据
    index_data = Functions.import_index_data_wande(index_code=index_code)
    # 3.个股数据除权处理, 默认后复权，直接替换OLHC列
    stock_data = Functions.cal_adjust_price(stock_data, return_type=return_type)
    # 3.合并个股数据和指数数据
    stock_data = Functions.merge_with_index_data(stock_data, index_data)
    # 4.添加涨跌停列
    stock_data = Functions.limit_up_down(stock_data)
    # 取得指定时间范围的数据
    stock_data = stock_data[stock_data['date'] >= pd.to_datetime(start_date)]

    return stock_data

