import os
import pandas as pd
import numpy as np
from typing import List, Tuple
from itertools import product


class MeanReversionBacktester:
    def __init__(self, ticker: str, start: str, end: str, sma=30, sigma=2, ptc=0):
        """
        Arguments
        - sigma - number of standard deviations from the SMA for upper and lower bound of the Bollinger band
        - ptc - proportional transaction cost
        """
        self._ticker = ticker
        self._sma = sma
        self._sigma = sigma
        self._start = start
        self._end = end
        self._ptc = ptc

        self._data = None
        self._results: pd.DataFrame = None
        self._optimization_results: pd.DataFrame = None

        self._load_data()
        self._results = self._get_results()

    def __repr__(self):
        return f"MeanReversionBacktester(ticker = {self._ticker}, sma = {self._sma}, sigma = {self._sigma}, start = {self._start}, end = {self._end})"

    @property
    def results(self) -> pd.DataFrame:
        return self._results

    @property
    def optimization_results(self):
        return self._optimization_results

    def _load_data(self):
        path = os.path.join(
            os.getcwd(),
            "courses/algo-trade-a-z/part3_defining-and-testing-trading-strategies/intraday.csv",
        )
        df = pd.read_csv(
            path,
            parse_dates=["time"],
            index_col="time",
        )

        df = df.loc[self._start : self._end]

        self._data = df

    def _get_results(self):
        """
        Returns the dataframe where many columns are added to the loaded data using the mean reversion strategy.
        - returns - daily log return of the price
        - sma - the number of days for the SMA rolling window
        - lower - the lower bound of the Bollinger band (sma - std for the rolling window)
        - upper - the upper bound of the Bollinger band (sma + std for the rolling window)
        - distance - the distance between the current price and the current sma
        - position - vectorized position for long(1), hold(0), short(-1)
        - strategy - today's return * yesterdays' position
        - trades - number of trades required to execute the yesterday's position
        - creturns - current cumulative return of the asset
        - cstrategy - current cumulative return of the strategy
        """
        df = self._data.copy()

        df["returns"] = df["price"].div(df["price"].shift(1)).apply(np.log)
        df["sma"] = df["price"].rolling(self._sma).mean()
        # having dropna here gives incorrect results because
        # we're rolling it again for the delta and the first 29 line would be NaN again
        # df.dropna(inplace=True)
        delta = df["price"].rolling(self._sma).std() * self._sigma
        df.dropna(inplace=True)

        df["lower"] = df["sma"].sub(delta)
        df["upper"] = df["sma"].add(delta)

        df["distance"] = df["price"].sub(df["sma"])

        df["position"] = np.where(df["price"] > df["upper"], -1, np.nan)
        df["position"] = np.where(df["price"] < df["lower"], 1, df["position"])
        # hold when price crosses sma
        df["position"] = np.where(
            df["distance"] * df["distance"].shift(1) < 0, 0, df["position"]
        )
        # forward-fill until the price hits the upper|lower bound
        df["position"].ffill(inplace=True)
        # we want to dropna before filling any values because that'll skew the result
        # eg. more holding will lower the cstrategy
        df["position"].fillna(0, inplace=True)

        df["strategy"] = df["returns"] * df["position"].shift(1)

        # For the same reason above, df needs to be removed of the empty rows
        # before calculating cumulative values.
        df["creturns"] = df["returns"].cumsum().apply(np.exp)
        df["cstrategy"] = df["strategy"].cumsum().apply(np.exp)

        # we're using yesterday's position to trade
        df["trades"] = df["position"].diff().fillna(0).abs().shift(1)

        # after the trading cost
        df["net_strategy"] = df["strategy"].sub(df["trades"] * self._ptc)
        df["net_cstrategy"] = df["net_strategy"].cumsum().apply(np.exp)

        df.dropna(inplace=True)

        return df

    def get_perfs(self):
        """
        returns (perf, outperf)
        perf - final return on strategy after the trading cost
        outperf - perf - benchmark(buy & hold)
        """
        perf = self.results["net_cstrategy"].iloc[-1]
        outperf = perf - self.results["creturns"].iloc[-1]
        return (perf, outperf)

    def set_params(self, sma: int, sigma: int):
        self._sma = sma
        self._sigma = sigma
        self._results = self._get_results()

    def optimize_params(self, sma_range: range, sigma_range: range):
        """
        Find the best combination of sma window and sigma for Bollinger band.
        1. Sets the sma and sigma of the instance with the above
        2. Updates the results df
        3. Populates `optimization_results` df

        Returns: ((sma, sigma), best_perf)
        """
        products = list(product(sma_range, sigma_range))
        perfs = []
        for (sma, sigma) in products:
            self.set_params(sma, sigma)
            (perf, _) = self.get_perfs()
            perfs.append(perf)
        best_perf = max(perfs)
        best_index = np.argmax(perfs)
        # if you hadn't converted the products into list, it would've been exhausted after iterating through
        (sma, sigma) = products[best_index]

        self.set_params(sma, sigma)
        self._optimization_results = self._get_optimization_results(products, perfs)

        return ((sma, sigma), best_perf)

    def _get_optimization_results(self, products: Tuple[int, int], perfs: List[float]):
        return pd.DataFrame(
            {
                "sma": (sma for (sma, _) in products),
                "sigma": (sigma for (_, sigma) in products),
                "perf": perfs,
            }
        )
