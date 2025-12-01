#!/usr/bin/env python3
"""
Karger's Min-Cut Algorithm Experimental Analysis
Runs experiments and generates performance graphs
"""

import subprocess
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, Counter
import os

def generate_graph(v, edges, trials=200):
    """Generate graph input string with trials parameter"""
    graph_str = f"{v} {len(edges)} {trials}\n"
    for u, w in edges:
        graph_str += f"{u} {w}\n"
    return graph_str

def run_karger(graph_input, trials=200):
    """Run Karger's algorithm and capture output"""
    try:
        result = subprocess.run(
            ['kargermincut.exe'],
            input=graph_input,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse output
        output = result.stdout
        for line in output.split('\n'):
            if 'Minimum cut found' in line:
                mincut = int(line.split(':')[-1].strip())
                return mincut
        return None
    except Exception as e:
        print(f"Error running algorithm: {e}")
        return None

def generate_complete_graph(n):
    """Generate complete graph Kn"""
    edges = []
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            edges.append((i, j))
    return edges

def generate_cycle(n):
    """Generate cycle graph Cn"""
    edges = [(i, i+1) for i in range(1, n)]
    edges.append((n, 1))
    return edges

def generate_path(n):
    """Generate path graph"""
    edges = [(i, i+1) for i in range(1, n)]
    return edges

def generate_two_clusters(k, bridges=1):
    """Generate two complete graphs connected by 'bridges' edges"""
    edges = []
    # First cluster (vertices 1 to k)
    for i in range(1, k+1):
        for j in range(i+1, k+1):
            edges.append((i, j))
    
    # Second cluster (vertices k+1 to 2k)
    for i in range(k+1, 2*k+1):
        for j in range(i+1, 2*k+1):
            edges.append((i, j))
    
    # Bridge edges
    for b in range(bridges):
        edges.append((k, k+1+b))
    
    return edges

def experiment_success_vs_trials():
    """Experiment: Success rate vs number of trials"""
    print("\n=== Experiment 1: Success Rate vs Trials ===")
    
    # Use moderate-sized graph for clearer demonstration
    edges = generate_two_clusters(4, bridges=2)  # 8 vertices, min-cut = 2
    expected_mincut = 2
    V = 8
    
    trial_counts = [1, 2, 3, 5, 10, 20, 50, 100, 200]
    success_rates = []
    
    for trials in trial_counts:
        print(f"Testing with {trials} trials...")
        successes = 0
        runs = 50  # Run 50 times to get better statistics
        
        for _ in range(runs):
            graph = generate_graph(V, edges, trials)
            mincut = run_karger(graph, trials)
            if mincut == expected_mincut:
                successes += 1
        
        success_rate = (successes / runs) * 100
        success_rates.append(success_rate)
        print(f"  Success rate: {success_rate:.1f}%")
    
    # Plot
    plt.figure(figsize=(11, 7))
    plt.plot(trial_counts, success_rates, 'go-', linewidth=3, markersize=10, label='Empirical Results', alpha=0.8)
    
    # Theoretical curve: P(success) = 1 - (1 - 2/(n(n-1)))^trials
    n = V
    theoretical = [100 * (1 - (1 - 2/(n*(n-1)))**t) for t in trial_counts]
    plt.plot(trial_counts, theoretical, 'b--', linewidth=2, label='Theoretical Lower Bound', alpha=0.7)
    
    # Add shaded region for high success
    plt.axhspan(90, 100, alpha=0.1, color='green', label='High Success Zone (>90%)')
    
    plt.xlabel('Number of Trials', fontsize=13)
    plt.ylabel('Success Rate (%)', fontsize=13)
    plt.title(f'Reliability Improves with Multiple Trials\n({V}-vertex graph, min-cut={expected_mincut})', 
              fontsize=15, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11, loc='lower right')
    plt.xscale('log')
    plt.ylim(-5, 105)
    plt.tight_layout()
    plt.savefig('success_vs_trials.png', dpi=300)
    print("Saved: success_vs_trials.png")
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11)
    plt.xscale('log')  # Log scale for better visualization
    plt.tight_layout()
    plt.savefig('success_vs_trials.png', dpi=300)
    print("Saved: success_vs_trials.png")

def experiment_runtime_vs_vertices():
    """Experiment: Runtime vs number of vertices"""
    print("\n=== Experiment 2: Runtime vs Vertices ===")
    
    vertex_counts = [5, 10, 15, 20, 30, 40, 50]
    runtimes_complete = []
    runtimes_cycle = []
    
    for v in vertex_counts:
        print(f"Testing with {v} vertices...")
        
        # Complete graph
        graph = generate_graph(v, generate_complete_graph(v), trials=50)
        start = time.time()
        run_karger(graph, trials=50)
        runtime = (time.time() - start) * 1000  # ms
        runtimes_complete.append(runtime)
        print(f"  Complete graph: {runtime:.2f} ms")
        
        # Cycle graph
        graph = generate_graph(v, generate_cycle(v), trials=50)
        start = time.time()
        run_karger(graph, trials=50)
        runtime = (time.time() - start) * 1000  # ms
        runtimes_cycle.append(runtime)
        print(f"  Cycle graph: {runtime:.2f} ms")
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(vertex_counts, runtimes_complete, 'ro-', linewidth=2, markersize=8, label='Complete Graph (dense)')
    plt.plot(vertex_counts, runtimes_cycle, 'bs-', linewidth=2, markersize=8, label='Cycle Graph (sparse)')
    
    plt.xlabel('Number of Vertices', fontsize=12)
    plt.ylabel('Runtime (ms) for 50 trials', fontsize=12)
    plt.title('Runtime vs Number of Vertices', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig('runtime_vs_vertices.png', dpi=300)
    print("Saved: runtime_vs_vertices.png")

def experiment_mincut_distribution():
    """Experiment: Comparing single-trial vs multi-trial performance"""
    print("\n=== Experiment 3: Single-Trial vs Multi-Trial Comparison ===")
    
    # Use a larger, more challenging graph (12-vertex)
    edges = generate_two_clusters(6, bridges=3)
    expected_mincut = 3
    V = 12
    
    # Single trial runs
    print("Running 150 single-trial executions...")
    single_cuts = []
    for i in range(150):
        graph = generate_graph(V, edges, trials=1)
        mincut = run_karger(graph, trials=1)
        single_cuts.append(mincut)
    
    # Multi-trial runs (20 trials each)
    print("Running 150 executions with 20 trials each...")
    multi_cuts = []
    for i in range(150):
        graph = generate_graph(V, edges, trials=20)
        mincut = run_karger(graph, trials=20)
        multi_cuts.append(mincut)
    
    # Count frequencies
    single_counts = Counter(single_cuts)
    multi_counts = Counter(multi_cuts)
    
    single_success = (single_cuts.count(expected_mincut) / 150) * 100
    multi_success = (multi_cuts.count(expected_mincut) / 150) * 100
    
    # Theoretical probability
    theoretical_single = (2.0 / (V * (V - 1))) * 100
    theoretical_multi = (1 - (1 - 2/(V*(V-1)))**20) * 100
    
    # Plot side-by-side comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Get all unique cut values and frequencies for both
    cuts_sorted = sorted(set(single_cuts + multi_cuts))
    single_freqs = [single_counts.get(c, 0) for c in cuts_sorted]
    multi_freqs = [multi_counts.get(c, 0) for c in cuts_sorted]
    
    # Single trial distribution
    colors1 = ['darkgreen' if c == expected_mincut else 'lightcoral' for c in cuts_sorted]
    
    ax1.bar(cuts_sorted, single_freqs, color=colors1, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.axvline(x=expected_mincut, color='darkgreen', linestyle='--', linewidth=3, 
                label=f'True Min-Cut = {expected_mincut}')
    ax1.set_xlabel('Cut Size Found', fontsize=12)
    ax1.set_ylabel('Frequency (out of 150 runs)', fontsize=12)
    ax1.set_title(f'Single Trial Performance\nSuccess: {single_success:.1f}% (Theory: ≥{theoretical_single:.1f}%)', 
                  fontsize=13, fontweight='bold', color='darkred')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.legend(fontsize=11)
    ax1.set_ylim(0, max(single_freqs + multi_freqs) * 1.1)
    
    # Multi-trial distribution
    colors2 = ['darkgreen' if c == expected_mincut else 'lightcoral' for c in cuts_sorted]
    
    ax2.bar(cuts_sorted, multi_freqs, color=colors2, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.axvline(x=expected_mincut, color='darkgreen', linestyle='--', linewidth=3, 
                label=f'True Min-Cut = {expected_mincut}')
    ax2.set_xlabel('Cut Size Found', fontsize=12)
    ax2.set_ylabel('Frequency (out of 150 runs)', fontsize=12)
    ax2.set_title(f'20 Trials Performance\nSuccess: {multi_success:.1f}% (Theory: ≥{theoretical_multi:.1f}%)', 
                  fontsize=13, fontweight='bold', color='darkgreen')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend(fontsize=11)
    ax2.set_ylim(0, max(single_freqs + multi_freqs) * 1.1)
    
    plt.suptitle(f'Effect of Multiple Trials on Accuracy ({V}-vertex graph)', 
                 fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('mincut_distribution.png', dpi=300)
    print(f"Saved: mincut_distribution.png")
    print(f"  Single trial: {single_success:.1f}% success (expected ≥{theoretical_single:.1f}%)")
    print(f"  20 trials: {multi_success:.1f}% success (expected ≥{theoretical_multi:.1f}%)")

def experiment_graph_types():
    """Experiment: Compare different graph types"""
    print("\n=== Experiment 4: Performance on Different Graph Types ===")
    
    graph_configs = [
        ("Complete K6", 6, generate_complete_graph(6), 5),
        ("Cycle C10", 10, generate_cycle(10), 2),
        ("Path P10", 10, generate_path(10), 1),
        ("2-Clusters (1 bridge)", 8, generate_two_clusters(4, 1), 1),
        ("2-Clusters (2 bridges)", 8, generate_two_clusters(4, 2), 2),
        ("2-Clusters (3 bridges)", 8, generate_two_clusters(4, 3), 3),
    ]
    
    results = []
    
    for name, v, edges, expected in graph_configs:
        print(f"Testing {name}...")
        
        successes = 0
        runs = 30
        start = time.time()
        
        for _ in range(runs):
            graph = generate_graph(v, edges, trials=100)
            mincut = run_karger(graph, trials=100)
            if mincut == expected:
                successes += 1
        
        runtime = (time.time() - start) / runs * 1000
        success_rate = (successes / runs) * 100
        
        results.append({
            'name': name,
            'vertices': v,
            'edges': len(edges),
            'expected': expected,
            'success_rate': success_rate,
            'runtime': runtime
        })
        
        print(f"  Success: {success_rate:.1f}%, Avg Runtime: {runtime:.2f} ms")
    
    # Plot success rates
    plt.figure(figsize=(12, 6))
    names = [r['name'] for r in results]
    success = [r['success_rate'] for r in results]
    
    plt.subplot(1, 2, 1)
    plt.barh(names, success, color='steelblue')
    plt.xlabel('Success Rate (%)', fontsize=11)
    plt.title('Success Rate by Graph Type (100 trials)', fontsize=12)
    plt.xlim([0, 105])
    plt.grid(True, alpha=0.3, axis='x')
    
    # Plot runtimes
    plt.subplot(1, 2, 2)
    runtimes = [r['runtime'] for r in results]
    plt.barh(names, runtimes, color='coral')
    plt.xlabel('Avg Runtime (ms)', fontsize=11)
    plt.title('Average Runtime by Graph Type', fontsize=12)
    plt.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('graph_types_comparison.png', dpi=300)
    print("Saved: graph_types_comparison.png")

def experiment_single_trial_performance():
    """Experiment: Why we need multiple trials"""
    print("\n=== Experiment 5: Probabilistic Nature Demonstration ===")
    
    # Use a 10-vertex graph to show probabilistic behavior
    edges = generate_two_clusters(5, bridges=2)
    expected_mincut = 2
    V = 10
    
    # Test different numbers of trials
    trial_options = [1, 5, 10, 50]
    all_results = []
    
    for num_trials in trial_options:
        print(f"Testing with {num_trials} trial(s) per run...")
        cuts = []
        runs = 100
        
        for _ in range(runs):
            graph = generate_graph(V, edges, num_trials)
            mincut = run_karger(graph, num_trials)
            cuts.append(mincut)
        
        success_rate = (cuts.count(expected_mincut) / runs) * 100
        all_results.append({
            'trials': num_trials,
            'cuts': cuts,
            'success': success_rate
        })
        print(f"  Success rate: {success_rate:.0f}%")
    
    # Create visualization
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Top row: histograms for each trial count
    for idx, result in enumerate(all_results[:4]):
        ax = fig.add_subplot(gs[idx//2, idx%2])
        
        counts = Counter(result['cuts'])
        cuts_sorted = sorted(counts.keys())
        freqs = [counts[c] for c in cuts_sorted]
        colors = ['green' if c == expected_mincut else 'lightgray' for c in cuts_sorted]
        
        bars = ax.bar(cuts_sorted, freqs, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.axvline(x=expected_mincut, color='darkgreen', linestyle='--', linewidth=3, alpha=0.7)
        
        ax.set_xlabel('Cut Size Found', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title(f'{result["trials"]} Trial(s): {result["success"]:.0f}% Success', 
                    fontsize=12, fontweight='bold',
                    color='darkgreen' if result['success'] >= 90 else 'darkred')
        ax.grid(True, alpha=0.2, axis='y')
        ax.set_ylim(0, 105)
    
    # Bottom row: summary comparison
    ax_summary = fig.add_subplot(gs[2, :])
    
    trial_counts = [r['trials'] for r in all_results]
    success_rates = [r['success'] for r in all_results]
    
    colors_bar = ['red' if s < 50 else 'orange' if s < 90 else 'green' for s in success_rates]
    bars = ax_summary.bar(range(len(trial_counts)), success_rates, color=colors_bar, alpha=0.7, 
                           edgecolor='black', linewidth=2)
    
    ax_summary.axhline(y=90, color='green', linestyle='--', linewidth=2, alpha=0.5, label='90% Threshold')
    ax_summary.set_xticks(range(len(trial_counts)))
    ax_summary.set_xticklabels([f'{t} trial(s)' for t in trial_counts], fontsize=12)
    ax_summary.set_ylabel('Success Rate (%)', fontsize=13)
    ax_summary.set_title('Summary: More Trials = Higher Reliability', fontsize=14, fontweight='bold')
    ax_summary.grid(True, alpha=0.3, axis='y')
    ax_summary.set_ylim(0, 105)
    ax_summary.legend(fontsize=11)
    
    # Add value labels on bars
    for bar, rate in zip(bars, success_rates):
        height = bar.get_height()
        ax_summary.text(bar.get_x() + bar.get_width()/2., height + 2,
                       f'{rate:.0f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.suptitle(f'Why Multiple Trials Matter (6-vertex graph, true min-cut = {expected_mincut})', 
                fontsize=16, fontweight='bold', y=0.995)
    
    plt.savefig('single_trial_performance.png', dpi=300)
    print("Saved: single_trial_performance.png")

def main():
    print("=" * 60)
    print("Karger's Min-Cut Algorithm - Experimental Analysis")
    print("=" * 60)
    
    # Check if executable exists
    if not os.path.exists('kargermincut.exe'):
        print("Error: kargermincut.exe not found!")
        print("Please compile first: g++ -o kargermincut.exe kargermincut.cpp -std=c++17")
        return
    
    # Run experiments
    experiment_success_vs_trials()
    experiment_runtime_vs_vertices()
    experiment_mincut_distribution()
    experiment_graph_types()
    experiment_single_trial_performance()
    
    print("\n" + "=" * 60)
    print("All experiments completed!")
    print("Generated graphs:")
    print("  - success_vs_trials.png")
    print("  - runtime_vs_vertices.png")
    print("  - mincut_distribution.png")
    print("  - graph_types_comparison.png")
    print("  - single_trial_performance.png")
    print("=" * 60)

if __name__ == "__main__":
    main()
