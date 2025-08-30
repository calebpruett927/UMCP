Clement — Friday, August 29, 2025 (America/Chicago).
Assumption: “full markdown” = a complete, copy-pasteable Markdown spec for the upgraded calculus, aligned to the UMCP/ULRC/RCFT runbook. No background tasks; produced now. Where data/policy would normally come from manifests, I mark unknown — hint.

# Collapse Calculus — Weld-Continuous Dynamics and Audit Guarantees
**Version:** 1.0.2 (spec draft)  
**Scope:** Elevate collapse algebra into a differential calculus with a frozen governance contract, exact identities, tunable closures, weld-consistent transport, and an auditable workflow that produces a deterministic ledger of acts (audit rows).

---

## 0) QuickStart (operational)
1. **/ingest** data (with timestamps) → echo channels + min/max.  
2. **/freeze** normalization map `(a,b)` per channel + method/window; record `norm_mode`.  
3. **/compute** per-timestamp: drift `ω`, fidelity `F`, entropy `S`, curvature `C`, reentry `τ_R`, integrity `IC`, log-integrity `κ`.  
4. **/regime** propose worst-of gates (Stable/Watch/Collapse) and resolve ties by `IC`.  
5. **/render** plots/tables and write one audit row per act.  
6. **/export** `{manifest|audit|figs}` with hashes.

---

## 1) Governance contract (frozen before compute)
- **Normalization map:** affine `y=(x−a)/b` with `b>0`, then **clip** to unit interval: `x̂=clip(y,0,1)`.  
- **Contracted constants (defaults):**  
  - `ic_form=normal; p=3; ε=1e−8; α=1.0; η=1e−3`  
  - **Regime gates:** Stable if `ω<0.038`, `F>0.90`, `S<0.15`, `C<0.14`; Watch `0.038–0.30`; Collapse `≥0.30` (Critical if `IC<0.30`).  
  - **Curvature window:** `K=3`.  
  - **Reentry tolerance (τ_R) policy:** `ε_ret = clip(k·σ_n, ε_min, ε_max)` with `k=2.5`, `ε_min=5e−4`, `ε_max=0.07`, debounce `L=2`, horizon `H_max=600`.  
  - **EMA for residuals (σ_n):** `λ=0.2` (≈5-sample memory).  
  - **Normalization mode:** `global_fixed` preferred.  
  - **Clip policy:** `ω` measured **pre-clip**; switch to **post-clip+guard** near walls/singular `b`.  
  - **Out-of-range (OOR) policy:** `clip_and_flag` (log OOR rate).  
  - **Hash:** `sha256`.  
  - **Timebase:** timestamps in UTC with `TZ=America/Chicago` recorded in the meta line; any resampling is part of the contract.  
- **Regime generator (CTMC):** column convention; enforce `1ᵀ Q = 0`, off-diagonals `≥ 0`.  
- **Face policy:** two faces (regular / near-wall). Pivot to near-wall face when guardbands trip.  
- **Guardbands for calibration:** `(ε_g, h_g) = (0.05, 0.05)`.  
- **Published tolerances:** `tol_W` (weld), `tol_T` (transport) **unknown — hint:** publish in policy table.

> **Freeze rule:** If `(a,b)` missing → **unknown — hint:** freeze `(a,b)` or authorize P1/P99 calibration with guardbands.

---

## 2) Invariants and derived quantities
Given a time-ordered series per channel:

- **Drift:** `ω_t = |Δy_t|` (pre-clip) or `|Δx̂_t|` (post-clip with guard).  
- **Fidelity:** `F_t = 1 − ω_t`.  
- **Entropy:** `S_t = −ln(1 − ω_t + ε)`.  
- **Curvature (K-window):**  
  \[
  C_t = \frac{1}{K} \sum_{k=1}^{K} ( \hat{x}_t - \hat{x}_{t-k} )^2
  \]
- **Reentry delay:**  
  \[
  \tau_{R,t} = \min\{ \Delta t>0 : |\hat{x}_t - \hat{x}_{t-\Delta t}| < \varepsilon_{\text{ret}}\}\quad
  \text{with debounce } L
  \]
- **Integrity:**  
  \[
  IC_t = F_t \cdot e^{-S_t} \cdot (1-\omega_t) \cdot \exp\!\Big(-\frac{\alpha\,C_t}{1+\tau_{R,t}}\Big),\quad
  \kappa_t = \ln(IC_t)
  \]

---

## 3) Identities (transport invariants and weld)
These hold independent of closures/hazard dials:

1. **Secant update for the face map:** For a smooth face potential `Φ(ω)` on the active face, define the **secant rate**
   \[
   \Gamma^{\text{sec}}_t = \frac{\Phi(\omega_t)-\Phi(\omega_{t-1})}{\omega_t-\omega_{t-1}} \quad (\omega_t\neq\omega_{t-1})
   \]
   and use `Γ^{sec}` in the discrete update to bridge steps without biasing the local tangent near the wall.
2. **Weld-consistency:** The update is chosen so that **κ-continuity** holds at welds:
   \[
   \kappa_{t^+} - \kappa_{t^-} = 0 \quad\text{(within } tol_W\text{)}
   \]
   Any gate change, manifest update, or weld operation must pass this equality.
3. **Transport identity for the curvature payload:** With
   \[
   U_t := \frac{C_t}{1+\tau_{R,t}},
   \]
   the discrete transport across a step preserves the welded payload:
   \[
   U_{t+1} = \mathcal{T}(U_t, \Delta t)\quad\text{and}\quad U_{t^+}-U_{t^-}=0\ \text{(within } tol_T\text{)}
   \]
   where `𝒯` is the exact transport induced by the secant face on that step.
4. **CTMC generator invariants:** With column convention, `Q` updates must satisfy `1ᵀ Q = 0` and `Q_{ij} ≥ 0` for `i≠j`. Discretizations must preserve non-negativity; if forward Euler is used, require `1 + Δt Q_{ii} ≥ 0`; otherwise use matrix exponential `exp(Δt Q)`.

---

## 4) Closures (tunable dials; declare when used)
- **Hazard/remainder templates:** e.g., rate laws `λ(ω)`, `μ(ω)`, and remainder terms for damping curvature near walls that yield a small-gain (ISS) style Lyapunov inequality for `V = −κ`.  
- **Default gates and horizons:** thresholds in §1; may vary by domain; publish per dataset.  
- **Near-wall pivot:** switch to post-clip+guard when `ω` approaches the wall (`1−ε_g`) or when `b` is ill-conditioned; log `lambda_wall>0`.  
- **Tolerances:** `tol_W`, `tol_T` **unknown — hint:** set numeric defaults (e.g., `1e−10` absolute, `1e−6` relative) and publish.  
- **Timebase policy:** resampling kernel and allowed jitter; publish in manifest.

> **Principle:** Identities are non-negotiable. Closures are explicitly declared and auditable.

---

## 5) Gates & regimes
- **Stable:** `ω<0.038`, `F>0.90`, `S<0.15`, `C<0.14`  
- **Watch:** `0.038 ≤ ω < 0.30`  
- **Collapse:** `ω ≥ 0.30` (mark **Critical** if `IC<0.30`)  
- Gate transitions may trigger a `Q` update. Use weld to enforce κ-continuity across regime switches.

---

## 6) Algorithms (pseudocode)

### 6.1 Compute pass (per channel, per timestamp)
```pseudo
require: frozen (a,b), ε, α, K, ε_ret-policy, norm_mode, face-policy
input: time series {t, x_t}

for t = 1..T:
  y_t  = (x_t - a)/b
  xhat_t = clip(y_t, 0, 1)             # record OOR flags
  if near_wall_or_singular_b:          # guard trigger
      drift_mode = POST_CLIP
  else:
      drift_mode = PRE_CLIP

  ω_t = abs(Δy_t) if PRE_CLIP else abs(Δxhat_t)
  F_t = 1 - ω_t
  S_t = -ln(1 - ω_t + ε)
  C_t = (1/K) * Σ_{k=1..K} (xhat_t - xhat_{t-k})^2
  τ_R,t = reentry_delay(xhat, ε_ret, L, H_max)
  IC_t = F_t * exp(-S_t) * (1 - ω_t) * exp(-α * C_t / (1 + τ_R,t))
  κ_t  = ln(IC_t)

  # regime proposal
  regime_t = gate(ω_t, F_t, S_t, C_t, IC_t)
end
```

### 6.2 Weld + transport (secant face)
```pseudo
# to apply a weld at time t_w (e.g., gate change or generator update)
Γ_sec = (Φ(ω_t) - Φ(ω_{t-1})) / (ω_t - ω_{t-1})
apply_transport_on_U = true   # U = C/(1+τ_R)

# enforce κ continuity (within tol_W)
assert |κ_{t_w^+} - κ_{t_w^-}| ≤ tol_W

# enforce payload transport (within tol_T)
assert |U_{t_w^+} - U_{t_w^-}| ≤ tol_T
```

### 6.3 Generator update (CTMC, column convention)
```pseudo
# Q has columns summing to zero; off-diagonals ≥ 0
if using_forward_euler:
   require 1 + Δt * Q_ii ≥ 0 for all i
else:
   P = exp(Δt * Q)  # stochastic matrix
```

---

## 7) Tiny Validator (box this in the doc)
> **Validator A — κ-weld:** `|κ_{t^+} − κ_{t^-}| ≤ tol_W`  
> **Validator B — Transport:** with `U=C/(1+τ_R)`, `|U_{t^+} − U_{t^-}| ≤ tol_T`  
> **Default tolerances:** **unknown — hint:** set and publish (see §4).

---

## 8) Policy table (publish with the spec)
```yaml
contract:
  ic_form: normal
  p: 3
  epsilon: 1e-8
  alpha: 1.0
  eta: 1e-3
  K: 3
  norm_mode: global_fixed
  ω_policy: pre_clip            # auto-pivot to post_clip+guard near wall
  calibration_guardbands: { ε_g: 0.05, h_g: 0.05 }
  τ_R_policy:
    k: 2.5
    ε_min: 5e-4
    ε_max: 7e-2
    debounce_L: 2
    horizon_H_max: 600
    EMA_λ: 0.2
  gates:
    stable:   { ω_max: 0.038, F_min: 0.90, S_max: 0.15, C_max: 0.14 }
    watch:    { ω_range: [0.038, 0.30) }
    collapse: { ω_min: 0.30, critical_if_IC_lt: 0.30 }
  CTMC:
    convention: column
    invariant: "1^T Q = 0, off-diagonals ≥ 0"
  OOR_policy: clip_and_flag
  hash: sha256
  timezone_stamp: America/Chicago
tolerances:
  tol_W: unknown   # hint: set e.g., abs=1e-10, rel=1e-6
  tol_T: unknown   # hint: set e.g., abs=1e-10, rel=1e-6
```

---

## 9) Audit schema and example
**Audit header** (per act):
```
[t,channel,x_raw,a,b,y,x̂,ω,F,S,C,τ_R,IC,regime,weld_id?,policy_id,manifest_id,run_id,sha256]
```

**Illustrative row** (fabricated numbers; for format only):
```
2025-08-29T14:03:11Z,ch_07,0.843,0.120,0.770,0.939,0.939,0.021,0.979,0.021,0.0042,37,0.936,Stable,weld_0000,policy_v1.0.2,manifest_3f12,run_20250829T140300Z,8c1b...a9e
```

---

## 10) Manifest snippet (JSON)
```json
{
  "manifest_id": "manifest_3f12",
  "created_at": "2025-08-29T14:00:00Z",
  "tz": "America/Chicago",
  "channels": ["ch_01", "ch_02", "..."],
  "normalization": {
    "mode": "global_fixed",
    "a": { "ch_01": "unknown", "ch_02": "unknown" },
    "b": { "ch_01": "unknown", "ch_02": "unknown" },
    "hint": "freeze (a,b) or authorize P1/P99 calibration with guardbands"
  },
  "timebase": {
    "sampling": "fixed",
    "Δt": "unknown",
    "jitter_allowed": "unknown"
  },
  "tolerances": { "tol_W": "unknown", "tol_T": "unknown" }
}
```

---

## 11) Secant vs. tangent (why secant for the weld)
- For a twice-differentiable `Φ(ω)`, the tangent update injects a local bias ∝ `Φ″(ξ) (Δω)^2`.  
- The **secant** update uses the true discrete slope over the step, eliminating the first-order mismatch and keeping `κ` continuous at welds without overfitting the local curvature.  
- Near the wall, switch faces and keep `Γ^{sec}` finite via guardbands.

---

## 12) CTMC generator notes (safety)
- Column convention is mandatory (`1ᵀ Q = 0`).  
- When step sizes are large or diagonals are strongly negative, use `P = exp(Δt Q)` to preserve stochasticity.  
- If Euler is used, assert `1 + Δt Q_{ii} ≥ 0` for all `i`. Promote this from “example” to “rule.”

---

## 13) Workflow “presence” definition
A computation “has presence” iff a weld (if any) passes `κ` and transport validators and exactly one audit row is written for the act with a valid `sha256`.

---

## 14) Reporting structure (every substantive output)
**Header:** absolute date (America/Chicago) + assumptions made.  
**Identities:** list the invariants used (κ-continuity, CTMC constraints, transport of `U`).  
**Closures:** list active policies (K, k, λ, tolerances, hazard form, face).  
**Results:** numbers/labels + one sample audit row.  
**Gaps:** any **unknown — hint:** items.

---

## 15) Gaps (to publish before tagging the spec)
- **(a,b) per domain:** **unknown — hint:** freeze per-channel or authorize guard-banded P1/P99 calibration.  
- **Transport/weld tolerances:** **unknown — hint:** publish `tol_W`, `tol_T`.  
- **Closure exemplars:** **unknown — hint:** ship one minimal hazard family for reproducible ISS-style demos.  
- **Weld catalog schema:** **unknown — hint:** include CSV header + a worked weld example in the appendix.

---

## 16) Meta line (append to every artifact)
```
Meta — Tags:<collapse-calculus; weld; CTMC; audit>; Slice:[t0,t1];
Contract:(a,b,ε)=(…, …, 1e-8); Bands:<Defaults>;
Ops:{omega=pre_clip→post_clip+guard near wall, ic=normal(p=3), K=3, α=1.0, η=1e-3, λ=0.2, k=2.5};
Q:{convention=column, 1ᵀQ=0};
Norm:global_fixed; OOR:clip_and_flag; TZ:America/Chicago;
Manifest:<id>; Weld:<id?>; Hash:<sha256>.
```

---

## 17) Changelog
- **1.0.2 (2025-08-29):** Add “Tiny Validator” box; make generator safety a rule; publish timebase in contract; clarify face pivot near wall; define `U=C/(1+τ_R)` transport identity.

---

### Identities vs. closures (declaration for this spec)
- **Identities:** affine normalization; κ-continuity at weld; transport of `U`; CTMC generator constraints (`1ᵀQ=0`, off-diagonals ≥0); audit hash and presence rule.  
- **Closures used in defaults:** window `K=3`; guardbands `(ε_g,h_g)`; reentry policy parameters `(k, ε_min, ε_max, L, H_max)`; EMA `λ`; regime gates; ω policy with near-wall pivot; tolerances `tol_W, tol_T` (to be published).

---

**End of markdown spec.**  
For next iteration, drop in concrete `tol_W`/`tol_T`, publish one hazard family, and include a single welded example with both Euler and `exp(ΔtQ)` transports to show the invariants hold numerically.
