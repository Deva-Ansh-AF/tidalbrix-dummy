"""
TidalBrix Dummy Worker
======================
Mirrors the real worker container behaviour:
  - Starts up, prints status
  - Simulates each processing step with a sleep
  - Exits cleanly

Real worker steps (from worker.py):
  1. Connecting to data folder
  2. Scanning .nc files
  3. Loading NetCDF data
  4. Processing tide/surge values
  5. Generating statistics
  6. Saving processed results
  7. Updating database metadata

This dummy does the same steps but just sleeps + prints — 
no actual files, no DB connection, no NetCDF parsing.
"""

import time
import os
from datetime import datetime

DELAY = int(os.environ.get("STEP_DELAY_SECONDS", "5"))

def banner(msg):
    width = 50
    print("=" * width)
    print(f"  {msg}")
    print("=" * width)

banner("TidalBrix Dummy Worker Starting")
print(f"Start Time : {datetime.utcnow().isoformat()} UTC")
print(f"Container  : {os.environ.get('HOSTNAME', 'unknown')}")
print(f"Step Delay : {DELAY}s (set STEP_DELAY_SECONDS to change)")
print()

steps = [
    ("Connecting to data folder",       "Checking /data mount... (dummy: no real mount needed)"),
    ("Scanning .nc files",              "Found 0 NetCDF files (dummy mode — no real files)"),
    ("Loading NetCDF data",             "Skipped — using mock data structures"),
    ("Processing tide/surge values",    "Running dummy tide calculation (sin wave)"),
    ("Generating statistics",           "min=-1.5m  max=+1.87m  mean=0.02m  (dummy values)"),
    ("Saving processed results",        "Would write to /data/*.parquet — skipped in dummy mode"),
    ("Updating database metadata",      "Would INSERT into tidalbrix.cache_log — skipped"),
]

for i, (step, detail) in enumerate(steps, 1):
    print(f"[WORKER] [{i}/{len(steps)}] {step}...", flush=True)
    time.sleep(DELAY)
    print(f"         → {detail}", flush=True)
    print()

banner("Worker Task Completed Successfully")
print(f"End Time: {datetime.utcnow().isoformat()} UTC")
print()
print("In the real app this container would:")
print("  • Read FES2022 tide model files from a volume mount")
print("  • Fetch metocean data from Copernicus Marine (CMEMS)")
print("  • Write Parquet cache files")
print("  • Update PostgreSQL via psycopg2")
