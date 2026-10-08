"""CPU obstacle baseline. Original implementation assisted by ChatGPT/Codex.
API reference: https://www.open3d.org/docs/release/tutorial/geometry/pointcloud.html
Uses Open3D voxel_down_sample, segment_plane and cluster_dbscan; no copied code.
KITTI LiDAR frame: x forward, y left, z up; metres.
"""
from dataclasses import dataclass
import numpy as np
import open3d as o3d

@dataclass(frozen=True)
class Config:
    voxel: float = .2
    threshold: float = .1
    eps: float = .6
    min_points: int = 10
    seed: int = 42
    iterations: int = 1000

    def __post_init__(self):
        for value in (self.voxel,self.threshold,self.eps):
            if not np.isfinite(value) or value <= 0:
                raise ValueError('voxel, threshold, eps must be finite and positive')
        if self.min_points < 1 or self.iterations < 1:
            raise ValueError('min_points and iterations must be positive')


def prepare(points,cfg):
    p=np.asarray(points)
    if p.ndim != 2 or p.shape[1] not in (3,4):
        raise ValueError('Expected Nx3 or Nx4 points')
    q=p[np.isfinite(p).all(axis=1),:3]
    roi=((q[:,0]>=0)&(q[:,0]<=30)&(np.abs(q[:,1])<=10)
         &(q[:,2]>=-3)&(q[:,2]<=3))
    return np.asarray(q[roi],dtype=np.float64)


def cloud(xyz):
    p=o3d.geometry.PointCloud()
    p.points=o3d.utility.Vector3dVector(np.asarray(xyz,dtype=np.float64))
    return p


def valid_ground(plane):
    p=np.asarray(plane,dtype=float)
    if p.shape!=(4,) or not np.isfinite(p).all(): return False
    norm=np.linalg.norm(p[:3])
    return bool(norm>0 and abs(p[2])/norm>=np.cos(np.radians(15)))


def fit_ground(xyz,cfg):
    if len(xyz)<3: return np.full(4,np.nan)
    o3d.utility.random.seed(cfg.seed)
    plane,_=cloud(xyz).segment_plane(distance_threshold=.1,ransac_n=3,
                                    num_iterations=cfg.iterations,probability=.999)
    plane=np.asarray(plane,dtype=float)
    plane/=np.linalg.norm(plane[:3])
    if plane[2]<0: plane=-plane
    return plane


def ground_mask(xyz,plane,threshold):
    p=np.asarray(plane,dtype=float)
    norm=np.linalg.norm(p[:3])
    if p.shape!=(4,) or not np.isfinite(p).all() or norm==0:
        raise ValueError('Invalid plane')
    return np.abs(np.asarray(xyz)@p[:3]+p[3])/norm<=threshold


def box_distance(lower,upper):
    lo,hi=np.asarray(lower)[:2],np.asarray(upper)[:2]
    closest=np.maximum(lo,np.minimum(np.zeros(2),hi))
    return float(np.linalg.norm(closest))


def cluster(xyz,cfg):
    if len(xyz)==0: return np.empty(0,dtype=int),[]
    labels=np.asarray(cloud(xyz).cluster_dbscan(eps=cfg.eps,
                      min_points=cfg.min_points,print_progress=False))
    boxes=[]
    for label in sorted(set(labels)-{-1}):
        obj=xyz[labels==label]
        box=cloud(obj).get_axis_aligned_bounding_box()
        lo,hi=np.asarray(box.min_bound),np.asarray(box.max_bound)
        boxes.append(dict(cluster_id=int(label),n_points=len(obj),lower=lo,
                          upper=hi,extent=hi-lo,distance_m=box_distance(lo,hi)))
    return labels,boxes


def process(points,cfg=Config(),plane=None):
    roi=prepare(points,cfg)
    xyz=np.asarray(cloud(roi).voxel_down_sample(cfg.voxel).points) if len(roi) else roi
    plane=fit_ground(xyz,cfg) if plane is None else np.asarray(plane,dtype=float)
    valid=valid_ground(plane)
    mask=ground_mask(xyz,plane,cfg.threshold) if valid else np.zeros(len(xyz),bool)
    obstacles=xyz[~mask]
    labels,boxes=cluster(obstacles,cfg)
    metrics=dict(n_raw=len(points),n_invalid=int((~np.isfinite(points).all(axis=1)).sum()),
                 n_roi=len(roi),n_voxel=len(xyz),n_ground=int(mask.sum()),
                 n_non_ground=len(obstacles),ground_valid=valid,
                 plane_tilt_deg=float(np.degrees(np.arccos(np.clip(abs(plane[2]),0,1)))) if valid else np.nan,
                 n_clusters=len(boxes),n_noise=int((labels==-1).sum()),
                 nearest_m=min((b['distance_m'] for b in boxes),default=np.nan),
                 no_cluster=not bool(boxes))
    return dict(roi=roi,voxel=xyz,ground=xyz[mask],non_ground=obstacles,
                labels=labels,boxes=boxes,plane=plane,metrics=metrics)
