import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas import DataFrame, Series
from itertools import product

from typing import Tuple


class BackTesterData(DataFrame):
    Close: Series
    returns: Series
    sma_s: Series
    sma_l: Series
    position: Series
    strategy: Series
    creturns: Series
    cstrategy: Series


class SmaBackTester:
    _data: BackTesterData

    def __init__(
        self, ticker: str, sma_s: int, sma_l: int, start: str, end: str, csv: str = None
    ):
        self._ticker = ticker
        self._sma_s = sma_s
        self._sma_l = sma_l
        self._start = start
        self._end = end

        self._load_data(csv)
        self._results = self._get_results()
        self._config()

    def __repr__(self):
        return f"{SmaBackTester.__name__}(symbol = {self._ticker}, sma_s = {self._sma_s}, sma_l = {self._sma_l}, start = {self._start}, end = {self._end})"

    def _load_data(self, csv=None):
        data = self._get_data(csv)
        self._data = data

    def _get_data(self, csv=None):
        df: DataFrame = None
        if csv is not None:
            df = pd.read_csv(csv, parse_dates=["Date"], index_col="Date")[self._ticker]
            df = df.loc[self._start : self._end].to_frame().copy()
            df.rename(columns={self._ticker: "price"}, inplace=True)
        else:
            df = yf.download(self._ticker, start=self._start, end=self._end)[
                "Close"
            ].copy()
            if type(df) is Series:
                df = df.to_frame()
            df.rename(columns={"Close": "price"}, inplace=True)

        return df

    def _get_results(self, sma_s=None, sma_l=None):
        if sma_s is None:
            sma_s = self._sma_s
        if sma_l is None:
            sma_l = self._sma_l

        df = self._data.copy().dropna()

        df["returns"] = df["price"].div(df["price"].shift(1)).apply(np.log)
        df["sma_s"] = df["price"].rolling(sma_s).mean()
        df["sma_l"] = df["price"].rolling(sma_l).mean()
        df.dropna(inplace=True)

        df["position"] = np.where(df["sma_s"] > df["sma_l"], 1, -1)
        df["strategy"] = df["returns"] * df["position"].shift(1)
        df.dropna(inplace=True)
        df["creturns"] = df["returns"].cumsum().apply(np.exp)
        df["cstrategy"] = df["strategy"].cumsum().apply(np.exp)

        return df

    def _config(self):
        plt.style.use("seaborn")

    @property
    def results(self):
        return self._results

    def get_perfs(self):
        """Returns (absolute return, out-performance against buy-and-hold)"""
        abs_perf_strategy = self._results.cstrategy[-1]
        abs_perf_buy_and_hold = self._results.creturns[-1]
        rel_perf_strategy = abs_perf_strategy - abs_perf_buy_and_hold

        return (abs_perf_strategy, rel_perf_strategy)

    def plot_results(self):
        self._results[["creturns", "cstrategy"]].plot(figsize=(15, 8))
        plt.title(f"{self._ticker} | SMA_S={self._sma_s} | SMA_L={self._sma_l}")
        plt.show()

    def set_params(self, sma_s: int = None, sma_l: int = None):
        if sma_s is not None:
            self._sma_s = sma_s
        if sma_l is not None:
            self._sma_l = sma_l
        self._results = self._get_results()

    def optimize_params(
        self, range_s_args: Tuple[int, int, int], range_l_args: Tuple[int, int, int]
    ):
        range_s = range(*range_s_args)
        range_l = range(*range_l_args)
        pairs = list(product(range_s, range_l))
        results = []

        for s, l in pairs:
            self._results = self._get_results(s, l)
            (abs_perf, _) = self.get_perfs()
            results.append(abs_perf)

        max_perf = np.max(results)
        max_index = np.argmax(results)
        max_pair = pairs[max_index]

        self.set_params(max_pair[0], max_pair[1])

        return (max_pair, max_perf)
