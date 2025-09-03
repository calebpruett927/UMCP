# face_parity_certificate.py — certify a vs b aggregates parity bound
from __future__ import annotations
import csv, argparse, math, json, sys
from pathlib import Path
from common import load_json, try_float, get_tolerances

def read_series(path: Path, col: str) -> list:
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            v = try_float(row.get(col))
            out.append(v)
    return out

def mean(xs):
    vals = [x for x in xs if x is not None]
    return sum(vals)/len(vals) if vals else None

def hoeffding_ci_width(N, alpha):
    if N <= 0: return None
    return math.sqrt(math.log(2.0/alpha)/(2.0*N))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--a", default="data/audit_a.csv", help="a-face audit CSV")
    ap.add_argument("--b", default="data/audit_b.csv", help="b-face audit CSV")
    ap.add_argument("--col", default="omega", help="column to compare (default: omega)")
    ap.add_argument("--L", type=float, default=1.0, help="Lipschitz constant for g in omega")
    ap.add_argument("--alpha", type=float, default=0.05, help="two-sided failure prob for CI")
    ap.add_argument("--weld_report", default="weld/weld_report.json", help="optional weld report to include m*eps/N term (for kappa only)")
    ap.add_argument("--out", default="render/face_parity_certificate.json")
    args = ap.parse_args()

    root = Path(args.root)
    A = root / args.a
    B = root / args.b

    if not A.exists() or not B.exists():
        print("Need both a-face and b-face audit CSVs; create them first.", file=sys.stderr)
        sys.exit(2)

    va = read_series(A, args.col)
    vb = read_series(B, args.col)
    N = min(len([x for x in va if x is not None]), len([x for x in vb if x is not None]))

    diffs = []
    r_oor = 0
    for x, y in zip(va, vb):
        if x is None or y is None: continue
        diffs.append(abs(y - x))
        if abs(y - x) > 1e-12:
            r_oor += 1
    r_oor = r_oor / N if N > 0 else None

    m_eps_over_N = 0.0
    weld_json = root / args.weld_report
    if weld_json.exists() and args.col == "kappa":
        wr = json.loads(weld_json.read_text(encoding="utf-8"))
        m = wr.get("summary", {}).get("m")
        eps = wr.get("summary", {}).get("eps_kappa")
        if isinstance(m, int) and isinstance(eps, (int,float)) and N > 0:
            m_eps_over_N = (m * eps) / N

    ci = hoeffding_ci_width(N, args.alpha) if N else None

    bound = None
    if r_oor is not None and ci is not None:
        bound = args.L * r_oor + m_eps_over_N + ci

    out = {
        "column": args.col,
        "N": N,
        "L": args.L,
        "alpha": args.alpha,
        "r_oor": r_oor,
        "m_eps_over_N": m_eps_over_N,
        "ci_width": ci,
        "parity_bound": bound,
        "notes": "Bound: |mean_b - mean_a| <= L*r_oor + m*eps_kappa/N (kappa only) + CI(N,alpha)"
    }
    (root / args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote parity certificate to {root / args.out}")

if __name__ == "__main__":
    main()
