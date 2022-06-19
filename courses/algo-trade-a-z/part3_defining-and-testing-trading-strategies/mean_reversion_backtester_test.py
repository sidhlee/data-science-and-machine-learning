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

        row = self.tester.results.iloc[-1]
        self.assertAlmostEqual(row["price"], 1.120355, 5)
        self.assertAlmostEqual(row["returns"], 0.000388, 5)
        self.assertAlmostEqual(row["sma"], 1.112256, 5)
        self.assertAlmostEqual(row["lower"], 1.103679, 5)
        self.assertAlmostEqual(row["upper"], 1.120832, 5)
        self.assertAlmostEqual(row["position"], -1)
        self.assertAlmostEqual(row["distance"], 0.008099, 5)
        self.assertAlmostEqual(row["strategy"], -0.000388, 5)
        self.assertAlmostEqual(row["creturns"], 0.937249, 5)
        self.assertAlmostEqual(row["cstrategy"], 1.078136, 5)
        self.assertAlmostEqual(row["trades"], 0.000000, 5)
        self.assertAlmostEqual(row["net_strategy"], -0.000388, 5)
        self.assertAlmostEqual(row["net_cstrategy"], 1.069792, 5)

    def test_get_perfs(self):
        (perf, outperf) = self.tester.get_perfs()
        self.assertAlmostEqual(perf, 1.0697915860752671)
        self.assertAlmostEqual(outperf, 0.1325422940180302)

    def test_set_params(self):
        self.tester.set_params(sma=50, sigma=3)
        self.assertEqual(self.tester._sma, 50)
        self.assertEqual(self.tester._sigma, 3)
        perf, outperf = self.tester.get_perfs()
        self.assertAlmostEqual(perf, 1.0604099136947522)
        self.assertAlmostEqual(outperf, 0.140566894281542)

    def test_optimize_params(self):
        sma_range = range(20, 100)
        sigma_range = range(1, 5)
        (optimized_params, after_cost_strategy_return) = self.tester.optimize_params(
            sma_range, sigma_range
        )
        self.assertEqual(optimized_params, (58, 1))
        self.assertAlmostEqual(after_cost_strategy_return, 1.2381106559998172)

        # updates sma and sigma
        self.assertEqual(self.tester._sma, 58)
        self.assertEqual(self.tester._sigma, 1)

        # updates results dataframe
        row = self.tester.results.iloc[-1]
        self.assertAlmostEqual(row["price"], 1.120355, 6)
        self.assertAlmostEqual(row["returns"], 0.000388, 6)
        self.assertAlmostEqual(row["sma"], 1.112306, 6)
        self.assertAlmostEqual(row["lower"], 1.108578, 6)
        self.assertAlmostEqual(row["upper"], 1.116033, 6)

        # populates optimization_trials field
        self.assertIsNotNone(self.tester.optimization_results)
        row = self.tester.optimization_results.iloc[152]
        self.assertEqual(row["sma"], 58)
        self.assertEqual(row["sigma"], 1)
        self.assertAlmostEqual(row["perf"], 1.238111, 6)
