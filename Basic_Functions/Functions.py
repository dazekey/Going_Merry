# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: Functions_v1.4_20171119.py
@time: 2017/11/19 15:05
"""

"""
v1.4 20171118
dui

v1.3 20171110
更新了网易财经的股票数据导入
替换所有import stock data函数里的input_data_path参数里的路径

Function modules:
1. importing stock data 导入股票数据
    1.1 import stock data from wande source: 从万得的数据导入股票数据
        import_stock_data_wande(stock_code, input_data_path='C:/all_trading_data/data/input_data/stock_data_wande/', other_columns=[], start_date='19890101')
    1.2  import stock data from xbx source 从xbx的数据导入股票数据
        import_stock_data_xbx(stock_code, input_data_path='C:/all_trading_data/data/input_data/stock_data/', other_columns=[], start_date='19890101')
    1.3 import stock data from money163 souurce 导入网易财经的股票数据

2. importing index data 导入指数数据
    2.1 import index data from wande source 从万得的数据导入指数数据
        import_index_data_wande(index_code='000001.SH', input_data_path='C:/all_trading_data/data/input_data/index_data_wande/', start_date='19890101')
    2.2 import index data from xbx source 从xbx的数据导入指数数据
        import_index_data_xbx(index_code='sh000001', input_data_path='C:/all_trading_data/data/input_data/index_data/', start_date='19890101')
3. Calculate the adjusted prices 计算个股的复权价
    cal_adjust_price(input_stock_data, adjust_type='adjust_back',return_type=0)
4. get the list of all stock codes from a specified folder 获得指定路径下 所有股票的代码，形成一个List返回
    4.1 get the list of all stock codes from wande folder 获得万得的股票代码列表
        get_stock_code_list_in_one_dir_wande(input_data_path='C:/all_trading_data/data/input_data/stock_data_wande/')
    4.2 get the list of all stock codes from xbx folder 获得xbx的股票代码列表
        get_stock_code_list_in_one_dir_xbx(input_data_path='C:/all_trading_data/data/input_data/stock_data/')
5. merge stock data with index data in daily status 将个股数据与大盘数据合并, 日周期
    merge_with_index_data(df, index_data)
6. transfer stock data to another time base 周期转换函数
    transfer_to_period_data(df, period_type='m')
7. line cross another line 曲线穿越函数，多用于技术分析
    7.1 上穿下穿函数
    cross_both(df, s1, s2)
    7.2 s1 上穿 s2, 反过来就是下穿
    cross_single(df, s1, s2)
8. add the columns of limit up and down 增加涨跌停列
    limit_up_down(df)


"""

import pandas as pd
import os
import urllib2
import time
import datetime
# pd.set_option('expand_frame_repr',False)  # 多列不换行

# 定义全局变量，所有数据的路径位置
# global input_data_path, out_put_path, stock_dir, index_dir
# input_data_path = 'C:/all_trading_data/data/input_data'
input_data_path = 'D:/all_trading_data/data/input_data'  # 更换存储盘符
# out_put_path = 'C:/all_trading_data/data/output_data'
out_put_path = 'D:/all_trading_data/data/output_data' # 更换盘符
stock_dir_wande = '/stock_data_wande/'
index_dir_wande = '/index_data_wande/'
stock_dir_xbx = '/stock_data/'
index_dir_xbx = '/index_data/'
stock_dir_money163 = '/stock_data_money163/test/'

# ====1 导入股票数据
# 1.1 导入股票数据for 万得
def import_stock_data_wande(stock_code, input_data_path=input_data_path+stock_dir_wande, other_columns=[], start_date='19890101'):
    """
    注：该函数专门适用于万得的数据，如果数据源发生变化，请仔细检查该代码，尤其是列名和列的数字属性，需要调整
    导入在data/input_data/stock_data_wande下的股票数据。
    :param stock_code: 股票数据代码
    :param input_data_path = 'C:/all_trading_data/data/input_data/stock_data_wande/' 万得得个股数据路径
    :param other_columns: 默认值导入制定数据字段，可以补充输入指定字段
        默认字段：'交易日期', '股票代码', '开盘价', '最高价', '最低价', '收盘价', '涨跌幅', '成交额'，'总市值’
    :param start_date = '19890101' 个股数据的开始时间
    :return: 返回DataFrame的数据
    """
    df = pd.read_csv(input_data_path + stock_code + '.CSV', encoding = 'gbk')
    df.columns = [i.encode('utf-8') for i in df.columns]
    df.fillna(0, inplace=True)  # 万得的数据很多开头为空值，所以要将空值填补为0，不然之后计算会有问题
    df.rename(columns={'日期': 'date', '代码': 'code', '开盘价(元)': 'open', '最高价(元)': 'high', '最低价(元)': 'low',
                       '收盘价(元)': 'close', '涨跌幅(%)': 'change', '成交金额(元)': 'money', '总市值(元)': 'market_value', '成交量(股)':'volume'}, inplace=True)
    df = df[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'money', 'volume', 'market_value'] + other_columns]    #互换了下顺序，这样print的时候open在前
    df['change'] = df['change']/100.0000  # 因为万德的涨跌幅没有除以100
    df.sort_values(by=['date'], inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= pd.to_datetime(start_date)]
    # df['股票代码'] = stock_code
    df.reset_index(inplace=True, drop=True)

    return df

# 1.2 导入股票数据for xbx
def import_stock_data_xbx(stock_code, input_data_path=input_data_path+stock_dir_xbx, other_columns=[], start_date='19890101'):
    """
    注：该函数专门适用于xbx的数据，如果数据源发生变化，请仔细检查该代码，尤其是列名和列的数字属性，需要调整
    导入在data/input_data/stock_data下的股票数据。
    :param stock_code: 股票数据代码
    :param input_data_path = 'C:/all_trading_data/data/input_data/stock_data/' xbx个股数据路径
    :param other_columns: 默认值导入制定数据字段，可以补充输入指定字段
        默认字段：'交易日期', '股票代码', '开盘价', '最高价', '最低价', '收盘价', '涨跌幅', '成交额', '总市值’
    :param start_date = '19890101' 个股数据的开始时间
    :return: 返回DataFrame的数据
    """
    df = pd.read_csv(input_data_path + stock_code + '.csv', encoding = 'gbk')
    df.columns = [i.encode('utf-8') for i in df.columns]
    df.fillna(0, inplace=True)  # 万得的数据很多开头为空值，所以要将空值填补为0，不然之后计算会有问题
    df.rename(columns={'交易日期': 'date', '股票名称': 'name', '股票代码': 'code','开盘价': 'open', '最高价': 'high', '最低价': 'low',
                       '收盘价': 'close', '涨跌幅': 'change', '成交额': 'money', '总市值': 'market_value'}, inplace=True)
    df = df[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'money', 'market_value'] + other_columns]    #互换了下顺序，这样print的时候open在前
    # df['change'] = df['change']/100.0000  # 因为万德的涨跌幅没有除以100
    df.sort_values(by=['date'], inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= pd.to_datetime(start_date)]
    # df['股票代码'] = stock_code
    df.reset_index(inplace=True, drop=True)

    return df

# 1.3 导入网易财经的股票数据
def import_stock_data_money163(stock_code, input_data_path=input_data_path + stock_dir_money163, other_columns=[], start_date='19890101'):
    """
    注：该函数专门适用于xbx的数据，如果数据源发生变化，请仔细检查该代码，尤其是列名和列的数字属性，需要调整
    导入在data/input_data/stock_data下的股票数据。
    :param stock_code: 股票数据代码
    :param input_data_path = 'C:/all_trading_data/data/input_data/stock_data/' xbx个股数据路径
    :param other_columns: 默认值导入制定数据字段，可以补充输入指定字段
        默认字段：'交易日期', '股票代码', '开盘价', '最高价', '最低价', '收盘价', '涨跌幅', '成交额', '总市值’
    :param start_date = '19890101' 个股数据的开始时间
    :return: 返回DataFrame的数据
    """
    df = pd.read_csv(input_data_path + stock_code + '.csv', encoding = 'gbk')
    df.dropna(how='all', inplace=True)  # 删除空值的行
    df.columns = [i.encode('utf-8') for i in df.columns]
    df.fillna(0, inplace=True)  # 万得的数据很多开头为空值，所以要将空值填补为0，不然之后计算会有问题
    df.rename(columns={'日期': 'date', '名称': 'name', '股票代码': 'code','开盘价': 'open', '最高价': 'high', '最低价': 'low',
                       '收盘价': 'close', '涨跌幅': 'change', '涨跌额': 'change_amount', '换手率': 'turnover_rate', '成交量': 'volume', '成交金额': 'money', '总市值': 'market_value', '流通市值': 'outstanding_value', '交易笔数': 'transaction_num'}, inplace=True)
    df = df[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'change_amount', 'turnover_rate', 'volume',  'money', 'market_value'] + other_columns]    #互换了下顺序，这样print的时候open在前
    # df['change'] = df['change']/100.0000  # 因为万德的涨跌幅没有除以100
    df['code'] = df['code'].apply(lambda x: x.split('\'')[1])

    df.loc[df['change'] == 'None', 'change'] = 0
    df['change'] = df['change'].astype('float')
    df['change'] = df['change'] / 100.00

    df.loc[df['change_amount'] == 'None', 'change_amount'] = 0
    df['change_amount'] = df['change_amount'].astype('float')
    df['change_amount'] = df['change_amount'] / 100.00

    # df['change'] = df['change'] / 100
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by=['date'], inplace=True)
    df = df[df['date'] >= pd.to_datetime(start_date)]
    # df['股票代码'] = stock_code
    df.reset_index(inplace=True, drop=True)

    return df

# ==== 2 导入指数数据
# 2.1 导入指数数据 for 万得
def import_index_data_wande(index_code='000001.SH', input_data_path = input_data_path + index_dir_wande, start_date='19890101'):
    """
    注：该函数专门适用于万得的数据，如果数据源发生变化，请仔细检查该代码，尤其是列名和列的数字属性，需要调整
    导入在data/input_data/index_data下的股票数据。
    :param index_code: 指数数据
    :param input_data_path = 'C:/all_trading_data/data/input_data/index_data_wande/' 万得个股数据路径
    :param start_date = '19890101' 指数开始读取的日期
    :return: 返回DataFrame的数据
    """
    df_index = pd.read_csv(input_data_path + index_code + '.CSV', encoding='gbk')
    df_index.columns = [i.encode('utf-8') for i in df_index.columns]
    df_index.rename(columns={'日期': 'date', '涨跌幅(%)': 'index_change', '收盘价': 'index_close'}, inplace=True)
    df_index['date'] = pd.to_datetime(df_index['date'])
    df_index['index_change'] = df_index['index_change'] / 100.0000  # 因为万德的涨跌幅没有除以100
    df_index = df_index[['date', 'index_change', 'index_close']]
    df_index.rename(columns={'change': 'index_change'}, inplace=True)  # 为了合并后区分直接在上面rename了
    df_index.sort_values(by=['date'], inplace=True)
    df_index.dropna(subset=['index_change'], inplace=True)  # 指数都不存在的日期一般是法定节假日
    df_index.fillna(0)
    df_index = df_index[df_index['date'] >= pd.to_datetime(start_date)]
    df_index.reset_index(inplace=True, drop=True)

    return df_index

# 2.2 导入指数数据 for xbx
def import_index_data_xbx(index_code='sh000001', input_data_path=input_data_path+index_dir_xbx, start_date='19890101'):
    """
    注：该函数专门适用于xbx的数据，如果数据源发生变化，请仔细检查该代码，尤其是列名和列的数字属性，需要调整
    导入在data/input_data/index_data下的股票数据。
    :param index_code: 指数数据
    :param input_data_path = 'C:/all_trading_data/data/input_data/index_data/' xbx的指数数据路径
    :param start_date = '19890101' 指数开始读取的日期
    :return: 返回DataFrame的数据
    """
    df_index = pd.read_csv(input_data_path + index_code + '.csv', encoding='gbk')
    # df_index.columns = [i.encode('utf-8') for i in df_index.columns]
    df_index.rename(columns={'change': 'index_change', 'close': 'index_close'}, inplace=True)
    df_index['date'] = pd.to_datetime(df_index['date'])
    # df_index['index_change'] = df_index['index_change'] / 100.0000  # 因为万德的涨跌幅没有除以100
    df_index = df_index[['date', 'index_change', 'index_close']]
    df_index.rename(columns={'change': 'index_change'}, inplace=True)  # 为了合并后区分直接在上面rename了
    df_index.sort_values(by=['date'], inplace=True)
    df_index.dropna(subset=['index_change'], inplace=True)  # 指数都不存在的日期一般是法定节假日
    df_index.fillna(0)
    df_index = df_index[df_index['date'] >= pd.to_datetime(start_date)]
    df_index.reset_index(inplace=True, drop=True)

    return df_index


# ==== 3. Calculate the adjusted prices 计算个股的复权价
def cal_adjust_price(input_stock_data, adjust_type='adjust_back', return_type=2):
    """
    计算复权价
    :param input_stock_data: 导入input_stock_data函数返回的df
    :param adjust_type: 复权类型：前复权 adjust_forth 后复权adjust_back， 默认：后复权adjust_back
    :param retrun_type:  默认值为 2
                        返回数据类型 0: 只返回调整后的OHLC四列数据，
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
        # 只返回股权调整后的OHLC四列
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

# ==== 4 获得指定路径下 所有股票的代码，形成一个List返回
# 4.1 获得万得的股票代码列表
def get_stock_code_list_in_one_dir_wande(input_data_path='D:/all_trading_data/data/input_data/stock_data_wande/'):
    """
    指定文件夹下找到所有股票代码
    :param path: 指定文件夹路径
    :return: 返回stock code list
    """
    stock_list = []
    path = str(input_data_path)
    # os.walk遍历文件
    for root, dirs, files in os.walk(input_data_path):
        if files:
            for f in files:
                # if f.endswith('.csv'):
                if f.endswith('.CSV'):  # 万得的数据是以CSV为后缀，不是csv。。
                    # stock_list.append(f[:8])
                    stock_list.append(f.split('.CSV')[0])
    return stock_list

# 4.2 获得xbx的股票代码列表
def get_stock_code_list_in_one_dir_xbx(input_data_path='C:/all_trading_data/data/input_data/stock_data/'):
    """
    指定文件夹下找到所有股票代码
    :param path: 指定文件夹路径
    :return: 返回stock code list
    """
    stock_list = []
    path = str(input_data_path)
    # os.walk遍历文件
    for root, dirs, files in os.walk(input_data_path):
        if files:
            for f in files:
                # if f.endswith('.csv'):
                if f.endswith('.csv'):  # 万得的数据是以CSV为后缀，不是csv。。
                    # stock_list.append(f[:8])
                    stock_list.append(f.split('.csv')[0])
    return stock_list

# ==== 5 将股票数据和指数数据合并 merge
def merge_with_index_data(df, index_data, source='wande'):
    """
    将股票数据和指数数据合并
    :param df: 股票数据的df
    :param index_data: 指数数据的df
    :return: 合并后的df, 增加列 index_change, index_close, trade
    """
    df = pd.merge(
        left=df,
        right=index_data,
        on='date',
        how='right', #以指数为基准
        sort=True,
        indicator=True  # 自动增加一列 _merge 告诉我们该行属于哪张表
    )

    # 将停盘时间的['涨跌幅’,'成交额]数据设置为0
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
    if source == 'wande':
        df.loc[df['money'] == 0, 'trade'] = 0
    elif source == 'xbx':
        df.loc[df[df['_merge'] == 'right_only'].index, 'trade'] = 0
    """之前加了indicator，right_only表示只有指数交易日期的单元格"""
    del df['_merge']

    return df

# ==== 6 将个股数据的周期转换函数
def transfer_to_period_data(df, period_type='m'):
    """
    日线周期转周w、月m、年y等周期
    :param df: 输入日线数据df
    :param period_type: 转换的周期，默认为月m
    附：常见时间频率
    A year
    M month
    W week
    D day
    H hour
    T minute
    S second
    :return: 返回转换好的df, 增加列daily capital_curve, last_change, trade_days, market_tarde_days
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
        if 'high' in i:
            period_df[i] = df[i].resample(rule=period_type).max()
        if 'low' in i:
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

# ==== 7
# 7.1 上穿下穿函数
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

# 7.2 上穿函数, 前后参数颠倒就
def cross_single(df, s1, s2, trade_type='buy'):
    """
    s1 上穿 s2
    :param df:
    :param s1:
    :param s2:
    :param trade_type: 设置买入卖出信号, 1 买入, 0 卖出
    :return: 变化的交易信号, 增加列signal_buy = 1 或者signal_sell = 0
    """
    df = df.copy()
    # 买入点
    # 条件1
    condition1 = df[s1] >= df[s2]
    # 条件2
    condition2 = df[s1].shift(1) < df[s2].shift(1)
    if trade_type == 'buy':
        df.loc[condition1 & condition2, 'signal_buy'] = 1
    elif trade_type == 'sell':
        df.loc[condition1 & condition2, 'signal_sell'] = 0
    return df




# ==== 8. add the columns of limit up and down 增加涨跌停列
def limit_up_down(df):
    """
    只能输入日线数据， 设置张跌停的序列
    :param df:
    :return: limit_up_open (开盘涨停), limit_up_close (收盘涨停)， limit_down_open(开盘跌停), limit_down_close (收盘跌停)
    """

    df = df.copy()

    # 涨停不能买的情况
    # 隔天开盘涨停的设置为1，买不进
    df.ix[df['open'] > df['close'].shift(1) * 1.097, 'limit_up_open'] = 1
    df['limit_up_open'].fillna(0, inplace=True)

    # 收盘涨停的股票
    df.ix[df['close'] > df['open'] * 1.097, 'limit_up_close'] = 1
    df['limit_up_close'].fillna(0, inplace=True)

    # 跌停不能卖的情况
    # 隔天开盘跌停不能卖
    df.ix[df['open'] < df['close'].shift(1) * 0.903, 'limit_down_open'] = 1
    df['limit_down_open'].fillna(0, inplace=True)

    # 收盘跌停不能卖
    df.ix[df['open'] < df['close'] * 0.903, 'limit_down_close'] = 1
    df['limit_down_close'].fillna(0, inplace=True)

    return df





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
