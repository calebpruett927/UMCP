#!/usr/bin/env python3
"""
UMCP Validation Example

This example demonstrates how to validate UMCP transport and weld invariants.
"""

import umcp
import numpy as np
import csv
import os

def create_sample_audit_data(filename="sample_audit.csv", n_points=100):
    """Create sample audit data for validation testing."""
    np.random.seed(42)
    
    # Generate synthetic time series
    t = np.linspace(0, 10, n_points)
    x_raw = 0.5 + 0.2 * t + 0.1 * np.random.randn(n_points)
    
    # Normalization parameters
    a, b = 0.3, 1.5
    
    # Compute invariants
    results = umcp.compute_invariants(x_raw.tolist(), a, b)
    
    # Write to CSV
    with open(filename, 'w', newline='') as f:
        fieldnames = ['t', 'omega', 'C', 'tau_R', 'IC', 'kappa']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, r in enumerate(results):
            writer.writerow({
                't': i,
                'omega': r['omega'],
                'C': r['C'],
                'tau_R': r['tau_R'],
                'IC': r['IC'],
                'kappa': r['kappa']
            })
    
    return filename, results

def load_audit_data(filename):
    """Load audit data from CSV."""
    with open(filename, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    print("=== UMCP Validation Example ===")
    
    # Create sample data
    print("Creating sample audit data...")
    audit_file, original_results = create_sample_audit_data()
    print(f"Created {audit_file} with {len(original_results)} data points")
    
    # Load the data back
    audit_data = load_audit_data(audit_file)
    print(f"Loaded {len(audit_data)} audit records")
    
    # Validate the sequence
    print("\nValidating transport and weld invariants...")
    validation_results, summary = umcp.validate_sequence(
        audit_data,
        alpha=1.0,           # Transport coefficient
        eps=1e-8,           # Small epsilon
        p=3.0,              # Face potential order
        tolT=1e-9,          # Transport tolerance
        tolW=1e-12,         # Weld tolerance
        pivot=0.99          # Face pivot threshold
    )
    
    print(f"Validation complete for {summary['total_steps']} transitions")
    print(f"Transport validation: {summary['transport_pass']}/{summary['total_steps']} "
          f"({summary['transport_pass_rate']:.1%} pass rate)")
    print(f"Weld validation: {summary['weld_pass']}/{summary['total_steps']} "
          f"({summary['weld_pass_rate']:.1%} pass rate)")
    
    # Show some validation details
    print("\nFirst 5 validation results:")
    for i, result in enumerate(validation_results[:5]):
        print(f"  Step {result['idx']}: ω={result['omega_n']:.4f}→{result['omega_np1']:.4f}, "
              f"faces={result['face_n']}→{result['face_np1']}, "
              f"rT={result['rT']:.2e}, rW={result['rW']:.2e}, "
              f"T_ok={bool(result['okT'])}, W_ok={bool(result['okW'])}")
    
    # Check for any validation failures
    transport_failures = [r for r in validation_results if r['okT'] == 0]
    weld_failures = [r for r in validation_results if r['okW'] == 0]
    
    if transport_failures:
        print(f"\nFound {len(transport_failures)} transport validation failures")
        print("Largest transport residuals:")
        transport_failures.sort(key=lambda x: abs(x['rT']), reverse=True)
        for r in transport_failures[:3]:
            print(f"  Step {r['idx']}: rT = {r['rT']:.2e}")
    
    if weld_failures:
        print(f"\nFound {len(weld_failures)} weld validation failures") 
        print("Largest weld residuals:")
        weld_failures.sort(key=lambda x: abs(x['rW']), reverse=True)
        for r in weld_failures[:3]:
            print(f"  Step {r['idx']}: rW = {r['rW']:.2e}")
    
    if not transport_failures and not weld_failures:
        print("\n✓ All validations passed!")
    
    # Clean up
    os.remove(audit_file)
    print(f"\nCleaned up {audit_file}")
    print("\n=== Validation Example Complete ===")

if __name__ == "__main__":
    main()