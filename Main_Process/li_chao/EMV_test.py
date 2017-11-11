# encoding: utf-8

"""
EMV大于MAEMV时，买入，信号为1；当EMV小于MAEMV时，卖出，信号为 0
计算所有股票使用此策略时的收益情况（参数可以设定一个范围或者设为确定值，当参数为范围时，取的为excessive_rtn最大的数据行）

"""

import os
import warnings
import pandas as pd
from Basic_Functions import Functions
from Strategy_test import TA_strategy
from Performance_analysis import pf_analysis
from Performance_analysis import equity_cal

warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)

# 导入指数数据,作为benchmark
index_data = Functions.import_index_data_wande()

# 遍历数据文件夹中所有股票文件的文件名，得到股票代码列表
stock_code_list = Functions.get_stock_code_list_in_one_dir_wande()
# print len(stock_code_list)
# exit()

# ====数据准备

for code in stock_code_list[0:]:    # 可以适当少选一点股票
    stock_data = Functions.import_stock_data_wande(code, other_columns=['成交量(股)'])

    if len(stock_data) < 250:    # 剔除发行时间小于约1年的数据
        continue
    print 'The progress is in %.2f%%.' % (stock_code_list.index(code) * 1.0 / len(stock_code_list) * 100)

    stock_data.rename(columns={'成交量(股)': 'volume'}, inplace=True)
    stock_data = Functions.cal_adjust_price(stock_data, adjust_type='adjust_back', return_type=2)
    # 和index合并
    stock_data = Functions.merge_with_index_data(stock_data, index_data)
    stock_data = stock_data[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume']]

    re = pd.DataFrame(columns=['code', 'start', 'param', 'stock_rtn', 'stock_md', 'strategy_rtn',
                               'strategy_md', 'excessive_rtn'])
    i = 0

    for p in range(16, 18, 2):
        for q in range(20, 21):

            df = TA_strategy.emv(stock_data, n=p, m=q)
            df = df[df['date'] >= pd.to_datetime('2005-01-01')]  # 采用2005年起的数据
            df.reset_index(inplace=True, drop=True)  # 在计算emv之后，最早的一部分数据没有对应的值，需要重新排index

            # EMV大于MAEMV时，买入，信号为1；当EMV小于MAEMV时，卖出，信号为 0
            # 计算EMV指标并得到信号和仓位
            df = Functions.cross_both(df, 'emv', 'maemv')
            df = equity_cal.position(df)
            df = equity_cal.equity_curve_complete(df)
            df = df[['date', 'code', 'open', 'high', 'low', 'close', 'change', 'volume', 'equity']]
            df['capital_rtn'] = df['equity'].pct_change(1)
            df.ix[0, 'capital_rtn'] = 0
            df['capital'] = (df['capital_rtn'] + 1).cumprod()

            df_stock = stock_data.copy()
            # 股票的年化收益
            rng_stock = pd.period_range(df_stock['date'].iloc[0], df_stock['date'].iloc[-1], freq='D')
            stock_rtn = pow(df_stock.ix[len(df_stock.index) - 1, 'close'] / df_stock.ix[0, 'close'], 250.00 / len(rng_stock)) - 1
            # 股票最大回撤
            df_stock['max2here_stock'] = pd.expanding_max(df_stock['close'])  # 计算当日之前的账户最大价值
            df_stock['dd2here_stock'] = df_stock['close'] / df_stock['max2here_stock'] - 1  # 计算当日的回撤
            temp = df_stock.sort_values(by='dd2here_stock').iloc[0][['date', 'dd2here_stock']]
            stock_md = temp['dd2here_stock']

            # 策略的年化收益
            # 在计算指标时因参数要求，最早的一部分数据会为空值，因此在计算收益率时需要重新计算天数
            rng_strategy = pd.period_range(df['date'].iloc[0], df['date'].iloc[-1], freq='D')
            strategy_rtn = pow(df.ix[len(df.index) - 1, 'equity'] / df.ix[0, 'equity'], 250.00 / len(rng_strategy)) - 1

            # 策略最大回撤
            df['max2here'] = pd.expanding_max(df['capital'])  # 计算当日之前的账户最大价值
            df['dd2here'] = df['capital'] / df['max2here'] - 1  # 计算当日的回撤
            temp = df.sort_values(by='dd2here').iloc[0][['date', 'dd2here']]
            strategy_md = temp['dd2here']

            re.loc[i, 'code'] = df['code'].iloc[0]
            re.loc[i, 'start'] = df.loc[0, 'date'].strftime('%Y-%m-%d')
            re.loc[i, 'param'] = str(p) + '_' + str(q)
            re.loc[i, 'stock_rtn'] = stock_rtn
            re.loc[i, 'stock_md'] = stock_md
            re.loc[i, 'strategy_rtn'] = strategy_rtn
            re.loc[i, 'strategy_md'] = strategy_md
            re.loc[i, 'excessive_rtn'] = strategy_rtn - stock_rtn

            i += 1

    re.sort_values(by='excessive_rtn', ascending=False, inplace=True)

    re.iloc[0:1, :].to_csv('C:/all_trading_data/data/output_data/emv_test.csv', mode='a', header=None, index=False)














