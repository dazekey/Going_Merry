# -*- encoding: utf-8 -*-

import pandas as pd
import tushare as ts

pd.set_option('expand_frame_repr', False)
# 获取历史K线数据数据, 没有涨跌幅,可以通过复权后股价计算
# stock_data = ts.get_k_data(code='000001', ktype='D', autype='hfq', index=False, start='1989-12-31', end='2017-10-01')
# print stock_data
"""
:param:
code ：证券代码：支持沪深A、B股、支持全部指数、支持ETF基金
ktype ： 数据类型：默认为D日线数据D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟
autype ：复权类型：qfq-前复权 hfq-后复权 None-不复权，默认为qfq 
index ： 是否为指数：默认为False，设定为True时认为code为指数代码
start : 开始日期 format：YYYY-MM-DD 为空时取当前日期
end : 结束日期 ：format：YYYY-MM-DD 

:return:
date : 日期和时间: 低频数据时为：YYYY-MM-DD 高频数为：YYYY-MM-DD HH:MM
open/close/high/low : 开盘价/收盘价/最高价/最低价
volume : 成交量
code : 证券代码

"""

# 返回股票的送转和分红预案情况。
# df = ts.profit_data(top=60)
# df.sort_values(by='shares', ascending=False)
# print df
"""
:param:
    year : 预案公布的年份，默认为2014
    top :取最新n条数据，默认取最近公布的25条
    retry_count：当网络异常后重试次数，默认为3
    pause:重试时停顿秒数，默认为0
    
:return:    
    code:股票代码
    name:股票名称
    year:分配年份
    report_date:公布日期
    divi:分红金额（每10股）
    shares:转增和送股数（每10股）
"""

# 按年度、季度获取业绩预告数据，接口提供从1998年以后每年的业绩预告数据，需指定年度、季度两个参数。
# print ts.forecast_data(2017, 4)
"""
:param:
    year:int 年度 e.g:2014
    quarter:int 季度 :1、2、3、4，只能输入这4个季度

:return:   
    code,代码
    name,名称
    type,业绩变动类型【预增、预亏等】
    report_date,发布日期
    pre_eps,上年同期每股收益
    range,业绩变动范围
"""


# 以月的形式返回限售股解禁情况，通过了解解禁股本的大小，判断股票上行的压力。可通过设定年份和月份参数获取不同时段的数据。
# print ts.xsg_data()
"""
:param:
    year:年份,默认为当前年
    month:解禁月份，默认为当前月
    retry_count：当网络异常后重试次数，默认为3
    pause:重试时停顿秒数，默认为0

:return:
    code：股票代码
    name：股票名称
    date:解禁日期
    count:解禁数量（万股）
    ratio:占总盘比率
"""


# 获取每个季度基金持有上市公司股票的数据。
# df = ts.fund_holdings(2017, 3)
# df.sort_values(by='ratio', ascending= False, inplace=True)
# print df
# print ts.fund_holdings(2017, 3)
"""
:param:
    year:年份,默认为当前年
    quarter:季度（只能输入1，2，3，4这个四个数字）
    retry_count：当网络异常后重试次数，默认为3
    pause:重试时停顿秒数，默认为0

:return:
    code：股票代码
    name：股票名称
    date:报告日期
    nums:基金家数
    nlast:与上期相比（增加或减少了）
    count:基金持股数（万股）
    clast:与上期相比
    amount:基金持股市值
    ratio:占流通盘比率

"""


# 获取IPO发行和上市的时间列表，包括发行数量、网上发行数量、发行价格已经中签率信息等。
# print ts.new_stocks()
"""
:param:
    retry_count：当网络异常后重试次数，默认为3
    pause:重试时停顿秒数，默认为0

:return:
    code：股票代码
    name：股票名称
    ipo_date:上网发行日期
    issue_date:上市日期
    amount:发行数量(万股)
    markets:上网发行数量(万股)
    price:发行价格(元)
    pe:发行市盈率
    limit:个人申购上限(万股)
    funds：募集资金(亿元)
    ballot:网上中签率(%)
"""



# 沪市的融资融券数据从上海证券交易所网站直接获取，提供了有记录以来的全部汇总和明细数据。根据上交所网站提示：数据根据券商申报的数据汇总，由券商保证数据的真实、完整、准确。
# print ts.sh_margins(start='2015-01-01', end='2017-09-30')
"""
:notes:
    本日融资融券余额＝本日融资余额＋本日融券余量金额
    本日融资余额＝前日融资余额＋本日融资买入额－本日融资偿还额；
    本日融资偿还额＝本日直接还款额＋本日卖券还款额＋本日融资强制平仓额＋本日融资正权益调整－本日融资负权益调整；
    本日融券余量=前日融券余量+本日融券卖出数量-本日融券偿还量；
    本日融券偿还量＝本日买券还券量＋本日直接还券量＋本日融券强制平仓量＋本日融券正权益调整－本日融券负权益调整－本日余券应划转量；
    融券单位：股（标的证券为股票）/份（标的证券为基金）/手（标的证券为债券）。
    明细信息中仅包含当前融资融券标的证券的相关数据，汇总信息中包含被调出标的证券范围的证券的余额余量相关数据。

:param:
    start:开始日期 format：YYYY-MM-DD 为空时取去年今日
    end:结束日期 format：YYYY-MM-DD 为空时取当前日期
    retry_count：当网络异常后重试次数，默认为3
    pause:重试时停顿秒数，默认为0

:return:
    opDate:信用交易日期
    rzye:本日融资余额(元)
    rzmre: 本日融资买入额(元)
    rqyl: 本日融券余量
    rqylje: 本日融券余量金额(元)
    rqmcl: 本日融券卖出量
    rzrqjyzl:本日融资融券余额(元)
"""


# 沪市融资融券明细数据
#如果不设symbol参数或者开始和结束日期时段设置过长，数据获取可能会比较慢，建议分段分步获取，比如一年为一个周期
# print ts.sh_margin_details(start='2015-01-01', end='2017-09-30', symbol='601989')
"""
:param:
    date:日期 format：YYYY-MM-DD 默认为空’‘,数据返回最近交易日明细数据
    symbol：标的代码，6位数字e.g.600848，默认为空’‘
    start:开始日期 format：YYYY-MM-DD 默认为空’‘
    end:结束日期 format：YYYY-MM-DD 默认为空’‘
    retry_count：当网络异常后重试次数，默认为3
    pause:重试时停顿秒数，默认为0

:return:
    opDate:信用交易日期
    stockCode:标的证券代码
    securityAbbr:标的证券简称
    rzye:本日融资余额(元)
    rzmre: 本日融资买入额(元)
    rzche:本日融资偿还额(元)
    rqyl: 本日融券余量
    rqmcl: 本日融券卖出量
    rqchl: 本日融券偿还量
"""

# 融资融券（深市）:深市的融资融券数据从深圳证券交易所网站直接获取，提供了有记录以来的全部汇总和明细数据。
# 无法获得时间跨度超过一年的数据。
# print ts.sz_margins(start='2016-09-30', end='2017-09-30')
"""
:notes:
    本日融资余额(元)=前日融资余额＋本日融资买入-本日融资偿还额
    本日融券余量(股)=前日融券余量＋本日融券卖出量-本日融券买入量-本日现券偿还量
    本日融券余额(元)=本日融券余量×本日收盘价
    本日融资融券余额(元)=本日融资余额＋本日融券余额；

:param:
    start:开始日期 format：YYYY-MM-DD 为空时取去年今日
    end:结束日期 format：YYYY-MM-DD 为空时取当前日期
    retry_count：当网络异常后重试次数，默认为3
    pause:重试时停顿秒数，默认为0

:return:
    opDate:信用交易日期(index)
    rzmre: 融资买入额(元)
    rzye:融资余额(元)
    rqmcl: 融券卖出量
    rqyl: 融券余量
    rqye: 融券余量(元)
    rzrqye:融资融券余额(元)
"""

# 深市融资融券明细数据
# 深市融资融券明细一次只能获取一天的明细数据，如果不输入参数，则为最近一个交易日的明细数据
print ts.sz_margin_details('2017-10-27')


"""
:param:
    date:日期 format：YYYY-MM-DD 默认为空’‘,数据返回最近交易日明细数据
    retry_count：当网络异常后重试次数，默认为3
    pause:重试时停顿秒数，默认为0

:return:
    stockCode:标的证券代码
    securityAbbr:标的证券简称
    rzmre: 融资买入额(元)
    rzye:融资余额(元)
    rqmcl: 融券卖出量
    rqyl: 融券余量
    rqye: 融券余量(元)
    rzrqye:融资融券余额(元)
    opDate:信用交易日期
"""

