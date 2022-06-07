from unittest import TestCase
from mean_reversion_backtester import MeanReversionBacktester


class MeanReversionBacktesterTestCase(TestCase):
    def setUp(self):
        proportional_transaction_cost = 0.00007
        self.tester = MeanReversionBacktester(
            "EURUSD", "2018-01-01", "2019-12-31", 30, 2, proportional_transaction_cost
        )

    def test_init(self):
        self.assertEqual(
            self.tester.__repr__(),
            "MeanReversionBacktester(ticker = EURUSD, sma = 30, sigma = 2, start = 2018-01-01, end = 2019-12-31)",
        )

    def test_get_perfs(self):
        self.assertAlmostEqual(self.tester.get_perfs(), (1.069792, 0.132076))
        self.assertEqual(len(self.tester._results), 2040)

        expected_columns = [
            "price",
            "returns",
            "sma",
            "lower",
            "upper",
            "distance",
            "position",
            "strategy",
            "trades",
            "creturns",
            "cstrategy",
        ]

        # get_perfs should populate the results dataframe
        self.assertEqual(self.tester.results.columns, expected_columns)

        row = self.tester.results.loc["2018-01-12 04:00"]
        self.assertAlmostEqual(row["price"], 1.212530)
        self.assertAlmostEqual(row["returns"], 0.006093)
        self.assertAlmostEqual(row["sma"], 1.200748)
        self.assertAlmostEqual(row["lower"], 1.190374)
        self.assertAlmostEqual(row["upper"], 1.211122)
        self.assertAlmostEqual(row["distance"], 0.011782)
        self.assertAlmostEqual(row["position"], -1)
        self.assertAlmostEqual(row["strategy"], -0.000070)
        self.assertAlmostEqual(row["trades"], 1.0)
        self.assertAlmostEqual(row["creturns"], 1.014865)
        self.assertAlmostEqual(row["cstrategy"], 0.999930)

    def test_optimize_params(self):
        (optimized_params, after_cost_return) = self.tester.optimize_params()
        self.assertEqual(optimized_params, (58, 1))
        self.assertAlmostEqual(after_cost_return, 1.238111)

        # updates sma and sigma
        self.assertEqual(self.tester._sma, 58)
        self.assertEqual(self.tester._sigma, 1)

        # updates results dataframe
        row = self.tester.results.iloc[1]
        self.assertAlmostEqual(row["price"], 1.225370)
        self.assertAlmostEqual(row["returns"], 0.000343)
        self.assertAlmostEqual(row["sma"], 1.210748)
        self.assertAlmostEqual(row["lower"], 1.198848)
        self.assertAlmostEqual(row["upper"], 1.222648)

        # populates optimization_trials field
        self.assertIsNotNone(self.tester.optimization_trials)
        row = self.tester.optimization_trials.iloc[0]
        self.assertEqual(row["sma"], 25)
        self.assertEqual(row["sigma"], 1)
        self.assertAlmostEqual(row["perf"], 0.995746)
