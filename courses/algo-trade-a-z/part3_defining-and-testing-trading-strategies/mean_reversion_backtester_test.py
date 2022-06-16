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

    def test_results(self):
        expected_columns = [
            "price",
            "returns",
            "sma",
            "lower",
            "upper",
            "distance",
            "position",
            "strategy",
            "creturns",
            "cstrategy",
            "trades",
            "net_strategy",
            "net_cstrategy",
        ]

        # get_perfs should populate the results dataframe
        self.assertListEqual(list(self.tester.results.columns), expected_columns)

        row = self.tester.results.loc["2018-02-12 04:00"]
        self.assertAlmostEqual(row["price"], 1.226390, 5)
        self.assertAlmostEqual(row["returns"], -0.001882, 5)
        self.assertAlmostEqual(row["sma"], 1.236001, 5)
        self.assertAlmostEqual(row["lower"], 1.217764, 5)
        self.assertAlmostEqual(row["upper"], 1.254237, 5)
        self.assertAlmostEqual(row["position"], 1)
        self.assertAlmostEqual(row["distance"], -0.009610, 5)
        self.assertAlmostEqual(row["strategy"], -0.001882, 5)
        self.assertAlmostEqual(row["creturns"], 1.025954, 5)
        self.assertAlmostEqual(row["cstrategy"], 0.989118, 5)
        self.assertAlmostEqual(row["trades"], 0.00000, 5)
        self.assertAlmostEqual(row["net_strategy"], -0.001882, 5)
        self.assertAlmostEqual(row["net_cstrategy"], 0.988911, 5)

    def test_get_perfs(self):
        (perf, outperf) = self.tester.get_perfs()
        self.assertAlmostEqual(perf, 1.0864666877031217)
        self.assertAlmostEqual(outperf, 0.14921739564588477)

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
