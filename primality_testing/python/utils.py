#!/usr/bin/env python3


import subprocess
import os
import time
import csv
from typing import Tuple, List, Dict
from pathlib import Path


def run_cpp_test(number: int, k: int, cpp_binary: str = "./build/primality_test") -> Dict:
    """
    Runs the C++ primality test program and parses output.

    Args:
        number: Number to test
        k: Number of iterations
        cpp_binary: Path to compiled C++ executable

    Returns:
        Dictionary with results:
        {
            'fermat_result': bool,
            'fermat_time': float,
            'miller_result': bool,
            'miller_time': float,
            'success': bool
        }

    Raises:
        FileNotFoundError: If C++ executable not found
        subprocess.CalledProcessError: If C++ program fails
    """

    if not os.path.exists(cpp_binary):
        raise FileNotFoundError(f"C++ executable not found: {cpp_binary}")

    try:
        # Run C++ program with number and k iterations
        result = subprocess.run(
            [cpp_binary, str(number), str(k)],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Parse output
        output_lines = result.stderr.split('\n') if result.stderr else result.stdout.split('\n')

        fermat_result = None
        fermat_time = None
        miller_result = None
        miller_time = None

        # State machine for parsing
        in_fermat_section = False
        in_miller_section = False

        for i, line in enumerate(output_lines):
            # Detect sections
            if 'Fermat Test:' in line:
                in_fermat_section = True
                in_miller_section = False
            elif 'Miller-Rabin Test:' in line:
                in_fermat_section = False
                in_miller_section = True
            elif 'Performance:' in line or 'Ground Truth:' in line:
                in_fermat_section = False
                in_miller_section = False

            # Parse results
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

            # Parse timing
            if 'Time:' in line and 'ms' in line:
                try:
                    time_ms = float(line.split()[-2])
                    if in_fermat_section and fermat_time is None:
                        fermat_time = time_ms
                    elif in_miller_section and miller_time is None:
                        miller_time = time_ms
                except (ValueError, IndexError):
                    pass

        return {
            'fermat_result': fermat_result,
            'fermat_time': fermat_time,
            'miller_result': miller_result,
            'miller_time': miller_time,
            'success': fermat_result is not None and miller_result is not None
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Test timed out after 30 seconds'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """
    Generates all prime numbers up to limit using Sieve of Eratosthenes.

    Args:
        limit: Upper bound (inclusive)

    Returns:
        List of all primes <= limit

    Time Complexity: O(n log log n)
    Space Complexity: O(n)

    Example:
        >>> sieve_of_eratosthenes(20)
        [2, 3, 5, 7, 11, 13, 17, 19]
    """

    if limit < 2:
        return []

    # Create boolean array, assume all numbers are prime initially
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False

    # Mark multiples of each prime as not prime
    p = 2
    while p * p <= limit:
        if is_prime[p]:
            # Mark all multiples of p as not prime
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
        p += 1

    # Collect all numbers marked as prime
    return [i for i in range(2, limit + 1) if is_prime[i]]


def is_prime_trial_division(n: int) -> bool:
    """
    Simple deterministic primality test using trial division.
    Used to verify ground truth for test cases.

    Args:
        n: Number to test

    Returns:
        True if n is prime, False otherwise

    Time Complexity: O(√n)

    Note: Only practical for numbers < 10^12
    """

    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    # Check divisibility by numbers of form 6k ± 1
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6

    return True


def get_carmichael_numbers(limit: int = 100000) -> List[int]:
    """
    Returns list of known Carmichael numbers up to limit.
    These are critical test cases.

    Args:
        limit: Upper bound

    Returns:
        List of Carmichael numbers <= limit
    """

    carmichael = [
        561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341,
        41041, 46657, 52633, 62745, 63973, 75361
    ]

    return [c for c in carmichael if c <= limit]


def save_results_to_csv(filename: str, data: List[Dict]) -> None:
    """
    Saves experimental results to CSV file.

    Args:
        filename: Output CSV filename
        data: List of result dictionaries
    """

    if not data:
        print(f"Warning: No data to save to {filename}")
        return

    # Get fieldnames from first dictionary
    fieldnames = data[0].keys()

    # Create directories if needed
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"✓ Results saved to {filename}")
    except IOError as e:
        print(f"✗ Error saving to {filename}: {e}")


def load_results_from_csv(filename: str) -> List[Dict]:
    """
    Loads experimental results from CSV file.

    Args:
        filename: Input CSV filename

    Returns:
        List of dictionaries from CSV
    """

    if not os.path.exists(filename):
        print(f"Warning: File not found: {filename}")
        return []

    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except IOError as e:
        print(f"Error loading {filename}: {e}")
        return []


def time_function(func, *args, **kwargs) -> Tuple:
    """
    Times the execution of a function.

    Args:
        func: Function to time
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Tuple of (result, execution_time_seconds)
    """

    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start

    return result, elapsed


if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")

    # Test sieve
    primes = sieve_of_eratosthenes(100)
    print(f"Primes up to 100: {len(primes)} found")

    # Test trial division
    test_cases = [17, 561, 97, 1729]
    for n in test_cases:
        result = is_prime_trial_division(n)
        print(f"{n} is {'prime' if result else 'composite'}")

    # Test Carmichael numbers
    carmichael = get_carmichael_numbers()
    print(f"\nFound {len(carmichael)} Carmichael numbers")
    print(f"First few: {carmichael[:5]}")
