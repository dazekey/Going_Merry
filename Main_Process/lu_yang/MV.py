# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: MV.py
@time: 2017/10/22 18:43
"""
"""
小市值策略
10年400倍
数据：万得
每月调仓
每次10个
选股策略 市值因子
实际买卖方式：每月末选股，买入，持有一个月
"""
import pandas as pd
from Basic_Functions import Functions
import matplotlib.pyplot as plt

pd.set_option('expand_frame_repr', False)

# =====建立all_stock_data_monthly
all_stock_data_monthly = pd.DataFrame()
# 获得stock_list
stock_list = Functions.get_stock_code_list_in_one_dir_wande()
# print stock_list

#
# range = stock_list
# for code in range:
#     # 获得每个股票的数据
#     df = Functions.import_stock_data_wande(code)
#     # 读取指数数据
#     index_df = Functions.import_index_data_wande()
#     # 个股与指数数据合并
#     df = Functions.merge_with_index_data(df,index_df)
#     # 截取20060101以后的数据
#     df = df[df['date']>pd.to_datetime('20060101')]
#     # 周期转化昵称月
#     df_month = Functions.transfer_to_period_data(df)
#     # 添加next_month_change列，为change的向上位移
#     df_month['next_month_change'] = df_month['change'].shift(-1)
#     # print df_month
#     all_stock_data_monthly = all_stock_data_monthly.append(df_month)
#     print 'The progess is in %.2f%%.' % (range.index(code) * 1.0 / len(range) * 100)
#
# all_stock_data_monthly.reset_index(drop=True, inplace=True)

# 将结果all_stock_data_monthly保存为本地hf5
# all_stock_data_monthly.to_hdf('C:/all_trading_data/data/output_data/Going_Merry/all_stock_data_month.h5', key='all', mode='w')

# all_stock_data = pd.read_hdf('C:/all_trading_data/data/output_data/Going_Merry/all_stock_data_20171005.h5')
# print all_stock_data
# exit()

# 读取本地的all_stock_data_monthly
all_stock_data_monthly = pd.read_hdf('C:/all_trading_data/data/output_data/Going_Merry/all_stock_data_month.h5', key='all', mode='r')
# print all_stock_data_monthly

# exit()

# 最后一天不交易的股票不能买入
all_stock_data_monthly = all_stock_data_monthly[all_stock_data_monthly['trade'] !=0]
# 当月停牌时间过长的股票不能买入
all_stock_data_monthly = all_stock_data_monthly[all_stock_data_monthly['trade_days'] >= 10]
# 最后一天不能涨停
all_stock_data_monthly = all_stock_data_monthly[all_stock_data_monthly['last_change'] <= 0.097]
# print all_stock_data_monthly[all_stock_data_monthly['code'] == '600000.SH']
# exit()

# 设立输出结果数据表
output = pd.DataFrame()


# ====xbx的方法
# 计算股票下月的平均涨幅
all_stock_data_monthly.sort_values(by=['date', 'code'], inplace=True)
output['next_mongth_change'] = all_stock_data_monthly.groupby('date')['next_month_change'].mean()

# 计算每月市值排名
all_stock_data_monthly['market_value_rank'] = all_stock_data_monthly.groupby('date')['market_value'].rank()

# 选取市值前十的股票
all_stock_data_monthly = all_stock_data_monthly[all_stock_data_monthly['market_value_rank'] < 10]

output['select_stock_next_month_change'] = all_stock_data_monthly.groupby('date')['next_month_change'].mean()
#输出选择股票的资金曲线
all_stock_data_monthly['code'] += ' '
output['code'] = all_stock_data_monthly.groupby('date')['code'].sum()
output['line_benchmark'] = (output['next_mongth_change'] + 1).cumprod()
output['line'] = (output['select_stock_next_month_change'] + 1 - 0.002).cumprod()

print output

# output.to_csv('output.csv')

# print all_stock_data_monthly
# print output
# 选取市值前十的股票
# exit()

#
# # ====我的方法
# # 按日期group
# group = all_stock_data_monthly.groupby('date')
# for day_df in group:
#     # 取出group后的分组数据
#     day_df = pd.DataFrame(day_df[1])
#     # 按市值升序
#     day_df.sort_values(by='market_value', ascending=True, inplace=True)
#     # 取出市值最小的十个股票数据
#     day_df = day_df.head(10)
#     output = output.append(day_df)
#
# # print output
# # exit()
# # 合并时间合并下个月的涨跌幅
# output1 = pd.DataFrame()
#
# output['code'] = output['code']+' '
# output1['code'] = output.groupby('date')['code'].sum()
#
# output1['next_month_change'] = all_stock_data_monthly.groupby('date')['next_month_change'].mean()
# output1['line_benchmark'] = (output1['next_month_change'] + 1).cumprod()
#
# output1['select_next_month_change'] = output.groupby('date')['next_month_change'].mean()
# # output['cum_return'] = output['next_month_change'].apply(lambda x: (x + 1.0)).cumprod() - 1
# output1['line'] = (output1['select_next_month_change'] + 1 - 0.002).cumprod()

# output1.to_csv('output1.csv')

# print output1

# 以上两种结果一样


# 画图部分
# 因为画图函数对数据列有要求，加入'equity'
fig = plt.figure(figsize=(12,5))
plt.plot(output['line'], label='strategy_rtn')
plt.plot(output['line_benchmark'], label='benchmark')
plt.legend(loc='best')
plt.show()