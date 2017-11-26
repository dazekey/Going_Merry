# -*- encoding: utf-8 -*-

import pandas as pd
from Basic_Functions import Functions
import time

df = pd.read_hdf('C:/all_trading_data/data/output_data/Jan_effect/' + 'all_stock_data_20171027.h5', key='all_stock')

df['trade_date'] = df['date']
df = df[(df['trade_date'] >= '2005-01-01') & (df['trade_date'] <= '2017-01-01')]    # 取了2005年至2016年数据
df.set_index('date', inplace=True)

# 定义上涨下跌的信号，1代表上涨，0代表停牌或者下跌
df.loc[(df['change'] > 0), 'up'] = 1
df.loc[(df['change'] <= 0), 'up'] = 0

# 取出个股数据对应的月份、年份
df['month'] = df['trade_date'].dt.month
df['year'] = df['trade_date'].dt.year

print df.groupby('month')['change'].mean()    # 计算历年所有股票在各月的平均涨幅
print df.groupby('month')['up'].sum()/df.groupby('month')['up'].count()    # 计算历年各月股票上涨个数的比例

# 计算各支股票在每年1-12月的月度涨幅排名，然后再对各个年份的月份排名求均值。
# 不满一年的股票会造成对应月份rank值减小,在此未做调整，因此此结果仅供参考。
# df['rank'] = df.groupby(['code', 'year'])['change'].rank()
# print df.groupby('month')['rank'].mean()

# print df
exit()