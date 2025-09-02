# UMCP/RCFT Full Run — 2025-08-30 10:46:14 CDT (America/Chicago)

**Dataset:** `per_step_with_weld_tests.csv`  •  **Rows:** 11036

**Frozen (a,b):** (0.36005807, 0.55429784)  •  **Tolerances:** W=1e-12, T=1e-09

## Identities
- y=(x−a)/b; x̂=clip(y,0,1)
- ω=|Δy|; F=1−ω; S=−ln(1−ω+ε)
- C: K-window (K=3); τ_R via EMA policy; IC composite; κ=ln(IC); U=C/(1+τ_R)

## Results (median)
- ω: 0.011119  •  C: 0.000000  •  τ_R: 1.000  •  κ: -0.033591
- |∂κ/∂ω|: 3.033733  •  |∂κ/∂C|: 0.500000  •  ∂κ/∂τ_R: 0.000000

**Regimes:** {'Stable': 8006, 'Watch': 1759, 'Collapse': 1271}  •  **Near-wall rate:** 89.0087%  •  **OOR rate:** 89.0087%

## Sample audit row
`t=idx:0`: y=0.162633, x̂=0.162633, ω=0.000000, C=0.000038, τ_R=1, κ=-0.000019, U=0.000019, tags=regime:Stable;near_wall:0;oor:0

## Hashes and Artifacts
- CSV: rcft_full_run.csv
- JSON: rcft_full_run.json
- MD: rcft_full_run.md
