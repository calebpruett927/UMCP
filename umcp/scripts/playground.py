#!/usr/bin/env python3
"""
UMCP Playground Script

Interactive what-if tool for tuning UMCP parameters and analyzing time series data.
"""

import argparse
import sys

import umcp


def main():
    """Main entry point for playground script."""
    parser = argparse.ArgumentParser(description='UMCP Playground: Interactive parameter tuning tool')
    parser.add_argument('--csv', required=True, help='CSV file with data')
    parser.add_argument('--channel', required=True, help='Column name for the data')
    parser.add_argument('--a', type=float, required=True, help='Frozen intercept (a)')
    parser.add_argument('--b', type=float, required=True, help='Frozen scale (b)')
    parser.add_argument('--epsilon', type=float, default=1e-8, help='Small epsilon for entropy calculation')
    parser.add_argument('--K', type=int, default=3, help='Curvature window length')
    parser.add_argument('--alpha', type=float, default=1.0, help='Transport coefficient')
    parser.add_argument('--out-dir', default='playground_out', help='Output directory')
    
    args = parser.parse_args()

    try:
        # Run playground analysis
        report_path = umcp.playground_analysis(
            csv_path=args.csv,
            channel=args.channel,
            a=args.a,
            b=args.b,
            epsilon=args.epsilon,
            K=args.K,
            alpha=args.alpha,
            out_dir=args.out_dir
        )
        print(f"Analysis complete. Report saved to: {report_path}")
        
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: File not found - {e}\n")
        sys.exit(1)
    except ValueError as e:
        sys.stderr.write(f"Error: Invalid data - {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error during analysis: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()