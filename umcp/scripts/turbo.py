#!/usr/bin/env python3
"""
UMCP Turbo Script

High-performance compatibility harness for UMCP computations with SPC overlays.
"""

import argparse
import csv
import time
import sys
from collections import deque

import umcp


def clip01(u):
    """Clip value to [0, 1] range."""
    return 0.0 if u < 0.0 else (1.0 if u > 1.0 else u)


def compute_spc_overlays(y_series, sigma=1.0):
    """Compute SPC (Statistical Process Control) overlays."""
    shewhart_flags = []
    ewma = []
    ewma_flags = []
    cusum_pos = []
    cusum_neg = []
    cusum_flags = []
    
    # EWMA parameters
    lam = 0.2
    z = None
    
    # CUSUM parameters
    k = 0.5 * sigma
    h = 5.0 * sigma
    
    for i, y_i in enumerate(y_series):
        # Shewhart 3σ control
        shewhart_flags.append(abs(y_i) > 3 * sigma)
        
        # EWMA
        if z is None:
            z = y_i
        else:
            z = lam * y_i + (1 - lam) * z
        ewma.append(z)
        
        # EWMA control limit
        L = 3.0
        sigma_z = sigma * (lam / (2.0 - lam)) ** 0.5
        ewma_flags.append(abs(z) > L * sigma_z)
        
        # CUSUM
        cp = max(0.0, (y_i - k) + (cusum_pos[-1] if cusum_pos else 0.0))
        cn = max(0.0, (-y_i - k) + (cusum_neg[-1] if cusum_neg else 0.0))
        cusum_pos.append(cp)
        cusum_neg.append(cn)
        cusum_flags.append(cp > h or cn > h)
    
    return {
        'shewhart_flags': shewhart_flags,
        'ewma': ewma,
        'ewma_flags': ewma_flags,
        'cusum_pos': cusum_pos,
        'cusum_neg': cusum_neg,
        'cusum_flags': cusum_flags
    }


def main():
    """Main entry point for turbo script."""
    parser = argparse.ArgumentParser(
        description="Turbo-Compat Harness: Fast UMCP computation with SPC overlays"
    )
    parser.add_argument("--csv", required=True, help="Input CSV with t,x_raw,a,b (b>0)")
    parser.add_argument("--out", default="turbo_compat_audit.csv", help="Output CSV path")
    parser.add_argument("--sigma", type=float, default=1.0, 
                       help="Standard deviation for SPC synthetic baseline")
    
    args = parser.parse_args()

    # Load data
    try:
        with open(args.csv, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        sys.stderr.write(f"Error loading CSV: {e}\n")
        sys.exit(1)

    if not rows:
        sys.stderr.write("Error: CSV file is empty\n")
        sys.exit(1)

    # Start timing
    t0 = time.time()

    # Extract data
    try:
        x_raw = [float(row["x_raw"]) for row in rows]
        a_vals = [float(row["a"]) for row in rows]
        b_vals = [float(row["b"]) for row in rows]
    except (KeyError, ValueError) as e:
        sys.stderr.write(f"Error parsing CSV data: {e}\n")
        sys.exit(1)

    # Use first values for normalization (assuming frozen parameters)
    a, b = a_vals[0], b_vals[0]
    
    if b <= 0:
        sys.stderr.write(f"Error: b parameter must be positive, got {b}\n")
        sys.exit(1)

    # Compute UMCP invariants
    try:
        results = umcp.compute_invariants(x_raw, a, b)
    except Exception as e:
        sys.stderr.write(f"Error computing invariants: {e}\n")
        sys.exit(1)

    # Extract y series for SPC
    y_series = [r['y'] for r in results]
    
    # Compute SPC overlays
    spc = compute_spc_overlays(y_series, args.sigma)

    # End timing
    t1 = time.time()
    elapsed_ms = (t1 - t0) * 1000.0

    # Write output
    try:
        with open(args.out, "w", newline="") as f:
            fieldnames = [
                "t", "x_raw", "a", "b", "y", "xhat", "omega", "F", "S", "C", 
                "tau_R", "IC", "kappa", "regime", "shewhart_flag", "ewma_flag", "cusum_flag"
            ]
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            
            for i, (row, result) in enumerate(zip(rows, results)):
                writer.writerow([
                    row.get("t", i),
                    result['x_raw'],
                    a_vals[i],
                    b_vals[i],
                    result['y'],
                    result['xhat'],
                    result['omega'],
                    result['F'],
                    result['S'],
                    result['C'],
                    result['tau_R'],
                    result['IC'],
                    result['kappa'],
                    result['regime'],
                    int(spc['shewhart_flags'][i]),
                    int(spc['ewma_flags'][i]),
                    int(spc['cusum_flags'][i])
                ])
    except Exception as e:
        sys.stderr.write(f"Error writing output: {e}\n")
        sys.exit(1)

    print(f"Turbo-Compat run complete in {elapsed_ms:.2f} ms over {len(rows)} rows. "
          f"(Identities: κ, U, weld-ready)")


if __name__ == "__main__":
    main()