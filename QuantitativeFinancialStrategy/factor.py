import pandas as pd
import numpy as np

class Factor:
    def __init__(self, data):
        self.data = data

    def calculate(self):
        pass


class MAFactor(Factor):
    def __init__(self, data, window):
        super().__init__(data)
        self.window = window

    def calculate(self):
        ma = self.data['close'].rolling(self.window).mean()
        return ma


class RSIFactor(Factor):
    def __init__(self, data, window):
        super().__init__(data)
        self.window = window

    def calculate(self):
        delta = self.data['close'].diff()
        gain = delta.mask(delta < 0, 0)
        loss = -delta.mask(delta > 0, 0)
        avg_gain = gain.rolling(self.window).mean()
        avg_loss = loss.rolling(self.window).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


class BollingerBandsFactor(Factor):
    def __init__(self, data, window, stddev):
        super().__init__(data)
        self.window = window
        self.stddev = stddev

    def calculate(self):
        rolling_mean = self.data['close'].rolling(self.window).mean()
        rolling_std = self.data['close'].rolling(self.window).std()
        upper_band = rolling_mean + self.stddev * rolling_std
        lower_band = rolling_mean - self.stddev * rolling_std
        return upper_band, rolling_mean, lower_band


class MACDFactor(Factor):
    def __init__(self, data):
        super().__init__(data)

    def calculate(self):
        short_ema = self.data['close'].ewm(span=12).mean()
        long_ema = self.data['close'].ewm(span=26).mean()
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=9).mean()
        return macd_line, signal_line


class ROCFactor(Factor):
    def __init__(self, data, window):
        super().__init__(data)
        self.window = window

    def calculate(self):
        roc = (self.data['close'] / self.data['close'].shift(self.window)) - 1
        return roc


class ChaikinMoneyFlowFactor(Factor):
    def __init__(self, data, window):
        super().__init__(data)
        self.window = window

    def calculate(self):
        high = self.data['high']
        low = self.data['low']
        close = self.data['close']
        volume = self.data['volume']
        mf_multiplier = ((close - low) - (high - close)) / (high - low)
        mf_volume = mf_multiplier * volume
        cmf = mf_volume.rolling(self.window).sum() / volume.rolling(self.window).sum()
        return cmf
