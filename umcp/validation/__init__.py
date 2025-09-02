"""
Validation module for UMCP Collapse Calculus.

This module provides validation functions for:
- Transport invariant validation
- Weld continuity checking
- Step-by-step sequence validation
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from ..core import phi, gamma_secant, gamma_pointwise, DEFAULT_EPS, DEFAULT_P, DEFAULT_ALPHA


def choose_face(omega: float, guard_on: bool = False, eps: float = DEFAULT_EPS, 
               pivot: float = 0.99) -> str:
    """
    Select the active face for a given drift value and guard flag.

    Policy: choose the **exact** face when the guardband is engaged OR when
    ω ≥ pivot (near-wall). Otherwise stay on the **normal** face.
    
    Parameters
    ----------
    omega : float
        Drift value
    guard_on : bool
        Whether guard band is active
    eps : float
        Small epsilon parameter
    pivot : float
        Pivot threshold for face selection
        
    Returns
    -------
    str
        Face selection: "exact" or "normal"
    """
    return "exact" if (guard_on or omega >= pivot) else "normal"


def transport_update_U(U_n: float, om_n: float, om_np1: float, 
                      alpha: float = DEFAULT_ALPHA, eps: float = DEFAULT_EPS, 
                      p: float = DEFAULT_P, face: str = "normal") -> float:
    """
    Transport the curvature payload U across one step using a secant Γ.
    
    Parameters
    ----------
    U_n : float
        Current U value
    om_n : float
        Current omega
    om_np1 : float
        Next omega
    alpha : float
        Transport coefficient
    eps : float
        Small epsilon
    p : float
        Face potential order
    face : str
        Face type ("normal" or "exact")
        
    Returns
    -------
    float
        Predicted U value
    """
    Gam = gamma_secant(om_n, om_np1, eps, p, face)
    return U_n - (1.0 / alpha) * Gam * (om_np1 - om_n)


def validate_step(row_n: Dict[str, Any], row_np1: Dict[str, Any],
                 alpha: float = DEFAULT_ALPHA, eps: float = DEFAULT_EPS, 
                 p: float = DEFAULT_P, tolT: float = 1e-9, tolW: float = 1e-12,
                 pivot: float = 0.99) -> Dict[str, Any]:
    """
    Validate transport and weld invariants for a single (n → n+1) step.

    Parameters
    ----------
    row_n : Dict[str, Any]
        Current step data with omega, C, tau_R, kappa/IC fields
    row_np1 : Dict[str, Any]
        Next step data
    alpha : float
        Transport coefficient α used in the update
    eps : float
        Small epsilon for the exact face potential
    p : float
        Order of the normal face potential (canonical p=3)
    tolT : float
        Tolerance for transport residual |U_pred − U|
    tolW : float
        Tolerance for weld residual |κ_{t+1} − κ_t|
    pivot : float
        Drift ω threshold to pivot to the exact face

    Returns
    -------
    Dict[str, Any]
        Validation results with inputs, faces, prediction, residuals, and pass flags
    """
    # Extract fields from current step
    om_n = float(row_n["omega"])
    C_n = float(row_n["C"])
    tau_n = float(row_n["tau_R"])
    
    # Handle kappa vs IC
    if "kappa" in row_n and row_n["kappa"] not in ("", None):
        k_n = float(row_n["kappa"])
    else:
        ic = float(row_n["IC"])
        ic = min(max(ic, 1e-300), 1.0)  # Guard against log(0)
        k_n = math.log(ic)
    
    U_n = C_n / (1.0 + tau_n)

    # Extract fields from next step
    om_np1 = float(row_np1["omega"])
    C_np1 = float(row_np1["C"])
    tau_np1 = float(row_np1["tau_R"])
    
    if "kappa" in row_np1 and row_np1["kappa"] not in ("", None):
        k_np1 = float(row_np1["kappa"])
    else:
        ic = float(row_np1["IC"])
        ic = min(max(ic, 1e-300), 1.0)
        k_np1 = math.log(ic)
    
    U_np1 = C_np1 / (1.0 + tau_np1)

    # Guard flags
    guard_n = _to_bool_flag(row_n.get("guard_on", "0"))
    guard_np1 = _to_bool_flag(row_np1.get("guard_on", "0"))

    # Face selection
    face_n = choose_face(om_n, guard_n, eps, pivot)
    face_np1 = choose_face(om_np1, guard_np1, eps, pivot)

    # Transport prediction with face handling
    if face_n != face_np1:
        # If faces differ, attempt split at pivot
        om_mid = pivot
        if not (min(om_n, om_np1) <= om_mid <= max(om_n, om_np1)):
            # Pivot not in range, use single face
            U_pred = transport_update_U(U_n, om_n, om_np1, alpha, eps, p, face_n)
        else:
            # Split transport at pivot
            U_mid = transport_update_U(U_n, om_n, om_mid, alpha, eps, p, face_n)
            U_pred = transport_update_U(U_mid, om_mid, om_np1, alpha, eps, p, face_np1)
    else:
        # Same face, single transport
        U_pred = transport_update_U(U_n, om_n, om_np1, alpha, eps, p, face_n)

    # Compute residuals
    rT = U_np1 - U_pred          # transport residual
    rW = k_np1 - k_n             # weld (κ) residual
    
    # Pass/fail flags
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


def validate_sequence(data: List[Dict[str, Any]], **kwargs) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Validate transport and weld invariants for an entire sequence.
    
    Parameters
    ----------
    data : List[Dict[str, Any]]
        List of time step data dictionaries
    **kwargs
        Additional parameters passed to validate_step
        
    Returns
    -------
    Tuple[List[Dict[str, Any]], Dict[str, Any]]
        (validation_results, summary)
    """
    if len(data) < 2:
        raise ValueError("Need at least two rows for validation")
    
    results = []
    passes_T = 0
    passes_W = 0
    total = len(data) - 1
    
    for i in range(total):
        res = validate_step(data[i], data[i + 1], **kwargs)
        res["idx"] = i
        results.append(res)
        
        passes_T += int(res["okT"] == 1.0)
        passes_W += int(res["okW"] == 1.0)
    
    summary = {
        "total_steps": total,
        "transport_pass": passes_T,
        "weld_pass": passes_W,
        "transport_pass_rate": passes_T / total if total > 0 else 0.0,
        "weld_pass_rate": passes_W / total if total > 0 else 0.0,
    }
    
    return results, summary


def _to_bool_flag(s: str) -> bool:
    """Convert string to boolean flag."""
    return str(s).strip() in {"1", "true", "True", "TRUE"}


def validate_weld(kappa_sequence: List[float], tolerance: float = 1e-12) -> List[bool]:
    """
    Validate weld continuity (κ should be approximately constant).
    
    Parameters
    ----------
    kappa_sequence : List[float]
        Sequence of kappa values
    tolerance : float
        Tolerance for kappa differences
        
    Returns
    -------
    List[bool]
        Pass/fail for each transition
    """
    if len(kappa_sequence) < 2:
        return []
    
    results = []
    for i in range(len(kappa_sequence) - 1):
        diff = abs(kappa_sequence[i + 1] - kappa_sequence[i])
        results.append(diff <= tolerance)
    
    return results


# Export main functions
__all__ = [
    "choose_face", "transport_update_U", "validate_step", 
    "validate_sequence", "validate_weld"
]