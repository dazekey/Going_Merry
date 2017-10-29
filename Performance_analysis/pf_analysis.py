
# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: pf_analysis.py
@time: 2017/10/3 11:55
"""
from __future__ import division  # 不引入这个的话，除法结果小于1的都是0
"""
1. annual_return(df) 计算年化收益的函数,对有'date', 'equity'列的df，计算获得annual return
2. max_drawdown(df) 计算最大回撤函数,对有'date', 'equity'列的df，计算获得[max_dd, start_date, end_date]
3. average_change(df) 计算平均涨幅,对有'date', 'equity'列的df，计算获得ave
4. prob_up(df) # 计算上涨概率,对有'date', 'equity'列的df，计算获得p_up
5. max_successive_up(df) 计算最大连续上涨天数和最大连续下跌天数
6. max_period_return(df) 计算最大单周期涨幅和最大单周期跌幅
7. volatility(df) 计算收益波动率的函数
8. beta(df) 计算beta的函数
9. alpha(df) 计算alpha的函数
10. sharp_ratio(df) 计算夏普比率
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 计算年化收益的函数
def annual_return(df):
    """
    对有'date', 'equity'列的df，计算获得annual return
    :param df:  有'date', 'equity'列的df
    :return:  返回一个值 annual
    """
    df = df.copy()
    rng = pd.period_range(df['date'].iloc[0], df['date'].iloc[-1], freq='D')
    # 计算年化收益率

    annual = pow(df.ix[len(df.index)-1, 'equity'] / df.ix[0, 'equity'], 250.00 / len(rng)) -1
    # annual = pow(df.iloc[-1, 'equity'] / df.ix[0, 'equity'], 250.00 / len(rng)) -1
    # pow 指数化运算
    print '年化收益率为： %f' % annual
    return annual

# 计算最大回撤函数
def max_drawdown(df):
    """
    对有'date', 'equity'列的df，计算获得[max_dd, start_date, end_date]
    :param df: 有'date', 'equity'列的df
    :return:  [max_dd, start_date, end_date]
    """

    df = df.copy()
    # df['max2here'] = pd.expanding_max(df['equity'])  # 计算当日之前的账户最大价值，旧的写法 被弃用
    df['max2here'] = df['equity'].expanding(min_periods=1).max()  # 计算当日之前的账户最大价值
    df['dd2here'] = df['equity'] / df['max2here'] - 1  # 计算当日的回撤

    # 计算最大回撤和结束时间
    temp = df.sort_values(by='dd2here').iloc[0][['date', 'dd2here']]
    max_dd = temp['dd2here']
    end_date = temp['date']

    # 计算开始时间
    df = df[df['date'] <= end_date]
    start_date = df.sort_values(by='equity', ascending=False).iloc[0]['date']

    print '最大回撤为：%f, 开始日期：%s, 结束日期：%s' % (max_dd, start_date, end_date)
    return [max_dd, start_date, end_date]

# 邢大说的一个终极指标：年化收益 / abs(最大回撤)--by lichao
"""
    对有'date', 'equity'列的df，计算获得annual return
    :param df:  有'date', 'equity'列的df
    :return:  返回一个值 ultimate_index
"""
def ultimate_index(df):
    df = df.copy()
    rng = pd.period_range(df['date'].iloc[0], df['date'].iloc[-1], freq='D')
    annual = pow(df.ix[len(df.index)-1, 'equity'] / df.ix[0, 'equity'], 250.00 / len(rng)) -1
    max_dd = max_drawdown(df)[0]
    ultimate_index = annual/abs(round(max_dd * 100, 2))
    print 'ultimate_index为：%f' % ultimate_index
    return ultimate_index

# 计算平均涨幅
def average_change(df, type=0):
    """
    对有'date', 'equity'列的df，计算获得ave
    :param df: 有'date', 'equity'列的df
    :param type: 0 计算策略的平均涨幅，1 计算自然的平均涨幅
    :return:  ave
    """
    df = df.copy()
    # type: 0 计算策略的上涨概率，1 计算自然的上涨概率
    if type == 0:
        df['rtn'] = df['change'] * df['pos']
    elif type == 1:
        df['rtn'] = df['change']

    ave = df['rtn'].mean()

    print '平均涨幅为：%f' % ave
    return ave

# 计算上涨概率
def prob_up(df, type=0):
    """
    对有'date', 'equity'列的df，计算获得p_up
    :param df: 有'date', 'equity'列的df
    :param type: 0 计算策略的上涨概率，1 计算自然的上涨概率
    :return:  ave
    """
    df = df.copy()
    # type: 0 计算策略的上涨概率，1 计算自然的上涨概率
    if type == 0:
        df['rtn'] = df['change'] * df['pos']
    elif type == 1:
        df['rtn'] = df['change']

    df.ix[df['rtn'] > 0, 'rtn'] = 1  # 收益率大于0的记为1
    df.ix[df['rtn'] <= 0, 'rtn'] = 0  # 收益率小于等于0的记为0
    # 统计1和0各出现的次数
    count = df['rtn'].value_counts()
    p_up = count.loc[1] / len(df.index)

    print '上涨概率为：%f' % p_up
    return p_up

# 计算最大连续上涨天数和最大连续下跌天数
def max_successive_up(df, type=0):
    """
    对有'date', 'pos'列的df，计算获得'rtn''up
    :param df:  有'date', 'pos'列的df
    :param type: 0 计算策略的连续上涨下跌天数，1 计算自然的连续上涨下跌天数
    :return:  返回一个值 annual
    """
    df = df.copy()
    # type: 0 计算策略的上涨概率，1 计算自然的上涨概率
    if type == 0:
        df['rtn'] = df['change'] * df['pos']

    elif type == 1:
        df['rtn'] = df['change']

    # print df
    # 新建一个全为空值的series,并作为dataframe新的一列
    s = pd.Series(np.nan, index=df.index)
    s.name = 'up'
    df = pd.concat([df[['pos', 'date', 'rtn']], s], axis=1)
    # 当收益率大于0时，up取1，小于0时，up取0，等于0时采用前向差值
    df.ix[df['rtn'] > 0, 'up'] = 1
    df.ix[df['rtn'] < 0, 'up'] = -1
    if type == 0:
        df.ix[df['pos'] == 0, 'up'] = 0

    # df.ix[df['rtn'] == 0, 'up'] = 0
    df['up'].fillna(method='ffill', inplace=True)
    # df['up'].fillna(0)
    # print df
    # 根据up这一列计算到某天为止连续上涨下跌的天数
    rtn_list = list(df['up'])
    successive_up_list = []
    num = 1
    for i in range(len(rtn_list)):
        if i == 0:
            successive_up_list.append(num)
        else:
            # if type == 0:
            #     if df.loc[i, 'pos'] == 0:
            #         num = 1
            if (rtn_list[i] == rtn_list[i - 1] == 1) or (rtn_list[i] == rtn_list[i - 1] == -1):
                num += 1
            else:
                num = 1
            successive_up_list.append(num)
    # 将计算结果赋给新的一列'successive_up'
    df['successive_up'] = successive_up_list
    # 分别在上涨和下跌的两个dataframe里按照'successive_up'的值排序并取最大值
    max_successive_up = df[df['up'] == 1].sort_values(by='successive_up', ascending=False)['successive_up'].iloc[0]
    max_successive_down = df[df['up'] == -1].sort_values(by='successive_up', ascending=False)['successive_up'].iloc[0]
    # df.to_csv('test.csv')
    print '最大连续上涨天数为：%d  最大连续下跌天数为：%d' % (max_successive_up, max_successive_down)
    return [max_successive_up, max_successive_down]

# 计算最大单周期涨幅和最大单周期跌幅
def max_period_return(df):
    """

    :param df: 有'pos'列的df
    :return: [max_return, min_return]
    """
    df = df.copy()

    for i in range(1, df.shape[0]):
        if df.loc[i, 'pos'] == 1:
            df.loc[i, 'rtn'] = (df.loc[i, 'change'] + 1) * df.loc[i -1, 'rtn']
        else:
            df.loc[i, 'rtn'] = 1

    # df['rtn'] = df['pos'] * df['rtn']
    # df.to_csv('test.csv')
    # 分别结算日收益率的最大值和最小值
    max_return = df['rtn'].max()
    min_return = df['rtn'].min()
    print '最大单周期涨幅为： %f  最大单周期跌幅： %f' %(max_return, min_return)
    return [max_return, min_return]

# 计算收益波动率的函数
def volatility(df):
    """

    :param df:
    :return:
    """

    from math import sqrt
    df['rtn'] = df['change'] * df['pos']
    # 计算收益率
    vol = df['rtn'].std() * sqrt(250)
    """sqrt开方, numpy.std()计算方差"""
    print '收益波动率为： %f' % vol
    return vol

# 计算beta的函数
def beta(df, type=0):
    """

    :param df: 有index_change列的df
    :return: beta
    """
    df = df.copy()
    # type: 0 计算策略的收益率，1 计算自然的收益率
    if type == 0:
        df['rtn'] = df['change'] * df['pos']
        # df['benchmark_rtn'] = df['index_change'] * df['pos']
    elif type == 1:
        df['rtn'] = df['change']
    df['benchmark_rtn'] = df['index_change']
    # 账户收益率和基准收益率的协方差除以基准收益率的方差
    beta = df['rtn'].cov(df['benchmark_rtn'])/df['benchmark_rtn'].var()
    print 'beta: %f' % beta
    return beta

# 计算alpha的函数
def alpha(df, rf=0.0284):
    """

    :param df: 有'date', 'equity', 'index_close, 'rtn', 'index_change'
    :param rf: 0.0284 无风险利率取10年期国债的到期年化收益率
    :return: 输出alpha值
    """
    # 将指数序列合并成dataframe并按日期排序

    df = df.copy()
    rng = pd.period_range(df['date'].iloc[0], df['date'].iloc[-1], freq='D')
    # rf = 0.0284  # 无风险利率取10年期国债的到期年化收益率

    annual_stock = pow(df.ix[len(df.index) - 1,'equity'] / df.ix[0,'equity'], 250 / len(rng)) - 1 #账户年化收益率
    annual_index = pow(df.ix[len(df.index) - 1, 'index_close'] / df.ix[0, 'index_close'], 250 / len(rng)) -1 #基准年化收益

    beta = df['rtn'].cov(df['index_change']) / df['index_change'].var()
    a = (annual_stock - rf) - beta * (annual_index - rf)  # alpha的计算公式
    print 'alpha: %f' % a
    return a

def sharp_ratio(df, rf = 0.0284):
    """

    :param df: 'date', 'equity', 'change'
    :param rf: 0.0284 无风险利率取10年期国债的到期年化收益率
    :return: 输出夏普比率
    """

    from math import sqrt
    # 将数据序列合并为一个dataframe并按日期排序
    df = df.copy()
    rng = pd.period_range(df['date'].iloc[0], df['date'].iloc[-1], freq='D')

    # 账户年化收益率
    annual_stock = pow(df.ix[len(df.index) - 1, 'equity'] / df.ix[0, 'equity'], 250/len(rng)) - 1
    # 计算收益波动率
    df['rtn'] = df['pos'] * df['change']
    volatility = df['rtn'].std() * sqrt(250)
    # 计算夏普比率
    sharpe = (annual_stock - rf) / volatility
    print 'Sharp raio: %f' % sharpe
    return sharpe

# 计算信息比率
def info_ratio(df):
    """

    :param df: 'date', 'index_change', 'change'
    :return: 输出夏普比率
    """
    from math import sqrt
    df = df.copy()
    df['rtn'] = df['pos'] * df['change']
    df['diff'] = df['rtn'] - df['index_change']
    annual_mean = df['diff'].mean()*250
    annual_std = df['diff'].std() * sqrt(250)
    info = annual_mean / annual_std
    print 'info_ratio : %f' % info
    return info

# 计算股票和基准在回测期间的累积收益率并画图
def plot_cumulative_return(df, nat_rtn=True, index=True):
    """

    :param date_line: 'date', 'index_change', 'change'
    :return: 画出股票和基准在回测期间的累计收益率的折线图
    """
    df = df.copy()
    df['rtn'] = df['change'] * df['pos']
    df['stock_cumret']= (df['rtn'] + 1).cumprod()
    """cumprod -- cumulative prod"""
    # df['benchmark_cumret'] = (df['index_change'] + 1).cumprod() * 1000000
    df['benchmark_cumret'] = (df['index_change'] + 1).cumprod()
    # 设置日期为Index,x轴才能显示日期
    df.set_index('date', inplace=True)
    # 画出股票和基准在回测期间的累计收益率的折线图
    fig = plt.figure(figsize=(12,5))
    ax = fig.add_subplot(1,1,1)
    ax.set_xlabel('Time')  # 设置横坐标x轴的名字
    ax.set_ylabel('Return')  # 设置Y轴
    # df['stock_cumret'].plot(style='r-', figsize=(12,5), label='stock_return')
    plt.plot(df['equity'], label='stock_return')
    # df['benchmark_cumret'].plot(style='k--', figsize=(12,5), label='benchmark_return')
    if index==True:
        plt.plot(df['benchmark_cumret'], label='benchmark_return')
    if nat_rtn==True:
        plt.plot(df['nat_equity'], label='nat_rtn')
    # df.to_csv('df.csv',index=False)
    plt.legend(loc='best')
    plt.show()

