# UMCP: Universal Measurement and Control Protocol

A comprehensive framework for **Collapse Calculus** and time series analysis with mathematical foundations in transport theory and weld validation.

## Overview

UMCP provides a sophisticated mathematical framework for analyzing time series data through the lens of collapse calculus. It computes fundamental invariants that characterize system behavior and validates mathematical consistency through transport and weld continuity checks.

### Core Mathematical Invariants

- **ω (omega)**: Drift magnitude measuring rate of change
- **F**: Fidelity coefficient (F = 1 - ω)  
- **S**: Entropy (-ln(1 - ω + ε))
- **C**: Curvature (mean squared differences over K-window)
- **τ_R**: Return time (discrete hazard measure)
- **IC**: Integrity Coefficient (composite stability measure)
- **κ (kappa)**: Log integrity (κ = ln(IC))
- **U**: Transport payload (U = C/(1+τ_R))

### Regime Classification

- **Stable**: ω < 0.038, F > 0.9, S < 0.15, C < 0.14
- **Watch**: 0.038 ≤ ω < 0.30  
- **Collapse**: ω ≥ 0.30
- **Critical**: Collapse regime with IC < 0.30

## Installation

### From Source

```bash
git clone https://github.com/calebpruett927/UMCP.git
cd UMCP
pip install -e .
```

### Dependencies

- Python ≥ 3.8
- matplotlib
- pandas  
- python-docx
- numpy (recommended)

## Quick Start

### Basic Usage

```python
import umcp

# Your time series data
x_raw = [1.0, 1.1, 0.9, 1.2, 1.1, ...]

# Normalization parameters (typically frozen from training)
a, b = 0.5, 2.0  # intercept, scale

# Compute all UMCP invariants
results = umcp.compute_invariants(x_raw, a, b)

# Analyze results
for r in results[:5]:
    print(f"t={r['t']}: ω={r['omega']:.3f}, regime={r['regime']}")
```

### Validation

```python
# Validate transport and weld continuity
validation_results, summary = umcp.validate_sequence(audit_data)
print(f"Transport pass rate: {summary['transport_pass_rate']:.1%}")
print(f"Weld pass rate: {summary['weld_pass_rate']:.1%}")
```

### Analysis and Visualization

```python
# Comprehensive time series analysis
analysis = umcp.analyze_time_series(x_raw, a, b)
print(f"Regime distribution: {analysis['statistics']['regime_counts']}")

# Generate plots and reports
umcp.playground_analysis(
    csv_path="data.csv", 
    channel="signal", 
    a=0.5, b=2.0,
    out_dir="analysis_output"
)
```

## Command Line Interface

### Validation

```bash
# Validate UMCP invariants in CSV data
umcp-validate --csv audit_data.csv --out validation_results.csv

# With custom parameters
umcp-validate --csv data.csv --alpha 1.0 --tolT 1e-9 --tolW 1e-12
```

### Interactive Analysis

```bash
# Run playground analysis
umcp-playground --csv data.csv --channel signal_col --a 0.5 --b 2.0 --out-dir results/

# Parameter sweep
umcp-turbo --csv input.csv --out turbo_results.csv --sigma 1.0
```

## Repository Structure

```
UMCP/
├── umcp/                   # Main Python package
│   ├── core/              # Core mathematical functions
│   ├── validation/        # Transport & weld validation
│   ├── analysis/          # High-level analysis tools
│   ├── scripts/          # Command-line interfaces
│   └── utils/            # Utilities and helpers
├── examples/             # Usage examples
├── tests/               # Test suite
├── docs/               # Documentation
├── configs/            # Configuration files
├── data/              # Sample data files
└── README.md          # This file
```

## Mathematical Foundation

UMCP implements a rigorous mathematical framework based on:

- **Transport Theory**: Face potentials Φ(ω) and secant rates Γ
- **Weld Validation**: Continuity checks for κ and U across time steps  
- **Regime Gates**: Threshold-based classification of system states
- **Invariant Computation**: Consistent calculation of all fundamental measures

### Face Potentials

- **Normal Face**: Φ(ω) = p·ln(1-ω) 
- **Exact Face**: Φ(ω) = 2·ln(1-ω) + ln(1-ω+ε)

### Transport Equation

```
U_{t+1} = U_t - (1/α) · Γ(ω_t, ω_{t+1}) · (ω_{t+1} - ω_t)
```

## Configuration

Key parameters can be configured via JSON files in `configs/`:

- `kernel_v2.0_2025-08-30.json`: Core kernel configuration
- `compiled_manifest.json`: System manifest with normalization parameters

## Examples

See the `examples/` directory for:

- `basic_usage.py`: Introduction to core functionality
- `validation_example.py`: Transport and weld validation workflow

## Testing

```bash
# Run basic functionality tests
python examples/basic_usage.py

# Run validation tests  
python examples/validation_example.py

# Test CLI tools
umcp-validate --help
umcp-playground --help
```

## Citation

If you use UMCP in your research, please cite:

```
UMCP: Universal Measurement and Control Protocol
Collapse Calculus Framework for Time Series Analysis
Version 2.0, 2025
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## Support

For questions and support:
- Check the `examples/` directory for usage patterns
- Review the `docs/` directory for detailed documentation  
- Open an issue on GitHub for bugs or feature requests
