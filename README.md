# Collapse Calculus — Frozen Contract Artifacts
Date: 2025-09-02 02:26 CDT

This bundle contains the frozen normalization parameters, a compiled manifest, LaTeX includeables, and helper guides to confirm the contract in the paper.

## Files
- `compiled_manifest.json` — canonical manifest with defaults and **equator_binding θ=0.35**.
- `frozen_ab_table.csv` — full per-channel `(a,b,method)` table from the freeze file.
- `timestep_index.csv` — time index harvested from available per-step files (deduplicated). May be empty if no `t` column is present.
- `MANIFEST_TABLE.tex` — LaTeX table you can `\input` into the main REVTeX.
- `CHANNELS_AB_TABLE.tex` — LaTeX table with full `(a,b)` for all channels.
- `WELD_TEST_GUIDE.txt` — step-by-step weld verification checklist.
- `HOWTO_BUILD.md` — compile instructions for the paper and how to include the tables.
- `SHA256SUMS.txt` — checksums for all artifacts in this bundle.

## Include in LaTeX
```latex
% In your preamble or near front-matter:
\input{MANIFEST_TABLE.tex}
\input{CHANNELS_AB_TABLE.tex}
```
