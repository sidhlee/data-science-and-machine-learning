import pandas as pd
from typing import Tuple


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
        self.ptc = ptc

        self._results: pd.DataFrame = None
        self._optimization_trials: pd.DataFrame = None

    def __repr__(self):
        return f"MeanReversionBacktester(ticker = {self._ticker}, sma = {self._sma}, sigma = {self._sigma}, start = {self._start}, end = {self._end})"

    @property
    def results(self) -> pd.DataFrame:
        return self._results

    @property
    def optimization_trials(self):
        return self._optimization_trials

    def get_perfs(self):
        pass

    def optimize_params(
        self, sma_range: Tuple[int, int, int], sigma_range: Tuple[int, int, int]
    ):
        pass
