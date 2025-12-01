#!/usr/bin/env python3

import csv
import subprocess
import sys
import math
from pathlib import Path
from typing import List, Dict
import matplotlib.pyplot as plt
import numpy as np
from path_utils import resolve_results_path, ensure_parent_dir, format_path


class AsymptoticBenchmark:
    """Benchmarks for asymptotic complexity analysis."""
    
    def __init__(self, cpp_binary: str = None):
        if cpp_binary is None:
            # Try to find the executable
            import platform
            import os
            if platform.system() == "Windows":
                # Check for WSL or native Windows executable
                possible_paths = [
                    "../cpp/primality_test",
                    "../cpp/main",
                    "../cpp/primality_test.exe",
                    "../cpp/main.exe",
                    "./build/primality_test.exe",
                    "./build/primality_test"
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        cpp_binary = path
                        break
                if cpp_binary is None:
                    cpp_binary = "../cpp/primality_test"  # Default, will use WSL
            else:
                cpp_binary = "../cpp/primality_test"
        
        self.cpp_binary = cpp_binary
        self.use_wsl = False
        
        # Check if we need to use WSL
        import platform
        import os
        if platform.system() == "Windows" and not os.path.exists(self.cpp_binary):
            self.use_wsl = True
        
        self.results_dir = resolve_results_path("asymptotic")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        if self.use_wsl:
            print(f"Using C++ binary via WSL: {self.cpp_binary}")
        else:
            print(f"Using C++ binary: {self.cpp_binary}")
    
    def run_cpp_test(self, number: int, k: int = 10) -> Dict:
        """Run C++ test on a single number."""
        try:
            import os
            
            # For Windows with WSL
            if self.use_wsl:
                # Convert path for WSL
                cwd = os.getcwd().replace('\\', '/')
                wsl_path = cwd.replace('C:', '/mnt/c').replace('c:', '/mnt/c')
                cpp_dir = wsl_path.replace('/python', '/cpp')
                
                cmd = f'wsl -e bash -c "cd {cpp_dir} && ./primality_test {number} {k}"'
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    shell=True
                )
            else:
                result = subprocess.run(
                    [self.cpp_binary, str(number), str(k)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            
            # Parse output for timing
            lines = result.stdout.split('\n')
            fermat_time = None
            miller_time = None
            
            for line in lines:
                if 'Time:' in line and 'ms' in line:
                    time_ms = float(line.split()[-2])
                    if fermat_time is None:
                        fermat_time = time_ms
                    elif miller_time is None:
                        miller_time = time_ms
            
            return {
                'success': True,
                'fermat_time': fermat_time,
                'miller_time': miller_time
            }
        except Exception as e:
            print(f"  Error testing {number}: {e}")
            return {'success': False}
    
    def benchmark_scaling(self, test_file: str = "../data/test_cases_large.csv", 
                         k: int = 10, runs_per_number: int = 10) -> None:
        """
        Benchmark scaling behavior across different magnitudes.
        
        Args:
            test_file: CSV file with test cases
            k: Number of iterations for primality tests
            runs_per_number: Number of times to run each test for averaging
        """
        print("\n" + "="*70)
        print("ASYMPTOTIC COMPLEXITY BENCHMARK")
        print("="*70)
        print(f"k={k}, runs per number={runs_per_number}")
        
        # Load test cases
        with open(test_file, 'r') as f:
            reader = csv.DictReader(f)
            test_cases = list(reader)
        
        # Group by magnitude
        by_magnitude = {}
        for row in test_cases:
            mag = int(row['magnitude'])
            if mag not in by_magnitude:
                by_magnitude[mag] = []
            by_magnitude[mag].append(int(row['number']))
        
        results = []
        
        print("\nTesting numbers by magnitude...")
        for magnitude in sorted(by_magnitude.keys()):
            numbers = by_magnitude[magnitude]
            
            # Test a sample (e.g., first 3 from each magnitude)
            sample = numbers[:3]
            
            for num in sample:
                print(f"  Testing 10^{magnitude-1} ({num})...", end=' ', flush=True)
                
                fermat_times = []
                miller_times = []
                
                for run in range(runs_per_number):
                    result = self.run_cpp_test(num, k)
                    
                    if result.get('success'):
                        if result.get('fermat_time') is not None:
                            fermat_times.append(result['fermat_time'])
                        if result.get('miller_time') is not None:
                            miller_times.append(result['miller_time'])
                
                if fermat_times:
                    avg_fermat = sum(fermat_times) / len(fermat_times)
                    avg_miller = sum(miller_times) / len(miller_times) if miller_times else 0
                    
                    results.append({
                        'number': num,
                        'magnitude': magnitude,
                        'log_n': math.log10(num),
                        'avg_fermat_ms': avg_fermat,
                        'avg_miller_ms': avg_miller,
                        'runs': len(fermat_times)
                    })
                    
                    print(f"Fermat: {avg_fermat:.4f}ms, Miller: {avg_miller:.4f}ms")
                else:
                    print("FAILED")
        
        # Save results
        output_file = self.results_dir / "asymptotic_scaling.csv"
        with open(output_file, 'w', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        print(f"\nResults saved to {output_file}")
        
        # Analyze complexity
        self.analyze_complexity(results)
        
        # Plot results
        self.plot_asymptotic_behavior(results)
    
    def analyze_complexity(self, results: List[Dict]) -> None:
        """Analyze and print complexity analysis."""
        print("\n" + "="*70)
        print("COMPLEXITY ANALYSIS")
        print("="*70)
        
        if len(results) < 2:
            print("Not enough data for analysis")
            return
        
        # Compute empirical slope on log-log plot
        log_n = np.array([r['log_n'] for r in results])
        log_time = np.array([math.log10(r['avg_fermat_ms']) for r in results if r['avg_fermat_ms'] > 0])
        
        if len(log_time) >= 2:
            # Linear regression on log-log plot
            coeffs = np.polyfit(log_n[:len(log_time)], log_time, 1)
            slope = coeffs[0]
            
            print(f"\nEmpirical complexity (Fermat test):")
            print(f"  Slope on log-log plot: {slope:.2f}")
            print(f"  Theoretical slope for O(log³n): ~3.0")
            
            if abs(slope - 3.0) < 0.5:
                print(f"  ✓ MATCHES theoretical prediction!")
            elif slope < 1.0:
                print(f"  ⚠ Much flatter than expected - still in constant-time regime")
            else:
                print(f"  ⚠ Deviation from theory (hardware effects or insufficient range)")
    
    def plot_asymptotic_behavior(self, results: List[Dict]) -> None:
        """Plot time vs input size to visualize complexity."""
        if not results:
            print("No results to plot")
            return
        
        print("\nGenerating plots...")
        
        magnitudes = [r['magnitude'] for r in results]
        fermat_times = [r['avg_fermat_ms'] for r in results]
        miller_times = [r['avg_miller_ms'] for r in results]
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Linear scale
        axes[0].scatter(magnitudes, fermat_times, label='Fermat', alpha=0.6, s=50)
        axes[0].scatter(magnitudes, miller_times, label='Miller-Rabin', alpha=0.6, s=50)
        axes[0].set_xlabel('Magnitude (digits)')
        axes[0].set_ylabel('Time (ms)')
        axes[0].set_title('Execution Time vs Input Size')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Log-log scale
        log_n = [r['log_n'] for r in results]
        axes[1].scatter(log_n, fermat_times, label='Fermat', alpha=0.6, s=50)
        axes[1].scatter(log_n, miller_times, label='Miller-Rabin', alpha=0.6, s=50)
        axes[1].set_xlabel('log₁₀(n)')
        axes[1].set_ylabel('Time (ms)')
        axes[1].set_yscale('log')
        axes[1].set_title('Log-Log Plot (slope ≈ 3 for O(log³n))')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, which='both')
        
        # Add theoretical O(log³n) reference line
        if log_n:
            min_log = min(log_n)
            max_log = max(log_n)
            x_theory = np.linspace(min_log, max_log, 100)
            # Normalize to match first data point
            if fermat_times[0] > 0:
                scale = fermat_times[0] / (log_n[0] ** 3)
                y_theory = scale * (x_theory ** 3)
                axes[1].plot(x_theory, y_theory, 'r--', alpha=0.5, label='O(log³n) reference')
                axes[1].legend()
        
        plt.tight_layout()
        
        output_file = self.results_dir / "asymptotic_plot.png"
        plt.savefig(output_file, dpi=150)
        print(f"Plot saved to {output_file}")
        plt.close()


def main():
    """Main execution."""
    import sys
    
    if len(sys.argv) > 1:
        cpp_binary = sys.argv[1]
    else:
        cpp_binary = "./build/primality_test"
    
    benchmark = AsymptoticBenchmark(cpp_binary)
    
    # Check if large dataset exists
    large_dataset = Path("../data/test_cases_large.csv")
    if not large_dataset.exists():
        print("Large dataset not found. Generating...")
        import large_number_generator
        large_number_generator.main()
    
    # Run benchmark
    benchmark.benchmark_scaling(
        test_file=str(large_dataset),
        k=10,
        runs_per_number=5  # Fewer runs for large numbers (they take longer)
    )


if __name__ == "__main__":
    main()
