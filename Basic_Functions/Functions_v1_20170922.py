# coding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: Functions_v1_20170922.py
@time: 2017/9/24 21:53
"""
"""
Function mdules:
1. import_stock_data(stock_code, other_columns=[]) # 导入股票数据，专门用于万德
2. import_index_data(index_code='000001.SH')  # 导入指数数据，专门用于万德
3. cal_adjust_price(input_stock_data, adjust_type='after_adjust',return_type=0) # 计算个股的复权价
4. get_stock_code_list_in_one_dir(path)  # 获得指定路径下 所有股票的代码，形成一个List返回
5. merge_with_index_data(df, index_data)  # 将个股数据与大盘数据合并
6. transfer_to_period_data(df, period_type='m')  # 周期转换函数
7. cross_both(df, s1, s2)  # 上穿下穿函数
8. cross_single(df, s1, s2)  # s1 上穿 s2
9. get_all_stock_data # 获取指定文件夹中所有股票代码的list

"""

import pandas as pd
import os
import urllib2
import time
import datetime
# pd.set_option('expand_frame_repr',False)  # 多列不换行

# 定义全局变量，所有数据的路径位置
# global input_data_path, out_put_path, stock_dir, index_dir
input_data_path = 'C:/all_trading_data/data/input_data'
out_put_path = 'C:/all_trading_data/data/output_data'
stock_dir_wande = '/stock_data_wande/'
index_dir_wande = '/index_data_wande/'

# 导入股票数据
def import_stock_data(stock_code, input_data_path=input_data_path, stock_dir=stock_dir_wande, other_columns=[], start_date='19890101'):
    """
    注：该函数专门适用于万得的数据，如果数据源发生变化，请仔细检查该代码，尤其是列名和列的数字属性，需要调整
    导入在data/input_data/stock_data_wande下的股票数据。
    :param stock_code: 股票数据代码
    :param other_columns: 默认值导入制定数据字段，可以补充输入指定字段
        默认字段：'交易日期', '股票代码', '开盘价', '最高价', '最低价', '收盘价', '涨跌幅', '成交额'
    :return: 返回DataFrame的数据
    """
    df = pd.read_csv(input_data_path + stock_dir + stock_code + '.CSV', encoding = 'gbk')
    df.columns = [i.encode('utf-8') for i in df.columns]
    df.fillna(0, inplace=True)  # 万得的数据很多开头为空值，所以要将空值填补为0，不然之后计算会有问题
    df.rename(columns={'日期': 'date', '代码': 'code', '开盘价(元)': 'open', '最高价(元)': 'high', '最低价(元)': 'low',
                       '收盘价(元)': 'close', '涨跌幅(%)': 'change', '成交金额(元)': 'money'}, inplace=True)
    df = df[['date', 'code', 'close', 'high', 'low', 'open', 'change', 'money'] + other_columns]
    df['change'] = df['change']/100.0000  # 因为万德的涨跌幅没有除以100
    df.sort_values(by=['date'], inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= pd.to_datetime(start_date)]
    # df['股票代码'] = stock_code
    df.reset_index(inplace=True, drop=True)

    return df

# 导入指数数据
def import_index_data(index_code='000001.SH', input_data_path=input_data_path, index_dir=index_dir_wande, start_date='19890101'):
    """
    注：该函数专门适用于万得的数据，如果数据源发生变化，请仔细检查该代码，尤其是列名和列的数字属性，需要调整
    从input_stock_data/index_data/导入指数数据
    :param index_code: 默认选择上证指数sh0000001
    :return: 返回指数的df
    """
    df_index = pd.read_csv(input_data_path + index_dir + index_code + '.CSV', encoding='gbk')
    df_index.columns = [i.encode('utf-8') for i in df_index.columns]
    df_index.rename(columns={'日期': 'date', '涨跌幅(%)': 'change', '收盘价': 'index_close'}, inplace=True)
    df_index['date'] = pd.to_datetime(df_index['date'])
    df_index['change'] = df_index['change'] / 100.0000  # 因为万德的涨跌幅没有除以100
    df_index = df_index[['date', 'change', 'index_close']]
    df_index.rename(columns={'change': 'index_change'}, inplace=True)  # 为了合并后区分
    df_index.sort_values(by=['date'], inplace=True)
    df_index.dropna(subset=['index_change'], inplace=True)  # 指数都不存在的日期一般是法定节假日
    df_index.fillna(0)
    df_index = df_index[df_index['date'] >= pd.to_datetime(start_date)]
    df_index.reset_index(inplace=True, drop=True)

    return df_index

# 计算个股的复权价
def cal_adjust_price(input_stock_data, adjust_type='adjust_forth',return_type=0):
    """
    计算复权价
    :param input_stock_data: 导入input_stock_data函数返回的df
    :param adjust_type: 复权类型：前复权former_adjust 后复权after_adjust， 默认：后复权after_adjust
    :param retrun_type: 返回数据类型 0: 只返回调整后的OHLC四列数据，
                                    1: 返回原数据+调整后的OHLC四列,
                                    2: 将原来的OHLC替换成调整后的OHLC
    :return:  高开低收的收盘价df
    """
    # 创建空的df
    df = pd.DataFrame()

    # 计算复权价
    num = {'adjust_back': 0, 'adjust_forth': -1}
    price1 = input_stock_data['close'].iloc[num[adjust_type]]
    df['change_factor'] = (1.0 + input_stock_data['change']).cumprod()
    price2 = df['change_factor'].iloc[num[adjust_type]]
    df['close_' + adjust_type] = df['change_factor'] * (price1 / price2)
    df['adjust_factor'] = df['close_' + adjust_type] / input_stock_data['close']
    df['open_' + adjust_type] = input_stock_data['open'] * df['adjust_factor']
    df['high_' + adjust_type] = input_stock_data['high'] * df['adjust_factor']
    df['low_' + adjust_type] = input_stock_data['low'] * df['adjust_factor']

    if return_type == 0:
        # 只返回股权调整后的OPHL四列
        return df[[i + '_' + adjust_type for i in 'open', 'high', 'low', 'close']]
    elif return_type == 1:
        # 返回股权调整后的stock_data
        input_stock_data[[i + '_' + adjust_type for i in 'open', 'high', 'low', 'close']] = \
            df[[i + '_' + adjust_type for i in 'open', 'high', 'low', 'close']]
        return input_stock_data
    elif return_type ==2:
        input_stock_data[['open', 'high', 'low', 'close']] = df[[i + '_' +
                                                                 adjust_type for i in 'open', 'high', 'low', 'close']]
        return input_stock_data
# print import_stock_data('sh600000')
# print cal_adjust_price(import_stock_data('sh600000'))

# 导入文件夹下所有股票的代码
def get_stock_code_list_in_one_dir(path=str(input_data_path+stock_dir)):
    """
    指定文件夹下找到所有股票代码
    :param path: 指定文件夹路径
    :return: 返回stock code list
    """
    stock_list = []

    # os.walk遍历文件
    for root, dirs, files in os.walk(path):
        if files:
            for f in files:
                # if f.endswith('.csv'):
                if f.endswith('.CSV'):  # 万得的数据是以CSV为后缀，不是csv。。
                    # stock_list.append(f[:8])
                    stock_list.append(f.split('.CSV')[0])
    return stock_list

# 将股票数据和指数数据合并 merge
def merge_with_index_data(df, index_data):
    """
    将股票数据和指数数据合并
    :param df: 股票数据的df
    :param index_data: 指数数据的df
    :return: 合并后的df
    """
    df = pd.merge(
        left=df,
        right=index_data,
        on='date',
        how='right', #以指数为基准
        sort=True,
        indicator=True  # 自动增加一列 _merge 告诉我们该行属于哪张表
    )

    # 将停盘时间的['涨跌幅’,'成交额]数据天部位0
    fill_0_list = ['change', 'money']
    df.loc[:, fill_0_list] = df[fill_0_list].fillna(value=0)

    # 空的收盘价用前一天的收盘价
    df['close'] = df['close'].fillna(method='ffill')

    # 空的O,H,L都用C补充
    df['open'] = df['open'].fillna(value=df['close'])
    df['high'] = df['high'].fillna(value=df['close'])
    df['low'] = df['low'].fillna(value=df['close'])

    # 如果输入的个股数据已经做过除权处理还要将除权后的OHL用C补充
    for i in df.columns:
        # if ('close' and 'adjust') in i:  # 为什么这个写法会出现含有 adjust的所有列
        if 'close' in i and 'adjust' in i:
            df['close_adjust'] = df[i]
    if 'close_adjust' in df.columns:
        for i in df.columns:
            if 'adjust' in i:
                df[i] = df[i].fillna(value=df['close_adjust'])

    # 用前一天的数据，补全其空值
    df.fillna(method='ffill', inplace=True)

    # 去除上市之前的数据
    df = df[df['code'].notnull()]
    df.reset_index(drop=True, inplace=True)

    # 计算当天是否交易
    df['trade'] = 1
    df.loc[df[df['_merge'] == 'right_only'].index, 'trade'] = 0
    """这个函数什么意思？"""
    del df['_merge']

    return df

# 周期转换函数
def transfer_to_period_data(df, period_type='m'):
    """
    日线周期转周w、月m、年y等周期
    :param df: 输入日线数据df
    :param period_type: 转换的周期，默认为月m
    :return: 返回转换好的df
    """

    # 将交易日期设置为index
    # df.columns = [i.encode('utf-8') for i in df.columns]
    df['trade_date'] = df['date']
    """因为转换时，默认的交易日期会以自然周期日，每周最后一天是星期六，但是实际交易日的最后一天是工作日"""
    df.set_index('date', inplace=True)

    # 转换为周期数据
    period_df = df.resample(rule=period_type).last()

    # 原来的写法
    # period_df['open'] = df['open'].resample(rule=period_type).first()
    # period_df['high'] = df['high'].resample(rule=period_type).max()
    # period_df['low'] = df['low'].resample(rule=period_type).min()
    # 如果输入的个股数据已经做过除权处理还要将除权后的OHL处理
    for i in period_df.columns:
        if 'open' in i:
            period_df[i] = df[i].resample(rule=period_type).first()
        elif 'high' in i:
            period_df[i] = df[i].resample(rule=period_type).max()
        elif 'low' in i:
            period_df[i] = df[i].resample(rule=period_type).min()

    period_df['money'] = df['money'].resample(rule=period_type).sum()
    period_df['change'] = df['change'].resample(rule=period_type).apply(lambda x: (1.0+x).prod()-1.0)

    period_df['daily_capital_curve'] = df['change'].resample(rule=period_type).apply(lambda x: list((x+1).cumprod()))
    """这句的意义是什么，简单的资金曲线怎么写，是运算apply还是先运算resample
        返回的是一个list 包含了这段周期内每日的涨跌幅累乘
    """
    # print period_df['资金曲线']
    # exit()
    period_df['last_change'] = df['change'].resample(period_type).last()
    period_df['trade_days'] = df['trade'].resample(period_type).sum()
    period_df['market_trade_days'] = df['code'].resample(period_type).size()

    # 去除一天都没有交易的周
    period_df.dropna(subset=['code'], inplace=True)

    # 重新设定index
    period_df.reset_index(inplace=True)
    period_df['date'] = period_df['trade_date']
    del period_df['trade_date']

    return period_df

# 上穿下穿函数
def cross_both(df, s1, s2):
    """

    :param df:
    :param s1: 序列1
    :param s2: 序列2
    :return:  有'signal'列的df
    """
    df = df.copy()
    # 买入点
    # 条件1
    condition1 = df[s1] >= df[s2]
    # 条件2
    condition2 = df[s1].shift(1) < df[s2].shift(1)
    df.loc[condition1 & condition2, 'signal'] = 1

    # 卖出点
    # 条件1
    condition1 = df[s1] <= df[s2]
    # 条件2
    condition2 = df[s1].shift(1) > df[s2].shift(1)
    df.loc[condition1 & condition2, 'signal'] = 0

    return df

# 上穿函数
def cross_signle(df, s1, s2, trade_type='buy'):
    """
    s1 上穿 s2
    :param df:
    :param s1:
    :param s2:
    :param trade_type: 设置买入卖出信号, 1 买入, 0 卖出
    :return: 变化的交易信号
    """
    df = df.copy()
    # 买入点
    # 条件1
    condition1 = df[s1] >= df[s2]
    # 条件2
    condition2 = df[s1].shift(1) < df[s2].shift(1)
    if trade_type == 'buy':
        df.loc[condition1 & condition2, 'signal'] = 1
    elif trade_type == 'sell':
        df.loc[condition1 & condition2, 'signal'] = 0
    return df

# 获取指定文件夹中所有股票代码的list
def get_all_stock_data(input_path='C:/all_trading_data/data/input_data/stock_data_wande',
                  output_path='C:/all_trading_data/data/output_data/Going_Merry/', save=True):
    """
    # 获取指定文件夹中所有股票代码的list
    :param input_path: 个股数据所在的文件夹
    :param output_path: 结果输出所在的文件夹
    :param save: 是否要保存数据
    :return: all_stock_data
    """
    all_stock_data = pd.DataFrame()
    stock_list = Functions.get_stock_code_list_in_one_dir(path=input_path)
    for code in stock_list:
        stock_data = Functions.import_stock_data(code)
        # 判断每天开盘是否涨停
        stock_data.ix[stock_data['open'] > stock_data['close'].shift(1) * 1.097, 'limit_up'] = 1
        stock_data['limit_up'].fillna(0, inplace=True)
        all_stock_data = all_stock_data.append(stock_data, ignore_index=True)
        date = time.strftime('%Y%m%d', time.localtime(time.time()))

        # 输出一个进度过程，不然都不知道运行到哪里了
        progess = ((stock_list.index(code) + 1.0) / len(stock_list)) * 100.00  # 读取当前股票在list中的位置， 除以总的list长度
        print 'stock %s in progress is %.2f%%' % (code, progess)
        if save == True:
            all_stock_data.to_hdf(output_path + 'all_stock_data_' + str(date) + '.h5', key='all_stock', mode='w')
            # all_stock_data.to_csv('C:/all_trading_data/data/output_data/Going_Merry/all_stock_data_20171005.csv')

    return all_stock_data
    print 'all_stock_data has been finished.'



# 判断开盘涨跌停
# def limit_up_down(stock_data):
#     # 判断每天开盘是否涨停
#     stock_data.ix[stock_data['开盘价(元)'] > stock_data['收盘价(元)'].shift(1) * 1.097, 'limit_up'] = 1
#     stock_data['limit_up'].fillna(0, inplace=True)
#     # 判断每天开盘是否跌停
#     stock_data.ix[stock_data['开盘价(元)'] < stock_data['收盘价(元)'].shift(1) * 1.097, 'limit_up'] = 1
#     stock_data['limit_up'].fillna(0, inplace=True)

# 生成中间数据all_stock_data用来模拟策略
# def get_all_stock_data(save_path, load_type='adjust_merge',save_type='hd5'):
#     """
#     生成中间数据all_stock_data用来模拟策略
#     :param load_path: 读取股票的路径
#     :param save_path: 存储结果的路径
#     :param load_type: 读取类型：默认为adjus_merge
#                         orignal：直接读取个股原始数据然后合并成大表
#                         adjust：读取数据后计算除权价，然后合并成大表
#                         merge：读取数据后与指数合并，然后合并成大表
#                         adjust_merge：读取数据后先计算除权价，然后与指数合并，再合并成大表
#     :param save_type: 结果存储类型：默认’hd5‘, ’csv'
#
#     :return:
#     """
#     stock_list = get_stock_code_list_in_one_dir(input_data_path+stock_dir)
#     print stock_list
#     all_stock_data = pd.DataFrame()
#     for code in stock_list:
#         if load_type == 'orginal':
#             stock_data = import_stock_data(code)
#             all_stock_data = all_stock_data.append(stock_data)
#             # print code +' is finished'
#
#     name = 'all_stock_data_' + load_type
#     if save_type == 'hd5':
#         all_stock_data.to_hdf(name + '.hdf5', )
#         print name
#     elif save_type == 'csv':
#         print name
#     else:
#         print 'save_type is wrong'
#     return all_stock_data
