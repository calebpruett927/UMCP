#!/usr/bin/env python3
"""Collapse Calculus step validator (transport + weld).

This utility checks that consecutive *audit rows* respect the transport identity
and κ-continuity (weld) conditions of the UMCP/Collapse Calculus kernel.

For each pair of rows (t, t+1) it:
  • chooses a face ("normal" or "exact") for the drift/integrity map,
  • transports the curvature payload U := C/(1+τ_R) via a **secant** rate Γ,
  • computes residuals rT := U_{t+1} − U_pred and rW := κ_{t+1} − κ_t,
  • emits pass/fail flags against tolerances.

Defaults follow the published tolerances and kernel constants (p=3, ε=1e−8, α=1)
while remaining fully overrideable from the CLI.

CSV requirements (per audit row):
  - Required numeric fields: omega, C, tau_R, and either kappa or IC.
  - Optional: guard_on (one of {0,1,true,True,TRUE}).
  - Rows must be time-sorted prior to validation.

Example
-------
$ python collapse_validate.py --csv umcp_full_audit.csv \
    --alpha 1 --eps 1e-8 --p 3 --tolT 1e-9 --tolW 1e-12 --pivot 0.99 \
    --out report.csv

Output schema (one row per transition):
  idx,omega_n,omega_np1,face_n,face_np1,U_n,U_np1,U_pred,rT,rW,okT,okW
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from typing import Dict, Iterable, Tuple

# ----------------------------- Face potentials -----------------------------

def phi(omega: float, eps: float, p: float, face: str) -> float:
    """Face potential Φ(ω).

    Parameters
    ----------
    omega : float
        Drift magnitude (ω ∈ [0,1)).
    eps : float
        Small ε used on the exact face near the wall.
    p : float
        Order for the normal face potential (canonical p=3).
    face : {"normal","exact"}
        Active face selection.
    """
    if face == "exact":
        # Exact product face (finite-wall counterpart): 2 ln(1-ω) + ln(1-ω+ε)
        return (
            2.0 * math.log(max(1.0 - omega, 1e-300))
            + math.log(max(1.0 - omega + eps, 1e-300))
        )
    # Normal (canonical) face: p ln(1-ω)
    return p * math.log(max(1.0 - omega, 1e-300))


def gamma_pointwise(omega: float, eps: float, p: float, face: str) -> float:
    """Pointwise tangent rate Γ(ω) on the active face."""
    if face == "exact":
        return 2.0 / (1.0 - omega) + 1.0 / (1.0 - omega + eps)
    return p / (1.0 - omega)


def gamma_secant(om_minus: float, om_plus: float, eps: float, p: float, face: str) -> float:
    """Secant rate Γ across [ω_n, ω_{n+1}] on a *fixed* face.

    Falls back to the pointwise tangent if Δω is below machine scale.
    """
    d_om = om_plus - om_minus
    if abs(d_om) < 1e-15:
        return gamma_pointwise(om_minus, eps, p, face)
    num = phi(om_minus, eps, p, face) - phi(om_plus, eps, p, face)
    return num / d_om


# ----------------------------- Policy helpers ------------------------------

def choose_face(omega: float, guard_on: bool, eps: float, pivot: float) -> str:
    """Select the active face for a given drift value and guard flag.

    Policy: choose the **exact** face when the guardband is engaged OR when
    ω ≥ pivot (near-wall). Otherwise stay on the **normal** face.
    """
    return "exact" if (guard_on or omega >= pivot) else "normal"


def transport_update_U(
    U_n: float, om_n: float, om_np1: float, alpha: float, eps: float, p: float, face: str
) -> float:
    """Transport the curvature payload U across one step using a secant Γ."""
    Gam = gamma_secant(om_n, om_np1, eps, p, face)
    return U_n - (1.0 / alpha) * Gam * (om_np1 - om_n)


# ------------------------------ Core validator -----------------------------

def _to_bool_flag(s: str) -> bool:
    return str(s).strip() in {"1", "true", "True", "TRUE"}


def _row_fields(row: Dict[str, str]) -> Tuple[float, float, float, float, float]:
    """Extract (ω, C, τ_R, κ, U) from a CSV row; raises ValueError on missing/NaN."""
    om = float(row["omega"])  # drift
    C = float(row["C"])       # curvature
    tau = float(row["tau_R"]) # re-entry delay
    # Prefer κ if present, otherwise compute from IC (κ = ln IC).
    if "kappa" in row and row["kappa"] != "" and row["kappa"] is not None:
        kappa = float(row["kappa"])
    else:
        ic = float(row["IC"])
        # Guard IC ∈ (0,1]; clip to avoid -inf if someone passes IC=0 numerically.
        ic = min(max(ic, 1e-300), 1.0)
        kappa = math.log(ic)
    U = C / (1.0 + tau)
    return om, C, tau, kappa, U


def validate_step(
    row_n: Dict[str, str],
    row_np1: Dict[str, str],
    alpha: float,
    eps: float,
    p: float,
    tolT: float,
    tolW: float,
    pivot: float,
) -> Dict[str, float]:
    """Validate transport and weld invariants for a single (n → n+1) step.

    Returns a small dict with inputs, faces, prediction, residuals, and pass flags.
    """
    om_n, C_n, tau_n, k_n, U_n = _row_fields(row_n)
    om_np1, C_np1, tau_np1, k_np1, U_np1 = _row_fields(row_np1)

    guard_n = _to_bool_flag(row_n.get("guard_on", "0"))
    guard_np1 = _to_bool_flag(row_np1.get("guard_on", "0"))

    face_n = choose_face(om_n, guard_n, eps, pivot)
    face_np1 = choose_face(om_np1, guard_np1, eps, pivot)

    # If faces differ across the step, attempt a split at ω=pivot; otherwise single-face update.
    if face_n != face_np1:
        om_mid = pivot
        # If pivot lies outside [ω_n, ω_{n+1}], fall back to single-face transport on the left face.
        if not (min(om_n, om_np1) <= om_mid <= max(om_n, om_np1)):
            U_pred = transport_update_U(U_n, om_n, om_np1, alpha, eps, p, face_n)
        else:
            U_mid = transport_update_U(U_n, om_n, om_mid, alpha, eps, p, face_n)
            U_pred = transport_update_U(U_mid, om_mid, om_np1, alpha, eps, p, face_np1)
    else:
        U_pred = transport_update_U(U_n, om_n, om_np1, alpha, eps, p, face_n)

    rT = U_np1 - U_pred          # transport residual
    rW = k_np1 - k_n              # weld (κ) residual
    okT = float(abs(rT) <= tolT)
    okW = float(abs(rW) <= tolW)

    return {
        "omega_n": om_n,
        "omega_np1": om_np1,
        "face_n": face_n,
        "face_np1": face_np1,
        "U_n": U_n,
        "U_np1": U_np1,
        "U_pred": U_pred,
        "rT": rT,
        "rW": rW,
        "okT": okT,
        "okW": okW,
    }


# ----------------------------------- CLI -----------------------------------

def _iter_rows(path: str) -> Iterable[Dict[str, str]]:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Validate UMCP/Collapse Calculus transport (U) and weld (κ) over an audit CSV"
    )
    ap.add_argument("--csv", required=True, help="Audit CSV sorted by time (with omega,C,tau_R,kappa|IC)" )
    ap.add_argument("--alpha", type=float, default=1.0, help="Transport coefficient α used in the update" )
    ap.add_argument("--eps", type=float, default=1e-8, help="Small epsilon for the exact face potential" )
    ap.add_argument("--p", type=float, default=3.0, help="Order of the normal face potential (canonical p=3)" )
    ap.add_argument("--tolT", type=float, default=1e-9, help="Tolerance for transport residual |U_pred − U|" )
    ap.add_argument("--tolW", type=float, default=1e-12, help="Tolerance for weld residual |κ_{t+1} − κ_t|" )
    ap.add_argument("--pivot", type=float, default=0.99, help="Drift ω threshold to pivot to the exact face" )
    ap.add_argument("--out", default="-", help="Output CSV path or '-' for stdout" )
    args = ap.parse_args()

    rows = list(_iter_rows(args.csv))
    if len(rows) < 2:
        sys.exit("need at least two rows in the audit CSV")

    out_fp = sys.stdout if args.out == "-" else open(args.out, "w", newline="")
    writer = csv.DictWriter(
        out_fp,
        fieldnames=[
            "idx","omega_n","omega_np1","face_n","face_np1",
            "U_n","U_np1","U_pred","rT","rW","okT","okW",
        ],
    )
    writer.writeheader()

    passes_T = 0
    passes_W = 0
    total = len(rows) - 1
    for i in range(total):
        res = validate_step(rows[i], rows[i+1], args.alpha, args.eps, args.p, args.tolT, args.tolW, args.pivot)
        res_with_idx = {"idx": i, **res}
        writer.writerow(res_with_idx)
        passes_T += int(res["okT"] == 1.0)
        passes_W += int(res["okW"] == 1.0)

    if out_fp is not sys.stdout:
        out_fp.close()

    print(f"# summary: transport_pass={passes_T}/{total}  weld_pass={passes_W}/{total}", file=sys.stderr)


if __name__ == "__main__":
    main()
