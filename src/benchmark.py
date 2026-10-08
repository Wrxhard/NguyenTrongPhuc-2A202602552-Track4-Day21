"""Independent sweeps with real timing; geometry checked on every repeat."""
import argparse
from dataclasses import asdict
from pathlib import Path
import hashlib
import json
import platform
import time
import numpy as np
import matplotlib.pyplot as plt
from starter.datasets import load_points
from src.obstacle import Config,process
from src.experiments import FRAMES,write_csv,box_rows


def configurations():
    return [('ground',t,Config(threshold=t)) for t in [.1,.2,.3]] + [
            ('voxel',v,Config(voxel=v)) for v in [.1,.2,.4]]


def latency_stats(samples):
    if len(samples)<20: raise ValueError('At least 20 measured repetitions required')
    return tuple(float(v) for v in np.percentile(samples,[50,95]))


def claim_drop(baseline,changed):
    a,b=np.mean(baseline),np.mean(changed)
    return float(100*(a-b)/a) if a>0 else np.nan


def fingerprint(r):
    h=hashlib.sha256()
    for key in ['voxel','ground','non_ground','labels','plane']:
        h.update(np.asarray(r[key]).tobytes())
    return h.hexdigest()


def hardware():
    cpu=platform.processor()
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            cpu=winreg.QueryValueEx(key,'ProcessorNameString')[0]
    except (ImportError,OSError): pass
    import open3d
    return {'cpu':cpu,'os':platform.platform(),'python':platform.python_version(),
            'numpy':np.__version__,'open3d':open3d.__version__,'device':'CPU',
            'open3d_max_threads':open3d.utility.get_max_threads(), 'ransac_probability':1.0}


def run_benchmark(root,out,frames,repeats=20):
    if repeats<20: raise ValueError('repeats must be >=20')
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    rows=[]; timed=[]; boxes=[]; reference={}
    points={f:load_points(root,f) for f in frames}
    for fid in frames:
        r=process(points[fid],Config())
        if not r['metrics']['ground_valid']: raise RuntimeError('Invalid reference ground: '+fid)
        reference[fid]=r['plane']
    for sweep,value,cfg in configurations():
        for fid in frames:
            plane=reference[fid] if sweep=='ground' else None
            warm=process(points[fid],cfg,plane=plane)
            digest=fingerprint(warm)
            samples=[]
            for repeat in range(repeats):
                start=time.perf_counter_ns()
                r=process(points[fid],cfg,plane=plane)
                ms=(time.perf_counter_ns()-start)/1e6
                if fingerprint(r)!=digest: raise RuntimeError('Non-deterministic geometry '+fid)
                samples.append(ms)
                timed.append(dict(sweep=sweep,value=value,frame_id=fid,repeat=repeat+1,
                                  latency_ms=ms))
            p50,p95=latency_stats(samples)
            extra=dict(sweep=sweep,value=value,frame_id=fid)
            rows.append({**extra,**asdict(cfg),**warm['metrics'],
                         'latency_p50_ms':p50,'latency_p95_ms':p95,
                         'geometry_sha256':digest})
            boxes.extend(box_rows(warm,extra))
            print(sweep,value,fid,warm['metrics']['n_non_ground'],warm['metrics']['n_clusters'],flush=True)
    summaries=[]
    for sweep,value,cfg in configurations():
        subset=[r for r in rows if r['sweep']==sweep and r['value']==value]
        times=[r['latency_ms'] for r in timed if r['sweep']==sweep and r['value']==value]
        p50,p95=latency_stats(times)
        summaries.append(dict(sweep=sweep,value=value,voxel=cfg.voxel,threshold=cfg.threshold,
             n_frames=len(subset),mean_non_ground=float(np.mean([r['n_non_ground'] for r in subset])),
             mean_clusters=float(np.mean([r['n_clusters'] for r in subset])),
             mean_nearest_m=float(np.nanmean([r['nearest_m'] for r in subset])),
             latency_p50_ms=p50,latency_p95_ms=p95,n_timed=len(times)))
    low=[r['n_non_ground'] for r in rows if r['sweep']=='ground' and r['value']==.1]
    high=[r['n_non_ground'] for r in rows if r['sweep']=='ground' and r['value']==.3]
    drop=claim_drop(low,high)
    metadata={'hardware':hardware(),'dataset':root,'frames':frames,'seed':42,
         'repeats_per_frame_config':repeats,'warmups_per_frame_config':1,
         'roi':{'x':[0,30],'y':[-10,10],'z':[-3,3]},
         'fixed_planes':{f:reference[f].tolist() for f in frames},
         'timing_scope':{'ground':'filter + voxel + fixed-plane classification + DBSCAN + AABB; reference fit excluded',
                         'voxel':'filter + voxel + RANSAC fit + classification + DBSCAN + AABB'},
         'excluded':'I/O, imports, plot, CSV writing, repeat fingerprint checks',
         'claim_drop_pct':drop,'claim_supported':bool(drop>=10)}
    write_csv(out/'obstacle_sweep.csv',rows)
    write_csv(out/'obstacle_summary.csv',summaries)
    write_csv(out/'latency_samples.csv',timed)
    write_csv(out/'sweep_clusters.csv',boxes)
    (out/'benchmark_config.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    fig,axes=plt.subplots(2,3,figsize=(14,7),layout='constrained')
    for i,sweep in enumerate(['ground','voxel']):
        subset=[r for r in summaries if r['sweep']==sweep]; x=[r['value'] for r in subset]
        for j,(metric,title) in enumerate([('mean_non_ground','Mean non-ground points'),
                                         ('mean_clusters','Mean cluster count'),
                                         ('latency_p95_ms','Pooled latency p95 (ms)')]):
            axes[i,j].plot(x,[r[metric] for r in subset],'-o')
            axes[i,j].set(xlabel=sweep+' size/threshold (m)',ylabel=title,xticks=x)
            axes[i,j].grid(alpha=.3)
    fig.suptitle(f'5 KITTI frames | two independent sweeps | seed 42 | claim drop={drop:.2f}%'+
                 '\nGround timing excludes fixed reference fit; voxel timing includes fit. CPU / Open3D threads=1.')
    (out/'figures').mkdir(exist_ok=True)
    fig.savefig(out/'figures'/'obstacle_sweep.png',dpi=160); plt.close(fig)
    print('CLAIM',drop,metadata['claim_supported'],flush=True)
    return rows,summaries,metadata


def main():
    ap=argparse.ArgumentParser(description='Ground and voxel sweeps, warm-up +20 latency repeats')
    ap.add_argument('--data-root',default='data/kitti_mini')
    ap.add_argument('--frames',nargs='+',default=FRAMES)
    ap.add_argument('--out',default='results')
    ap.add_argument('--repeats',type=int,default=20)
    args=ap.parse_args()
    run_benchmark(args.data_root,args.out,args.frames,args.repeats)

if __name__=='__main__': main()
