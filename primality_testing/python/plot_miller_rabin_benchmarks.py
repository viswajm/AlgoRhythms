#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

import matplotlib.pyplot as plt
import numpy as np
import csv
from pathlib import Path
import sys

from path_utils import ensure_parent_dir, format_path, resolve_results_path


class MillerRabinPlotter:
    """Creates plots for Miller-Rabin benchmarks."""

    def __init__(self, results_dir: str | Path | None = None):
        """Initialize plotter with results directory."""
        if results_dir is None:
            self.results_dir = resolve_results_path("miller_rabin_benchmarks")
        else:
            candidate = Path(results_dir)
            self.results_dir = candidate if candidate.is_absolute() else resolve_results_path(candidate)
        self.plots_dir = self.results_dir / "plots"
        self.plots_dir.mkdir(parents=True, exist_ok=True)

    def load_csv(self, filename: str):
        """Load CSV data from results directory."""
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
        """Plot Miller-Rabin performance vs input size."""
        data = self.load_csv("miller_rabin_scaling.csv")
        if not data or not data['rows']:
            print("No scaling data available")
            return
        
        numbers = [int(row['number']) for row in data['rows']]
        avg_times = [float(row['avg_ms']) for row in data['rows']]
        median_times = [float(row['median_ms']) for row in data['rows']]
        std_devs = [float(row['std_dev']) for row in data['rows']]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Log-log plot
        ax1.loglog(numbers, avg_times, 'o-', label='Average', linewidth=2, markersize=8, color='#2E86AB')
        ax1.loglog(numbers, median_times, 's-', label='Median', linewidth=2, markersize=6, color='#A23B72')
        ax1.fill_between(numbers, 
                         np.array(avg_times) - np.array(std_devs),
                         np.array(avg_times) + np.array(std_devs),
                         alpha=0.2, color='#2E86AB', label='±1 Std Dev')
        
        ax1.set_xlabel('Input Size (Number)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Wall-Clock Time (ms)', fontsize=12, fontweight='bold')
        ax1.set_title('Miller-Rabin Test: Performance Scaling', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3, which='both')
        ax1.legend(fontsize=10)
        
        # Plot 2: Coefficient of variation
        std_dev_pct = [(std / avg * 100) for std, avg in zip(std_devs, avg_times)]
        ax2.semilogx(numbers, std_dev_pct, 'D-', linewidth=2, markersize=8, color='#F18F01')
        ax2.axhline(y=5, color='red', linestyle='--', alpha=0.5, label='5% threshold')
        
        ax2.set_xlabel('Input Size (Number)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
        ax2.set_title('Measurement Stability', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=10)
        
        fig.tight_layout()
        
        if save_path:
            output_path = self.plots_dir / save_path
        else:
            output_path = self.plots_dir / "miller_rabin_scaling.png"
        
        ensure_parent_dir(output_path)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {format_path(output_path)}")
        plt.close(fig)

    def plot_k_variation(self, save_path: str = None):
        """Plot how performance varies with k (number of iterations)."""
        data = self.load_csv("miller_rabin_k_variation.csv")
        if not data or not data['rows']:
            print("No k-variation data available")
            return
        
        k_values = [int(row['k']) for row in data['rows']]
        avg_times = [float(row['avg_ms']) for row in data['rows']]
        median_times = [float(row['median_ms']) for row in data['rows']]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Time vs k
        ax1.plot(k_values, avg_times, 'o-', label='Average', linewidth=2, markersize=8, color='#2E86AB')
        ax1.plot(k_values, median_times, 's-', label='Median', linewidth=2, markersize=6, color='#A23B72')
        
        ax1.set_xlabel('Number of Iterations (k)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Wall-Clock Time (ms)', fontsize=12, fontweight='bold')
        ax1.set_title('Miller-Rabin: Performance vs Iterations', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=10)
        
        # Plot 2: Linear fit to check O(k) scaling
        coeffs = np.polyfit(k_values, avg_times, 1)
        linear_fit = np.poly1d(coeffs)
        
        ax2.plot(k_values, avg_times, 'o', markersize=8, color='#2E86AB', label='Measured')
        ax2.plot(k_values, linear_fit(k_values), '--', linewidth=2, color='red', 
                label=f'Linear fit: {coeffs[0]:.4f}k + {coeffs[1]:.4f}')
        
        ax2.set_xlabel('Number of Iterations (k)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Average Time (ms)', fontsize=12, fontweight='bold')
        ax2.set_title('Verification of O(k) Scaling', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=10)
        
        fig.tight_layout()
        
        if save_path:
            output_path = self.plots_dir / save_path
        else:
            output_path = self.plots_dir / "miller_rabin_k_variation.png"
        
        ensure_parent_dir(output_path)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {format_path(output_path)}")
        plt.close(fig)

    def plot_comprehensive(self, save_path: str = None):
        """Create comprehensive multi-panel benchmark summary."""
        scaling_data = self.load_csv("miller_rabin_scaling.csv")
        k_data = self.load_csv("miller_rabin_k_variation.csv")
        
        if not scaling_data or not k_data:
            print("Missing data for comprehensive plot")
            return
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Panel 1: Scaling (log-log)
        ax1 = fig.add_subplot(gs[0:2, 0:2])
        numbers = [int(row['number']) for row in scaling_data['rows']]
        avg_times = [float(row['avg_ms']) for row in scaling_data['rows']]
        
        ax1.loglog(numbers, avg_times, 'o-', linewidth=2, markersize=8, color='#2E86AB')
        ax1.set_xlabel('Input Size', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Time (ms)', fontsize=11, fontweight='bold')
        ax1.set_title('A. Performance Scaling', fontsize=12, fontweight='bold', loc='left')
        ax1.grid(True, alpha=0.3, which='both')
        
        # Panel 2: K-variation
        ax2 = fig.add_subplot(gs[0, 2])
        k_values = [int(row['k']) for row in k_data['rows']]
        k_times = [float(row['avg_ms']) for row in k_data['rows']]
        
        ax2.plot(k_values, k_times, 'o-', linewidth=2, markersize=6, color='#A23B72')
        ax2.set_xlabel('Iterations (k)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Time (ms)', fontsize=11, fontweight='bold')
        ax2.set_title('B. Time vs k', fontsize=12, fontweight='bold', loc='left')
        ax2.grid(True, alpha=0.3)
        
        # Panel 3: Distribution (box plot)
        ax3 = fig.add_subplot(gs[1, 2])
        box_data = [[float(row['avg_ms'])] for row in scaling_data['rows'][:5]]
        ax3.boxplot(box_data, tick_labels=[row['number'] for row in scaling_data['rows'][:5]])
        ax3.set_xlabel('Input Size', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Time (ms)', fontsize=11, fontweight='bold')
        ax3.set_title('C. Distribution', fontsize=12, fontweight='bold', loc='left')
        ax3.grid(True, alpha=0.3, axis='y')
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Panel 4: Performance summary table
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('off')
        
        table_data = []
        for row in scaling_data['rows'][:6]:
            table_data.append([
                row['number'],
                f"{float(row['avg_ms']):.4f}",
                f"{float(row['median_ms']):.4f}",
                f"{float(row['std_dev']):.4f}",
                row.get('result', 'N/A')
            ])
        
        table = ax4.table(cellText=table_data,
                         colLabels=['Number', 'Avg (ms)', 'Median (ms)', 'Std Dev', 'Result'],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Style header
        for i in range(5):
            table[(0, i)].set_facecolor('#2E86AB')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternate row colors
        for i in range(1, len(table_data) + 1):
            for j in range(5):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#F0F0F0')
        
        fig.suptitle('Miller-Rabin Test: Comprehensive Benchmark Summary', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        if save_path:
            output_path = self.plots_dir / save_path
        else:
            output_path = self.plots_dir / "miller_rabin_comprehensive.png"
        
        ensure_parent_dir(output_path)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {format_path(output_path)}")
        plt.close(fig)

    def generate_all_plots(self):
        """Generate all Miller-Rabin benchmark plots."""
        print("\nMiller-Rabin Benchmark Plotter")
        print("="*70)
        print("Generating Miller-Rabin benchmark plots...")
        print("="*70)
        
        self.plot_scaling()
        self.plot_k_variation()
        self.plot_comprehensive()
        
        print("\n" + "="*70)
        print("All plots generated successfully!")
        print(f"Location: {format_path(self.plots_dir)}")
        print("="*70)


def main():
    plotter = MillerRabinPlotter()
    plotter.generate_all_plots()


if __name__ == '__main__':
    main()
