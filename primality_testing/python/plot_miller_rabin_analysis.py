#!/usr/bin/env python3

import csv
import subprocess
import sys
import math
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

from path_utils import ensure_parent_dir, format_path, resolve_results_path


class MillerRabinAnalyzer:
    """Generate all plots for Miller-Rabin test analysis."""
    
    def __init__(self):
        try:
            import shutil
            self.use_wsl = shutil.which('wsl') is not None
        except Exception:
            self.use_wsl = False
        self.output_dir = resolve_results_path("miller_rabin_analysis/plots")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_plot(self, relative_path: str, *, fig=None, dpi: int = 300, bbox_inches: str = 'tight') -> None:
        """Save plot to output directory."""
        output_path = self.output_dir / relative_path
        ensure_parent_dir(output_path)
        target = fig if fig is not None else plt
        target.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
        print(f"\n✓ Saved: {format_path(output_path)}")
    
    def run_miller_rabin_test(self, number: int, k: int) -> Dict:
        """Run C++ Miller-Rabin test on a single number."""
        try:
            import os, shutil
            script_dir = Path(__file__).resolve().parent
            repo_root = script_dir.parent
            cpp_dir = repo_root / 'cpp'

            if self.use_wsl and shutil.which('wsl'):
                cpp_path_wsl = str(cpp_dir).replace('C:', '/mnt/c').replace('c:', '/mnt/c').replace('\\', '/')
                cmd = f'wsl -e bash -c "cd {cpp_path_wsl} && ./primality_test {number} {k}"'
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
            else:
                cmd = f'cd "{cpp_dir}" && ./primality_test {number} {k}'
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
            
            # Parse Miller-Rabin output
            lines = result.stdout.split('\n')
            miller_result = None
            miller_time = None
            
            in_miller_section = False
            
            for line in lines:
                if 'Miller-Rabin Test:' in line:
                    in_miller_section = True
                elif 'Ground Truth:' in line:
                    in_miller_section = False
                
                if in_miller_section:
                    if 'Result:' in line:
                        miller_result = 'PROBABLY PRIME' in line or 'PRIME' in line
                    elif 'Time:' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            time_str = parts[1].strip().split()[0]
                            miller_time = float(time_str)
            
            return {
                'is_prime': miller_result,
                'time_ms': miller_time or 0.0
            }
        except Exception as e:
            print(f"Warning: Failed to run Miller-Rabin test: {e}")
            return {'is_prime': None, 'time_ms': 0.0}
    
    def load_test_data(self) -> List[Dict]:
        """Load test cases from CSV."""
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent
        data_path = repo_root / 'data' / 'test_cases.csv'
        
        if not data_path.exists():
            print(f"Error: {data_path} not found!")
            return []
        
        test_cases = []
        with open(data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle both "True"/"False" strings and "1"/"0" integers
                is_prime_str = row['is_prime'].strip()
                if is_prime_str.lower() in ('true', '1'):
                    is_prime = True
                elif is_prime_str.lower() in ('false', '0'):
                    is_prime = False
                else:
                    is_prime = int(is_prime_str) == 1
                
                test_cases.append({
                    'number': int(row['number']),
                    'is_prime': is_prime,
                    'category': row['category']
                })
        
        return test_cases
    
    def plot_accuracy_vs_k(self):
        """Plot 1: Miller-Rabin accuracy vs iterations (should be 100% for all k)."""
        print("\n" + "="*70)
        print("PLOT 1: Miller-Rabin Accuracy vs k (iterations)")
        print("="*70)
        
        test_cases = self.load_test_data()
        if not test_cases:
            return
        
        k_values = [1, 2, 3, 5, 10, 20, 30, 50]
        accuracies = []
        
        for k in k_values:
            print(f"Testing with k={k}...")
            correct = 0
            total = 0
            
            for case in test_cases[:100]:  # Sample for speed
                result = self.run_miller_rabin_test(case['number'], k)
                if result['is_prime'] is not None:
                    if result['is_prime'] == case['is_prime']:
                        correct += 1
                    total += 1
            
            accuracy = (correct / total * 100) if total > 0 else 0
            accuracies.append(accuracy)
            print(f"  Accuracy: {accuracy:.2f}%")
        
        # Plot
        plt.figure(figsize=(10, 6))
        plt.plot(k_values, accuracies, 'o-', linewidth=2, markersize=8, color='darkblue', label='Miller-Rabin')
        plt.axhline(y=100, color='green', linestyle='--', alpha=0.5, label='Perfect Accuracy')
        plt.xlabel('Number of Iterations (k)', fontsize=12)
        plt.ylabel('Accuracy (%)', fontsize=12)
        plt.title('Miller-Rabin: Accuracy vs Iterations\n(Should be 100% for all k)', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.ylim([95, 101])
        plt.legend()
        plt.tight_layout()
        
        self._save_plot('miller_rabin_accuracy_vs_k.png')
        plt.close()
    
    def plot_false_positive_rates(self):
        """Plot 2: False positive rates by category (should be 0% for all)."""
        print("\n" + "="*70)
        print("PLOT 2: Miller-Rabin False Positive Rates by Category")
        print("="*70)
        
        test_cases = self.load_test_data()
        if not test_cases:
            return
        
        k = 10
        category_stats = defaultdict(lambda: {'fp': 0, 'total': 0})
        
        for case in test_cases:
            if not case['is_prime']:  # Only test composites
                result = self.run_miller_rabin_test(case['number'], k)
                category = case['category']
                
                if result['is_prime'] is not None:
                    category_stats[category]['total'] += 1
                    if result['is_prime']:  # False positive
                        category_stats[category]['fp'] += 1
        
        # Calculate rates
        categories = []
        fp_rates = []
        
        for cat in ['carmichael', 'composite', 'pseudoprime']:
            if cat in category_stats and category_stats[cat]['total'] > 0:
                total = category_stats[cat]['total']
                fp = category_stats[cat]['fp']
                rate = (fp / total * 100)
                categories.append(cat.capitalize())
                fp_rates.append(rate)
                print(f"{cat}: {rate:.2f}% ({fp}/{total})")
        
        # Plot
        plt.figure(figsize=(10, 6))
        bars = plt.bar(categories, fp_rates, color=['#2E86AB', '#A23B72', '#F18F01'], alpha=0.8)
        plt.xlabel('Number Category', fontsize=12)
        plt.ylabel('False Positive Rate (%)', fontsize=12)
        plt.title('Miller-Rabin: False Positive Rates by Category\n(k=10, Should be 0% for all)', 
                 fontsize=14, fontweight='bold')
        plt.ylim([0, 5])
        plt.grid(True, axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}%', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        self._save_plot('miller_rabin_false_positive_rates.png')
        plt.close()
    
    def plot_asymptotic_complexity(self):
        """Plot 3: Asymptotic complexity analysis."""
        print("\n" + "="*70)
        print("PLOT 3: Miller-Rabin Asymptotic Complexity")
        print("="*70)
        
        # Read from comprehensive asymptotic analysis if available
        comprehensive_file = resolve_results_path("comprehensive/asymptotic_analysis.csv")
        
        if not comprehensive_file.exists():
            print("Error: asymptotic_analysis.csv not found. Run comprehensive_analysis.py first.")
            return
        
        # Parse CSV
        magnitudes = []
        miller_times = []
        
        with open(comprehensive_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                magnitudes.append(int(row['magnitude']))
                # Column is named 'miller_ms' in the CSV
                miller_times.append(float(row['miller_ms']))
        
        if not magnitudes or not miller_times:
            print("Error: No data found in asymptotic_analysis.csv")
            return
        
        # Theoretical O(log n) curve
        magnitudes_np = np.array(magnitudes)
        theoretical = miller_times[0] * (magnitudes_np / magnitudes_np[0])
        
        # Plot
        plt.figure(figsize=(10, 6))
        plt.plot(magnitudes, miller_times, 'o-', linewidth=2, markersize=8, 
                color='darkblue', label='Miller-Rabin (Measured)')
        plt.plot(magnitudes, theoretical, '--', linewidth=2, alpha=0.7,
                color='red', label='O(log n) Theoretical')
        
        plt.xlabel('Input Magnitude (log₁₀n)', fontsize=12)
        plt.ylabel('Execution Time (ms)', fontsize=12)
        plt.title('Miller-Rabin: Asymptotic Time Complexity', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        self._save_plot('miller_rabin_asymptotic_complexity.png')
        plt.close()
    
    def plot_time_distribution(self):
        """Plot 5: Execution time distribution across different input sizes."""
        print("\n" + "="*70)
        print("PLOT 5: Miller-Rabin Execution Time Distribution")
        print("="*70)
        
        k = 10
        magnitudes = [3, 5, 7, 9, 11]
        test_numbers = [
            [1009, 1021, 1031, 1033],
            [100003, 100019, 100043, 100049],
            [10000019, 10000079, 10000103, 10000121],
            [1000000007, 1000000009, 1000000021, 1000000033],
            [100000000003, 100000000019, 100000000057, 100000000063]
        ]
        
        data = []
        for magnitude, numbers in zip(magnitudes, test_numbers):
            times = []
            for num in numbers:
                for _ in range(5):  # Multiple runs
                    result = self.run_miller_rabin_test(num, k)
                    if result['time_ms'] > 0:
                        times.append(result['time_ms'])
            data.append(times)
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        bp = ax.boxplot(data, tick_labels=[f'10^{m}' for m in magnitudes],
                       patch_artist=True, showmeans=True)
        
        # Customize colors
        for patch in bp['boxes']:
            patch.set_facecolor('#2E86AB')
            patch.set_alpha(0.7)
        
        ax.set_xlabel('Input Magnitude', fontsize=12)
        ax.set_ylabel('Execution Time (ms)', fontsize=12)
        ax.set_title('Miller-Rabin: Execution Time Distribution\n(k=10, logarithmic scale)', 
                    fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        self._save_plot('miller_rabin_time_distribution.png')
        plt.close()
    
    def generate_summary_statistics(self):
        """Generate summary statistics CSV."""
        print("\n" + "="*70)
        print("GENERATING SUMMARY STATISTICS")
        print("="*70)
        
        test_cases = self.load_test_data()
        k_values = [1, 5, 10, 20, 50]
        
        summary = []
        for k in k_values:
            correct = 0
            total = 0
            false_positives = 0
            false_negatives = 0
            total_time = 0
            
            for case in test_cases[:100]:
                result = self.run_miller_rabin_test(case['number'], k)
                if result['is_prime'] is not None:
                    total += 1
                    total_time += result['time_ms']
                    
                    if result['is_prime'] == case['is_prime']:
                        correct += 1
                    elif result['is_prime'] and not case['is_prime']:
                        false_positives += 1
                    elif not result['is_prime'] and case['is_prime']:
                        false_negatives += 1
            
            accuracy = (correct / total * 100) if total > 0 else 0
            avg_time = (total_time / total) if total > 0 else 0
            
            summary.append({
                'k': k,
                'accuracy': f"{accuracy:.2f}%",
                'false_positives': false_positives,
                'false_negatives': false_negatives,
                'avg_time_ms': f"{avg_time:.4f}"
            })
        
        # Save to CSV
        output_file = resolve_results_path("miller_rabin_analysis/miller_rabin_summary_statistics.csv")
        ensure_parent_dir(output_file)
        
        with open(output_file, 'w', newline='') as f:
            if summary:
                writer = csv.DictWriter(f, fieldnames=summary[0].keys())
                writer.writeheader()
                writer.writerows(summary)
        
        print(f"\n✓ Saved: {format_path(output_file)}")
    
    def generate_all_plots(self):
        """Generate all Miller-Rabin analysis plots."""
        print("\n" + "="*70)
        print("MILLER-RABIN PRIMALITY TEST - COMPREHENSIVE ANALYSIS")
        print("="*70)
        
        self.plot_accuracy_vs_k()
        self.plot_false_positive_rates()
        self.plot_asymptotic_complexity()
        self.plot_time_distribution()
        self.generate_summary_statistics()
        
        print("\n" + "="*70)
        print("ALL MILLER-RABIN ANALYSIS PLOTS GENERATED!")
        print("="*70)
        print(f"Plots saved in: {format_path(self.output_dir)}")
        print("Generated figures:")
        print("  1. miller_rabin_accuracy_vs_k.png")
        print("  2. miller_rabin_false_positive_rates.png")
        print("  3. miller_rabin_asymptotic_complexity.png")
        print("  4. miller_rabin_time_distribution.png")
        print(f"Summary statistics: {format_path(resolve_results_path('miller_rabin_analysis/miller_rabin_summary_statistics.csv'))}")


def main():
    analyzer = MillerRabinAnalyzer()
    analyzer.generate_all_plots()


if __name__ == '__main__':
    main()
