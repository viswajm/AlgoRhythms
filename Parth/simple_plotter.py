"""Plot benchmark results produced by the C++ Monte Carlo benchmark.

This script reads a CSV file produced by `monte_carlo.cpp` (default
`monte_carlo_results.csv`) and generates per-function convergence plots.

The CSV format expected is (header):
Function,Samples,Trial,Estimate,StdError,AbsError,RelError(%),Time(ms)

Usage:
    python simple_plotter.py --csv monte_carlo_results.csv --outdir plots --show

This script uses only the Python standard library plus `matplotlib` for
plotting. If `matplotlib` is not installed, install via `pip install matplotlib`.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
from collections import defaultdict
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt


def sanitize_filename(s: str) -> str:
    """Make a safe filename from a title string."""
    keep = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    return "".join(c if c in keep else "_" for c in s)[:200]


def read_results(csv_path: str) -> Dict[str, Dict[int, List[Dict[str, float]]]]:
    """Read CSV and return nested dict: func -> samples -> list of trial dicts.

    Each trial dict contains keys: Estimate, StdError, AbsError, RelError, Time
    """
    data: Dict[str, Dict[int, List[Dict[str, float]]]] = defaultdict(lambda: defaultdict(list))
    with open(csv_path, newline="") as fh:
        sample = fh.readline()
        fh.seek(0)
        has_header = False
        if sample:
            lower = sample.lower()
            if "function" in lower or "estimate" in lower or "abs" in lower or "time" in lower:
                has_header = True

        if has_header:
            reader = csv.DictReader(fh)
            for row in reader:
                func = row.get("Function", row.get("function", "unknown"))
                try:
                    samples = int(row.get("Samples", row.get("samples", "0")))
                except ValueError:
                    continue
                def fget(keys, default=float("nan")):
                    for k in keys:
                        if k in row and row[k] not in (None, ""):
                            try:
                                return float(row[k])
                            except ValueError:
                                return default
                    return default

                estimate = fget(("Estimate", "estimate"))
                std_err = fget(("StdError", "stderr", "std_err"))
                abs_err = fget(("AbsError", "abs_err", "abs error", "abs"))
                rel_err = fget(("RelError(%)", "RelError", "rel_err", "relerror"))
                time_ms = fget(("Time(ms)", "Time", "time_ms", "time"))

                data[func][samples].append({
                    "estimate": estimate,
                    "std_err": std_err,
                    "abs_err": abs_err,
                    "rel_err": rel_err,
                    "time_ms": time_ms,
                })
        else:
            # Headerless CSV: parse rows len 4 or len >=4
            reader = csv.reader(fh)
            for row in reader:
                if not row:
                    continue
                # strip quotes and whitespace
                func = row[0].strip().strip('"')
                try:
                    samples = int(row[1])
                except Exception:
                    continue
                # Interpret remaining columns
                # If there are exactly 4 columns: assume [func, samples, abs_err, time_ms]
                estimate = float("nan")
                std_err = float("nan")
                abs_err = float("nan")
                rel_err = float("nan")
                time_ms = float("nan")

                try:
                    if len(row) == 4:
                        abs_err = float(row[2])
                        time_ms = float(row[3])
                    elif len(row) >= 5:
                        # try mapping common patterns: [func, samples, estimate, abs_err, time]
                        estimate = float(row[2])
                        abs_err = float(row[3])
                        time_ms = float(row[4])
                except Exception:
                    # if conversion fails, leave values as nan
                    pass

                data[func][samples].append({
                    "estimate": estimate,
                    "std_err": std_err,
                    "abs_err": abs_err,
                    "rel_err": rel_err,
                    "time_ms": time_ms,
                })
    return data


def summarize(data: Dict[int, List[Dict[str, float]]]) -> Tuple[List[int], List[float], List[float], List[float], List[float]]:
    """Return sorted sample sizes and stats: mean_est, std_est, mean_abs_err, mean_time_ms."""
    sizes = sorted(data.keys())
    mean_est = []
    std_est = []
    mean_abs_err = []
    mean_time = []

    for s in sizes:
        trials = data[s]
        estimates = [t["estimate"] for t in trials]
        abs_errs = [t["abs_err"] for t in trials]
        times = [t["time_ms"] for t in trials]

        mean_est.append(statistics.mean(estimates))
        # Compute population std-dev manually to avoid compatibility issues
        if len(estimates) > 1:
            mean_e = statistics.mean(estimates)
            var = sum((e - mean_e) ** 2 for e in estimates) / len(estimates)
            std_est.append(math.sqrt(var))
        else:
            std_est.append(0.0)
        mean_abs_err.append(statistics.mean(abs_errs))
        mean_time.append(statistics.mean(times))

    return sizes, mean_est, std_est, mean_abs_err, mean_time


def plot_function(func_name: str, data: Dict[int, List[Dict[str, float]]], outdir: str, show: bool = False) -> None:
    sizes, mean_est, std_est, mean_abs_err, mean_time = summarize(data)

    if not sizes:
        print(f"No data for function: {func_name}")
        return

    sanitized = sanitize_filename(func_name)
    
    # Check if we have valid estimate data (not all NaN)
    has_estimates = any(not math.isnan(e) for e in mean_est)
    
    if has_estimates:
        # Create 3-subplot layout with estimates
        plt.figure(figsize=(10, 8))
        
        ax1 = plt.subplot(2, 1, 1)
        ax1.errorbar(sizes, mean_est, yerr=std_est, fmt="o-", capsize=4)
        if any(s > 0 for s in sizes):
            ax1.set_xscale("log")
            ax1.set_xlabel("Samples (log scale)")
        else:
            ax1.set_xlabel("Samples")
        ax1.set_ylabel("Estimate")
        ax1.set_title(f"Estimate convergence: {func_name}")
        ax1.grid(True, which="both", ls="--", alpha=0.5)

        ax2 = plt.subplot(2, 2, 3)
        ax3 = plt.subplot(2, 2, 4)
    else:
        # Create 2-subplot layout (side by side, no estimates)
        plt.figure(figsize=(12, 5))
        ax2 = plt.subplot(1, 2, 1)
        ax3 = plt.subplot(1, 2, 2)
    
    # Plot absolute error
    ax2.plot(sizes, mean_abs_err, "s-", color="C1")
    if any(s > 0 for s in sizes):
        ax2.set_xscale("log")
        ax2.set_xlabel("Samples (log)")
    else:
        ax2.set_xlabel("Samples")
    if any(e > 0 for e in mean_abs_err):
        ax2.set_yscale("log")
        ax2.set_ylabel("Mean Absolute Error (log)")
    else:
        ax2.set_ylabel("Mean Absolute Error")
    ax2.set_title(f"Error vs Samples: {func_name}")
    ax2.grid(True, which="both", ls="--", alpha=0.5)

    # Plot timing
    ax3.plot(sizes, mean_time, "^-", color="C2")
    if any(s > 0 for s in sizes):
        ax3.set_xscale("log")
        ax3.set_xlabel("Samples (log)")
    else:
        ax3.set_xlabel("Samples")
    ax3.set_ylabel("Mean Time (ms)")
    ax3.set_title(f"Time vs Samples: {func_name}")
    ax3.grid(True, which="both", ls="--", alpha=0.5)

    plt.tight_layout()
    outpath = os.path.join(outdir, f"{sanitized}.png")
    plt.savefig(outpath)
    print(f"Saved plot: {outpath}")
    if show:
        plt.show()
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot Monte Carlo benchmark CSV results")
    parser.add_argument("--csv", type=str, default="monte_carlo_results.csv", help="Path to CSV results file")
    parser.add_argument("--outdir", type=str, default="plots", help="Directory to save plots")
    parser.add_argument("--show", action="store_true", help="Show plots interactively after saving")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"CSV file not found: {args.csv}")
        return

    os.makedirs(args.outdir, exist_ok=True)

    data = read_results(args.csv)
    if not data:
        print("No data found in CSV.")
        return

    for func_name, group in data.items():
        plot_function(func_name, group, args.outdir, show=args.show)


if __name__ == "__main__":
    main()
