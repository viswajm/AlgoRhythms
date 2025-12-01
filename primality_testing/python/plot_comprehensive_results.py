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
from path_utils import resolve_results_path, ensure_parent_dir, format_path


class ComprehensivePlotter:
    """Generate all plots for comprehensive analysis."""
    
    def __init__(self):
        # Auto-detect whether WSL is available
        try:
            import shutil
            self.use_wsl = shutil.which('wsl') is not None
        except Exception:
            self.use_wsl = False
        
        self.output_dir = resolve_results_path("comprehensive/plots")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_cpp_test(self, number: int, k: int) -> Dict:
        """Run C++ test on a single number."""
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
            else:
                # Run the binary directly on native Unix (Linux/macOS)
                cmd = f'cd "{cpp_dir}" && ./primality_test {number} {k}'
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=True)
            
            # Parse output
            lines = result.stdout.split('\n')
            fermat_result = None
            miller_result = None
            fermat_time = None
            miller_time = None
            
            in_fermat_section = False
            in_miller_section = False
            
            for line in lines:
                if 'Fermat Test:' in line:
                    in_fermat_section = True
                    in_miller_section = False
                elif 'Miller-Rabin Test:' in line:
                    in_fermat_section = False
                    in_miller_section = True
                elif 'Performance:' in line:
                    in_fermat_section = False
                    in_miller_section = False
                
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
    
    def plot_accuracy_vs_k(self):
        """
        Plot 1: Accuracy vs number of iterations (k)
        Similar to Figure 1 in the PDF
        """
        print("\n" + "="*70)
        print("PLOT 1: Accuracy vs k (iterations)")
        print("="*70)
        
        # Load small dataset
        dataset_path = Path("../data/test_cases_small.csv")
        with open(dataset_path, 'r') as f:
            reader = csv.DictReader(f)
            test_cases = list(reader)
        
        # Test with different k values
        k_values = [1, 2, 3, 5, 10, 20, 30, 50]
        fermat_accuracies = []
        miller_accuracies = []
        
        for k in k_values:
            print(f"\nTesting with k={k}...")
            correct_fermat = 0
            correct_miller = 0
            total = 0
            
            # Sample subset for speed
            sample_size = min(100, len(test_cases))
            import random
            random.seed(42)
            sample = random.sample(test_cases, sample_size)
            
            for case in sample:
                number = int(case['number'])
                is_prime = case['is_prime'] == 'True'
                
                result = self.run_cpp_test(number, k)
                if not result.get('success'):
                    continue
                
                total += 1
                if result['fermat_result'] == is_prime:
                    correct_fermat += 1
                if result['miller_result'] == is_prime:
                    correct_miller += 1
            
            if total > 0:
                fermat_accuracies.append(100.0 * correct_fermat / total)
                miller_accuracies.append(100.0 * correct_miller / total)
                print(f"  Fermat: {fermat_accuracies[-1]:.2f}%, Miller-Rabin: {miller_accuracies[-1]:.2f}%")
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(k_values, fermat_accuracies, 'o-', label='Fermat Test', linewidth=2, markersize=8)
        plt.plot(k_values, miller_accuracies, 's-', label='Miller-Rabin Test', linewidth=2, markersize=8)
        plt.xlabel('Number of Iterations (k)', fontsize=12)
        plt.ylabel('Accuracy (%)', fontsize=12)
        plt.title('Primality Test Accuracy vs Number of Iterations', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.ylim([85, 101])
        
        output_file = self.output_dir / "accuracy_vs_k.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {output_file}")
        plt.close()
    
    def plot_false_positive_rates(self):
        """
        Plot 2: False Positive Rates by Category
        Similar to Figure 2 in the PDF
        """
        print("\n" + "="*70)
        print("PLOT 2: False Positive Rates by Category")
        print("="*70)
        
        # Load small dataset
        dataset_path = Path("../data/test_cases_small.csv")
        with open(dataset_path, 'r') as f:
            reader = csv.DictReader(f)
            test_cases = list(reader)
        
        k = 10
        stats = defaultdict(lambda: {
            'total': 0,
            'fermat_fp': 0,
            'miller_fp': 0
        })
        
        for case in test_cases:
            number = int(case['number'])
            is_prime = case['is_prime'] == 'True'
            category = case['category']
            
            # Only count composites for FP rate
            if is_prime:
                continue
            
            result = self.run_cpp_test(number, k)
            if not result.get('success'):
                continue
            
            stats[category]['total'] += 1
            
            if result['fermat_result']:  # False positive
                stats[category]['fermat_fp'] += 1
            if result['miller_result']:  # False positive
                stats[category]['miller_fp'] += 1
        
        # Calculate rates
        categories = []
        fermat_rates = []
        miller_rates = []
        
        for category in sorted(stats.keys()):
            s = stats[category]
            if s['total'] == 0:
                continue
            
            categories.append(category.capitalize())
            fermat_rates.append(100.0 * s['fermat_fp'] / s['total'])
            miller_rates.append(100.0 * s['miller_fp'] / s['total'])
            
            print(f"{category}: Fermat={fermat_rates[-1]:.2f}%, Miller-Rabin={miller_rates[-1]:.2f}%")
        
        # Create grouped bar chart
        x = np.arange(len(categories))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width/2, fermat_rates, width, label='Fermat Test', alpha=0.8)
        bars2 = ax.bar(x + width/2, miller_rates, width, label='Miller-Rabin Test', alpha=0.8)
        
        ax.set_xlabel('Number Category', fontsize=12)
        ax.set_ylabel('False Positive Rate (%)', fontsize=12)
        ax.set_title('False Positive Rates by Number Category (k=10)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(True, axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.1f}%',
                           ha='center', va='bottom', fontsize=9)
        
        output_file = self.output_dir / "false_positive_rates.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {output_file}")
        plt.close()
    
    def plot_asymptotic_complexity(self):
        """
        Plot 3: Asymptotic Complexity Analysis
        Similar to Figure 3 in the PDF
        """
        print("\n" + "="*70)
        print("PLOT 3: Asymptotic Complexity Analysis")
        print("="*70)
        
        # Load results
        results_file = resolve_results_path("comprehensive/asymptotic_analysis.csv")
        if not results_file.exists():
            print(f"Error: {format_path(results_file)} not found. Run comprehensive_analysis.py first.")
            return
        
        with open(results_file, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
        
        # Extract data
        numbers = [int(r['number']) for r in results]
        fermat_times = [float(r['fermat_ms']) for r in results if float(r['fermat_ms']) > 0]
        miller_times = [float(r['miller_ms']) for r in results if float(r['miller_ms']) > 0]
        log_n = [math.log10(int(r['number'])) for r in results]
        
        # Create log-log plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Left plot: Linear scale
        ax1.plot(log_n, fermat_times, 'o', label='Fermat Test', alpha=0.6, markersize=6)
        ax1.plot(log_n, miller_times, 's', label='Miller-Rabin Test', alpha=0.6, markersize=6)
        ax1.set_xlabel('log₁₀(n)', fontsize=12)
        ax1.set_ylabel('Time (ms)', fontsize=12)
        ax1.set_title('Execution Time vs Input Size', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        # Right plot: Log-log scale for complexity
        log_fermat_times = [math.log10(t) for t in fermat_times]
        log_miller_times = [math.log10(t) for t in miller_times]
        
        ax2.plot(log_n[:len(log_fermat_times)], log_fermat_times, 'o', label='Fermat Test', alpha=0.6, markersize=6)
        ax2.plot(log_n[:len(log_miller_times)], log_miller_times, 's', label='Miller-Rabin Test', alpha=0.6, markersize=6)
        
        # Fit lines
        if len(log_fermat_times) >= 2:
            coeffs_fermat = np.polyfit(log_n[:len(log_fermat_times)], log_fermat_times, 1)
            coeffs_miller = np.polyfit(log_n[:len(log_miller_times)], log_miller_times, 1)
            
            x_fit = np.linspace(min(log_n), max(log_n), 100)
            ax2.plot(x_fit, np.polyval(coeffs_fermat, x_fit), '--', alpha=0.5, 
                    label=f'Fermat fit (slope={coeffs_fermat[0]:.2f})')
            ax2.plot(x_fit, np.polyval(coeffs_miller, x_fit), '--', alpha=0.5,
                    label=f'Miller-Rabin fit (slope={coeffs_miller[0]:.2f})')
            
            # Add theoretical O(log³n) line
            theoretical_slope = 3.0
            y_theory = log_fermat_times[0] + theoretical_slope * (x_fit - log_n[0])
            ax2.plot(x_fit, y_theory, 'k:', linewidth=2, alpha=0.5, label='Theoretical O(log³n)')
        
        ax2.set_xlabel('log₁₀(n)', fontsize=12)
        ax2.set_ylabel('log₁₀(Time in ms)', fontsize=12)
        ax2.set_title('Log-Log Plot: Empirical Complexity Analysis', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "asymptotic_complexity.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {output_file}")
        plt.close()
    
    def plot_performance_comparison(self):
        """
        Plot 4: Performance Comparison (Fermat vs Miller-Rabin)
        Similar to Figure 4 in the PDF
        """
        print("\n" + "="*70)
        print("PLOT 4: Performance Comparison")
        print("="*70)
        
        # Load results
        results_file = resolve_results_path("comprehensive/asymptotic_analysis.csv")
        if not results_file.exists():
            print(f"Error: {format_path(results_file)} not found.")
            return
        
        with open(results_file, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
        
        # Group by magnitude
        by_magnitude = defaultdict(list)
        for r in results:
            mag = int(r['magnitude'])
            fermat_time = float(r['fermat_ms'])
            miller_time = float(r['miller_ms'])
            if fermat_time > 0 and miller_time > 0:
                by_magnitude[mag].append({
                    'fermat': fermat_time,
                    'miller': miller_time,
                    'ratio': miller_time / fermat_time
                })
        
        # Calculate averages
        magnitudes = []
        avg_fermat = []
        avg_miller = []
        avg_ratio = []
        
        for mag in sorted(by_magnitude.keys()):
            data = by_magnitude[mag]
            magnitudes.append(mag)
            avg_fermat.append(np.mean([d['fermat'] for d in data]))
            avg_miller.append(np.mean([d['miller'] for d in data]))
            avg_ratio.append(np.mean([d['ratio'] for d in data]))
        
        # Create comparison plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Top: Absolute times
        ax1.plot(magnitudes, avg_fermat, 'o-', label='Fermat Test', linewidth=2, markersize=8)
        ax1.plot(magnitudes, avg_miller, 's-', label='Miller-Rabin Test', linewidth=2, markersize=8)
        ax1.set_xlabel('Input Size (10^x)', fontsize=12)
        ax1.set_ylabel('Average Time (ms)', fontsize=12)
        ax1.set_title('Average Execution Time by Input Size', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(magnitudes)
        ax1.set_xticklabels([f'10^{m}' for m in magnitudes], rotation=45, ha='right')
        
        # Bottom: Miller-Rabin overhead
        overhead_pct = [(r - 1) * 100 for r in avg_ratio]
        colors = ['red' if o > 0 else 'green' for o in overhead_pct]
        ax2.bar(magnitudes, overhead_pct, color=colors, alpha=0.6)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_xlabel('Input Size (10^x)', fontsize=12)
        ax2.set_ylabel('Miller-Rabin Overhead (%)', fontsize=12)
        ax2.set_title('Miller-Rabin Performance Overhead vs Fermat', fontsize=14, fontweight='bold')
        ax2.grid(True, axis='y', alpha=0.3)
        ax2.set_xticks(magnitudes)
        ax2.set_xticklabels([f'10^{m}' for m in magnitudes], rotation=45, ha='right')
        
        plt.tight_layout()
        output_file = self.output_dir / "performance_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {output_file}")
        plt.close()
    
    def plot_carmichael_detection(self):
        """
        Plot 5: Carmichael Number Detection Rates
        Additional analysis specific to Carmichael numbers
        """
        print("\n" + "="*70)
        print("PLOT 5: Carmichael Number Detection")
        print("="*70)
        
        # Load small dataset
        dataset_path = Path("../data/test_cases_small.csv")
        with open(dataset_path, 'r') as f:
            reader = csv.DictReader(f)
            carmichael_cases = [r for r in reader if r['category'] == 'carmichael']
        
        print(f"Testing {len(carmichael_cases)} Carmichael numbers...")
        
        k = 10
        detection_by_size = defaultdict(lambda: {'total': 0, 'fermat_caught': 0, 'miller_caught': 0})
        
        for case in carmichael_cases:
            number = int(case['number'])
            
            # Categorize by size
            if number < 1000:
                size_cat = "< 1,000"
            elif number < 10000:
                size_cat = "1K - 10K"
            elif number < 100000:
                size_cat = "10K - 100K"
            elif number < 1000000:
                size_cat = "100K - 1M"
            else:
                size_cat = "> 1M"
            
            result = self.run_cpp_test(number, k)
            if not result.get('success'):
                continue
            
            detection_by_size[size_cat]['total'] += 1
            
            # Carmichael numbers are composite, so correct result is False
            if result['fermat_result'] == False:
                detection_by_size[size_cat]['fermat_caught'] += 1
            if result['miller_result'] == False:
                detection_by_size[size_cat]['miller_caught'] += 1
        
        # Prepare data
        categories = ["< 1,000", "1K - 10K", "10K - 100K", "100K - 1M", "> 1M"]
        fermat_rates = []
        miller_rates = []
        
        for cat in categories:
            stats = detection_by_size[cat]
            if stats['total'] > 0:
                fermat_rates.append(100.0 * stats['fermat_caught'] / stats['total'])
                miller_rates.append(100.0 * stats['miller_caught'] / stats['total'])
            else:
                fermat_rates.append(0)
                miller_rates.append(0)
        
        # Create plot
        x = np.arange(len(categories))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width/2, fermat_rates, width, label='Fermat Test', alpha=0.8)
        bars2 = ax.bar(x + width/2, miller_rates, width, label='Miller-Rabin Test', alpha=0.8)
        
        ax.set_xlabel('Carmichael Number Size Range', fontsize=12)
        ax.set_ylabel('Detection Rate (%)', fontsize=12)
        ax.set_title('Carmichael Number Detection Rates (k=10)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_ylim([0, 105])
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}%',
                       ha='center', va='bottom', fontsize=10)
        
        output_file = self.output_dir / "carmichael_detection.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {output_file}")
        plt.close()


def main():
    """Generate all plots."""
    print("="*70)
    print("COMPREHENSIVE PLOTTING - PUBLICATION QUALITY FIGURES")
    print("="*70)
    
    plotter = ComprehensivePlotter()
    
    # Generate all plots
    plotter.plot_accuracy_vs_k()
    plotter.plot_false_positive_rates()
    plotter.plot_asymptotic_complexity()
    plotter.plot_performance_comparison()
    plotter.plot_carmichael_detection()
    
    print("\n" + "="*70)
    print("ALL PLOTS GENERATED SUCCESSFULLY!")
    print("="*70)
    print(f"\nPlots saved in: {plotter.output_dir}")
    print("\nGenerated figures:")
    print("  1. accuracy_vs_k.png - Accuracy vs number of iterations")
    print("  2. false_positive_rates.png - FP rates by category")
    print("  3. asymptotic_complexity.png - Time complexity analysis")
    print("  4. performance_comparison.png - Fermat vs Miller-Rabin")
    print("  5. carmichael_detection.png - Carmichael number detection")


if __name__ == "__main__":
    main()
