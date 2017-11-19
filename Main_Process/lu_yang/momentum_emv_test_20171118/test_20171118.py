# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: test_20171118.py
@time: 2017/11/18 16:12
"""

import pandas as pd
from Basic_functions import Functions
from Strategy_test import TA_strategy

stock_data =
pd.set_option('expand_frame_repr', False)

data = pd.read_hdf('EMV600000.h5')
data.to_csv('EMV600000.csv')
print data