# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: momentum_contrarian_v1.py
@time: 2017/11/24 22:10
"""


"""
版本 v1.0
对单个股票进行emv, sma模拟
通过不同的参数输入，得到不同收益率，并合并成一张大表

emv_range()
sma_range()
momentum_contraian()
"""

import pandas as pd
from Basic_Functions import Functions
from Basic_Functions import Data_standardize
from Strategy_test import TA_strategy
from Performance_analysis import equity_cal
import matplotlib.pyplot as plt
import warnings
from Performance_analysis import pf_analysis
# import tushare as ts

pd.set_option('expand_frame_repr', False)

# 对不同的参数测试emv的收益情况，使用的是复杂收益法
def emv_range():
    output = pd.DataFrame()
    for p in range(15, 30):
        for q in range(15, 30):
            # 调用emv函数，添加emv列
            df = TA_strategy.emv(stock_data, n=p, m=q, ph='high_adjust_back', pl='low_adjust_back', vol='volume')
            # 计算交易信号
            # emv上穿maemv买入，下穿maemv卖出
            df = Functions.cross_both(df, 'emv', 'maemv')

            # 计算仓位信号，根据交易信号
            # print stock_data
            df = equity_cal.position(df)
            # stock_data = equity_cal.equity_curve_simple(stock_data)
            # 计算交易结果，复杂版
            df = equity_cal.equity_curve_complete(df, slippage=0.01, c_rate=3./10000, t_rate=1./1000)
            # print stock_data
            # 复杂版的收益结果直接是资金金额，所以除以初始金额，换算成收益率
            df['EMV_' + str(p) + '_' + str(q)] = df['equity']/1000000
            # concat = pd.concat([concat, df['EMV_' + str(p) + '_' + str(q)]], axis=1, join='outer')
            # concat['date'] = df['date']
            # 如果输出表为空，则直接等于结果，否则并表添加
            if output.empty:
                df = equity_cal.nat_equity(df)
                output = df[['date', 'index_change', 'nat_equity', 'EMV_' + str(p) + '_' + str(q)]]
            # print df['EMV_' + str(p) + '_' + str(q)]
            else:
                output = pd.merge(right=df[['date','EMV_' + str(p) + '_' + str(q)]], left=output, on='date', how='outer')
            return output

# 简单移动平均线的参数测试
def sma_range():
    #建立空表
    output = pd.DataFrame()
    for p in range(1, 30):
        for q in range(10, 60):
            # df = TA_strategy.emv(stock_data, n=p, m=q, ph='high_adjust_back', pl='low_adjust_back', vol='volume')
            # 添加sma指标
            df = TA_strategy.simple_ma(stock_data, ma_short=p, ma_long=q, price='close_adjust_back')
            # 计算交易信号
            # df = Functions.cross_both(df, 'emv', 'maemv')
            # 短期均线上穿长期均线买入，下穿卖出
            df = Functions.cross_both(df, 'ma_short', 'ma_long')

            # 计算仓位信号
            # print stock_data
            df = equity_cal.position(df)
            # stock_data = equity_cal.equity_curve_simple(stock_data)
            # 计算交易结果，复杂版
            df = equity_cal.equity_curve_complete(df, slippage=0.01, c_rate=3. / 10000, t_rate=1. / 1000)
            # print stock_data
            # 复杂版的收益结果直接是资金金额，所以除以初始金额，换算成收益率
            df['SMA_' + str(p) + '_' + str(q)] = df['equity'] / 1000000
            # concat = pd.concat([concat, df['EMV_' + str(p) + '_' + str(q)]], axis=1, join='outer')
            # concat['date'] = df['date']
            # 如果输出表为空，则直接等于结果，否则并表添加
            if output.empty:
                df = equity_cal.nat_equity(df)
                output = df[['date', 'index_change', 'nat_equity', 'SMA_' + str(p) + '_' + str(q)]]
            # print df['EMV_' + str(p) + '_' + str(q)]
            else:
                output = pd.merge(right=df[['date', 'SMA_' + str(p) + '_' + str(q)]], left=output, on='date',
                                  how='outer')
            return output
        # print


# 动量函数
def momentum_contrarian(df, type='momentum', window=3):

    df_index_nat = df[df.columns[0:2]]
    df_index_nat.reset_index(inplace=True)
    df = df[df.columns[2:]] # 因为df的前二列index_change, nat_equity 其实不参与计算
    df.reset_index(inplace=True)

    # print df
    # 建立输出空表
    momentum_output = pd.DataFrame()
    contrarian_output = pd.DataFrame()
    output = pd.DataFrame()
    # 先尝试计算一行结果
    # 起始日期为指定日期减窗口期，一般直接窗口期后日期

    for i in range(window, len(df) - 1):  # 因为行是从0开始所以要减1
        start_month = df['date'].iloc[i - window]
        end_month = df['date'].iloc[i]
        temp = df[(df['date'] >= start_month) & (df['date'] < end_month)]  # 因为pandas计数从零开始所以要前闭后开

        # 计算每只股票在排名期使用不同参数的累积收益率
        temp.set_index('date', inplace=True)
        # print temp
        # 将多行转换成一行计算输出
        grouped = (temp + 1.0).prod() - 1.0

        # 将该列排序
        grouped.sort_values(inplace=True)  # Series排序

        param_momentum = grouped.index[-1]  # 在收益率相等的时候取最大的参数
        param_contrarian = grouped.index[1]  # 在收益率相等的时候取最小的参数
        # print grouped
        # print param
        # print df.at[i, 'date'], df.at[i, param]
        output.at[i - window, 'date'] = df.at[i, 'date']


        if type == 'momentum':
            output.at[i - window, 'change_momentum'] = df.at[i, param_momentum]
            output.at[i - window, 'param_momentum'] = param_momentum

        elif type == 'contrarian':
            output.at[i - window, 'change_contrarian'] = df.at[i, param_contrarian]
            output.at[i - window, 'param_contrarian'] = param_contrarian

        elif type == 'both':
            output.at[i - window, 'change_momentum'] = df.at[i, param_momentum]
            output.at[i - window, 'param_momentum'] = param_momentum
            output.at[i - window, 'change_contrarian'] = df.at[i, param_contrarian]
            output.at[i - window, 'param_contrarian'] = param_contrarian
    output = pd.merge(right=output, left=df_index_nat, on='date', how='inner')

    # 将change都换算成equity
    output['equity_momentum'] = (output['change_momentum'] + 1).cumprod()
    output['equity_contrarian'] = (output['change_contrarian'] + 1).cumprod()
    output['nat_equity'] = (output['nat_equity'] + 1).cumprod()
    output['index_change'] = (output['index_change'] + 1).cumprod()

    return output


code = '000001.SZ'

# 获得一个股票的多参数下的模拟结果
def get_stock_param_results(code):
    # 读取万得的非除权数据，然后进行数据标准化
    stock_data = Functions.import_stock_data_wande(code)
    stock_data = Data_standardize.data_standardize_wande(stock_data, adjust_type='adjust_back', start_date='20050101')

    # ====生成有很多参数收益率结果的表格
    stock_data['equity'] = stock_data['equity'] / 1000000
    stock_data = equity_cal.nat_equity(stock_data)
    # pf_analysis.plot_cumulative_return(stock_data)
    # output = sma_range()
    # # 将结果输出成csv
    # output.to_csv(Functions.out_put_path+'/Going_Merry/range_test/'+'600000sma1_60.csv', mode='w', index=False)
    # print stock_data
    # 读取输出结果


df = pd.read_csv(Functions.out_put_path+'/Going_Merry/range_test/'+'600000sma1_60.csv')
# 日期列转换成日期格式,为了月度转换resample
df['date'] = pd.to_datetime(df['date'])

# ====动量和反转运算前的准备，先做月份转换处理
# 设置日期为Index
df.set_index('date', inplace=True)
# 通过pct_change,将收益率转换成change
df[df.columns[1:]] = df[df.columns[1:]].pct_change()
# 将空值补充为0，不然会引起运算错误
df.fillna(value=0.00, inplace=True)
# 将日数据转换成月数据
df_monthly = df.resample(rule='m').apply(lambda x:(1.0+x).prod()-1.0)
# print df_monthly
# 同样将空值补充为0
df_monthly.fillna(value=0.00, inplace=True)

# print df_monthly['date']
# exit()

# ====生成动量函数的结果
output = momentum_contrarian(df_monthly, type='both')
output.to_csv(Functions.out_put_path + '/Going_Merry/range_test/'+'600000sma1_momentum_contrarian.csv')

# output= pd.read_csv(Functions.out_put_path + '/Going_Merry/range_test/'+'600000sma1_momentum.csv')
# print output

# ====作图
fig = plt.figure(figsize=(16,6))
plt.plot(output['equity_momentum'], label='momentum')
plt.plot(output['equity_contrarian'], label='contrarian')
plt.plot(output['index_change'], label='index')
plt.plot(output['nat_equity'], label='nat')
plt.legend(loc='best')
plt.show()
