from dataLoader import DataLoader
from factor import *
from SingleStrategy import *
from backTest import *


# data = DataLoader('000001', '2015-01-01', '2020-01-01')
# with data:
#     df = data.get_data()
#
# # Create factor and strategy objects
# factor = MAFactor(df, window = 30)
# strategy = MovingAverageCrossoverStrategy(factor, short_window = 7, long_window = 30)
#
# # Create backtest object
# backtest = Backtest(df, strategy)
#
# # Run the backtest and plot
# backtest.run_backtest()
#
#
# print(backtest.portfolio['returns'])

if __name__ == '__main__':

    # Read the stock data from SQLite into a DataFrame
    data = DataLoader('000001', '2003-01-01', '2023-01-01')
    with data:
        df = data.get_data()

    # Create factors
    ma_factor = MAFactor(df, window=50)
    rsi_factor = RSIFactor(df, window=14)
    bb_factor = BollingerBandsFactor(df, window=20, stddev=2)
    macd_factor = MACDFactor(df)
    roc_factor = ROCFactor(df, window=12)
    cmf_factor = ChaikinMoneyFlowFactor(df, window=20)

    # Create strategies
    ma_strategy = MovingAverageCrossoverStrategy(ma_factor, short_window=10, long_window=50)
    rsi_strategy = RSIStrategy(rsi_factor, window=14, lower_threshold=30, upper_threshold=70)
    bb_strategy = BollingerBandsStrategy(bb_factor, window=20, stddev=2)

    # Create backtests
    ma_backtest = Backtest(df, ma_strategy)
    rsi_backtest = Backtest(df, rsi_strategy)
    bb_backtest = Backtest(df, bb_strategy)

    # Run backtests
    ma_portfolio = ma_backtest.run_backtest()
    rsi_portfolio = rsi_backtest.run_backtest()
    bb_portfolio = bb_backtest.run_backtest()

    # Plot
    ma_portfolio.plot_candlestick()
    ma_portfolio.plot_portfolio_returns()

    rsi_portfolio.plot_candlestick()
    rsi_portfolio.plot_portfolio_returns()

    bb_portfolio.plot_candlestick()
    bb_portfolio.plot_portfolio_returns()

    print(ma_portfolio.evaluation_metrics)

