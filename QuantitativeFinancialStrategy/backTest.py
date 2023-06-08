import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
from datetime import datetime


class Backtest:
    def __init__(self, data, strategy, make_plots = True):
        self.data = data
        self.strategy = strategy
        self.make_plots = make_plots
        # Create a portfolio to track trades and equity
        self.portfolio = pd.DataFrame(index=self.data.index).fillna(0.0)
        self.evaluation_metrics = {}
    def run_backtest(self):
        signals = self.strategy.generate_signals()

        # Create a portfolio to track trades and equity
        self.portfolio['position'] = signals['signal']
        self.portfolio['close'] = self.data['close']

        # trading process: change between holding and cash
        self.portfolio['holdings'] = 0.0          # 持仓价值
        self.portfolio['holding_amount'] =  0.0   # 持仓股数
        self.portfolio['cash'] = 100.0            # 手上现金价值（不买股票，仅在手上持有，等待下次买入)

        # Calculate cash balance and holdings
        # 仅在收盘时进行买入、卖出
        for i in range(len(self.portfolio)):
             # 如果是第二天以后（则存在昨天)
            if i > 0:
                # 昨天信号为0，今天信号为1： 买入，cash转为holding
                if self.portfolio['position'].iloc[i-1] == 0 and self.portfolio['position'].iloc[i] == 1:
                    # 计算昨天的cash在今天的收盘价，可以买多少股（允许小数）
                    self.portfolio['holding_amount'].iloc[i] = self.portfolio['cash'].iloc[i-1] / self.data['close'].iloc[i]
                    # 昨天的cash在今天全部买入，所有cash转为holding
                    self.portfolio['holdings'].iloc[i] = self.portfolio['cash'].iloc[i-1]
                    # 买入后，cash为0
                    self.portfolio['cash'].iloc[i] = 0

                # （昨天信号为1且今天信号为1）或（昨天信号为0且今天信号为0），无任何动作，持有或者持仓为空
                elif ((self.portfolio['position'].iloc[i-1] == 1 and self.portfolio['position'].iloc[i] == 1)
                      or (self.portfolio['position'].iloc[i-1] == 0 and self.portfolio['position'].iloc[i] == 0)):
                    # 持有状态，不买入不卖出
                    self.portfolio['cash'].iloc[i] = self.portfolio['cash'].iloc[i-1]
                    self.portfolio['holding_amount'].iloc[i] = self.portfolio['holding_amount'].iloc[i-1]
                    # 今日收盘时手上持仓价值，为 收盘价*仓位
                    self.portfolio['holdings'].iloc[i] = self.portfolio['holding_amount'].iloc[i] * self.portfolio['close'].iloc[i]

                # 昨天信号为1,且今天信号为0, 卖出
                else:
                    self.portfolio['cash'].iloc[i] = self.portfolio['holdings'].iloc[i-1]
                    self.portfolio['holdings'].iloc[i] = 0.0
                    self.portfolio['holding_amount'].iloc[i] = 0.0
            # 第一天
            else:
                # 如果触发买入信号，全部买入，cash转为holding
                if self.portfolio['position'].iloc[i] == 1:
                    self.portfolio['holdings'].iloc[i] = self.portfolio['cash'].iloc[i]
                    self.portfolio['holding_amount'].iloc[i] = self.portfolio['cash'].iloc[i] / self.data['close'].iloc[i]
                    self.portfolio['cash'].iloc[i] = 0.0
                # 如果第一天不触发买入，则什么都不做（这块可删）
                else:
                    pass


        # calculate return
        self.portfolio['total'] = self.portfolio['cash'] + self.portfolio['holdings']
        self.portfolio['returns'] = self.portfolio['total'].pct_change()
        self.portfolio['returns'].replace([np.inf, -np.inf], 0, inplace=True)

        # Calculate accumulated return
        self.portfolio['accumulated_returns'] = (1 + self.portfolio['returns']).cumprod()

        # evaluation
        self.evaluation_metrics['annual_return'] = (self.portfolio['accumulated_returns'].iloc[-1]** (1 / (len(self.portfolio) / 252)) - 1) # Assuming 252 trading days in a year
        self.evaluation_metrics['num_trades ']= signals['signal'].diff().abs().sum()
        self.evaluation_metrics['total_return'] = self.portfolio['accumulated_returns'].iloc[-1] - 1
        average_return = self.portfolio['returns'].mean()
        std_return = self.portfolio['returns'].std()
        self.evaluation_metrics['sharpe_ratio'] = (average_return / std_return) * np.sqrt(252)  # Assuming 252 trading days in a year
        drawdown = (self.portfolio['accumulated_returns'] / self.portfolio['accumulated_returns'].cummax()) - 1
        self.evaluation_metrics['max_drawdown']  = drawdown.min()

        # Plot
        if self.make_plots:

            self.plot_candlestick()
            self.plot_portfolio_returns()
            self.plot_accumulated_returns()

        return self

    def plot_candlestick(self):
        ohlc = self.data[['open', 'high', 'low', 'close']]
        ohlc.reset_index(inplace=True)
        ohlc['date'] = [datetime.strptime(date_str, '%Y-%m-%d') for date_str in ohlc['date']]
        ohlc['date'] = ohlc['date'].map(mpl_dates.date2num)

        fig, ax = plt.subplots()
        candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red')
        ax.xaxis_date()
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title('Candlestick Chart')
        plt.xticks(rotation=45)
        plt.show()

    def plot_portfolio_returns(self):
        fig, ax = plt.subplots()
        ax.plot(self.portfolio['returns'].index, self.portfolio['returns'].values)
        ax.set_xlabel('Date')
        ax.set_ylabel('Returns')
        ax.set_title('Portfolio Returns')
        x_ticks = range(0, len(self.portfolio), 90)
        plt.xticks(x_ticks, self.portfolio.index[::90], rotation=45, fontsize = 6)
        plt.show()

    def plot_accumulated_returns(self):
        fig, ax = plt.subplots()
        ax.plot(self.portfolio['accumulated_returns'].index, self.portfolio['accumulated_returns'].values)
        ax.set_xlabel('Date')
        ax.set_ylabel('Returns')
        annual_return = self.evaluation_metrics['annual_return']
        ax.set_title(f'annual return: {annual_return: .3%}')
        x_tick_day_gap = len(self.portfolio) // 20
        x_ticks = range(0, len(self.portfolio), x_tick_day_gap)
        plt.xticks(x_ticks, self.portfolio.index[::x_tick_day_gap], rotation=45, fontsize = 6)
        plt.show()
