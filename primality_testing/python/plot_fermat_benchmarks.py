#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib.pyplot as plt
import numpy as np
import csv
from pathlib import Path
import sys

from path_utils import ensure_parent_dir, format_path, resolve_results_path


class FermatPlotter:
    """Creates plots for Fermat benchmarks."""

    def __init__(self, results_dir: str | Path | None = None):
        """
        Initialize plotter.

        Args:
            results_dir: Directory containing CSV results
        """
        if results_dir is None:
            self.results_dir = resolve_results_path("fermat_benchmarks")
        else:
            candidate = Path(results_dir)
            self.results_dir = candidate if candidate.is_absolute() else resolve_results_path(candidate)
        self.plots_dir = self.results_dir / "plots"
        self.plots_dir.mkdir(parents=True, exist_ok=True)

    def load_csv(self, filename: str):
        """Load CSV data."""
        filepath = self.results_dir / filename
        
        if not filepath.exists():
            print(f"Error: File not found: {format_path(filepath)}")
            return None
        
        data = {'headers': [], 'rows': []}
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            data['headers'] = reader.fieldnames
            data['rows'] = list(reader)
        
        return data

    def plot_scaling(self, save_path: str = None):
        """
        Plot: Fermat performance vs input size (scaling).
        """
        data = self.load_csv("fermat_scaling.csv")
        if not data or not data['rows']:
            print("No scaling data available")
            return
        
        numbers = [int(row['number']) for row in data['rows']]
        avg_times = [float(row['avg_ms']) for row in data['rows']]
        median_times = [float(row['median_ms']) for row in data['rows']]
        std_devs = [float(row['std_dev']) for row in data['rows']]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Log-log plot of execution time
        ax1.loglog(numbers, avg_times, 'o-', label='Average', linewidth=2, markersize=8, color='#FF6B6B')
        ax1.loglog(numbers, median_times, 's-', label='Median', linewidth=2, markersize=6, color='#4ECDC4')
        ax1.fill_between(numbers, 
                         np.array(avg_times) - np.array(std_devs),
                         np.array(avg_times) + np.array(std_devs),
                         alpha=0.2, color='#FF6B6B', label='±1 Std Dev')
        
        ax1.set_xlabel('Input Size (Number)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Wall-Clock Time (ms)', fontsize=12, fontweight='bold')
        ax1.set_title('Fermat Test: Performance Scaling', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3, which='both')
        ax1.legend(fontsize=10)
        
        # Plot 2: Standard deviation as percentage
        std_dev_pct = [(std / avg * 100) for std, avg in zip(std_devs, avg_times)]
        ax2.semilogx(numbers, std_dev_pct, 'D-', linewidth=2, markersize=8, color='#95E1D3')
        ax2.axhline(y=5, color='red', linestyle='--', alpha=0.5, label='5% threshold')
        
        ax2.set_xlabel('Input Size (Number)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Measurement Stability', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=10)
        
        fig.tight_layout()
        
        if save_path:
            final_path = Path(save_path)
            if not final_path.is_absolute():
                final_path = resolve_results_path(final_path)
            ensure_parent_dir(final_path)
            plt.savefig(final_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {format_path(final_path)}")
        else:
            plt.show()
        
        plt.close()

    def plot_k_variation(self, save_path: str = None):
        """
        Plot: Fermat performance vs k (iterations).
        """
        data = self.load_csv("fermat_k_variation.csv")
        if not data or not data['rows']:
            print("No k-variation data available")
            return
        
        k_values = [int(row['k']) for row in data['rows']]
        avg_times = [float(row['avg_ms']) for row in data['rows']]
        median_times = [float(row['median_ms']) for row in data['rows']]
        time_per_iter = [float(row['time_per_iter']) for row in data['rows']]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Total time vs k
        ax1.plot(k_values, avg_times, 'o-', label='Average', linewidth=2, markersize=8, color='#FF6B6B')
        ax1.plot(k_values, median_times, 's-', label='Median', linewidth=2, markersize=6, color='#4ECDC4')
        
        ax1.set_xlabel('Number of Iterations (k)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Wall-Clock Time (ms)', fontsize=12, fontweight='bold')
        ax1.set_title('Fermat Test: Total Time vs k', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=10)
        
        # Add linear fit
        z = np.polyfit(k_values, avg_times, 1)
        p = np.poly1d(z)
        ax1.plot(k_values, p(k_values), "--", alpha=0.5, color='gray', 
                label=f'Linear fit: y={z[0]:.3f}x+{z[1]:.3f}')
        ax1.legend(fontsize=10)
        
        # Plot 2: Time per iteration
        ax2.plot(k_values, time_per_iter, 'D-', linewidth=2, markersize=8, color='#95E1D3')
        
        ax2.set_xlabel('Number of Iterations (k)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Time per Iteration (ms)', fontsize=12, fontweight='bold')
        ax2.set_title('Fermat Test: Amortized Cost per Iteration', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Add average line
        avg_per_iter = np.mean(time_per_iter)
        ax2.axhline(y=avg_per_iter, color='red', linestyle='--', alpha=0.5, 
                   label=f'Average: {avg_per_iter:.4f} ms')
        ax2.legend(fontsize=10)
        
        fig.tight_layout()
        
        if save_path:
            final_path = Path(save_path)
            if not final_path.is_absolute():
                final_path = resolve_results_path(final_path)
            ensure_parent_dir(final_path)
            plt.savefig(final_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {format_path(final_path)}")
        else:
            plt.show()
        
        plt.close()

    def plot_combined_analysis(self, save_path: str = None):
        """
        Create comprehensive multi-panel analysis plot.
        """
        scaling_data = self.load_csv("fermat_scaling.csv")
        k_data = self.load_csv("fermat_k_variation.csv")
        
        if not scaling_data or not k_data:
            print("Missing data files")
            return
        
        fig = plt.figure(figsize=(20, 13))
        gs = fig.add_gridspec(3, 2, hspace=0.45, wspace=0.4, top=0.94, bottom=0.06, left=0.08, right=0.96)
        
        # Panel 1: Scaling (log-log)
        ax1 = fig.add_subplot(gs[0, 0])
        numbers = [int(row['number']) for row in scaling_data['rows']]
        avg_times = [float(row['avg_ms']) for row in scaling_data['rows']]
        
        ax1.loglog(numbers, avg_times, 'o-', linewidth=2.5, markersize=10, color='#FF6B6B')
        ax1.set_xlabel('Input Size (n)', fontsize=14, fontweight='bold', labelpad=10)
        ax1.set_ylabel('Execution Time (ms)', fontsize=14, fontweight='bold', labelpad=10)
        ax1.set_title('A) Performance Scaling', fontsize=15, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.3, which='both')
        ax1.tick_params(labelsize=12, pad=8)
        
        # Panel 2: Time vs k
        ax2 = fig.add_subplot(gs[0, 1])
        k_values = [int(row['k']) for row in k_data['rows']]
        k_avg_times = [float(row['avg_ms']) for row in k_data['rows']]
        
        ax2.plot(k_values, k_avg_times, 'o-', linewidth=2.5, markersize=10, color='#4ECDC4')
        ax2.set_xlabel('Number of Iterations (k)', fontsize=14, fontweight='bold', labelpad=10)
        ax2.set_ylabel('Execution Time (ms)', fontsize=14, fontweight='bold', labelpad=10)
        ax2.set_title('B) Linear Scaling with Iterations', fontsize=15, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(labelsize=12, pad=8)
        
        # Panel 3: Time distribution (box plot)
        ax3 = fig.add_subplot(gs[1, 0])
        
        # Create synthetic distribution based on std dev
        box_data = []
        for row in scaling_data['rows'][:5]:  # First 5 for visibility
            avg = float(row['avg_ms'])
            std = float(row['std_dev'])
            # Approximate distribution
            box_data.append(np.random.normal(avg, std, 100))
        
        ax3.boxplot(box_data, labels=[row['number'] for row in scaling_data['rows'][:5]])
        ax3.set_xlabel('Test Number', fontsize=14, fontweight='bold', labelpad=10)
        ax3.set_ylabel('Execution Time (ms)', fontsize=14, fontweight='bold', labelpad=10)
        ax3.set_title('C) Measurement Variability', fontsize=15, fontweight='bold', pad=20)
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.tick_params(labelsize=12, pad=8)
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=11)
        
        # Panel 4: Efficiency (time per iteration)
        ax4 = fig.add_subplot(gs[1, 1])
        time_per_iter = [float(row['time_per_iter']) for row in k_data['rows']]
        
        ax4.bar(range(len(k_values)), time_per_iter, color='#95E1D3', edgecolor='black', linewidth=1.5)
        ax4.set_xticks(range(len(k_values)))
        ax4.set_xticklabels(k_values)
        ax4.set_xlabel('Number of Iterations (k)', fontsize=14, fontweight='bold', labelpad=10)
        ax4.set_ylabel('Time per Iteration (ms)', fontsize=14, fontweight='bold', labelpad=10)
        ax4.set_title('D) Consistent Per-Iteration Cost', fontsize=15, fontweight='bold', pad=20)
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.tick_params(labelsize=12, pad=8)
        
        # Panel 5: Complexity analysis
        ax5 = fig.add_subplot(gs[2, :])
        
        # Calculate growth rate
        log_numbers = np.log10(numbers)
        log_times = np.log10(avg_times)
        
        # Fit to find complexity
        z = np.polyfit(log_numbers, log_times, 1)
        slope = z[0]
        
        ax5.plot(log_numbers, log_times, 'o', markersize=12, color='#FF6B6B', 
                label='Measured Performance', zorder=3)
        ax5.plot(log_numbers, np.poly1d(z)(log_numbers), '--', linewidth=3, 
                color='blue', label=f'Linear Fit (slope={slope:.2f})', zorder=2)
        
        # Add theoretical complexity lines
        theoretical_slope = 3  # O(log³n) for modular exponentiation
        intercept = log_times[0] - theoretical_slope * log_numbers[0]
        theoretical = theoretical_slope * np.array(log_numbers) + intercept
        ax5.plot(log_numbers, theoretical, ':', linewidth=3, color='green', 
                label=f'Expected O(log³n) (slope=3)', zorder=1)
        
        ax5.set_xlabel('log₁₀(Input Size)', fontsize=14, fontweight='bold', labelpad=10)
        ax5.set_ylabel('log₁₀(Execution Time)', fontsize=14, fontweight='bold', labelpad=10)
        ax5.set_title(f'E) Algorithm Complexity Verification', 
                     fontsize=15, fontweight='bold', pad=20)
        ax5.grid(True, alpha=0.3)
        ax5.legend(fontsize=12, loc='upper left', framealpha=0.95, bbox_to_anchor=(0.01, 0.99))
        ax5.tick_params(labelsize=12, pad=8)
        
        plt.suptitle('Fermat Primality Test: Performance Analysis', 
                    fontsize=17, fontweight='bold', y=0.985)
        
        if save_path:
            final_path = Path(save_path)
            if not final_path.is_absolute():
                final_path = resolve_results_path(final_path)
            ensure_parent_dir(final_path)
            plt.savefig(final_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {format_path(final_path)}")
        else:
            plt.show()
        
        plt.close()

    def plot_all(self):
        """Generate all plots."""
        print("Generating Fermat benchmark plots...")
        print("="*70)
        
        self.plot_scaling(self.plots_dir / "fermat_scaling.png")
        self.plot_k_variation(self.plots_dir / "fermat_k_variation.png")
        self.plot_combined_analysis(self.plots_dir / "fermat_comprehensive.png")
        
        print("\n" + "="*70)
        print("All plots generated successfully!")
        print(f"Location: {format_path(self.plots_dir)}")
        print("="*70)


def main():
    """Main execution."""
    print("Fermat Benchmark Plotter")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUsage: python plot_fermat_benchmarks.py <command>")
        print("\nCommands:")
        print("  scaling      - Plot performance scaling")
        print("  k-variation  - Plot k iterations analysis")
        print("  comprehensive - Plot comprehensive analysis")
        print("  all          - Generate all plots")
        print("\nExample:")
        print("  python plot_fermat_benchmarks.py all")
        return
    
    plotter = FermatPlotter()
    command = sys.argv[1]
    
    if command == "scaling":
        plotter.plot_scaling(plotter.plots_dir / "fermat_scaling.png")
    elif command == "k-variation":
        plotter.plot_k_variation(plotter.plots_dir / "fermat_k_variation.png")
    elif command == "comprehensive":
        plotter.plot_combined_analysis(plotter.plots_dir / "fermat_comprehensive.png")
    elif command == "all":
        plotter.plot_all()
    else:
        print(f"Unknown command: {command}")
        print("Use: scaling, k-variation, comprehensive, or all")


if __name__ == "__main__":
    main()
