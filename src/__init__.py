"""Student obstacle experiments; set thread count before importing Open3D."""
import os
from pathlib import Path
os.environ['OMP_NUM_THREADS'] = '1'
os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1] / '.venv' / 'mplcache'))
