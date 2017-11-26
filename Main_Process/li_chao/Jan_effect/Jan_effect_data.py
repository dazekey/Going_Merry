# -*- encoding: utf-8 -*-

import pandas as pd
from Basic_Functions import Functions
import time

pd.set_option('expand_frame_repr', False)
stock_list = Functions.get_stock_code_list_in_one_dir()
# print len(stock_list)
# exit()
index_data = Functions.import_index_data()
all_stock_data = pd.DataFrame()

for code in stock_list:
    stock_data = Functions.import_stock_data(code)
    stock_data = Functions.merge_with_index_data(stock_data, index_data)
    stock_data = Functions.transfer_to_period_data(stock_data, 'm')

    # 此处由于没有行业、板块数据，因此仅取出日期、股票代码、涨跌幅三个字段进行分析，未来视数据丰富度可做修改
    stock_data = stock_data[['date', 'code', 'change']]
    progress = ((stock_list.index(code) + 1.0) / len(stock_list)) * 100.00  # 读取当前股票在list中的位置， 除以总的list长度
    print ('stock %s in progress is %.2f%%' % (code, progress))
    all_stock_data = all_stock_data.append(stock_data, ignore_index=True)
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    all_stock_data.to_hdf('C:/all_trading_data/data/output_data/Jan_effect/' + 'all_stock_data_' + str(date) + '.h5', key='all_stock', mode='w')

print 'all_stock_data has been finished.'


