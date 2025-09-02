#!/usr/bin/env python3
"""
Basic UMCP Usage Example

This example demonstrates how to use the UMCP library for time series analysis.
"""

import umcp
import numpy as np

# Generate sample time series data
np.random.seed(42)
n_points = 1000
t = np.linspace(0, 10, n_points)

# Create a signal with trend, noise, and some regime changes
trend = 0.1 * t
noise = 0.05 * np.random.randn(n_points)
regime_change = np.where(t > 5, 0.2 * np.sin(2 * t), 0)
x_raw = trend + noise + regime_change

print("=== UMCP Basic Usage Example ===")
print(f"Generated {len(x_raw)} time series points")

# Define normalization parameters (typically frozen from training data)
a = 0.5  # intercept
b = 2.0  # scale

print(f"Using normalization parameters: a={a}, b={b}")

# Compute all UMCP invariants
print("\nComputing UMCP invariants...")
results = umcp.compute_invariants(x_raw.tolist(), a, b)

print(f"Computed invariants for {len(results)} time steps")

# Analyze regime distribution
regimes = [r['regime'] for r in results]
regime_counts = {}
for regime in regimes:
    regime_counts[regime] = regime_counts.get(regime, 0) + 1

print("\nRegime Distribution:")
for regime, count in regime_counts.items():
    percentage = (count / len(regimes)) * 100
    print(f"  {regime}: {count} ({percentage:.1f}%)")

# Find critical periods
critical_indices = [i for i, r in enumerate(results) if r['regime'] in ['Collapse', 'Critical']]
if critical_indices:
    print(f"\nCritical periods detected at indices: {critical_indices[:10]}...")  # Show first 10
else:
    print("\nNo critical periods detected")

# Show some statistics
omega_values = [r['omega'] for r in results]
C_values = [r['C'] for r in results]
IC_values = [r['IC'] for r in results]

print(f"\nStatistics:")
print(f"  Mean omega (drift): {np.mean(omega_values):.4f}")
print(f"  Max omega: {np.max(omega_values):.4f}")
print(f"  Mean C (curvature): {np.mean(C_values):.4f}")
print(f"  Min IC (integrity): {np.min(IC_values):.4f}")

# Validate weld continuity
print("\nValidating weld continuity...")
kappa_values = [r['kappa'] for r in results]
weld_results = umcp.validate_weld(kappa_values, tolerance=1e-10)
weld_pass_rate = sum(weld_results) / len(weld_results) if weld_results else 0
print(f"Weld validation pass rate: {weld_pass_rate:.2%}")

print("\n=== Example Complete ===")