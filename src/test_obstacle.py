"""Tests catch lost ROI boundaries, unnormalized planes and unsafe empty defaults."""
import unittest
import numpy as np
try:
    from src import obstacle as m
except ImportError:
    m = None

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(m, 'obstacle pipeline is not implemented')

    def test_finite_and_roi_inclusive(self):
        p = np.array([[0,-10,-3,1],[30,10,3,1],[31,0,0,1],
                      [2,0,0,np.nan],[2,np.inf,0,1]], float)
        q = m.prepare(p,m.Config())
        np.testing.assert_array_equal(q,[[0,-10,-3],[30,10,3]])

    def test_normalized_plane_and_threshold_boundary(self):
        p=np.array([[1,0,.1],[1,0,.10001],[1,0,-.2]])
        np.testing.assert_array_equal(m.ground_mask(p,[0,0,2,0],.1),[True,False,False])

    def test_nearest_rectangle_not_center(self):
        self.assertEqual(m.box_distance([3,4,0],[8,9,2]),5.)
        self.assertEqual(m.box_distance([-1,-1,0],[1,1,2]),0.)

    def test_empty_and_all_noise_are_not_free_space(self):
        r=m.process(np.empty((0,4)),m.Config())
        self.assertEqual(r['metrics']['n_clusters'],0)
        self.assertTrue(np.isnan(r['metrics']['nearest_m']))
        self.assertFalse(r['metrics']['ground_valid'])
        labels,boxes=m.cluster(np.array([[1,0,1],[10,0,1]]),m.Config())
        self.assertEqual(boxes,[])
        np.testing.assert_array_equal(labels,[-1,-1])

    def test_kitti_plane_repeats_with_seed(self):
        from starter.datasets import load_points
        p=load_points('data/kitti_mini','000001')
        cfg=m.Config(voxel=.1)
        a=m.process(p,cfg)
        for _ in range(4):
            b=m.process(p,cfg)
            np.testing.assert_array_equal(a['plane'],b['plane'])
            np.testing.assert_array_equal(a['labels'],b['labels'])

    def test_scaled_plane_tilt_metric(self):
        p=np.array([[1,0,1,1],[2,0,1,1]])
        a=m.process(p,m.Config(),plane=[0,.1,1,0])
        b=m.process(p,m.Config(),plane=[0,.2,2,0])
        self.assertAlmostEqual(a["metrics"]["plane_tilt_deg"],5.710593137499643)
        self.assertAlmostEqual(b["metrics"]["plane_tilt_deg"],5.710593137499643)

    def test_vertical_plane_rejected(self):
        self.assertFalse(m.valid_ground([1,0,0,-3]))
        self.assertTrue(m.valid_ground([0,0,1,1.7]))
        with self.assertRaises(ValueError): m.ground_mask(np.zeros((1,3)),[0,0,0,0],.1)

    def test_two_obstacles_survive_flat_ground(self):
        x,y=np.meshgrid(np.linspace(1,12,30),np.linspace(-4,4,30))
        ground=np.column_stack([x.ravel(),y.ravel(),np.zeros(x.size)])
        rng=np.random.default_rng(7)
        a=rng.uniform([3,-2,.5],[3.4,-1.6,1],(150,3))
        b=rng.uniform([8,2,.5],[8.4,2.4,1],(150,3))
        xyz=np.vstack([ground,a,b]); p=np.column_stack([xyz,np.ones(len(xyz))])
        c=m.Config(voxel=.05,eps=.3,min_points=5)
        r=m.process(p,c)
        self.assertTrue(r['metrics']['ground_valid'])
        self.assertEqual(r['metrics']['n_clusters'],2)
        self.assertGreater(r['metrics']['n_ground'],850)
        self.assertGreater(r['metrics']['n_non_ground'],150)
        self.assertGreater(r['metrics']['nearest_m'],3)

if __name__=='__main__': unittest.main()
