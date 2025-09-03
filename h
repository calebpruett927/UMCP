# weld_check.py — compute per-boundary weld checks and summary
from __future__ import annotations
import csv, argparse, math, sys, json
from pathlib import Path
from common import load_json, write_json, try_float, get_tolerances

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--audit", default="data/audit.csv")
    ap.add_argument("--out", default="weld/weld_report.json")
    args = ap.parse_args()

    root = Path(args.root)
    freeze = load_json(root / "freeze" / "freeze.json")
    tol = get_tolerances(freeze)

    eps_kappa = tol.get("eps_kappa", None)
    eps_U_abs = tol.get("eps_U_abs", None)
    eps_U_rel = tol.get("eps_U_rel", None)
    tau_min_hint = try_float(freeze.get("tolerances", {}).get("tau_min_hint")) or 0.0

    if eps_kappa is None or eps_U_abs is None or eps_U_rel is None:
        print("Tolerances are symbolic or missing; checks will be marked 'unknown'.", file=sys.stderr)

    audit_path = root / args.audit
    weld_path = root / args.out

    # load rows
    rows = []
    with open(audit_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            def num(k): return try_float(r.get(k))
            rows.append({
                "t": r.get("t"),
                "kappa": try_float(r.get("kappa")),
                "U": try_float(r.get("U")),
                "C": try_float(r.get("C")),
                "tau_R": try_float(r.get("tau_R")),
            })

    welds = []
    cum_jump = 0.0
    for i in range(len(rows)-1):
        L, R = rows[i], rows[i+1]
        kL, kR = L["kappa"], R["kappa"]
        UL, UR = L["U"], R["U"]
        CL, CR = L["C"], R["C"]
        tL, tR = L["tau_R"], R["tau_R"]

        kd = None if (kL is None or kR is None) else (kR - kL)
        Ud = None if (UL is None or UR is None) else (UR - UL)

        # pass flags
        pass_kappa = None if (eps_kappa is None or kd is None) else (abs(kd) <= eps_kappa)
        # U transport absolute/relative
        if Ud is None or eps_U_abs is None or eps_U_rel is None or UL is None or UR is None:
            pass_U = None
        else:
            cap = max(eps_U_abs, eps_U_rel * max(abs(UL), abs(UR)))
            pass_U = abs(Ud) <= cap

        # Lipschitz bound from EQ–008
        if CL is None or CR is None or tL is None or tR is None:
            pass_lip = None
            bound = None
        else:
            tau_min = max(tau_min_hint, min(tL, tR) if (tL is not None and tR is not None) else 0.0, 0.0)
            Cmax = max(abs(CL), abs(CR))
            bound = (abs((CR-CL) if (CR is not None and CL is not None) else 0.0) / (1.0 + tau_min)) + (Cmax * abs((tR - tL) if (tR is not None and tL is not None) else 0.0) / ((1.0 + tau_min)**2))
            if Ud is None:
                pass_lip = None
            else:
                pass_lip = abs(Ud) <= bound

        welds.append({
            "boundary_index": i,
            "t_L": rows[i]["t"],
            "t_R": rows[i+1]["t"],
            "kappa_L": kL, "kappa_R": kR, "kappa_delta": kd,
            "U_L": UL, "U_R": UR, "U_delta": Ud,
            "C_L": CL, "C_R": CR,
            "tau_L": tL, "tau_R": tR,
            "pass_kappa": pass_kappa,
            "pass_U": pass_U,
            "pass_lip": pass_lip,
            "lip_bound": bound
        })
        if kd is not None:
            cum_jump += abs(kd)

    m = len(welds)
    summary = {
        "m": m,
        "eps_kappa": eps_kappa,
        "cum_kappa_jump": cum_jump,
        "bound": None if eps_kappa is None else (m * eps_kappa),
        "pass": None if (eps_kappa is None) else (cum_jump <= m * eps_kappa)
    }
    out = {"spec_version": 1, "generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
           "tolerances": tol, "welds": welds, "summary": summary}
    write_json(Path(weld_path), out)
    print(f"Weld report written to {weld_path} with m={m}")

if __name__ == "__main__":
    main()
