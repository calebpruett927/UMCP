# UMCP 2.0 Kernel — Refined Invariants (Pinned 2025-08-30, America/Chicago)

**Contract (frozen):** mode=global_fixed, (a,b,epsilon)=(frozen>0, frozen>0, 1e-08).

## Identities
- Normalization: y=(x-a)/b (b>0); x_hat=clip(y,0,1)
- Drift omega: default pre_clip -> omega=|Δy|; near-wall pivot -> omega=|Δx_hat| (record pivot)
- Fidelity/Entropy: F=1-omega; S=-ln(1-omega+epsilon)
- Curvature (K=3): C=(1/K) * sum_k (x_hat_t - x_hat[t-k])^2
- Re-entry tau_R: min over Δt>0 such that |x_hat_t - x_hat[t-Δt]| < epsilon_ret; debounce L=2; horizon H_max=600
  * epsilon_ret policy: epsilon_ret = clip(k*sigma_n, epsilon_min, epsilon_max), sigma_n via EMA(lambda=0.2),
    k=2.5, epsilon_min=5e-4, epsilon_max=7e-2
- Integrity & log-integrity: IC = F*exp(-S)*(1-omega)*exp(-alpha*C/(1+tau_R)), kappa=ln(IC)
  * Compact kappa: kappa = 2*ln(1-omega) + ln(1-omega+epsilon) - alpha*C/(1+tau_R)
- Sensitivities: d kappa/d omega = -[2/(1-omega) + 1/(1-omega+epsilon)],
                 d kappa/d C = -alpha/(1+tau_R), d kappa/d tau_R = alpha*C/(1+tau_R)^2
- Transport payload: U = C/(1+tau_R)
- Weld identity: Delta kappa at [t_hat] = 0 and Delta U at [t_hat] = 0 within tolerances (tol_W, tol_T)
- Multi-channel aggregation: geometric mean on IC (sum on kappa)
- CTMC generator constraint: column convention; 1^T Q = 0; off-diagonals >= 0

## Closures (defaults)
omega policy=pre_clip; near-wall pivot=post_clip+guard; K=3; alpha=1.0; epsilon=1e-08;
EMA lambda=0.2; tau_R policy {k=2.5, epsilon_min=5e-4, epsilon_max=7e-2, L=2, H_max=600};
normalization=global_fixed; OOR=clip_and_flag; lambda_wall=0.0 (enable on saturation); aggregator=geometric_mean.

## Regime gates (worst-of, tie-break by IC)
Stable: omega<0.038 & F>0.90 & S<0.15 & C<0.14;
Watch: 0.038<=omega<0.30;
Collapse: omega>=0.30 (Critical if IC<0.30).
