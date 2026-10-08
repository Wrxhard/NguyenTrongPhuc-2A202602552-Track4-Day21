"""Ground-truth point membership for failure diagnostics, not KITTI AP evaluation.
GT conventions from provided starter/kitti_io.py; code written with Codex.
"""
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
from starter.datasets import load_frame
from src.obstacle import Config,process,cloud
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
from src.experiments import write_csv,scatter


def rotation(obj):
    c,s=np.cos(obj.rotation_y),np.sin(obj.rotation_y)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]])


def in_gt_box(xyz,obj,calib):
    cam=np.column_stack([xyz,np.ones(len(xyz))])@calib.T_cam_velo.T
    local=(cam[:,:3]-obj.location)@rotation(obj)
    h,w,l=obj.dimensions
    tol=1e-8
    return ((np.abs(local[:,0])<=l/2+tol)&(np.abs(local[:,2])<=w/2+tol)
            &(local[:,1]>=-h-tol)&(local[:,1]<=tol))


def gt_corners(obj,calib):
    h,w,l=obj.dimensions
    bottom=np.array([[l/2,0,w/2],[l/2,0,-w/2],[-l/2,0,-w/2],[-l/2,0,w/2]])
    top=bottom.copy(); top[:,1]=-h
    cam=np.vstack([bottom,top])@rotation(obj).T+obj.location
    return (np.column_stack([cam,np.ones(8)])@np.linalg.inv(calib.T_cam_velo).T)[:,:3]


def memberships(frame,r,eps):
    rows=[]
    for index,obj in enumerate(frame['labels']):
        mask=in_gt_box(r['non_ground'],obj,frame['calib'])
        count=int(mask.sum())
        labels,counts=np.unique(r['labels'][mask],return_counts=True)
        k=int(np.argmax(counts)) if count else 0
        rows.append(dict(eps=eps,gt_index=index,gt_class=obj.type,n_non_ground_in_gt=count,
                         dominant_cluster=int(labels[k]) if count else -1,
                         dominant_count=int(counts[k]) if count else 0,
                         dominant_fraction=float(counts[k]/count) if count else np.nan,
                         n_roi_in_gt=int(in_gt_box(r['roi'],obj,frame['calib']).sum()),
                         n_voxel_in_gt=int(in_gt_box(r['voxel'],obj,frame['calib']).sum()),
                         noise_count=int((r['labels'][mask]<0).sum())))
    return rows



def neighbor_counts(result,mask,eps):
    tree=__import__('open3d').geometry.KDTreeFlann(cloud(result['non_ground']))
    return np.array([tree.search_radius_vector_3d(p,eps)[0]
                     for p in result['non_ground'][mask]],dtype=int)


def occupancy_counts(xyz,size=.2):
    if not np.isfinite(size) or size<=0: raise ValueError('Grid size must be positive')
    grid,_,_=np.histogram2d(xyz[:,0],xyz[:,1],
                bins=[np.linspace(0,30,int(round(30/size))+1),
                      np.linspace(-10,10,int(round(20/size))+1)])
    return grid.astype(int)


def render_occupancy(result,out,frame):
    grid=occupancy_counts(result['non_ground'])
    rows=[]
    for ix,iy in zip(*np.nonzero(grid)):
        rows.append(dict(x_center_m=(ix+.5)*.2,y_center_m=-10+(iy+.5)*.2,
                         n_points=int(grid[ix,iy]),state='occupied_candidate'))
    write_csv(out/'occupancy_cells.csv',rows)
    fig,ax=plt.subplots(figsize=(11,7),layout='constrained')
    ax.imshow((grid.T>0).astype(int),origin='lower',extent=[0,30,-10,10],
              cmap=ListedColormap(['#e4e4e4','#173c4d']),vmin=0,vmax=1,aspect='equal')
    ax.scatter([0],[0],c='red',marker='^',s=60,label='LiDAR origin')
    ax.set(xlabel='x forward (m)',ylabel='y left (m)',
           title=f'KITTI {frame}: BEV occupied candidates, cell 0.20 m; {len(rows)} occupied cells')
    ax.legend(handles=[Line2D([],[],color='#173c4d',lw=8,label='Non-ground point observed'),
                       Line2D([],[],color='#e4e4e4',lw=8,label='No obstacle evidence / unknown (not free)'),
                       Line2D([],[],color='red',marker='^',linestyle='',label='LiDAR origin')],loc='upper right')
    fig.savefig(out/'figures'/'occupancy_000019.png',dpi=160); plt.close(fig)
    return len(rows)


def run_failure(root,out,frame_id='000011'):
    out=Path(out); (out/'figures').mkdir(parents=True,exist_ok=True)
    f=load_frame(root,frame_id)
    reference=process(f['points'],Config())
    plane=reference['plane']
    results=[process(f['points'],Config(eps=e),plane=plane) for e in [.6,.3,.2]]
    rows=[]; details=[]
    for eps,r in zip([.6,.3,.2],results):
        rows.extend(memberships(f,r,eps))
        mask=in_gt_box(r['non_ground'],f['labels'][0],f['calib'])
        counts=neighbor_counts(r,mask,eps)
        details.append(dict(eps=eps,gt_index=0,gt_class='Pedestrian',n_points=int(mask.sum()),
                            n_noise=int((r['labels'][mask]<0).sum()),
                            n_core_in_gt=int((counts>=10).sum()),
                            min_neighbors=int(counts.min()),max_neighbors=int(counts.max()),
                            median_neighbors=float(np.median(counts))))
    # The saved failure must be observed, not assumed from a parameter choice.
    if details[0]['n_noise']!=0 or details[2]['n_noise']!=details[2]['n_points']:
        raise RuntimeError('Selected pedestrian failure no longer observed; investigate geometry')
    write_csv(out/'failure_gt_membership.csv',rows)
    write_csv(out/'failure_density.csv',details)
    corners=gt_corners(f['labels'][0],f['calib'])
    other=gt_corners(f['labels'][1],f['calib'])
    lo=np.minimum(corners[:,:2].min(axis=0),other[:,:2].min(axis=0))-.7
    hi=np.maximum(corners[:,:2].max(axis=0),other[:,:2].max(axis=0))+.7
    fig,axes=plt.subplots(2,3,figsize=(14,8),layout='constrained')
    for j,(eps,r,d) in enumerate(zip([.6,.3,.2],results,details)):
        ax=axes[0,j]; xyz=r['non_ground']; labels=r['labels']
        ax.scatter(xyz[:,0],xyz[:,1],c='#bbb',s=6)
        mask=in_gt_box(xyz,f['labels'][0],f['calib'])
        colors=['#d33' if lab<0 else ['#0072B2','#009E73','#56B4E9','#CC79A7','#F0E442','#222222'][int(lab)%6] for lab in labels[mask]]
        ax.scatter(xyz[mask,0],xyz[mask,1],c=colors,s=25,zorder=4)
        ax.add_patch(Polygon(corners[:4,:2],fill=False,edgecolor='green',lw=2,ls='--'))
        ax.add_patch(Polygon(other[:4,:2],fill=False,edgecolor='purple',lw=1,ls=':'))
        for b in r['boxes']:
            l,u=b['lower'],b['upper']
            ax.add_patch(Rectangle((l[0],l[1]),u[0]-l[0],u[1]-l[1],fill=False,
                                   edgecolor='black',lw=.7))
        ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),xlabel='x forward (m)',ylabel='y left (m)',
               title=f"eps={eps:.2f} m: {d['n_noise']}/{d['n_points']} GT points are noise")
        ax.set_aspect('equal'); ax.grid(alpha=.2)
        ax=axes[1,j]; counts=neighbor_counts(r,mask,eps)
        ax.hist(counts,bins=np.arange(0,max(12,int(counts.max())+2)),color='#277b93')
        ax.axvline(10,color='#d33',ls='--',label='min_points=10')
        ax.set(xlabel='Neighbors within eps (including self)',ylabel='GT point count',
               title=f"Core points inside GT: {d['n_core_in_gt']}/{d['n_points']}")
        ax.legend(); ax.grid(alpha=.2)
    fig.suptitle('FAILURE: same pedestrian / same non-ground cloud, smaller eps removes its cluster\n'
                 'Green dashed: target GT. Purple dotted: occluded neighbor GT. Black: predicted AABB. Red dots: noise.\n'
                 'KITTI 000011, voxel=0.20 m, ground=0.10 m, min_points=10; source: KITTI Vision Benchmark Suite')
    fig.savefig(out/'figures'/'fail_01_dbscan_pedestrian.png',dpi=160); plt.close(fig)
    n_cells=render_occupancy(process(load_frame(root,'000019')['points'],Config()),out,'000019')
    import json
    (out/'failure_config.json').write_text(json.dumps({'dataset':root,'frame':frame_id,
        'target_gt_index':0,'eps':[.6,.3,.2],'min_points':10,'voxel_m':.2,
        'ground_threshold_m':.1,'seed':42,'fixed_plane':plane.tolist(),
        'occupied_cells_000019':n_cells,
        'gt_convention':'camera bottom center; h,w,l; yaw around y; inverse T_cam_velo'},indent=2))
    print(details)
    print('Occupied candidate cells:',n_cells)


def main():
    ap=argparse.ArgumentParser(description='Real pedestrian density failure and BEV occupied candidates')
    ap.add_argument('--data-root',default='data/kitti_mini')
    ap.add_argument('--out',default='results')
    args=ap.parse_args()
    run_failure(args.data_root,args.out)

if __name__=='__main__': main()
