"""
Core mathematical functions for UMCP Collapse Calculus.

This module contains the fundamental mathematical operations for:
- Face potentials and transport rates
- Invariant computations
- Transport theory implementation
"""

import math
from typing import List, Dict, Any, Union, Optional
import numpy as np


# Constants
DEFAULT_EPS = 1e-8
DEFAULT_K = 3
DEFAULT_ALPHA = 1.0
DEFAULT_P = 3.0


def clip01(value: float) -> float:
    """Clip value to [0, 1] range."""
    return max(0.0, min(1.0, value))


def phi(omega: float, eps: float = DEFAULT_EPS, p: float = DEFAULT_P, face: str = "normal") -> float:
    """
    Face potential Φ(ω).

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

    Returns
    -------
    float
        Face potential value.
    """
    if face == "exact":
        # Exact product face (finite-wall counterpart): 2 ln(1-ω) + ln(1-ω+ε)
        return (
            2.0 * math.log(max(1.0 - omega, 1e-300))
            + math.log(max(1.0 - omega + eps, 1e-300))
        )
    # Normal (canonical) face: p ln(1-ω)
    return p * math.log(max(1.0 - omega, 1e-300))


def gamma_pointwise(omega: float, eps: float = DEFAULT_EPS, p: float = DEFAULT_P, face: str = "normal") -> float:
    """Pointwise tangent rate Γ(ω) on the active face."""
    if face == "exact":
        return 2.0 / (1.0 - omega) + 1.0 / (1.0 - omega + eps)
    return p / (1.0 - omega)


def gamma_secant(om_minus: float, om_plus: float, eps: float = DEFAULT_EPS, 
                p: float = DEFAULT_P, face: str = "normal") -> float:
    """
    Secant rate Γ across [ω_n, ω_{n+1}] on a *fixed* face.

    Falls back to the pointwise tangent if Δω is below machine scale.
    """
    d_om = om_plus - om_minus
    if abs(d_om) < 1e-15:
        return gamma_pointwise(om_minus, eps, p, face)
    num = phi(om_minus, eps, p, face) - phi(om_plus, eps, p, face)
    return num / d_om


def compute_omega(y_series: List[float], policy: str = "pre_clip") -> List[float]:
    """
    Compute drift (omega) from normalized y values.
    
    Parameters
    ----------
    y_series : List[float]
        Normalized y values
    policy : str
        "pre_clip" or "post_clip" - when to apply clipping
        
    Returns
    -------
    List[float]
        Omega (drift) values
    """
    omega = [0.0]  # First value is always 0
    
    for i in range(1, len(y_series)):
        if policy == "pre_clip":
            drift = abs(y_series[i] - y_series[i-1])
        else:  # post_clip
            y_prev = clip01(y_series[i-1])
            y_curr = clip01(y_series[i])
            drift = abs(y_curr - y_prev)
        omega.append(drift)
    
    return omega


def compute_fidelity(omega: List[float]) -> List[float]:
    """Compute fidelity F = 1 - ω."""
    return [1.0 - w for w in omega]


def compute_entropy(omega: List[float], eps: float = DEFAULT_EPS) -> List[float]:
    """Compute entropy S = -ln(1 - ω + ε)."""
    return [-math.log(1.0 - w + eps) for w in omega]


def compute_curvature(xhat: List[float], K: int = DEFAULT_K) -> List[float]:
    """
    Compute curvature C as mean of squared differences over K-window.
    
    Parameters
    ----------
    xhat : List[float]
        Clipped signal values
    K : int
        Window length for curvature computation
        
    Returns
    -------
    List[float]
        Curvature values
    """
    C = []
    
    for i in range(len(xhat)):
        if i < K:
            C.append(0.0)
        else:
            diffs = [(xhat[i] - xhat[i-k])**2 for k in range(1, K+1)]
            C.append(sum(diffs) / K)
    
    return C


def compute_tau_ret(eps_ret: float, xhat_series: List[float], t: int, 
                   max_h: int = 600, debounce_L: int = 2) -> int:
    """
    Return minimal Δt>0 s.t. |xhat_t - xhat_{t-Δt}| < eps_ret with debounce.
    
    Parameters
    ----------
    eps_ret : float
        Return threshold
    xhat_series : List[float]
        Signal series up to time t inclusive
    t : int
        Current time index
    max_h : int
        Maximum horizon to search
    debounce_L : int
        Debounce length required
        
    Returns
    -------
    int
        Return time tau_R
    """
    if t == 0:
        return 1
        
    target = xhat_series[t]
    seen = 0
    
    for dt in range(1, min(t + 1, max_h) + 1):
        if abs(target - xhat_series[t - dt]) < eps_ret:
            seen += 1
            if seen >= debounce_L:
                return dt
        else:
            seen = 0
    
    return max_h


def compute_integrity_coefficient(F: float, S: float, omega: float, C: float, 
                                tau_R: int, alpha: float = DEFAULT_ALPHA) -> float:
    """
    Compute Integrity Coefficient IC.
    
    IC = F * exp(-S) * (1-ω) * exp(-α*C/(1+τ_R))
    """
    return F * math.exp(-S) * (1.0 - omega) * math.exp(-alpha * C / (1.0 + tau_R))


def compute_kappa(IC: float) -> float:
    """Compute κ = ln(IC)."""
    return math.log(max(IC, 1e-300))


def compute_U(C: float, tau_R: int) -> float:
    """Compute transport payload U = C/(1+τ_R)."""
    return C / (1.0 + tau_R)


def compute_invariants(x_raw: List[float], a: float, b: float, 
                      eps: float = DEFAULT_EPS, K: int = DEFAULT_K,
                      alpha: float = DEFAULT_ALPHA) -> List[Dict[str, Any]]:
    """
    Compute all UMCP invariants for a time series.
    
    Parameters
    ----------
    x_raw : List[float]
        Raw input time series
    a : float
        Normalization intercept (frozen parameter)
    b : float
        Normalization scale (frozen parameter, must be > 0)
    eps : float
        Small epsilon for entropy calculation
    K : int
        Curvature window length
    alpha : float
        Transport coefficient
        
    Returns
    -------
    List[Dict[str, Any]]
        List of dictionaries containing all invariants for each time step
    """
    if b <= 0:
        raise ValueError("Parameter b must be positive")
    
    # Normalize
    y = [(x - a) / b for x in x_raw]
    xhat = [clip01(yi) for yi in y]
    
    # Compute core invariants
    omega = compute_omega(y, policy="pre_clip")
    F = compute_fidelity(omega)
    S = compute_entropy(omega, eps)
    C = compute_curvature(xhat, K)
    
    # Compute tau_R with adaptive threshold
    tau_R = []
    res_sigma = 0.0
    EMA_LAMBDA = 0.2
    TAUR_K = 2.5
    EPS_MIN = 5e-4
    EPS_MAX = 0.07
    
    for i in range(len(xhat)):
        if i == 0:
            tau_R.append(1)
            res_sigma = 0.0
        else:
            # Update residual sigma estimate
            rres = xhat[i] - xhat[i-1]
            res_sigma = EMA_LAMBDA * abs(rres) + (1 - EMA_LAMBDA) * res_sigma
            
            # Compute adaptive threshold
            eps_ret = max(EPS_MIN, min(TAUR_K * res_sigma, EPS_MAX))
            tau_r = compute_tau_ret(eps_ret, xhat, i)
            tau_R.append(tau_r)
    
    # Compute derived quantities
    results = []
    for i in range(len(x_raw)):
        IC = compute_integrity_coefficient(F[i], S[i], omega[i], C[i], tau_R[i], alpha)
        kappa = compute_kappa(IC)
        U = compute_U(C[i], tau_R[i])
        
        # Classify regime
        regime = classify_regime(omega[i], F[i], S[i], C[i], IC)
        
        results.append({
            't': i,
            'x_raw': x_raw[i],
            'y': y[i],
            'xhat': xhat[i],
            'omega': omega[i],
            'F': F[i],
            'S': S[i],
            'C': C[i],
            'tau_R': tau_R[i],
            'IC': IC,
            'kappa': kappa,
            'U': U,
            'regime': regime
        })
    
    return results


def classify_regime(omega: float, F: float, S: float, C: float, IC: float) -> str:
    """
    Classify regime based on invariant values.
    
    Parameters
    ----------
    omega, F, S, C, IC : float
        Invariant values
        
    Returns
    -------
    str
        Regime classification: "Stable", "Watch", or "Collapse"
    """
    # Stable regime gates
    if (omega < 0.038 and F > 0.9 and S < 0.15 and C < 0.14):
        return "Stable"
    
    # Collapse regime gates
    if omega >= 0.30:
        if IC < 0.30:  # Critical overlay
            return "Critical"
        return "Collapse"
    
    # Watch regime (between stable and collapse)
    if 0.038 <= omega < 0.30:
        return "Watch"
    
    # Default fallback
    return "Stable"


# Export main functions
__all__ = [
    "phi", "gamma_pointwise", "gamma_secant",
    "compute_omega", "compute_fidelity", "compute_entropy", 
    "compute_curvature", "compute_tau_ret", "compute_integrity_coefficient",
    "compute_kappa", "compute_U", "compute_invariants", "classify_regime",
    "clip01"
]