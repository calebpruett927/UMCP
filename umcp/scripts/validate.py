#!/usr/bin/env python3
"""
UMCP Validation Script

Command-line interface for validating UMCP transport and weld invariants.
"""

import argparse
import csv
import sys
from typing import List, Dict, Any

import umcp


def load_csv_data(csv_path: str) -> List[Dict[str, str]]:
    """Load data from CSV file."""
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def main():
    """Main entry point for validation script."""
    parser = argparse.ArgumentParser(
        description="Validate UMCP/Collapse Calculus transport (U) and weld (κ) over an audit CSV"
    )
    parser.add_argument("--csv", required=True, 
                       help="Audit CSV sorted by time (with omega,C,tau_R,kappa|IC)")
    parser.add_argument("--alpha", type=float, default=1.0, 
                       help="Transport coefficient α used in the update")
    parser.add_argument("--eps", type=float, default=1e-8, 
                       help="Small epsilon for the exact face potential")
    parser.add_argument("--p", type=float, default=3.0, 
                       help="Order of the normal face potential (canonical p=3)")
    parser.add_argument("--tolT", type=float, default=1e-9, 
                       help="Tolerance for transport residual |U_pred − U|")
    parser.add_argument("--tolW", type=float, default=1e-12, 
                       help="Tolerance for weld residual |κ_{t+1} − κ_t|")
    parser.add_argument("--pivot", type=float, default=0.99, 
                       help="Drift ω threshold to pivot to the exact face")
    parser.add_argument("--out", default="-", 
                       help="Output CSV path or '-' for stdout")
    
    args = parser.parse_args()

    # Load data
    try:
        rows = load_csv_data(args.csv)
    except Exception as e:
        sys.stderr.write(f"Error loading CSV: {e}\n")
        sys.exit(1)

    if len(rows) < 2:
        sys.stderr.write("Error: need at least two rows in the audit CSV\n")
        sys.exit(1)

    # Validate sequence
    try:
        results, summary = umcp.validate_sequence(
            rows,
            alpha=args.alpha,
            eps=args.eps,
            p=args.p,
            tolT=args.tolT,
            tolW=args.tolW,
            pivot=args.pivot
        )
    except Exception as e:
        sys.stderr.write(f"Validation error: {e}\n")
        sys.exit(1)

    # Write output
    if args.out == "-":
        out_fp = sys.stdout
    else:
        try:
            out_fp = open(args.out, "w", newline="")
        except Exception as e:
            sys.stderr.write(f"Error opening output file: {e}\n")
            sys.exit(1)

    try:
        fieldnames = [
            "idx", "omega_n", "omega_np1", "face_n", "face_np1",
            "U_n", "U_np1", "U_pred", "rT", "rW", "okT", "okW",
        ]
        writer = csv.DictWriter(out_fp, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow(result)
            
    finally:
        if out_fp is not sys.stdout:
            out_fp.close()

    # Print summary to stderr
    sys.stderr.write(
        f"# summary: transport_pass={summary['transport_pass']}/{summary['total_steps']}  "
        f"weld_pass={summary['weld_pass']}/{summary['total_steps']}\n"
    )


if __name__ == "__main__":
    main()