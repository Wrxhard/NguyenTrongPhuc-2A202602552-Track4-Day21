import unittest
from types import SimpleNamespace
import numpy as np
try:
    from src import failure as m
except ImportError:
    m=None

class GeometryTests(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(m,'GT diagnostic is not implemented')

    def test_bottom_center_and_rotated_box(self):
        obj=SimpleNamespace(dimensions=np.array([2.,2.,4.]),location=np.array([10.,0.,10.]),rotation_y=0.)
        calib=SimpleNamespace(T_cam_velo=np.eye(4))
        p=np.array([[10,-1,10],[12,0,11],[10,.1,10],[10,-2.1,10],[12.1,-1,10]])
        np.testing.assert_array_equal(m.in_gt_box(p,obj,calib),[True,True,False,False,False])
        obj.rotation_y=np.pi/2
        np.testing.assert_array_equal(m.in_gt_box(np.array([[10,-1,12],[12,-1,10]]),obj,calib),[True,False])

    def test_occupancy_includes_boundary_points(self):
        grid=m.occupancy_counts(np.array([[0,-10,0],[30,10,0],[.1,-9.9,1]]),.2)
        self.assertEqual(grid.shape,(150,100))
        self.assertEqual(int(grid.sum()),3)
        self.assertEqual(int(grid[0,0]),2)
        self.assertEqual(int(grid[-1,-1]),1)

    def test_cam_to_lidar_translation_for_corners(self):
        obj=SimpleNamespace(dimensions=np.array([2.,2.,4.]),location=np.array([10.,0.,10.]),rotation_y=0.)
        t=np.eye(4); t[:3,3]=[1,2,3]
        corners=m.gt_corners(obj,SimpleNamespace(T_cam_velo=t))
        np.testing.assert_allclose(corners.min(axis=0),[7,-4,6])
        np.testing.assert_allclose(corners.max(axis=0),[11,-2,8])

if __name__=='__main__': unittest.main()
