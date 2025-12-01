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


class FermatAnalyzer:
    """Generate all plots for Fermat test analysis."""
    
    def __init__(self):
        # Auto-detect whether WSL is available; on native Linux/macOS run binaries directly
        try:
            import shutil
            self.use_wsl = shutil.which('wsl') is not None
        except Exception:
            self.use_wsl = False
        self.output_dir = resolve_results_path("fermat_analysis/plots")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_plot(self, relative_path: str, *, fig=None, dpi: int = 300, bbox_inches: str = 'tight') -> None:
        """Persist the current plot under the shared results directory."""
        output_path = self.output_dir / relative_path
        ensure_parent_dir(output_path)
        target = fig if fig is not None else plt
        target.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
        print(f"\n✓ Saved: {format_path(output_path)}")
    
    def run_fermat_test(self, number: int, k: int) -> Dict:
        """Run C++ Fermat test on a single number."""
        try:
            import os, shutil
            # Resolve the cpp directory relative to this script reliably
            script_dir = Path(__file__).resolve().parent
            repo_root = script_dir.parent
            cpp_dir = repo_root / 'cpp'

            if self.use_wsl and shutil.which('wsl'):
                # When running on Windows + WSL, invoke via wsl
                cpp_path_wsl = str(cpp_dir).replace('C:', '/mnt/c').replace('c:', '/mnt/c').replace('\\', '/')
                cmd = f'wsl -e bash -c "cd {cpp_path_wsl} && ./primality_test {number} {k}"'
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
            else:
                # Run the binary directly on native Unix (Linux/macOS)
                cmd = f'cd "{cpp_dir}" && ./primality_test {number} {k}'
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
            
            # Parse Fermat output only
            lines = result.stdout.split('\n')
            fermat_result = None
            fermat_time = None
            
            in_fermat_section = False
            
            for line in lines:
                if 'Fermat Test:' in line:
                    in_fermat_section = True
                elif 'Miller-Rabin Test:' in line:
                    in_fermat_section = False
                
                if in_fermat_section:
                    if 'Result:' in line:
                        if 'PROBABLY PRIME' in line:
                            fermat_result = True
                        elif 'COMPOSITE' in line:
                            fermat_result = False
                    
                    if 'Time:' in line and 'ms' in line:
                        try:
                            time_str = line.split('Time:')[1].strip().split()[0]
                            fermat_time = float(time_str)
                        except:
                            pass
            
            return {
                'success': True,
                'result': fermat_result,
                'time': fermat_time
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def plot_accuracy_vs_k(self):
        """
        Plot 1: Fermat Test Accuracy vs number of iterations (k)
        """
        print("\n" + "="*70)
        print("PLOT 1: Fermat Accuracy vs k (iterations)")
        print("="*70)
        
        # Load small dataset
        dataset_path = Path("../data/test_cases_small.csv")
        with open(dataset_path, 'r') as f:
            reader = csv.DictReader(f)
            test_cases = list(reader)
        
        # Test with different k values
        k_values = [1, 2, 3, 5, 10, 20, 30, 50]
        accuracies = []
        
        for k in k_values:
            print(f"\nTesting with k={k}...")
            correct = 0
            total = 0
            
            # Sample subset for speed
            sample_size = min(100, len(test_cases))
            import random
            random.seed(42)
            sample = random.sample(test_cases, sample_size)
            
            for case in sample:
                number = int(case['number'])
                is_prime = case['is_prime'] == 'True'
                
                result = self.run_fermat_test(number, k)
                if not result.get('success'):
                    continue
                
                total += 1
                if result['result'] == is_prime:
                    correct += 1
            
            if total > 0:
                accuracies.append(100.0 * correct / total)
                print(f"  Accuracy: {accuracies[-1]:.2f}%")
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(k_values, accuracies, 'o-', color='#2E86AB', linewidth=2.5, markersize=10)
        plt.xlabel('Number of Iterations (k)', fontsize=13, fontweight='bold')
        plt.ylabel('Accuracy (%)', fontsize=13, fontweight='bold')
        plt.title('Fermat Primality Test: Accuracy vs Number of Iterations', fontsize=15, fontweight='bold')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.ylim([85, 101])
        plt.xticks(k_values)
        
        # Add value labels
        for i, (k, acc) in enumerate(zip(k_values, accuracies)):
            plt.text(k, acc + 0.5, f'{acc:.1f}%', ha='center', fontsize=9)
        
        self._save_plot("fermat_accuracy_vs_k.png")
        plt.close()
    
    def plot_false_positive_rates(self):
        """
        Plot 2: Fermat False Positive Rates by Number Category
        """
        print("\n" + "="*70)
        print("PLOT 2: Fermat False Positive Rates by Category")
        print("="*70)
        
        # Load small dataset
        dataset_path = Path("../data/test_cases_small.csv")
        with open(dataset_path, 'r') as f:
            reader = csv.DictReader(f)
            test_cases = list(reader)
        
        k = 10
        stats = defaultdict(lambda: {'total': 0, 'false_positives': 0})
        
        for case in test_cases:
            number = int(case['number'])
            is_prime = case['is_prime'] == 'True'
            category = case['category']
            
            # Only count composites for FP rate
            if is_prime:
                continue
            
            result = self.run_fermat_test(number, k)
            if not result.get('success'):
                continue
            
            stats[category]['total'] += 1
            
            if result['result']:  # False positive (composite called prime)
                stats[category]['false_positives'] += 1
        
        # Calculate rates
        categories = []
        fp_rates = []
        counts = []
        
        for category in sorted(stats.keys()):
            s = stats[category]
            if s['total'] == 0:
                continue
            
            categories.append(category.capitalize())
            fp_rates.append(100.0 * s['false_positives'] / s['total'])
            counts.append(s['total'])
            
            print(f"{category}: {fp_rates[-1]:.2f}% ({s['false_positives']}/{s['total']})")
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(12, 7))
        colors = ['#E63946' if rate > 20 else '#F77F00' if rate > 5 else '#06A77D' for rate in fp_rates]
        bars = ax.bar(categories, fp_rates, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
        
        ax.set_xlabel('Number Category', fontsize=13, fontweight='bold')
        ax.set_ylabel('False Positive Rate (%)', fontsize=13, fontweight='bold')
        ax.set_title('Fermat Test: False Positive Rates by Number Category (k=10)', 
                     fontsize=15, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        
        # Rotate x labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, rate, count in zip(bars, fp_rates, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{rate:.1f}%\n(n={count})',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        self._save_plot("fermat_false_positive_rates.png")
        plt.close()
    
    def plot_asymptotic_complexity(self):
        """
        Plot 3: Fermat Test Asymptotic Complexity Analysis
        """
        print("\n" + "="*70)
        print("PLOT 3: Fermat Asymptotic Complexity")
        print("="*70)
        
        # Load results
        results_file = Path("./results/comprehensive/asymptotic_analysis.csv")
        if not results_file.exists():
            print("Error: asymptotic_analysis.csv not found. Run comprehensive_analysis.py first.")
            return
        
        with open(results_file, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
        
        # Extract Fermat data
        numbers = [int(r['number']) for r in results]
        times = [float(r['fermat_ms']) for r in results if float(r['fermat_ms']) > 0]
        log_n = [math.log10(int(r['number'])) for r in results if float(r['fermat_ms']) > 0]
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Left plot: Linear scale
        ax1.scatter(log_n, times, s=80, alpha=0.6, color='#2E86AB', edgecolors='black', linewidth=1)
        ax1.set_xlabel('log₁₀(n) - Input Size', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Execution Time (ms)', fontsize=13, fontweight='bold')
        ax1.set_title('Fermat Test: Execution Time vs Input Size', fontsize=15, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        
        # Add trend line
        z = np.polyfit(log_n, times, 1)
        p = np.poly1d(z)
        ax1.plot(log_n, p(log_n), "r--", alpha=0.8, linewidth=2, label=f'Linear fit')
        ax1.legend(fontsize=11)
        
        # Right plot: Log-log scale
        log_times = [math.log10(t) for t in times if t > 0]
        valid_log_n = log_n[:len(log_times)]
        
        ax2.scatter(valid_log_n, log_times, s=80, alpha=0.6, color='#E63946', edgecolors='black', linewidth=1)
        
        # Fit line and calculate slope
        if len(log_times) >= 2:
            coeffs = np.polyfit(valid_log_n, log_times, 1)
            empirical_slope = coeffs[0]
            
            x_fit = np.linspace(min(valid_log_n), max(valid_log_n), 100)
            ax2.plot(x_fit, np.polyval(coeffs, x_fit), '--', color='blue', linewidth=2.5, 
                    label=f'Empirical: slope = {empirical_slope:.2f}')
            
            # Add theoretical O(log³n) line
            theoretical_slope = 3.0
            y_theory = log_times[0] + theoretical_slope * (x_fit - valid_log_n[0])
            ax2.plot(x_fit, y_theory, ':', color='green', linewidth=2.5, 
                    label=f'Theoretical O(log³n): slope = {theoretical_slope:.1f}')
            
            # Add annotation
            mid_x = (min(valid_log_n) + max(valid_log_n)) / 2
            mid_y = (min(log_times) + max(log_times)) / 2
            ax2.text(mid_x, mid_y, 
                    f'Empirical complexity: O(log^{empirical_slope:.2f}n)',
                    fontsize=12, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax2.set_xlabel('log₁₀(n) - Input Size', fontsize=13, fontweight='bold')
        ax2.set_ylabel('log₁₀(Time in ms)', fontsize=13, fontweight='bold')
        ax2.set_title('Fermat Test: Log-Log Complexity Analysis', fontsize=15, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        self._save_plot("fermat_asymptotic_complexity.png")
        plt.close()
    
    def plot_carmichael_analysis(self):
        """
        Plot 4: Fermat Test Performance on Carmichael Numbers
        """
        print("\n" + "="*70)
        print("PLOT 4: Fermat Test on Carmichael Numbers")
        print("="*70)
        
        # Load small dataset
        dataset_path = Path("../data/test_cases_small.csv")
        with open(dataset_path, 'r') as f:
            reader = csv.DictReader(f)
            carmichael_cases = [r for r in reader if r['category'] == 'carmichael']
        
        print(f"Analyzing {len(carmichael_cases)} Carmichael numbers...")
        
        # Test with multiple k values
        k_values = [1, 5, 10, 20, 50]
        detection_rates = []
        
        for k in k_values:
            print(f"\nTesting with k={k}...")
            detected = 0
            total = 0
            
            for case in carmichael_cases[:20]:  # Sample for speed
                number = int(case['number'])
                result = self.run_fermat_test(number, k)
                
                if not result.get('success'):
                    continue
                
                total += 1
                # Carmichael numbers are composite, so correct answer is False
                if result['result'] == False:
                    detected += 1
            
            if total > 0:
                rate = 100.0 * detected / total
                detection_rates.append(rate)
                print(f"  Detection rate: {rate:.1f}%")
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(range(len(k_values)), detection_rates, 
                     color='#F77F00', alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Number of Iterations (k)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Detection Rate (%)', fontsize=13, fontweight='bold')
        ax.set_title('Fermat Test: Carmichael Number Detection Rate vs k', 
                     fontsize=15, fontweight='bold')
        ax.set_xticks(range(len(k_values)))
        ax.set_xticklabels([f'k={k}' for k in k_values])
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim([0, 105])
        
        # Add value labels
        for i, (bar, rate) in enumerate(zip(bars, detection_rates)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{rate:.1f}%',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Add horizontal line at 100%
        ax.axhline(y=100, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Perfect Detection')
        ax.legend(fontsize=11)
        
        self._save_plot("fermat_carmichael_detection.png")
        plt.close()
    
    def plot_execution_time_distribution(self):
        """
        Plot 5: Distribution of Fermat Test Execution Times
        """
        print("\n" + "="*70)
        print("PLOT 5: Fermat Execution Time Distribution")
        print("="*70)
        
        # Load results
        results_file = resolve_results_path("comprehensive/asymptotic_analysis.csv")
        if not results_file.exists():
            print(f"Error: {format_path(results_file)} not found.")
            return
        
        with open(results_file, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
        
        # Group times by magnitude
        by_magnitude = defaultdict(list)
        for r in results:
            mag = int(r['magnitude'])
            time = float(r['fermat_ms'])
            if time > 0:
                by_magnitude[mag].append(time)
        
        # Create box plot
        fig, ax = plt.subplots(figsize=(14, 7))
        
        magnitudes = sorted(by_magnitude.keys())
        data = [by_magnitude[m] for m in magnitudes]
        
        bp = ax.boxplot(data, labels=[f'10^{m}' for m in magnitudes],
                       patch_artist=True, showmeans=True)
        
        # Color boxes
        for patch in bp['boxes']:
            patch.set_facecolor('#2E86AB')
            patch.set_alpha(0.6)
        
        ax.set_xlabel('Input Size (10^x)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Execution Time (ms)', fontsize=13, fontweight='bold')
        ax.set_title('Fermat Test: Execution Time Distribution by Input Size', 
                     fontsize=15, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3, linestyle='--')
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        self._save_plot("fermat_time_distribution.png")
        plt.close()
    
    def generate_summary_statistics(self):
        """
        Generate summary statistics table
        """
        print("\n" + "="*70)
        print("GENERATING SUMMARY STATISTICS")
        print("="*70)
        
        # Load small dataset
        dataset_path = Path("../data/test_cases_small.csv")
        with open(dataset_path, 'r') as f:
            reader = csv.DictReader(f)
            test_cases = list(reader)
        
        k = 10
        stats = {
            'total': 0,
            'correct': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'true_positives': 0,
            'true_negatives': 0
        }
        
        category_stats = defaultdict(lambda: dict(stats))
        
        for case in test_cases:
            number = int(case['number'])
            is_prime = case['is_prime'] == 'True'
            category = case['category']
            
            result = self.run_fermat_test(number, k)
            if not result.get('success'):
                continue
            
            fermat_says_prime = result['result']
            
            stats['total'] += 1
            category_stats[category]['total'] += 1
            
            if fermat_says_prime == is_prime:
                stats['correct'] += 1
                category_stats[category]['correct'] += 1
            
            if fermat_says_prime and not is_prime:
                stats['false_positives'] += 1
                category_stats[category]['false_positives'] += 1
            elif not fermat_says_prime and is_prime:
                stats['false_negatives'] += 1
                category_stats[category]['false_negatives'] += 1
            elif fermat_says_prime and is_prime:
                stats['true_positives'] += 1
                category_stats[category]['true_positives'] += 1
            elif not fermat_says_prime and not is_prime:
                stats['true_negatives'] += 1
                category_stats[category]['true_negatives'] += 1
        
        # Save to CSV
        output_file = resolve_results_path("fermat_analysis/fermat_summary_statistics.csv")
        ensure_parent_dir(output_file)
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Total', 'Correct', 'Accuracy (%)', 
                           'False Positives', 'False Negatives', 
                           'True Positives', 'True Negatives'])
            
            for category in sorted(category_stats.keys()):
                s = category_stats[category]
                if s['total'] > 0:
                    acc = 100.0 * s['correct'] / s['total']
                    writer.writerow([
                        category.capitalize(),
                        s['total'],
                        s['correct'],
                        f'{acc:.2f}',
                        s['false_positives'],
                        s['false_negatives'],
                        s['true_positives'],
                        s['true_negatives']
                    ])
            
            # Overall
            acc = 100.0 * stats['correct'] / stats['total']
            writer.writerow([
                'OVERALL',
                stats['total'],
                stats['correct'],
                f'{acc:.2f}',
                stats['false_positives'],
                stats['false_negatives'],
                stats['true_positives'],
                stats['true_negatives']
            ])
        
        print(f"\n✓ Saved: {format_path(output_file)}")


def main():
    """Generate all Fermat-focused plots."""
    print("="*70)
    print("FERMAT PRIMALITY TEST - COMPREHENSIVE ANALYSIS")
    print("="*70)
    
    analyzer = FermatAnalyzer()
    
    # Generate all plots
    analyzer.plot_accuracy_vs_k()
    analyzer.plot_false_positive_rates()
    analyzer.plot_asymptotic_complexity()
    analyzer.plot_carmichael_analysis()
    analyzer.plot_execution_time_distribution()
    analyzer.generate_summary_statistics()
    
    print("\n" + "="*70)
    print("ALL FERMAT ANALYSIS PLOTS GENERATED!")
    print("="*70)
    print(f"\nPlots saved in: {format_path(analyzer.output_dir)}")
    print("\nGenerated figures:")
    print("  1. fermat_accuracy_vs_k.png")
    print("  2. fermat_false_positive_rates.png")
    print("  3. fermat_asymptotic_complexity.png")
    print("  4. fermat_carmichael_detection.png")
    print("  5. fermat_time_distribution.png")
    summary_path = resolve_results_path("fermat_analysis/fermat_summary_statistics.csv")
    print(f"\nSummary statistics: {format_path(summary_path)}")


if __name__ == "__main__":
    main()
