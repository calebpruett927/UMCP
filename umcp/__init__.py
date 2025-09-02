"""
UMCP: Universal Measurement and Control Protocol

A comprehensive framework for collapse calculus and time series analysis
with mathematical foundations in transport theory and weld validation.

Core Components:
- Transport theory with face potentials and secant rates
- Mathematical invariants (omega, F, S, C, tau_R, IC, kappa)
- Regime classification (Stable, Watch, Collapse)
- Validation framework for transport and weld continuity
"""

__version__ = "2.0.0"
__author__ = "UMCP Development Team"

# Core API imports
from .core import (
    compute_invariants, classify_regime, compute_omega, compute_fidelity,
    compute_entropy, compute_curvature, compute_integrity_coefficient,
    compute_kappa, compute_U, phi, gamma_pointwise, gamma_secant, clip01
)
from .validation import (
    validate_step, validate_sequence, validate_weld, choose_face, transport_update_U
)
from .analysis import (
    analyze_time_series, parse_csv_channel, playground_analysis, parameter_sweep
)

__all__ = [
    # Core mathematical functions
    "compute_invariants", "classify_regime", "compute_omega", "compute_fidelity",
    "compute_entropy", "compute_curvature", "compute_integrity_coefficient",
    "compute_kappa", "compute_U", "phi", "gamma_pointwise", "gamma_secant", "clip01",
    
    # Validation functions
    "validate_step", "validate_sequence", "validate_weld", "choose_face", "transport_update_U",
    
    # Analysis tools
    "analyze_time_series", "parse_csv_channel", "playground_analysis", "parameter_sweep",
]