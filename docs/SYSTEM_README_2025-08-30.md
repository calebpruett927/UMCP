# System Operator Runbook (Pinned 2025-08-30, America/Chicago)

Artifacts: kernel_v2.0_2025-08-30.{md,json}, freeze_contract.json, tolerances.json, configs (generator.yaml, datasets.yaml, BandPack.yaml, compat_lane.yaml), validator (collapse_validate.py), data (rcft_full_run.*), stacks, manifests.

Runbook:
1) Freeze (a,b) from freeze_contract.json (already frozen).
2) Compute invariants (omega,F,S,C,tau_R,IC,kappa) and label regimes.
3) Validate welds (Delta kappa & Delta U) via collapse_validate.py.
4) Export and log hashes (manifest CSV/JSON).
