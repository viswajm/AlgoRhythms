#!/usr/bin/env python3

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments

import csv
from path_utils import ensure_parent_dir, format_path, resolve_results_path
import sys


def plot_accuracy_vs_iterations(csv_file: str, output_file: str = None):
    """
    Create plot: Accuracy vs number of iterations.

    Args:
        csv_file: Input CSV file path
        output_file: Output PNG file (optional)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Error: matplotlib required. Install with: pip install matplotlib")
        return

    csv_path = resolve_results_path(csv_file)

    if not csv_path.exists():
        print(f"Error: File not found: {format_path(csv_path)}")
        return

    # Load data
    k_values = []
    fermat_acc = []
    miller_acc = []

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            k_values.append(int(row['k']))
            fermat_acc.append(float(row['fermat_accuracy']))
            miller_acc.append(float(row['miller_accuracy']))

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, fermat_acc, 'o-', label='Fermat Test', linewidth=2, markersize=8)
    plt.plot(k_values, miller_acc, 's-', label='Miller-Rabin Test', linewidth=2, markersize=8)

    plt.xlabel('Number of Iterations (k)', fontsize=12, fontweight='bold')
    plt.ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    plt.title('Primality Test Accuracy vs Iterations', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11, loc='lower right')
    plt.ylim([0, 105])

    # Add annotations
    for i, k in enumerate(k_values):
        if i % 2 == 0:  # Annotate every other point
            plt.annotate(f'{fermat_acc[i]:.1f}%', 
                        xy=(k, fermat_acc[i]), 
                        xytext=(0, 5),
                        textcoords='offset points',
                        fontsize=9,
                        ha='center')

    if output_file:
        output_path = resolve_results_path(output_file)
        ensure_parent_dir(output_path)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"* Plot saved to {format_path(output_path)}")
    else:
        plt.show()
    
    plt.close()  # Close the figure to free memory


def plot_carmichael_comparison(csv_file: str, output_file: str = None):
    """
    Create plot: Carmichael numbers - Fermat vs Miller-Rabin.

    Args:
        csv_file: Input CSV file path
        output_file: Output PNG file (optional)
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Error: matplotlib required. Install with: pip install matplotlib")
        return

    csv_path = resolve_results_path(csv_file)

    if not csv_path.exists():
        print(f"Error: File not found: {format_path(csv_path)}")
        return

    # Load data for k=10
    carmichael_nums = []
    fermat_results = []
    miller_results = []

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['k']) == 10:  # Focus on k=10
                carmichael_nums.append(int(row['number']))
                fermat_results.append(1 if row['fermat_result'] == 'COMPOSITE' else 0)
                miller_results.append(1 if row['miller_result'] == 'COMPOSITE' else 0)

    # Remove duplicates while preserving order
    seen = set()
    unique_nums = []
    unique_fermat = []
    unique_miller = []

    for n, f, m in zip(carmichael_nums, fermat_results, miller_results):
        if n not in seen:
            seen.add(n)
            unique_nums.append(n)
            unique_fermat.append(f)
            unique_miller.append(m)

    # Create plot
    x = np.arange(len(unique_nums))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 6))

    rects1 = ax.bar(x - width/2, unique_fermat, width, label='Fermat Test', color='#FF6B6B')
    rects2 = ax.bar(x + width/2, unique_miller, width, label='Miller-Rabin Test', color='#4ECDC4')

    ax.set_ylabel('Correctly Identified as Composite', fontsize=12, fontweight='bold')
    ax.set_xlabel('Carmichael Number', fontsize=12, fontweight='bold')
    ax.set_title('Carmichael Numbers: Critical Test (k=10)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(unique_nums, rotation=45)
    ax.set_ylim([0, 1.2])
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    # Add labels on bars
    for rect in rects1:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height,
                'X' if height == 0 else 'OK',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    for rect in rects2:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height,
                'X' if height == 0 else 'OK',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    fig.tight_layout()

    if output_file:
        output_path = resolve_results_path(output_file)
        ensure_parent_dir(output_path)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"* Plot saved to {format_path(output_path)}")
    else:
        plt.show()
    
    plt.close()  # Close the figure to free memory


def plot_performance(csv_file: str, output_file: str = None):
    """
    Create plot: Performance comparison.

    Args:
        csv_file: Input CSV file path
        output_file: Output PNG file (optional)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Error: matplotlib required. Install with: pip install matplotlib")
        return

    csv_path = resolve_results_path(csv_file)

    if not csv_path.exists():
        print(f"Error: File not found: {format_path(csv_path)}")
        return

    # Load data
    numbers = []
    fermat_times = []
    miller_times = []

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            numbers.append(int(row['number']))
            fermat_times.append(float(row['fermat_time_ms']))
            miller_times.append(float(row['miller_time_ms']))

    # Create plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Absolute time
    ax1.loglog(numbers, fermat_times, 'o-', label='Fermat Test', linewidth=2, markersize=8)
    ax1.loglog(numbers, miller_times, 's-', label='Miller-Rabin Test', linewidth=2, markersize=8)
    ax1.set_xlabel('Input Size (Number)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Execution Time (ms)', fontsize=11, fontweight='bold')
    ax1.set_title('Performance vs Input Size', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, which='both')
    ax1.legend(fontsize=10)

    # Plot 2: Overhead percentage
    overheads = [((m - f) / f * 100) if f > 0 else 0 for f, m in zip(fermat_times, miller_times)]
    ax2.semilogx(numbers, overheads, 'D-', color='#FF6B6B', linewidth=2, markersize=8)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Input Size (Number)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Miller-Rabin Overhead (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Performance Overhead', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()

    if output_file:
        output_path = resolve_results_path(output_file)
        ensure_parent_dir(output_path)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"* Plot saved to {format_path(output_path)}")
    else:
        plt.show()
    
    plt.close()  # Close the figure to free memory


def main():
    """Main execution."""
    print("Plotter: Create visualizations from experimental results")
    print("="*70)
    print("\nUsage: python plotter.py [command] [csv_file] [output_file]")
    print("\nCommands:")
    print("  accuracy    - Plot accuracy vs iterations")
    print("  carmichael  - Plot Carmichael comparison")
    print("  performance - Plot performance analysis")
    print("  all         - Generate all plots")
    print("\nExample:")
    print("  python plotter.py accuracy results/accuracy_vs_k.csv results/plots/accuracy.png")

    if len(sys.argv) < 2:
        print("\nNo command specified. Showing available files:")
        results_dir = resolve_results_path()
        if results_dir.exists():
            for csv_path in results_dir.glob("*.csv"):
                print(f"  - {format_path(csv_path)}")
        return

    command = sys.argv[1]
    default_inputs = {
        "accuracy": "results/accuracy_vs_k.csv",
        "carmichael": "results/carmichael_analysis.csv",
        "performance": "results/performance_results.csv",
    }

    csv_file = sys.argv[2] if len(sys.argv) > 2 else default_inputs.get(command)
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    if command == "accuracy":
        plot_accuracy_vs_iterations(csv_file or "results/accuracy_vs_k.csv", output_file)
    elif command == "carmichael":
        plot_carmichael_comparison(csv_file or "results/carmichael_analysis.csv", output_file)
    elif command == "performance":
        plot_performance(csv_file or "results/performance_results.csv", output_file)
    elif command == "all":
        print("Generating all plots...")
        plot_accuracy_vs_iterations("results/accuracy_vs_k.csv", "results/plots/accuracy.png")
        plot_carmichael_comparison("results/carmichael_analysis.csv", "results/plots/carmichael.png")
        plot_performance("results/performance_results.csv", "results/plots/performance.png")


if __name__ == "__main__":
    main()
