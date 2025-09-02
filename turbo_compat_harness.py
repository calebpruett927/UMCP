#!/usr/bin/env python3
"""
Turbo-Compat Harness (keeps identities; shows we *could* be fastest if we wanted).
- Reads a CSV with columns: t, x_raw, a, b  (b>0; (a,b) frozen upstream)
- Computes y, xhat, ω, F, S, C, τ_R, IC, κ
- Computes simple SPC overlays (Shewhart, EWMA, CUSUM) for comparability.
- Emits an audit row CSV and a quick timing summary.
This is a minimal skeleton; plug into your CI as a check job, not a primary path.
"""
import csv, math, time, argparse
from collections import deque

EPS=1e-8
K=3
ALPHA=1.0
EMA_LAMBDA=0.2
TAUR_K=2.5
EPS_MIN=5e-4
EPS_MAX=0.07

def clip01(u):
    return 0.0 if u<0.0 else (1.0 if u>1.0 else u)

def compute_tau_ret(eps, series, t, max_h=600, debounce_L=2):
    """Return minimal Δt>0 s.t. |xhat_t - xhat_{t-Δt}| < eps with debounce.
    series is list of xhat up to t inclusive."""
    target = series[t]
    seen=0
    for dt in range(1, min(t+1, max_h)+1):
        if abs(target - series[t-dt]) < eps:
            seen += 1
            if seen >= debounce_L:
                return dt
        else:
            seen = 0
    return max_h

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Input CSV with t,x_raw,a,b (b>0)")
    ap.add_argument("--out", default="turbo_compat_audit.csv")
    ap.add_argument("--sigma", type=float, default=1.0, help="Std for Shewhart/CUSUM synthetic baseline")
    args = ap.parse_args()

    t0 = time.time()
    rows = []
    with open(args.csv, "r", newline="") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)

    # Pre-alloc
    y=[]; xhat=[]; omega=[]; F=[]; S=[]; C=[]; tauR=[]; IC=[]; kappa=[]
    # SPC overlays
    shewhart_flags=[]; ewma=[]; ewma_flags=[]; cusum_pos=[]; cusum_neg=[]; cusum_flags=[]

    # Rolling for curvature
    xhat_win = deque(maxlen=K+1)
    # EWMA
    z=None
    # CUSUM params
    k = 0.5 * args.sigma
    h = 5.0 * args.sigma

    # Simple residual sigma estimate (EMA) for τ_R
    res_sigma=None

    for i, r in enumerate(rows):
        xr = float(r["x_raw"]); a = float(r["a"]); b = float(r["b"])
        y_i = (xr - a) / b
        xh = clip01(y_i)
        y.append(y_i); xhat.append(xh)

        # Drift (pre-clip as default policy)
        if i==0:
            w = 0.0
        else:
            w = abs(y[i] - y[i-1])
        omega.append(w)

        # Fidelity/Entropy
        f = 1.0 - w
        s = -math.log(1.0 - w + EPS)
        F.append(f); S.append(s)

        # Curvature (mean of squared deltas over K lag window)
        xhat_win.append(xh)
        if len(xhat_win) < K+1:
            c = 0.0
        else:
            diffs = [(xhat_win[-1] - xhat_win[-k])**2 for k in range(1, K+1)]
            c = sum(diffs)/K
        C.append(c)

        # Residuals EMA for τ_R tolerance
        if i==0:
            res_sigma = 0.0
        else:
            rres = xhat[i] - xhat[i-1]
            res_sigma = EMA_LAMBDA*abs(rres) + (1-EMA_LAMBDA)*res_sigma

        eps_ret = max(EPS_MIN, min(TAUR_K*res_sigma, EPS_MAX))
        tr = compute_tau_ret(eps_ret, xhat, i)
        tauR.append(tr)

        # Integrity
        ic = f * math.exp(-s) * (1.0 - w) * math.exp(-ALPHA * c / (1.0 + tr))
        kappa.append(math.log(max(ic, 1e-300)))
        IC.append(ic)

        # SPC overlays (Shewhart 3σ on y)
        shewhart_flags.append( abs(y_i) > 3*args.sigma )

        # EWMA
        if z is None: z = y_i
        else: z = 0.2*y_i + 0.8*z
        ewma.append(z)
        # 3σ equivalent control limit for EWMA (approx)
        L=3.0; lam=0.2
        sigma_z = args.sigma * math.sqrt( lam/(2.0 - lam) )
        ewma_flags.append( abs(z) > L*sigma_z )

        # CUSUM
        cp = max(0.0, (y_i - k) + (cusum_pos[-1] if cusum_pos else 0.0))
        cn = max(0.0, (-y_i - k) + (cusum_neg[-1] if cusum_neg else 0.0))
        cusum_pos.append(cp); cusum_neg.append(cn)
        cusum_flags.append( cp>h or cn>h )

    t1 = time.time()
    elapsed_ms = (t1 - t0)*1000.0

    # Emit audit-style CSV (minimal)
    with open(args.out, "w", newline="") as g:
        cols = ["t","x_raw","a","b","y","xhat","omega","F","S","C","tau_R","IC","kappa",
                "shewhart_flag","ewma_flag","cusum_flag"]
        wtr = csv.writer(g)
        wtr.writerow(cols)
        for i, r in enumerate(rows):
            wtr.writerow([r.get("t", i), r["x_raw"], r["a"], r["b"],
                          y[i], xhat[i], omega[i], F[i], S[i], C[i], tauR[i], IC[i], kappa[i],
                          int(shewhart_flags[i]), int(ewma_flags[i]), int(cusum_flags[i])])

    print(f"Turbo-Compat run complete in {elapsed_ms:.2f} ms over {len(rows)} rows. "
          f"(Identities: κ, U, weld-ready)")
if __name__ == "__main__":
    main()
