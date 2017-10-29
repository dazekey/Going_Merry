# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: Month_effects.py
@time: 2017/10/29 15:15
"""
"""
测试月份效应
建议数据采用xbx的数据，因为xbx的数据有行业
1.测试股票市场哪个月份的涨幅最高
2.测试不同行业的月份表现

"""

import pandas as pd
from Basic_Functions import Functions
pd.set_option('expand_frame_repr', False)

output_path = Functions.out_put_path + '/Going_Merry/month_effects'

# ==== 读取文件夹里的每一个股票，然后按照数据要求生成list放入一个h5文件中
# code = 'sh600000'
# stock_list = Functions.get_stock_code_list_in_one_dir_xbx()
# all_df = pd.DataFrame()
# for code in stock_list:
#     df = Functions.import_stock_data_xbx(code, other_columns=['新浪行业'])
#     df.rename(columns={'新浪行业': 'industry'}, inplace=True)
#     df['month'] = df['date'].dt.month
#     df['year'] = df['date'].dt.year
#     df.set_index('date', inplace=True)
#     df_month = df.resample('M').last()
#     df_month['change'] = df['change'].resample('M').sum()
#     all_df = all_df.append(df_month)
#     print 'The progess is in %.2f%%' % (stock_list.pos(code) / len(stock_list)) * 100

# all_df.to_hdf('C:/all_trading_data/data/output_data/Going_Merry/month_effects/all_stock_data_monthly_xbx_20171029.h5', key='all', mode='w')
# print df_month

all_df = pd.read_hdf('C:/all_trading_data/data/output_data/Going_Merry/month_effects/all_stock_data_monthly_xbx_20171029.h5', key='all', mode='r')
# all_df = all_df[all_df.index > pd.to_datetime('20060101')]
all_df.dropna(subset=['change'], how='any', inplace=True)

# print all_df.groupby('code').count().shape

month_change = pd.DataFrame()
month_change['sum'] = all_df.groupby('month')['change'].sum()
month_change['rank_sum'] = month_change['sum'].rank()
month_change['mean'] = all_df.groupby('month')['change'].mean()
month_change['rank_mean'] = month_change['mean'].rank()
month_change.to_csv(output_path + '/month_change.csv')
print month_change

all_df['year_month_rank'] = all_df.groupby(['code','year'])['change'].rank()
group_year = all_df.groupby(['month', 'year'])[['change']].sum()
print group_year
# group_year = pd.DataFrame(group_year)
group_year.reset_index(inplace=True)
# group_year['rank'] = group_year['change']
group_year_pivot = group_year.pivot(index='month', columns='year', values='change')
for i in group_year_pivot.columns:
    group_year_pivot[i] = group_year_pivot[i].rank()
group_year_pivot.to_csv(output_path + '/group_year_pivot.csv')

print group_year_pivot

# ====根据行业来分析月份效应
