# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: data_collecting.py
@time: 2017/11/7 23:28
"""


import tushare as ts
import pandas as pd
import time
from Basic_Functions import Functions
import warnings
import os
import urllib2
import csv
import datetime

pd.set_option('expand_frame_repr', False)
warnings.filterwarnings('ignore')
date_now = time.strftime('%Y%m%d', time.localtime(time.time()))
# print date_now

stock_data_path_money163_test = '/stock_data_money163/test/'
stock_data_path_money163_raw = '/stock_data_money163/raw/'
# url = 'http://quotes.money.163.com/service/chddata.html?code=1000001&start=19910403&end=20171107&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'

# I. ======Use tushare package to download stock_list
# 1. ====download stock list 含停牌，上市，即将上市，退市的所有股票
def get_stock_list_all(save=False):
    # 当前上市的股票
    stock_basics = ts.get_stock_basics()
    # stock_basics.to_csv(Functions.input_data_path + '/stock_list_tushare/stock_bacis_'+ date_now + '.csv', encoding='gbk')  # 包含了停牌的股票，但没有包含终止上市的股票
    # 历史上被退市的股票的股票
    stock_terminated = ts.get_terminated()
    stock_terminated['oDate'] = pd.to_datetime(stock_terminated['oDate'])
    stock_terminated.loc[stock_terminated['tDate'] == '-', 'tDate'] = '19000101'
    stock_terminated['tDate'] = pd.to_datetime(stock_terminated['tDate'])
    # print stock_terminated['oDate'].dtypes
    # exit()
    # 暂时停牌的股票
    # stock_suspend = ts.get_suspended()
    # stock_basics.to_csv(Functions.input_data_path + '/stock_list_tushare/stock_suspend_'+ date_now + '.csv', encoding='gbk')

    stock_basics.reset_index(inplace=True)
    stock_list = stock_basics[['code', 'name', 'timeToMarket']]
    stock_list['oDate'] = stock_list['timeToMarket'].astype('str')
    # '0' 无法被转换成时间日期，先将'0'转换成'19000101'
    stock_list.loc[stock_list['oDate'] == '0', 'oDate'] = '19000101'
    stock_list['oDate'] = pd.to_datetime(stock_list['oDate'])
    # print stock_list['timeToMarket'].dtypes
    # delete the columns of 'timeToMarket'
    stock_list.drop(['timeToMarket'], axis=1, inplace=True)
    stock_list['tDate'] = ''
    stock_list['trade'] = '1'
    # print stock_list
    # 生成含交易、停牌、终止所有股票的list
    stock_list_all = pd.DataFrame()
    stock_terminated['trade'] = '0'
    stock_list_all = stock_list.append(stock_terminated)
    stock_list_all.reset_index(drop=True, inplace=True)
    stock_list_all['code'] = '\'' + stock_list_all['code']
    if save == True:
        stock_list_all.to_csv(Functions.input_data_path + '/stock_list_tushare/stock_list_all_' + date_now + '.csv', mode='w', encoding='gbk', index=False)
    return stock_list_all

# print stock_list_all

# II ===== 个股数据初始化模块
# 1====初始化tushare个股数据
def initial_stock_data_tushare():
    # 根据stock_list_all 下载所有股票数据
    # print ts.get_k_data('600000', start='19000101')
    # 为了不每次重复下载股票，会先从文件夹里看下现在有的股票数据，生成exist_list
    exist_list = []
    for root, dirs, files in os.walk(Functions.input_data_path + '/stock_data_tushare/raw'):
        for file in files:
            exist_list.append(file.split('.csv')[0])

    stock_list_all = pd.read_csv(Functions.input_data_path + '/stock_list_tushare/stock_list_all_' + date_now + '.csv',
                                 encoding='gbk', converters={'code': str})
    stock_list_all['code'] = stock_list_all['code'].apply(lambda x: x.split('\'')[1])
    stock_list_all = stock_list_all.loc[(stock_list_all['oDate'] != '1900/01/01') & (stock_list_all['trade'] == 1), :]
    download_list = list(set(list(stock_list_all['code'])).difference(set(exist_list)))

    cons = ts.get_apis()

    for code in download_list:
        # code = code.split('\'')[1]
        print code + ' downloading.'
        df = ts.bar(code, start_date='1900-01-01', conn=cons)
        # df['name'] = stock_list_all.ix[stock_list_all['code'] == code, 'name'].values
        # print stock_list_all.iat[stock_list_all['code'] == code, 'name']
        # print df
        df.to_csv(Functions.input_data_path + '/stock_data_tushare/' + code + '.csv', encoding='gbk', index=False)
        # time.sleep(3)
        print "Downloaded %s stock data. Progess is in %.2f%%."  % (code, (float(download_list.index(code)) / len(download_list) * 100))
    print "Initial stock data tushare finished."

# 2====初始化股票数据：从网易的API接口直接下载股票数据的CSV 然后保存到本地
# 下载存储函数
def download_stock_data_money163(code, start='19890101', end=str(date_now), mode='initial', save_path=Functions.input_data_path + stock_data_path_money163_raw):
    # print code + ' is downloading.'
    # print type(code[0])
    if code[0] == '6':
        signal=str(0)
    else: signal = str(1)
    # url = 'http://quotes.money.163.com/service/chddata.html?code='+ signal + code + '&start=' + start + '&end=' + end +'&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
    url = 'http://quotes.money.163.com/service/chddata.html?code=' + signal + code + '&start=' + start + '&end=' + end
    # print url
    response = urllib2.urlopen(url)
    csvReader = response.read().decode('gbk')
    # df = pd.DataFrame()
    # csvReader = csvReader.split('\n')
    # for row in df:
    #     print row
    rows = csvReader.split('\n')
    if mode == 'initial':
        csvfile = open(save_path + code + '.csv', mode='wb')
        writer = csv.writer(csvfile)
        for row in rows:
            split_row = row.split(',')
            full_data = []
            for row_s in split_row:
                row_s = row_s.encode('gbk')
                full_data.append(row_s)
            # print full_data
            writer.writerow(full_data)
        csvfile.close()
    elif mode == 'update':
        csvfile = open(save_path + code + '.csv', mode='ab')
        writer = csv.writer(csvfile)
        i = 0
        for row in rows:
            split_row = row.split(',')
            full_data = []
            if i == 1:
                for row_s in split_row:
                    row_s = row_s.encode('gbk')
                    full_data.append(row_s)
                # print full_data
                writer.writerow(full_data)
            i += 1
        csvfile.close()

# download_stock_data_money163(code='000002', mode='update')
# exit()

def initial_stock_data_money163(path = Functions.input_data_path + stock_data_path_money163_raw):
    # 根据stock_list_all 下载所有股票数据
    # print ts.get_k_data('600000', start='19000101')
    # 为了不每次重复下载股票，会先从文件夹里看下现在有的股票数据，生成exist_list
    exist_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            exist_list.append(file.split('.csv')[0])

    stock_list_all = pd.read_csv(Functions.input_data_path + '/stock_list_tushare/stock_list_all_' + date_now + '.csv',
                                 encoding='gbk', converters={'code': str})
    stock_list_all = stock_list_all.loc[(stock_list_all['oDate'] != '1900/1/1') & (stock_list_all['trade'] == 1), :]
    stock_list_all['code'] = stock_list_all['code'].apply(lambda x: x.split('\'')[1])
    download_list = list(set(list(stock_list_all['code'])).difference(set(exist_list)))

    for code in download_list:
        print code + ' downloading.'
        download_stock_data_money163(code, save_path=Functions.input_data_path + stock_data_path_money163_test)
        time.sleep(3)  # 每下载一个休息1秒
        # time.sleep(3)
        print "Downloaded %s stock data. Progess is in %.2f%%."  % (code, (float(download_list.index(code)) / len(download_list) * 100))
    print "Initial stock data money163 finished."


# 定义更新函数，读取本地的数据列，如果最新一天的日期小于当前日期则更新
def update_stock_data_money163(path = Functions.input_data_path + stock_data_path_money163_raw):
    exist_list = []
    for root, dirs, files in os.walk(Functions.input_data_path + '/stock_data_money163/test'):
        for file in files:
            exist_list.append(file.split('.csv')[0])
    # print exist_list
    for code in exist_list:
        data = pd.read_csv(path + str(code) + '.csv', encoding='gbk')
        if data.shape[0] == 0:
            continue
        else:
            data.dropna(how='all', inplace=True)
            data[u'日期'] = pd.to_datetime(data[u'日期'])
            data.sort_values(by= u'日期', ascending=False, inplace=True)
            data.drop_duplicates(subset=[u'日期'], inplace=True)
            data.reset_index(drop=True, inplace=True)
            # print data
            data.to_csv(path + str(code) + '.csv', encoding='gbk', index=False)
            # print data.columns
            # 读取日期的第一格
            # if latest_date.empty
            latest_date = data.loc[0, u'日期']
            # print data.loc[0, u'日期'].replace('-','')
            if latest_date >= pd.to_datetime(date_now):
                print code + ' latest date is ' + str(latest_date).split(' ')[0] + ',no updates.'
            elif latest_date < pd.to_datetime(date_now):
                latest_date = latest_date + datetime.timedelta(days=1)
                latest_date = str(latest_date).split(' ')[0]
                # print latest_date
                latest_date = latest_date.replace('-', '')
                download_stock_data_money163(code, mode='update', start=latest_date, save_path=Functions.input_data_path + stock_data_path_money163_test)
                time.sleep(3)
                print code + ' has been updated from ' + latest_date +' to ' + date_now
            else:
                print code + ' has no data.'
            print "Updated %s stock data. Progess is in %.2f%%." % (code, (float(exist_list.index(code)) / len(exist_list) * 100))
    print "Update stock data money163 finished."






# ===main：
get_stock_list_all(save=True)
initial_stock_data_money163(path=Functions.input_data_path + stock_data_path_money163_test)
update_stock_data_money163(path=Functions.input_data_path + stock_data_path_money163_test)

# ===test
# data = pd.read_csv('D:/all_trading_data/data/input_data/stock_data_money163/test/002911.csv')
# if data.shape[0] == 0:
#     print True

# while True:
#     try:  # 尝试做以下事情
#         update_stock_data_money163(path=Functions.input_data_path + stock_data_path_money163_test)
#     except urllib2.URLError as e:  # 如果因为各种原因报错
#         print 'Download error: ', e.reason
#         # tyr_num += 1
#         time.sleep(5)

        # if tyr_num > max_try_num:
        #     print '超过最大尝试次数，下载失败'
        #     # 此处需要执行相关程序，通知某些人
        #     break