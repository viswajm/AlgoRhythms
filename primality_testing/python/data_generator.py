#!/usr/bin/env python3

import csv
from pathlib import Path
from typing import List, Tuple
from utils import sieve_of_eratosthenes, get_carmichael_numbers, is_prime_trial_division


class DataGenerator:
    """Generates test datasets for primality testing."""

    def __init__(self, output_dir: str = "./data"):
        """
        Initialize the data generator.

        Args:
            output_dir: Directory to save generated data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_primes(self, limit: int = 10000) -> List[int]:
        """
        Generate list of prime numbers up to limit.

        Args:
            limit: Upper bound for prime generation

        Returns:
            List of prime numbers
        """
        primes = sieve_of_eratosthenes(limit)

        # Add some large Mersenne primes
        large_primes = [
            2147483647,      # 2^31 - 1
            2305843009213693951  # 2^61 - 1 (large, use carefully)
        ]

        primes.extend([p for p in large_primes if p <= limit * 1000])

        return sorted(set(primes))

    def generate_composites(self, limit: int = 10000) -> List[int]:
        """
        Generate list of composite numbers up to limit.

        Args:
            limit: Upper bound

        Returns:
            List of composite numbers
        """
        composites = []

        # Add regular composites
        for i in range(4, limit + 1):
            if not is_prime_trial_division(i):
                composites.append(i)

        # Add Fermat pseudoprimes (base 2)
        pseudoprimes = [341, 561, 645, 1105, 1387, 1729, 1905, 2047, 2465, 2701,
                       2821, 6601, 8911, 10585, 15841, 29341, 41041, 46657, 52633]
        composites.extend([p for p in pseudoprimes if p <= limit])

        return sorted(set(composites))

    def generate_test_suite(self) -> List[Tuple[int, bool, str]]:
        """
        Generate complete test suite with ground truth.

        Returns:
            List of (number, is_prime, category) tuples
        """
        test_suite = []

        # Generate primes
        primes = self.generate_primes(1000)  # Use smaller limit for speed
        for p in primes[:100]:  # Take first 100
            test_suite.append((p, True, 'prime'))

        # Generate regular composites (avoiding pseudoprimes and Carmichael numbers)
        carmichael_set = set(get_carmichael_numbers())
        pseudoprime_set = {341, 645, 1387}  # Pseudoprimes that are NOT Carmichael
        
        composites = self.generate_composites(1000)
        composite_count = 0
        for c in composites:
            # Skip if it's a Carmichael number or pseudoprime (will be added separately)
            if c not in carmichael_set and c not in pseudoprime_set:
                test_suite.append((c, False, 'composite'))
                composite_count += 1
                if composite_count >= 100:
                    break

        # Add pseudoprimes (Fermat pseudoprimes base-2 that are NOT Carmichael)
        # 341, 645, 1387 are pseudoprimes but NOT Carmichael numbers
        for p in pseudoprime_set:
            test_suite.append((p, False, 'pseudoprime'))

        # Add ALL Carmichael numbers (CRITICAL - these are the key test cases)
        carmichael = get_carmichael_numbers()
        for c in carmichael[:16]:  # First 16
            test_suite.append((c, False, 'carmichael'))

        return test_suite

    def save_test_suite_to_csv(self, filename: str = "test_cases.csv") -> None:
        """
        Save test suite to CSV file.

        Args:
            filename: Output filename (relative to output_dir)
        """
        test_suite = self.generate_test_suite()
        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['number', 'is_prime', 'category'])
                writer.writeheader()
                for number, is_prime, category in test_suite:
                    writer.writerow({
                        'number': number,
                        'is_prime': is_prime,
                        'category': category
                    })
            print(f"✓ Test suite saved to {filepath}")
            print(f"  Generated {len(test_suite)} test cases")
        except IOError as e:
            print(f"✗ Error saving test suite: {e}")

    def print_summary(self) -> None:
        """Print summary of generated datasets."""
        test_suite = self.generate_test_suite()

        print("\n" + "="*70)
        print("GENERATED TEST SUITE SUMMARY")
        print("="*70)

        categories = {}
        for _, _, category in test_suite:
            categories[category] = categories.get(category, 0) + 1

        print(f"\nTotal test cases: {len(test_suite)}")
        print("\nBreakdown by category:")
        for category, count in sorted(categories.items()):
            print(f"  {category:15s}: {count:4d} cases")

        # Show some examples
        print("\nExamples:")
        for category in ['prime', 'composite', 'carmichael']:
            examples = [n for n, _, c in test_suite if c == category][:3]
            if examples:
                print(f"  {category:15s}: {examples}")


def main():
    """Main execution."""
    print("Data Generator for Primality Testing Project")
    print("="*70)

    generator = DataGenerator()
    generator.save_test_suite_to_csv()
    generator.print_summary()


if __name__ == "__main__":
    main()
