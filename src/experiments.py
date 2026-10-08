"""Reproducible topic D demo and benchmarks (student code, AI assisted)."""
import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from starter.datasets import load_points
from src.obstacle import Config,process

FRAMES=['000001','000011','000019','000025','000049']


def write_csv(path,rows):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def box_rows(result,extra):
    rows=[]
    for b in result['boxes']:
        row={**extra,'cluster_id':b['cluster_id'],'n_points':b['n_points'],
             'nearest_m':b['distance_m']}
        for i,axis in enumerate('xyz'):
            row.update({axis+'_min':b['lower'][i],axis+'_max':b['upper'][i],
                        axis+'_size':b['extent'][i]})
        rows.append(row)
    return rows


def scatter(ax,xyz,vertical=False,labels=None):
    j=2 if vertical else 1
    if len(xyz):
        colors=xyz[:,2] if labels is None else np.where(labels<0,-1,labels%20)
        ax.scatter(xyz[:,0],xyz[:,j],c=colors,s=.7,cmap='turbo',rasterized=True)
    ax.set(xlim=(0,30),ylim=(-3,3) if vertical else (-10,10),
           xlabel='x forward (m)',ylabel='z up (m)' if vertical else 'y left (m)')
    ax.grid(alpha=.2)
    if not vertical: ax.set_aspect('equal')


def draw_boxes(ax,result,vertical=False):
    j=2 if vertical else 1
    for b in result['boxes']:
        lo,hi=b['lower'],b['upper']
        ax.add_patch(Rectangle((lo[0],lo[j]),hi[0]-lo[0],hi[j]-lo[j],
                               fill=False,edgecolor='black',linewidth=.7))


def demo_figure(result,frame,path,cfg,dataset="data/kitti_mini"):
    fig,axes=plt.subplots(4,2,figsize=(12,12),layout='constrained')
    stages=[('Input ROI','roi'),('Voxel downsample','voxel'),
            ('Ground removed','non_ground'),('DBSCAN + AABB','non_ground')]
    for i,(name,key) in enumerate(stages):
        for j in range(2):
            scatter(axes[i,j],result[key],vertical=bool(j),labels=result['labels'] if i==3 else None)
            axes[i,j].set_title(f'{name}: {len(result[key]):,} points'+
                                (f", {len(result['boxes'])} clusters" if i==3 else ''))
            if i==3: draw_boxes(axes[i,j],result,bool(j))
    source='KITTI Vision Benchmark Suite' if 'kitti' in dataset else 'Provided synthetic dataset'
    fig.suptitle(f'{dataset} / {frame} | voxel={cfg.voxel} m, ground={cfg.threshold} m, eps={cfg.eps} m\n'
                 f'Left: BEV. Right: side view. Source: {source}')
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=150); plt.close(fig)


def demo(args):
    cfg=Config(voxel=args.voxel,threshold=args.threshold,eps=args.eps,min_points=args.min_points)
    rows=[]; boxes=[]
    for frame in args.frames:
        r=process(load_points(args.data_root,frame),cfg)
        rows.append({'frame_id':frame,**asdict(cfg),**r['metrics']})
        boxes.extend(box_rows(r,{'frame_id':frame}))
        demo_figure(r,frame,Path(args.out)/'figures'/f'demo_{frame}.png',cfg,args.data_root)
        print(frame,r['metrics'])
    write_csv(Path(args.out)/'baseline.csv',rows)
    if boxes: write_csv(Path(args.out)/'baseline_clusters.csv',boxes)
    (Path(args.out)/'baseline_config.json').write_text(json.dumps({'dataset':args.data_root,
        'frames':args.frames,'roi':{'x':[0,30],'y':[-10,10],'z':[-3,3]},
        'config':asdict(cfg),'plane_fit_threshold_m':.1,'max_ground_tilt_deg':15},indent=2))


def main():
    ap=argparse.ArgumentParser(description='Topic D: voxel/RANSAC/DBSCAN obstacle experiments')
    ap.add_argument('mode',choices=['demo'])
    ap.add_argument('--data-root',default='data/kitti_mini')
    ap.add_argument('--frames',nargs='+',default=FRAMES)
    ap.add_argument('--out',default='results')
    ap.add_argument('--voxel',type=float,default=.2)
    ap.add_argument('--threshold',type=float,default=.1)
    ap.add_argument('--eps',type=float,default=.6)
    ap.add_argument('--min-points',type=int,default=10)
    args=ap.parse_args()
    demo(args)

if __name__=='__main__': main()
