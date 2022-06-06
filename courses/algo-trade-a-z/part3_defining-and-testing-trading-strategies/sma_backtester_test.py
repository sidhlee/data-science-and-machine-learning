from unittest import TestCase
from unittest.mock import patch
from sma_back_tester import SmaBackTester
import pandas as pd

TEST_CSV_PATH = "courses/algo-trade-a-z/part3_defining-and-testing-trading-strategies/eur_usd_yf_download.csv"


class SmaBackTesterTestCase(TestCase):
    def setUp(self):
        download_patcher = patch("yfinance.download")
        self.addCleanup(download_patcher.stop)
        self.mock_download = download_patcher.start()
        self.mock_download.return_value = pd.read_csv(
            TEST_CSV_PATH,
            parse_dates=["Date"],
            index_col="Date",
        )

        self.tester = SmaBackTester("EURUSD=X", 50, 200, "2004-01-01", "2020-06-30")

    def test_repr(self):
        expected = "SmaBackTester(symbol = EURUSD=X, sma_s = 50, sma_l = 200, start = 2004-01-01, end = 2020-06-30)"
        self.assertEqual(self.tester.__repr__(), expected)

    def test_attributes(self):
        self.assertEqual(self.tester._sma_s, 50)
        self.assertEqual(self.tester._sma_l, 200)
        self.assertEqual(self.tester._start, "2004-01-01")
        self.assertEqual(self.tester._end, "2020-06-30")

    def test_init_loads_data(self):
        self.assertIsNotNone(self.tester._data)
        expected_data = (
            self.mock_download.return_value["Close"]
            .to_frame()
            .rename(columns={"Close": "price"})
        )
        self.assertTrue(self.tester._data.equals(expected_data))

    def test_init_loads_results(self):
        results = self.tester._results
        self.assertEqual(len(results), 4075)

        expected_columns = [
            "price",
            "returns",
            "sma_s",
            "sma_l",
            "position",
            "strategy",
            "creturns",
            "cstrategy",
        ]
        self.assertEqual(list(results.columns), expected_columns)

        self.assertEqual(results.iloc[-1]["price"].round(5), 1.124720)

    def test_get_perfs(self):
        perfs = self.tester.get_perfs()
        expected_perfs = (1.2835003323288539, 0.3676743925451338)
        self.assertAlmostEqual(perfs[0], expected_perfs[0])
        self.assertAlmostEqual(perfs[1], expected_perfs[1])

    def test_optimize_params(self):
        (best_pair, best_perf) = self.tester.optimize_params((44, 48, 1), (135, 139, 1))
        self.assertEqual(best_pair, (46, 137))
        self.assertAlmostEqual(best_perf, 2.5266939897810805)

        (abs_perf, rel_perf) = self.tester.get_perfs()
        self.assertAlmostEqual(abs_perf, 2.5266939897810805)
        self.assertAlmostEqual(rel_perf, 1.6210467811232694)
