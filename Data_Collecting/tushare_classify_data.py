# -*- encoding: utf-8 -*-

import pandas as pd
import tushare as ts

pd.set_option('expand_frame_repr', False)

# 行业分类:本接口按照sina财经对沪深股票进行的行业分类，返回所有股票所属行业的信息。
# 考虑到是一次性在线获取数据，调用接口时会有一定的延时，请在数据返回后自行将数据进行及时存储。
# print ts.get_industry_classified()    # 返回了2396条数据，看来不是所有股票都有确定的行业。
"""
:param:
:return:
    code：股票代码
    name：股票名称
    c_name：行业名称
"""

# 概念分类：sina财经提供的概念分类信息
# print ts.get_concept_classified()    # 返回了7508条数据，存在一支股票对应多个概念的情况。
"""
:param:
:return:
    code：股票代码
    name：股票名称
    c_name：行业名称
"""

# 地域分类：按地域对股票进行分类，即查找出哪些股票属于哪个省份。
# print ts.get_area_classified()    # 返回3430条数据，应该是一一对应的关系。
"""
:param:
:return:
    code：股票代码
    name：股票名称
    area：地域名称
"""

# 沪深300成份及权重：获取沪深300当前成份股及所占权重
# print ts.get_hs300s()    # 历史的成份无法获取
"""
:param:
:return:
    code :股票代码
    name :股票名称
    date :日期
    weight:权重
"""

# 上证50成份股
# print ts.get_sz50s()    # 仅有股票名称，不含权重
"""
:param:
:return:
    code：股票代码
    name：股票名称
"""

# 中证500成份股
# print ts.get_zz500s()
"""
:param:
:return:
    code：股票代码
    name：股票名称
    weight:权重
"""

# 终止上市股票列表:获取已经被终止上市的股票列表，数据从上交所获取，目前只有在上海证券交易所交易被终止的股票。
# print ts.get_terminated()
"""
:param:
:return:
    code：股票代码
    name：股票名称
    oDate:上市日期
    tDate:终止上市日期
"""

# 暂停上市股票列表： 获取被暂停上市的股票列表，数据从上交所获取，目前只有在上海证券交易所交易被终止的股票。
# print ts.get_suspended()
"""
:param:
:return:
    code：股票代码
    name：股票名称
    oDate:上市日期
    tDate:暂停上市日期
"""















