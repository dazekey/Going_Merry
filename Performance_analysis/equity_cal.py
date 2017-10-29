# encoding: utf-8
"""
@author: Ocean_Lane
@contract: dazekey@163.com
@file: euqity_cal.py
@time: 2017/10/2 12:59
"""

"""
本模块主要用来计算仓位和资金曲线
1. position(df) 计算仓位
2. equity_curve_simple(df) 简单版计算资金曲线
3. equity_curve_complete(df) 完整版计算资金曲线
4. nat_rnt(df) 计算自然收益率
"""

# ==== 1. 计算仓位
def position(df, shift=True):
    """
    根据交易信号列'signal'计算每天持有股票的仓位
    :param df:
    :return:  返回带有pos列的df
    """
    df = df.copy()
    # 由signal计算每天持有的仓位
    if shift == True:
        df['pos'] = df['signal'].shift()  # 因为交易日是在signal出现的后一天，特别是那些买入卖出信号是以close为基准的
    df['pos'].fillna(method='ffill', inplace=True)

    # 将涨跌停时不能交易的情况考虑进来
    # 今天的开盘价比昨天收盘价高9.7%不能买
    cond_cannot_buy = df['open'] > df['close'].shift(1) * 1.097
    df.loc[cond_cannot_buy & (df['pos'] == 1), 'pos'] = None

    # 今天的开盘价比昨天收盘价跌9.7%不能卖
    cond_cannot_sell = df['open'] < df['close'].shift(1) * 0.903
    df.loc[cond_cannot_sell & (df['pos'] == 0), 'pos'] = None

    # position为空的日期，不能买卖，position只能和前一个交易日保持一致
    df['pos'].fillna(method='ffill', inplace=True)

    # 在position为空的日期，全部补为0
    df['pos'].fillna(value=0, inplace=True)

    return df


# 简单版本计算资金曲线
def equity_curve_simple(df):
    """
    简单版本，没有考虑手续费，印花税和滑点
    :param df:  输入带有'pos'列的df
    :return: 输出带有‘equity_curve_s'列的df
    """
    df = df.copy()
    # ====计算资金曲线
    # 当当天空仓时，pos为0，资产涨幅为0
    # 当当天满仓时，pos为1，资产涨幅为股票本身的涨跌幅
    df['equity'] = df['change'] * df['pos']
    # 根据每天的涨幅计算资金曲线
    df['equity'] = (df['equity'] + 1).cumprod()

    return df

# 完整版计算资金曲线
def equity_curve_complete(df, initial_money=1000000, slippage=0.01, c_rate=5.0/10000, t_rate=1.0/1000):
    """

    :param df: 有'pos'列的df
    :param initial_money: 初始资金，默认为1000000元
    :param slippage: 滑点，默认为0.01元？ 是不是用百分比更好?
    :param c_rate: 手续费，commission_fees, 默认为万分之5
    :param t_rate: 印花税， tax， 默认为千分之1
    :return:  返回带有’equity_curve_c'的列
    """
    df = df.copy()
    # ====第一天的情况
    df.at[0, 'hold_num'] = 0  # 持股数
    df.at[0, 'stock_value'] = 0  # 持有股票市值
    df.at[0, 'actual_pos'] = 0  # 每日的实际仓位比例 = 股票市值(stock_value) / 总资产(equity)
    df.at[0, 'cash'] = initial_money  # 持有现金
    df.at[0, 'equity'] = initial_money  # 总资产 = 持有股票市值 + 现金

    # ====第一天之后的每天情况
    for i in range(1, df.shape[0]):

        # 当前持有股票的数量 = 前一天持有的股票的数量
        hold_num = df.at[i-1, 'hold_num']

        # 若发生除权，需要调整hold_num =  昨天的市值 / 调整后的昨天收盘价
        if abs((df.at[i, 'close'] / df.at[i - 1, 'close'] - 1) - df.at[i, 'change']) > 0.001:
            stock_value = df.at[i-1, 'stock_value']  # 当前持有市值是昨天收盘的市值
            last_price = df.at[i, 'close'] / (df.at[i, 'change'] + 1)  # 因为除权，昨天的收盘价要发生变化
            hold_num = stock_value / last_price  # 新的持有股数产生
            hold_num = int(hold_num)

        # 判断是否需要调整仓位
        # 需要调整仓位
        if df.at[i, 'pos'] != df.at[i - 1, 'pos']:  # 仓位发生变化


            # 持有的股票数 = 昨天的总资产 * 今天的仓位 / 今天的开盘价  因为是按开盘价买入
            # theory_num = df.at[i-1, 'equtiy'] * df.at[i, 'pos'] / df.at[i, 'open']
            """上面这种写法没有考虑tax,commission,slippage"""
            theory_num = (df.at[i-1, 'equity'] * (1 - c_rate - t_rate)) * df.at[i, 'pos'] / (df.at[i, 'open'] + slippage)
            # 对需要持有的股票数取整数
            theory_num = int(theory_num / 100) * 100  # 向下取百取整


            # 判断是加仓还是调仓
            # 加仓
            if theory_num >= hold_num:
                # 计算实际需要买入的股票数量
                # 买入的时候，根据持有现金来重新计算理论数量，就不会超额购买了
                theory_num = df.at[i - 1, 'cash'] / ((df.at[i, 'open'] + slippage)*(1+c_rate))
                buy_num = theory_num - hold_num
                # 买入股票只能整百，对buy_num进行向下取整百
                buy_num = int(buy_num / 100) * 100

                # 计算买入股票花去的现金
                buy_cash = buy_num * (df.at[i, 'open'] + slippage)
                # 计算买入股票花去的手续费
                commission = round(buy_cash * c_rate, 2)
                # 不足5元，按5元收
                if commission < 5 and commission != 0:
                    commission = 5
                df.at[i, 'commission'] = commission

                # 计算当天收盘价时持有股票的数量和现金
                df.at[i, 'hold_num'] = hold_num + buy_num  # 持有股票 = 昨天的持有股数 + 买入股数
                df.at[i, 'cash'] = df.at[i-1, 'cash'] - buy_cash - commission  # 剩余现金

            # 减仓
            else:
                # 计算卖出股票数量，卖出股票可以不是整数，不需要取整百
                sell_num = hold_num - theory_num

                # 计算卖出股票得到的现金
                sell_cash = sell_num * (df.at[i, 'open'] - slippage)
                # 计算手续费，不足5元5元保留2位小数
                commission = round(max(sell_cash * c_rate, 5), 2)
                df.at[i, 'commission'] = commission
                # 计算印花税，保留2位小数，历史上有段时间，买入也会收取印花税
                tax = round(sell_cash * t_rate, 2)
                df.at[i, 'tax'] = tax

                # 计算当天收盘价持有股票的数量和现金
                df.at[i, 'hold_num'] = hold_num - sell_num  # 持有股数 = 昨天的持有股数 - 卖出股数
                df.at[i, 'cash'] = df.at[i-1, 'cash'] + sell_cash - commission - tax  # 持有现金

        # 不需要调仓
        else:
            # 计算当天收盘时持有股票的数量和现金
            df.at[i, 'hold_num'] = hold_num  # 持有股票
            df.at[i, 'cash'] = df.at[i - 1, 'cash']  # 剩余现金

        # 计算收盘时当天的各种数据
        df.at[i, 'stock_value'] = df.at[i, 'hold_num'] * df.at[i, 'close']  # 股票资产
        df.at[i, 'equity'] = df.at[i, 'cash'] + df.at[i, 'stock_value']  # 总资产
        df.at[i, 'actual_pos'] = df.at[i, 'stock_value'] / df.at[i, 'equity']  # 实际仓位比例

    return df

# 计算自然收益率
def nat_equity(df, type=0, initial_money=1000000):
    """

    :param df:
    :param type: 0, 简单的自然收益率， 1 完整的自然收益率，有初始资金
    :param initial_money: 初始资金，默认为 1000000元
    :return: 有'equity'列的df
    """
    df = df.copy()
    initial_money = float(initial_money)
    # 简单的自然收益率
    if type == 1:
        df['nat_equity'] = (df['change'] + 1.00).cumprod()
        df['nat_equity'] = df['nat_equity'] * initial_money
        # df['nat_equity'].apply(lambda x: int(round(x, 2)))
    else:
        df['nat_equity'] = (df['change'] + 1.00).cumprod()
    return df


# 复杂版计算资金曲线, 增加了平仓和获利卖出,卖出价比
def equity_curve_complex(df, initial_money=1000000, slippage=0.01, c_rate=5.0/10000, t_rate=1.0/1000, sell_pec=0.01):
    """

    :param df: 有'pos'列的df
    :param initial_money: 初始资金，默认为1000000元
    :param slippage: 滑点，默认为0.01元？ 是不是用百分比更好?
    :param c_rate: 手续费，commission_fees, 默认为万分之5
    :param t_rate: 印花税， tax， 默认为千分之1
    :param sell_pec: 滑点百分比
    :return:  返回带有’equity_curve_c'的列
    """
    df = df.copy()
    # ====第一天的情况
    df.at[0, 'hold_num'] = 0  # 持股数
    df.at[0, 'stock_value'] = 0  # 持有股票市值
    df.at[0, 'actual_pos'] = 0  # 每日的实际仓位比例 = 股票市值(stock_value) / 总资产(equity)
    df.at[0, 'cash'] = initial_money  # 持有现金
    df.at[0, 'equity'] = initial_money  # 总资产 = 持有股票市值 + 现金

    # ====第一天之后的每天情况
    for i in range(1, df.shape[0]):

        # 当前持有股票的数量 = 前一天持有的股票的数量
        hold_num = df.at[i-1, 'hold_num']

        # 若发生除权，需要调整hold_num =  昨天的市值 / 调整后的昨天收盘价
        if abs((df.at[i, 'close'] / df.at[i - 1, 'close'] - 1) - df.at[i, 'change']) > 0.001:
            stock_value = df.at[i-1, 'stock_value']  # 当前持有市值是昨天收盘的市值
            last_price = df.at[i, 'close'] / (df.at[i, 'change'] + 1)  # 因为除权，昨天的收盘价要发生变化
            hold_num = stock_value / last_price  # 新的持有股数产生
            hold_num = int(hold_num)

        # 判断是否需要调整仓位
        # 需要调整仓位
        if df.at[i, 'pos'] != df.at[i - 1, 'pos']:  # 仓位发生变化

            # 持有的股票数 = 昨天的总资产 * 今天的仓位 / 今天的开盘价  因为是按开盘价买入
            theory_num = df.at[i-1, 'equtiy'] * df.at[i, 'pos'] / df.at[i, 'open']
            """上面这种写法没有考虑tax,commission,slippage"""
            """但是下面那种写法没有考虑减仓的情况"""
            # 1 买入 0 平仓 -1 获利建仓
            # if df.at[i, 'pos'] == 1:
            #     theory_num = (df.at[i-1, 'equity'] * (1 - c_rate - t_rate)) * df.at[i, 'pos'] / (df.at[i, 'open'] + slippage)
            # 不加也无所谓，默认为NA
            # else:
            #     theory_num = 0
            # 对需要持有的股票数取整数
            theory_num = int(theory_num / 100) * 100  # 向下取百取整

            # 判断是加仓还是调仓
            # 加仓
            if theory_num >= hold_num:
                # 计算实际需要买入的股票数量
                buy_num = theory_num - hold_num
                # 买入股票只能整百，对buy_num进行向下取整百
                buy_num = int(buy_num / 100) * 100

                # 计算买入股票花去的现金
                buy_cash = buy_num * (df.at[i, 'open'] + slippage)
                # 计算买入股票花去的手续费
                commission = round(buy_cash * c_rate, 2)
                # 不足5元，按5元收
                if commission < 5 and commission != 0:
                    commission = 5
                df.at[i, 'commission'] = commission

                # 计算当天收盘价时持有股票的数量和现金
                df.at[i, 'hold_num'] = hold_num + buy_num  # 持有股票 = 昨天的持有股数 + 买入股数
                df.at[i, 'cash'] = df.at[i-1, 'cash'] - buy_cash - commission  # 剩余现金

            # 获利减仓
            elif df.at[i, 'pos'] == -1:
                # 计算卖出股票数量，卖出股票可以不是整数，不需要取整百
                sell_num = hold_num - theory_num

                # 计算卖出股票得到的现金
                sell_cash = sell_num * (df.at[i - 1, 'cost'] * (1+sell_pec) - slippage)
                # 计算手续费，不足5元5元保留2位小数
                commission = round(max(sell_cash * c_rate, 5), 2)
                df.at[i, 'commission'] = commission
                # 计算印花税，保留2位小数，历史上有段时间，买入也会收取印花税
                tax = round(sell_cash * t_rate, 2)
                df.at[i, 'tax'] = tax

                # 计算当天收盘价持有股票的数量和现金
                df.at[i, 'hold_num'] = hold_num - sell_num  # 持有股数 = 昨天的持有股数 - 卖出股数
                df.at[i, 'cash'] = df.at[i-1, 'cash'] + sell_cash - commission - tax  # 持有现金

            # 强制平仓
            else:
                # 计算卖出股票数量，卖出股票可以不是整数，不需要取整百
                sell_num = hold_num - theory_num

                # 计算卖出股票得到的现金
                sell_cash = sell_num * (df.at[i - 1, 'open'] - slippage)
                # 计算手续费，不足5元5元保留2位小数
                commission = round(max(sell_cash * c_rate, 5), 2)
                df.at[i, 'commission'] = commission
                # 计算印花税，保留2位小数，历史上有段时间，买入也会收取印花税
                tax = round(sell_cash * t_rate, 2)
                df.at[i, 'tax'] = tax

                # 计算当天收盘价持有股票的数量和现金
                df.at[i, 'hold_num'] = hold_num - sell_num  # 持有股数 = 昨天的持有股数 - 卖出股数
                df.at[i, 'cash'] = df.at[i-1, 'cash'] + sell_cash - commission - tax  # 持有现金


        # 不需要调仓
        else:
            # 计算当天收盘时持有股票的数量和现金
            df.at[i, 'hold_num'] = hold_num  # 持有股票
            df.at[i, 'cash'] = df.at[i - 1, 'cash']  # 剩余现金

        # 计算收盘时当天的各种数据
        df.at[i, 'stock_value'] = df.at[i, 'hold_num'] * df.at[i, 'close']  # 股票资产
        df.at[i, 'equity'] = df.at[i, 'cash'] + df.at[i, 'stock_value']  # 总资产
        df.at[i, 'actual_pos'] = df.at[i, 'stock_value'] / df.at[i, 'equity']  # 实际仓位比例

    return df







