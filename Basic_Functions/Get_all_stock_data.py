# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: Get_all_stock_data.py
@time: 2017/10/26 23:56
"""
"""
1.获取指定文件夹中所有股票代码的集合
    1.1 从万得的股票数据 获得all_stock_data1.1 从万得的股票数据 获得all_stock_data
        get_all_stock_data_wande(input_path='C:/all_trading_data/data/input_data/stock_data_wande',
                  output_path='C:/all_trading_data/data/output_data/Going_Merry/', save=True)
    1.2 从xbx的数据获得 all stock data
        get_all_stock_data_xbx(input_path='C:/all_trading_data/data/input_data/stock_data',
                  output_path='C:/all_trading_data/data/output_data/Going_Merry/', save=True)

"""
import pandas as pd
from Basic_Functions import Functions
from Basic_Functions import Data_standardize
import time

# ==== 1 获取指定文件夹中所有股票代码的集合
# 1.1 从万得的股票数据 获得all_stock_data
def get_all_stock_data_wande(input_path='C:/all_trading_data/data/input_data/stock_data_wande',
                  output_path='C:/all_trading_data/data/output_data/Going_Merry/', save=True):
    """
    # 获取指定文件夹中所有股票代码的list
    :param input_path: 个股数据所在的文件夹
    :param output_path: 结果输出所在的文件夹
    :param save: 是否要保存数据
    :return: all_stock_data
    """
    all_stock_data = pd.DataFrame()
    stock_list = Functions.get_stock_code_list_in_one_dir_wande(input_path)
    for code in stock_list:

        # stock_data = Functions.import_stock_data_wande(code)
        # # 判断每天开盘是否涨停
        # stock_data.ix[stock_data['open'] > stock_data['close'].shift(1) * 1.097, 'limit_up'] = 1
        # stock_data['limit_up'].fillna(0, inplace=True)

        # 获取标准化的个股数据，除权、指数合并、涨跌停列添加
        stock_data = Data_standardize.data_standardize_wande(code)

        all_stock_data = all_stock_data.append(stock_data, ignore_index=True)
        date = time.strftime('%Y%m%d', time.localtime(time.time()))

        # 输出一个进度过程，不然都不知道运行到哪里了
        progess = ((stock_list.index(code) + 1.0) / len(stock_list)) * 100.00  # 读取当前股票在list中的位置， 除以总的list长度
        print 'stock %s in progress is %.2f%%' % (code, progess)
        if save == True:
            all_stock_data.to_hdf(output_path + 'all_stock_data_wande_' + str(date) + '.h5', key='all_stock', mode='w')
            # all_stock_data.to_csv('C:/all_trading_data/data/output_data/Going_Merry/all_stock_data_20171005.csv')

    return all_stock_data
    print 'all_stock_data has been finished.'

# 1.2 从xbx的数据获得 all stock data
def get_all_stock_data_xbx(input_path='C:/all_trading_data/data/input_data/stock_data',
                  output_path='C:/all_trading_data/data/output_data/Going_Merry/', save=True):
    """
    # 获取指定文件夹中所有股票代码的list
    :param input_path: 个股数据所在的文件夹
    :param output_path: 结果输出所在的文件夹
    :param save: 是否要保存数据
    :return: all_stock_data
    """
    all_stock_data = pd.DataFrame()
    stock_list = Functions.get_stock_code_list_in_one_dir_wande(input_path)
    for code in stock_list:
        # stock_data = Functions.import_stock_data_wande(code)
        # # 判断每天开盘是否涨停
        # stock_data.ix[stock_data['open'] > stock_data['close'].shift(1) * 1.097, 'limit_up'] = 1
        # stock_data['limit_up'].fillna(0, inplace=True)

        # 获取标准化的个股数据，除权、指数合并、涨跌停列添加
        stock_data = Data_standardize.data_standardize_xbx(code)

        all_stock_data = all_stock_data.append(stock_data, ignore_index=True)
        date = time.strftime('%Y%m%d', time.localtime(time.time()))

        # 输出一个进度过程，不然都不知道运行到哪里了
        progess = ((stock_list.index(code) + 1.0) / len(stock_list)) * 100.00  # 读取当前股票在list中的位置， 除以总的list长度
        print 'stock %s in progress is %.2f%%' % (code, progess)
        if save == True:
            all_stock_data.to_hdf(output_path + 'all_stock_data_xbx_' + str(date) + '.h5', key='all_stock', mode='w')
            # all_stock_data.to_csv('C:/all_trading_data/data/output_data/Going_Merry/all_stock_data_20171005.csv')

    return all_stock_data
    print 'all_stock_data has been finished.'

# get_all_stock_data_wande()
# get_all_stock_data_xbx()


