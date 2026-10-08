import unittest
import numpy as np
try:
    from src import benchmark as m
except ImportError:
    m=None

class BenchmarkTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(m,'benchmark is not implemented')

    def test_quantiles_and_twenty_repeats(self):
        p50,p95=m.latency_stats(list(range(1,21)))
        self.assertAlmostEqual(p50,10.5)
        self.assertAlmostEqual(p95,19.05)
        with self.assertRaises(ValueError): m.latency_stats([1]*19)

    def test_sweeps_change_only_one_configuration(self):
        configs=m.configurations()
        self.assertEqual(len(configs),6)
        for sweep,value,c in configs:
            self.assertEqual(c.eps,.6)
            self.assertEqual(c.min_points,10)
            if sweep=='ground':
                self.assertEqual(c.voxel,.2); self.assertEqual(c.threshold,value)
            else:
                self.assertEqual(c.threshold,.1); self.assertEqual(c.voxel,value)

    def test_claim_is_ratio_of_means_not_mean_of_percentages(self):
        self.assertAlmostEqual(m.claim_drop([100,900],[0,810]),19)
        self.assertTrue(np.isnan(m.claim_drop([0],[0])))

if __name__=='__main__': unittest.main()
