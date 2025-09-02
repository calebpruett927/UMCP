# RCFT Playground

An interactive what‑if tool to explore UMCP parameter effects. The playground loads a CSV data slice, computes invariants (ω, F, S, C, τ_R, IC, κ) under the given (a,b), epsilon and window length K. It produces summary statistics, a density plot of ω vs curvature C, and exports a DOCX report.

## Usage

```bash
python3 playground.py --csv data.csv --channel y --a 0.36 --b 0.55 --epsilon 1e-8 --K 3 --out_dir out_play
```

- `--csv`: Input CSV with a header row including the measurement column.
- `--channel`: Column name for the measurement values.
- `--a`, `--b`: Frozen normalization contract.
- `--epsilon`: Small epsilon used in entropy calculation (default 1e-8).
- `--K`: Window length for curvature (default 3).
- `--out_dir`: Directory to write outputs (summary.json, density.png, report.docx).

## Outputs

- `summary.json`: Summary of invariants and regime counts.
- `density.png`: A hexbin density plot of ω vs curvature C, with gate lines.
- `report.docx`: A DOCX report summarizing the run with the plot embedded.

## Dependencies

```
pip install matplotlib python-docx pandas
```

## Example

```
python3 playground.py --csv example.csv --channel pressure --a 0.35 --b 0.55 --out_dir results
```

## License

Provided for educational demonstration.
