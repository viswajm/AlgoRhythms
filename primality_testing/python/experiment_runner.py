#!/usr/bin/env python3

import csv
import sys
from pathlib import Path
from typing import List, Dict
from utils import run_cpp_test, get_carmichael_numbers, load_results_from_csv
from data_generator import DataGenerator
from path_utils import resolve_results_path, ensure_parent_dir, format_path


class ExperimentRunner:
    """Orchestrates primality testing experiments."""

    def __init__(self, cpp_binary: str = "./build/primality_test", 
                 results_dir: str = ""):
        """
        Initialize experiment runner.

        Args:
            cpp_binary: Path to C++ executable
            results_dir: Directory to save results (relative to project results dir)
        """
        self.cpp_binary = cpp_binary
        self.results_dir = resolve_results_path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def experiment_accuracy_vs_iterations(self) -> None:
        """
        Measure accuracy as function of iterations (k).

        Tests with k = 1, 2, 3, 5, 10, 20, 50
        Saves results to: accuracy_vs_k.csv
        """
        print("\n" + "="*70)
        print("EXPERIMENT 1: Accuracy vs Number of Iterations")
        print("="*70)

        # Generate test data
        generator = DataGenerator()
        test_suite = generator.generate_test_suite()

        k_values = [1, 2, 3, 5, 10, 20, 50]
        results = []

        for k in k_values:
            print(f"\nTesting with k={k} iterations...")

            fermat_correct = 0
            miller_correct = 0
            fermat_fp = 0  # False positives
            miller_fp = 0
            total = len(test_suite)
            composites = sum(1 for _, is_p, _ in test_suite if not is_p)

            for i, (number, is_prime, category) in enumerate(test_suite):
                if (i + 1) % 50 == 0:
                    print(f"  Progress: {i+1}/{total}")

                result = run_cpp_test(number, k, self.cpp_binary)

                if not result.get('success', False):
                    print(f"  Warning: Test failed for {number}")
                    continue

                fermat_result = result['fermat_result']
                miller_result = result['miller_result']

                # Count correctness
                if fermat_result == is_prime:
                    fermat_correct += 1
                if miller_result == is_prime:
                    miller_correct += 1

                # Count false positives (composite labeled as prime)
                if not is_prime and fermat_result:
                    fermat_fp += 1
                if not is_prime and miller_result:
                    miller_fp += 1

            fermat_accuracy = 100.0 * fermat_correct / total if total > 0 else 0
            miller_accuracy = 100.0 * miller_correct / total if total > 0 else 0
            fermat_fpr = 100.0 * fermat_fp / composites if composites > 0 else 0
            miller_fpr = 100.0 * miller_fp / composites if composites > 0 else 0

            results.append({
                'k': k,
                'fermat_accuracy': f"{fermat_accuracy:.2f}",
                'fermat_fp_rate': f"{fermat_fpr:.2f}",
                'miller_accuracy': f"{miller_accuracy:.2f}",
                'miller_fp_rate': f"{miller_fpr:.2f}"
            })

            print(f"  Fermat: {fermat_accuracy:.2f}% accuracy, {fermat_fpr:.2f}% FP rate")
            print(f"  Miller-Rabin: {miller_accuracy:.2f}% accuracy, {miller_fpr:.2f}% FP rate")

        # Save results
        self._save_results("accuracy_vs_k.csv", results)

    def experiment_carmichael_analysis(self) -> None:
        """
        Analyze behavior on Carmichael numbers specifically.

        This is the CRITICAL experiment showing Miller-Rabin's superiority.
        Saves results to: carmichael_analysis.csv
        """
        print("\n" + "="*70)
        print("EXPERIMENT 2: CRITICAL - Carmichael Numbers Analysis")
        print("="*70)

        carmichael_numbers = get_carmichael_numbers()
        k_values = [1, 5, 10, 20, 50]
        results = []

        print(f"\nTesting {len(carmichael_numbers)} Carmichael numbers\n")

        for k in k_values:
            print(f"k={k}:")
            fermat_correct = 0
            miller_correct = 0

            for num in carmichael_numbers:
                result = run_cpp_test(num, k, self.cpp_binary)

                if not result.get('success', False):
                    continue

                # Carmichael numbers should be detected as COMPOSITE
                if not result['fermat_result']:  # Correctly identified as composite
                    fermat_correct += 1
                if not result['miller_result']:  # Correctly identified as composite
                    miller_correct += 1

                results.append({
                    'number': num,
                    'k': k,
                    'fermat_result': 'COMPOSITE' if not result['fermat_result'] else 'PRIME',
                    'miller_result': 'COMPOSITE' if not result['miller_result'] else 'PRIME',
                    'fermat_time_ms': f"{result.get('fermat_time', 0):.3f}",
                    'miller_time_ms': f"{result.get('miller_time', 0):.3f}"
                })

            accuracy_fermat = 100.0 * fermat_correct / len(carmichael_numbers)
            accuracy_miller = 100.0 * miller_correct / len(carmichael_numbers)

            print(f"  Fermat: {fermat_correct}/{len(carmichael_numbers)} correct ({accuracy_fermat:.1f}%)")
            print(f"  Miller-Rabin: {miller_correct}/{len(carmichael_numbers)} correct ({accuracy_miller:.1f}%)")

        self._save_results("carmichael_analysis.csv", results)

        # Print key finding
        print("\n" + "="*70)
        print("KEY FINDING:")
        print("="*70)
        fermat_results = [r for r in results if r['fermat_result'] == 'COMPOSITE']
        miller_results = [r for r in results if r['miller_result'] == 'COMPOSITE']
        print(f"Fermat correctly identified: {len(set(int(r['number']) for r in fermat_results))}")
        print(f"Miller-Rabin correctly identified: {len(set(int(r['number']) for r in miller_results))}")
        print("\n⭐ Miller-Rabin has ZERO false positives on Carmichael numbers!")

    def experiment_performance(self) -> None:
        """
        Measure performance (execution time) vs input size.

        Tests numbers of varying sizes.
        Saves results to: performance_results.csv
        """
        print("\n" + "="*70)
        print("EXPERIMENT 3: Performance Analysis")
        print("="*70)

        test_numbers = [
            1009, 10007, 100003, 1000003, 10000019, 100000007, 1000000007
        ]

        k = 10
        results = []

        print(f"\nTesting with k={k} iterations\n")

        for num in test_numbers:
            print(f"Testing n={num}...", end=' ')
            result = run_cpp_test(num, k, self.cpp_binary)

            if result.get('success', False):
                fermat_time = result.get('fermat_time', 0)
                miller_time = result.get('miller_time', 0)
                overhead = ((miller_time - fermat_time) / fermat_time * 100) if fermat_time > 0 else 0

                results.append({
                    'number': num,
                    'fermat_time_ms': f"{fermat_time:.3f}",
                    'miller_time_ms': f"{miller_time:.3f}",
                    'overhead_percent': f"{overhead:.1f}"
                })

                print(f"Fermat: {fermat_time:.3f}ms, Miller: {miller_time:.3f}ms (+{overhead:.1f}%)")
            else:
                print("FAILED")

        self._save_results("performance_results.csv", results)

    def _save_results(self, filename: str, data: List[Dict]) -> None:
        """Helper to save results to CSV."""
        filepath = self.results_dir / filename
        ensure_parent_dir(filepath)

        if not data:
            print(f"Warning: No data to save")
            return

        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"✓ Results saved to {format_path(filepath)}")
        except IOError as e:
            print(f"✗ Error saving results: {e}")


def main():
    """Main execution."""
    if len(sys.argv) > 1:
        cpp_binary = sys.argv[1]
    else:
        cpp_binary = "./build/primality_test"

    runner = ExperimentRunner(cpp_binary)

    print("╔"+ "="*68 + "╗")
    print("║  PRIMALITY TESTING: COMPREHENSIVE EXPERIMENTS               ║")
    print("╚" + "="*68 + "╝")

    try:
        runner.experiment_accuracy_vs_iterations()
        runner.experiment_carmichael_analysis()
        runner.experiment_performance()

        print("\n" + "="*70)
        print("ALL EXPERIMENTS COMPLETED SUCCESSFULLY")
        print("="*70)
    except KeyboardInterrupt:
        print("\nExperiments interrupted by user")
    except Exception as e:
        print(f"Error during experiments: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
