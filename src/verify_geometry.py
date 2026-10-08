"""Verify saved CP3 geometry against a fresh run without remeasuring latency."""
import argparse
import csv
import json
from pathlib import Path
from starter.datasets import load_points
from src.obstacle import Config,process
from src.benchmark import fingerprint


def verify(results):
    path=Path(results)
    metadata=json.loads((path/'benchmark_config.json').read_text(encoding='utf-8'))
    with (path/'obstacle_sweep.csv').open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    points={fid:load_points(metadata['dataset'],fid) for fid in metadata['frames']}
    # Recompute reference fits, rather than trusting the saved planes.
    reference={fid:process(p,Config())['plane'] for fid,p in points.items()}
    for row in rows:
        cfg=Config(voxel=float(row['voxel']),threshold=float(row['threshold']),
                   eps=float(row['eps']),min_points=int(row['min_points']),
                   seed=int(row['seed']),iterations=int(row['iterations']))
        plane=reference[row['frame_id']] if row['sweep']=='ground' else None
        result=process(points[row['frame_id']],cfg,plane=plane)
        if fingerprint(result)!=row['geometry_sha256']:
            raise AssertionError(f'Geometry mismatch {row["sweep"]}/{row["value"]}/{row["frame_id"]}')
    print(f'PASS: {len(rows)} frame/configuration geometries match exactly; latency not compared.')


def main():
    ap=argparse.ArgumentParser(description='Reproduce CP3 geometry and compare hashes')
    ap.add_argument('--results',default='results')
    verify(ap.parse_args().results)

if __name__=='__main__': main()
