# regime_gate.py — apply gates to audit.csv to produce audit_regimes.csv
from __future__ import annotations
import csv, argparse, sys
from pathlib import Path
from common import load_json, try_float

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--audit", default="data/audit.csv")
    ap.add_argument("--out", default="data/audit_regimes.csv")
    args = ap.parse_args()

    root = Path(args.root)
    freeze = load_json(root / "freeze" / "freeze.json")
    theta_S = try_float(freeze.get("gates", {}).get("theta_S"))
    theta_C = try_float(freeze.get("gates", {}).get("theta_C"))
    theta_IC = try_float(freeze.get("gates", {}).get("theta_IC"))

    if theta_S is None or theta_C is None:
        print("Gates are symbolic or missing; writing 'unknown' regimes.", file=sys.stderr)

    audit_path = root / args.audit
    out_path = root / args.out

    with open(audit_path, newline="", encoding="utf-8") as f, open(out_path, "w", newline="", encoding="utf-8") as g:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames) + ["regime"]
        writer = csv.DictWriter(g, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            w = try_float(row.get("omega"))
            ic = try_float(row.get("IC"))
            regime = "unknown"
            if w is not None:
                if theta_C is not None and w >= theta_C:
                    regime = "Collapse"
                    if ic is not None and theta_IC is not None and ic < theta_IC:
                        regime = "CollapseCritical"
                elif theta_S is not None and w < theta_S:
                    # apply other caps only if present; otherwise still Stable by ω-only
                    regime = "Stable"
                elif theta_S is not None or theta_C is not None:
                    regime = "Watch"
            row["regime"] = regime
            writer.writerow(row)

    print(f"Wrote regimes to {out_path}")

if __name__ == "__main__":
    main()
