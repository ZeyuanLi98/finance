import pandas as pd
import numpy as np

class SingleStrategy:
    def __init__(self, factor):
        self.factor = factor

    def generate_signals(self):
        pass


class MovingAverageCrossoverStrategy(SingleStrategy):
    def __init__(self, factor, short_window, long_window):
        super().__init__(factor)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self):
        signals = pd.DataFrame(index=self.factor.data.index)
        signals['signal'] = 0.0

        # Generate signals based on moving average crossover
        signals['short_mavg'] = self.factor.calculate().rolling(self.short_window).mean()
        signals['long_mavg'] = self.factor.calculate().rolling(self.long_window).mean()
        signals.loc[self.short_window:, 'signal'] = np.where(
            signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:],
            1.0,
            0.0
        )
        return signals


class RSIStrategy(SingleStrategy):
    def __init__(self, factor, window, lower_threshold, upper_threshold):
        super().__init__(factor)
        self.window = window
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold

    def generate_signals(self):
        signals = pd.DataFrame(index=self.factor.data.index)
        signals['signal'] = 0.0

        # Generate signals based on RSI thresholds
        rsi = self.factor.calculate()
        signals.loc[rsi > self.upper_threshold, 'signal'] = 0.0
        signals.loc[rsi < self.lower_threshold, 'signal'] = 1.0
        return signals


class BollingerBandsStrategy(SingleStrategy):
    def __init__(self, factor, window, stddev):
        super().__init__(factor)
        self.window = window
        self.stddev = stddev

    def generate_signals(self):
        signals = pd.DataFrame(index=self.factor.data.index)
        signals['signal'] = 0.0

        # Generate signals based on Bollinger Bands
        upper_band, _, lower_band = self.factor.calculate()
        signals.loc[self.factor.data['close'] > upper_band, 'signal'] = 0.0
        signals.loc[self.factor.data['close'] < lower_band, 'signal'] = 1.0
        return signals
