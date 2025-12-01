#!/usr/bin/env python3

import subprocess
import sys
import csv
from pathlib import Path
from typing import List, Dict

from path_utils import (
    CPP_DIR,
    detect_cpp_binary,
    ensure_parent_dir,
    format_path,
    resolve_python_path,
    resolve_results_path,
    to_wsl_path,
)


class MillerRabinBenchmark:
    """Benchmarks MillerRabin primality test."""

    def __init__(self, cpp_binary: str = None):
        """
        Initialize benchmark.

        Args:
            cpp_binary: Path to C++ benchmark executable
        """
        import platform

        if cpp_binary is None:
            binary_name = "benchmark_miller_rabin.exe" if platform.system() == "Windows" else "benchmark_miller_rabin"
            cpp_path = detect_cpp_binary(binary_name, "benchmark_miller_rabin")
        else:
            candidate = Path(cpp_binary)
            cpp_path = candidate if candidate.is_absolute() else resolve_python_path(cpp_binary)

        self.cpp_binary = cpp_path.resolve()
        self.cpp_dir = self.cpp_binary.parent if self.cpp_binary.parent != Path('.') else CPP_DIR
        self.results_dir = resolve_results_path("miller_rabin_benchmarks")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self._use_wsl = platform.system() == "Windows" and not self.cpp_binary.exists()
        if self._use_wsl:
            print(f"Using C++ binary via WSL: {format_path(self.cpp_binary)}")
        else:
            print(f"Using C++ binary: {format_path(self.cpp_binary)}")

    def run_cpp_benchmark(self, command: str) -> str:
        """
        Run C++ benchmark and return output.

        Args:
            command: Benchmark command (single, scaling, k-variation, carmichael, all)

        Returns:
            Output string from benchmark
        """
        try:
            import platform

            if platform.system() == "Windows" and self._use_wsl:
                cpp_dir = to_wsl_path(self.cpp_dir)
                cmd = f'wsl -e bash -c "cd {cpp_dir} && ./benchmark_miller_rabin {command}"'
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    shell=True
                )
            else:
                result = subprocess.run(
                    [str(self.cpp_binary), command],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=str(self.cpp_dir)
                )
            
            return result.stdout
        except subprocess.TimeoutExpired:
            return "ERROR: Benchmark timed out"
        except FileNotFoundError:
            return f"ERROR: Executable not found: {self.cpp_binary}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def parse_scaling_output(self, output: str) -> List[Dict]:
        """Parse scaling benchmark output to CSV-ready data."""
        lines = output.split('\n')
        data = []
        
        parsing = False
        for line in lines:
            if 'Number' in line and 'Avg (ms)' in line:
                parsing = True
                continue
            if parsing and line.strip() and not line.startswith('='):
                if '---' in line:
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        data.append({
                            'number': parts[0],
                            'avg_ms': parts[1],
                            'median_ms': parts[2],
                            'std_dev': parts[3],
                            'result': parts[4] if len(parts) > 4 else 'N/A'
                        })
                    except (ValueError, IndexError):
                        pass
        
        return data

    def parse_k_variation_output(self, output: str) -> List[Dict]:
        """Parse k-variation benchmark output to CSV-ready data."""
        lines = output.split('\n')
        data = []
        
        parsing = False
        for line in lines:
            if line.strip().startswith('k') and 'Avg (ms)' in line:
                parsing = True
                continue
            if parsing and line.strip() and not line.startswith('='):
                if '---' in line:
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        data.append({
                            'k': parts[0],
                            'avg_ms': parts[1],
                            'median_ms': parts[2],
                            'time_per_iter': parts[3]
                        })
                    except (ValueError, IndexError):
                        pass
        
        return data

    def save_to_csv(self, filename: str, data: List[Dict]) -> None:
        """Save benchmark data to CSV."""
        if not data:
            print(f"No data to save for {filename}")
            return
        
        filepath = self.results_dir / filename
        
        try:
            ensure_parent_dir(filepath)
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"✓ Saved: {format_path(filepath)}")
        except Exception as e:
            print(f"✗ Error saving {filename}: {e}")

    def benchmark_all(self) -> None:
        """Run all benchmarks and save results."""
        print("="*70)
        print("MILLER_RABIN PRIMALITY TEST - COMPREHENSIVE BENCHMARK")
        print("="*70)
        
        # Scaling benchmark
        print("\n[1/3] Running scaling benchmark...")
        output = self.run_cpp_benchmark("scaling")
        print(output)
        data = self.parse_scaling_output(output)
        if data:
            self.save_to_csv("miller_rabin_scaling.csv", data)
        
        # K-variation benchmark
        print("\n[2/3] Running k-variation benchmark...")
        output = self.run_cpp_benchmark("k-variation")
        print(output)
        data = self.parse_k_variation_output(output)
        if data:
            self.save_to_csv("miller_rabin_k_variation.csv", data)
        
        # Carmichael benchmark
        print("\n[3/3] Running Carmichael benchmark...")
        output = self.run_cpp_benchmark("carmichael")
        print(output)
        
        print("\n" + "="*70)
        print("BENCHMARK COMPLETE")
        print(f"Results saved to: {format_path(self.results_dir)}")
        print("="*70)
        
        # Generate plots
        print("\n" + "="*70)
        print("GENERATING PLOTS")
        print("="*70)
        try:
            from plot_miller_rabin_benchmarks import MillerRabinPlotter
            plotter = MillerRabinPlotter(self.results_dir)
            plotter.generate_all_plots()
        except ImportError as e:
            print(f"Warning: Could not generate plots: {e}")
            print("To generate plots manually, run:")
            print("  python plot_miller_rabin_benchmarks.py all")

    def benchmark_custom(self, number: int, k: int, iterations: int = 100) -> None:
        """
        Run custom benchmark on specific number.

        Args:
            number: Number to test
            k: Number of iterations for MillerRabin test
            iterations: Number of benchmark runs
        """
        print(f"Running custom benchmark: n={number}, k={k}, iterations={iterations}")
        
        try:
            import platform

            if platform.system() == "Windows" and self._use_wsl:
                cpp_dir = to_wsl_path(self.cpp_dir)
                cmd = f'wsl -e bash -c "cd {cpp_dir} && ./benchmark_miller_rabin {number} {k} {iterations}"'
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    shell=True
                )
            else:
                result = subprocess.run(
                    [str(self.cpp_binary), str(number), str(k), str(iterations)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(self.cpp_dir)
                )
            
            print(result.stdout)
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main execution."""
    print("MillerRabin Primality Test - Benchmark Suite")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python benchmark_miller_rabin.py <command>")
        print("  python benchmark_miller_rabin.py <number> <k> <iterations>")
        print("\nCommands:")
        print("  all         - Run all benchmarks")
        print("  scaling     - Benchmark across input sizes")
        print("  k-variation - Benchmark with different k values")
        print("  carmichael  - Benchmark on Carmichael numbers")
        print("\nExamples:")
        print("  python benchmark_miller_rabin.py all")
        print("  python benchmark_miller_rabin.py 1000000007 10 100")
        return
    
    benchmark = MillerRabinBenchmark()
    
    command = sys.argv[1]
    
    if command == "all":
        benchmark.benchmark_all()
    elif command in ["scaling", "k-variation", "carmichael"]:
        output = benchmark.run_cpp_benchmark(command)
        print(output)
    elif len(sys.argv) == 4:
        # Custom benchmark
        number = int(sys.argv[1])
        k = int(sys.argv[2])
        iterations = int(sys.argv[3])
        benchmark.benchmark_custom(number, k, iterations)
    else:
        print(f"Unknown command: {command}")
        print("Use: all, scaling, k-variation, or carmichael")


if __name__ == "__main__":
    main()
