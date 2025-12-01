#!/usr/bin/env python3

import csv
import subprocess
import sys
import math
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from path_utils import resolve_results_path, ensure_parent_dir, format_path


class ComprehensiveAnalyzer:
    """Analyzes primality tests on both small and large datasets."""
    
    def __init__(self):
        self.cpp_binary = None
        self.use_wsl = False
        self.setup_executable()
    
    def setup_executable(self):
        """Find and configure C++ executable."""
        import platform
        import os
        
        # On Windows, always use WSL
        if platform.system() == "Windows":
            self.cpp_binary = "../cpp/primality_test"
            self.use_wsl = True
            print(f"Using C++ binary via WSL: {self.cpp_binary}")
            return
        
        # On Linux/Mac, try to find native binary
        possible_paths = [
            "../cpp/primality_test",
            "../cpp/main",
            "./build/primality_test"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.cpp_binary = path
                print(f"Using C++ binary: {self.cpp_binary}")
                return
    
    def run_cpp_test(self, number: int, k: int = 10) -> Dict:
        """Run C++ test on a single number."""
        try:
            import os
            
            if self.use_wsl:
                cwd = os.getcwd().replace('\\', '/')
                wsl_path = cwd.replace('C:', '/mnt/c').replace('c:', '/mnt/c')
                cpp_dir = wsl_path.replace('/python', '/cpp')
                
                cmd = f'wsl -e bash -c "cd {cpp_dir} && ./primality_test {number} {k}"'
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
            else:
                result = subprocess.run(
                    [self.cpp_binary, str(number), str(k)],
                    capture_output=True, text=True, timeout=60
                )
            
            # Parse output
            lines = result.stdout.split('\n')
            fermat_result = None
            miller_result = None
            fermat_time = None
            miller_time = None
            
            in_fermat_section = False
            in_miller_section = False
            
            for line in lines:
                # Section detection
                if 'Fermat Test:' in line:
                    in_fermat_section = True
                    in_miller_section = False
                elif 'Miller-Rabin Test:' in line:
                    in_fermat_section = False
                    in_miller_section = True
                elif 'Performance:' in line:
                    in_fermat_section = False
                    in_miller_section = False
                
                # Result parsing
                if 'Result:' in line:
                    if 'PROBABLY PRIME' in line:
                        if in_fermat_section:
                            fermat_result = True
                        elif in_miller_section:
                            miller_result = True
                    elif 'COMPOSITE' in line:
                        if in_fermat_section:
                            fermat_result = False
                        elif in_miller_section:
                            miller_result = False
                
                # Time parsing
                if 'Time:' in line and 'ms' in line:
                    try:
                        time_str = line.split('Time:')[1].strip().split()[0]
                        time_ms = float(time_str)
                        if in_fermat_section:
                            fermat_time = time_ms
                        elif in_miller_section:
                            miller_time = time_ms
                    except:
                        pass
            
            return {
                'success': True,
                'fermat_result': fermat_result,
                'miller_result': miller_result,
                'fermat_time': fermat_time,
                'miller_time': miller_time
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def analyze_accuracy_small_numbers(self, k: int = 10):
        """
        Analyze accuracy on small numbers dataset.
        Focus: Fermat vs Miller-Rabin accuracy, especially on Carmichael numbers.
        """
        print("\n" + "="*70)
        print("ACCURACY ANALYSIS - SMALL NUMBERS")
        print("="*70)
        print(f"Testing with k={k} iterations\n")
        
        # Load dataset
        dataset_path = Path("../data/test_cases_small.csv")
        if not dataset_path.exists():
            print(f"Dataset not found: {dataset_path}")
            print("Run: python comprehensive_dataset_generator.py")
            return
        
        with open(dataset_path, 'r') as f:
            reader = csv.DictReader(f)
            test_cases = list(reader)
        
        print(f"Loaded {len(test_cases)} test cases")
        
        # Statistics by category
        stats = defaultdict(lambda: {
            'total': 0,
            'fermat_correct': 0,
            'miller_correct': 0,
            'fermat_fp': 0,
            'miller_fp': 0
        })
        
        # Test each number
        success_count = 0
        for i, case in enumerate(test_cases):
            number = int(case['number'])
            is_prime = case['is_prime'] == 'True'
            category = case['category']
            
            if (i + 1) % 50 == 0:
                print(f"Progress: {i+1}/{len(test_cases)} (successful: {success_count})")
            
            result = self.run_cpp_test(number, k)
            
            if not result.get('success'):
                print(f"  Failed on {number}: {result.get('error', 'unknown error')}")
                continue
            
            fermat_result = result['fermat_result']
            miller_result = result['miller_result']
            
            if fermat_result is None or miller_result is None:
                print(f"  Parse error on {number}: fermat={fermat_result}, miller={miller_result}")
                continue
            
            success_count += 1
            
            stats[category]['total'] += 1
            
            # Check correctness
            if fermat_result == is_prime:
                stats[category]['fermat_correct'] += 1
            if miller_result == is_prime:
                stats[category]['miller_correct'] += 1
            
            # Check false positives (composite called prime)
            if not is_prime:
                if fermat_result:
                    stats[category]['fermat_fp'] += 1
                if miller_result:
                    stats[category]['miller_fp'] += 1
        
        # Print results
        print("\n" + "="*70)
        print("RESULTS BY CATEGORY")
        print("="*70)
        
        for category in sorted(stats.keys()):
            s = stats[category]
            total = s['total']
            if total == 0:
                continue
            
            fermat_acc = 100.0 * s['fermat_correct'] / total
            miller_acc = 100.0 * s['miller_correct'] / total
            fermat_fpr = 100.0 * s['fermat_fp'] / total if total > 0 else 0
            miller_fpr = 100.0 * s['miller_fp'] / total if total > 0 else 0
            
            print(f"\n{category.upper()} ({total} cases):")
            print(f"  Fermat:       {fermat_acc:6.2f}% accuracy, {fermat_fpr:6.2f}% FP rate")
            print(f"  Miller-Rabin: {miller_acc:6.2f}% accuracy, {miller_fpr:6.2f}% FP rate")
        
        # Overall statistics
        print("\n" + "="*70)
        print("OVERALL STATISTICS")
        print("="*70)
        
        total_correct_fermat = sum(s['fermat_correct'] for s in stats.values())
        total_correct_miller = sum(s['miller_correct'] for s in stats.values())
        total_tests = sum(s['total'] for s in stats.values())
        
        print(f"\nOverall accuracy:")
        print(f"  Fermat:       {100.0 * total_correct_fermat / total_tests:.2f}%")
        print(f"  Miller-Rabin: {100.0 * total_correct_miller / total_tests:.2f}%")
        
        # Carmichael analysis
        if 'carmichael' in stats:
            c = stats['carmichael']
            print(f"\nCarmichael Numbers Analysis:")
            print(f"  Total tested: {c['total']}")
            print(f"  Fermat failures: {c['fermat_fp']} ({100.0*c['fermat_fp']/c['total']:.1f}%)")
            print(f"  Miller-Rabin failures: {c['miller_fp']} ({100.0*c['miller_fp']/c['total']:.1f}%)")
    
    def analyze_asymptotic_large_numbers(self, k: int = 10, samples_per_magnitude: int = 3):
        """
        Analyze asymptotic complexity on large numbers.
        Focus: Measure execution time vs input size.
        """
        print("\n" + "="*70)
        print("ASYMPTOTIC COMPLEXITY ANALYSIS - LARGE NUMBERS")
        print("="*70)
        print(f"Testing with k={k} iterations, {samples_per_magnitude} samples per magnitude\n")
        
        # Load dataset
        dataset_path = Path("../data/test_cases_large.csv")
        if not dataset_path.exists():
            print(f"Dataset not found: {dataset_path}")
            print("Run: python comprehensive_dataset_generator.py")
            return
        
        with open(dataset_path, 'r') as f:
            reader = csv.DictReader(f)
            test_cases = list(reader)
        
        # Group by magnitude
        by_magnitude = defaultdict(list)
        for case in test_cases:
            mag = int(case['magnitude'])
            by_magnitude[mag].append(int(case['number']))
        
        print(f"Testing {len(by_magnitude)} different magnitudes...")
        
        results = []
        
        for magnitude in sorted(by_magnitude.keys()):
            numbers = by_magnitude[magnitude]
            sample = numbers[:samples_per_magnitude]
            
            print(f"\n10^{magnitude-1} ({magnitude} digits) - Testing {len(sample)} numbers:")
            
            for num in sample:
                result = self.run_cpp_test(num, k)
                
                if result.get('success'):
                    fermat_time = result.get('fermat_time', 0)
                    miller_time = result.get('miller_time', 0)
                    
                    results.append({
                        'number': num,
                        'magnitude': magnitude,
                        'log_n': math.log10(num),
                        'fermat_ms': fermat_time,
                        'miller_ms': miller_time
                    })
                    
                    print(f"  {num:>20,}: Fermat={fermat_time:.4f}ms, Miller={miller_time:.4f}ms")
        
        # Save results
        output_file = resolve_results_path("comprehensive/asymptotic_analysis.csv")
        ensure_parent_dir(output_file)
        
        with open(output_file, 'w', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        print(f"\nResults saved to {format_path(output_file)}")
        
        # Analyze complexity
        if len(results) >= 2:
            print("\n" + "="*70)
            print("COMPLEXITY ANALYSIS")
            print("="*70)
            
            import numpy as np
            
            log_n = np.array([r['log_n'] for r in results])
            log_time_fermat = np.array([math.log10(r['fermat_ms']) for r in results if r['fermat_ms'] > 0])
            
            if len(log_time_fermat) >= 2:
                coeffs = np.polyfit(log_n[:len(log_time_fermat)], log_time_fermat, 1)
                slope = coeffs[0]
                
                print(f"\nEmpirical complexity (Fermat test):")
                print(f"  Slope on log-log plot: {slope:.2f}")
                print(f"  Theoretical slope for O(log³n): 3.0")
                
                if abs(slope - 3.0) < 0.5:
                    print(f"  ✓ MATCHES theoretical prediction!")
                elif slope < 1.0:
                    print(f"  ⚠ Much flatter - 64-bit arithmetic runs in near-constant time")
                    print(f"    This is EXPECTED for numbers < 2^64")
                else:
                    print(f"  ⚠ Deviation from theory")
                
                # Show actual slowdown
                min_time = min(r['fermat_ms'] for r in results)
                max_time = max(r['fermat_ms'] for r in results)
                min_n = min(r['number'] for r in results)
                max_n = max(r['number'] for r in results)
                
                print(f"\nActual measurements:")
                print(f"  Smallest number: {min_n:,} -> {min_time:.4f} ms")
                print(f"  Largest number:  {max_n:,} -> {max_time:.4f} ms")
                print(f"  Input size increase: {max_n/min_n:.2e}x")
                print(f"  Time increase: {max_time/min_time:.2f}x")
                
                expected_slowdown = (math.log2(max_n) / math.log2(min_n)) ** 3
                print(f"  Expected slowdown (O(log³n)): {expected_slowdown:.1f}x")


def main():
    """Run comprehensive analysis."""
    analyzer = ComprehensiveAnalyzer()
    
    print("="*70)
    print("COMPREHENSIVE PRIMALITY TESTING ANALYSIS")
    print("="*70)
    
    # Check if datasets exist
    small_exists = Path("../data/test_cases_small.csv").exists()
    large_exists = Path("../data/test_cases_large.csv").exists()
    
    if not (small_exists and large_exists):
        print("\nDatasets not found! Generating...")
        import comprehensive_dataset_generator
        comprehensive_dataset_generator.main()
    
    # Run both analyses
    analyzer.analyze_accuracy_small_numbers(k=10)
    analyzer.analyze_asymptotic_large_numbers(k=10, samples_per_magnitude=3)
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()
