#!/usr/bin/env python3

import csv
import random
from pathlib import Path
from typing import List, Tuple


def miller_rabin_deterministic(n: int, witnesses: List[int]) -> bool:
    """Deterministic Miller-Rabin for ground truth verification."""
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
        return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for a in witnesses:
        if a >= n:
            continue
        
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        composite = True
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                composite = False
                break
        
        if composite:
            return False
    
    return True


def is_prime_deterministic(n: int) -> bool:
    """Deterministic primality test."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    if n < 9:
        return n in [2, 3, 5, 7]
    if n % 3 == 0:
        return False
    
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    return miller_rabin_deterministic(n, witnesses)


def sieve_of_eratosthenes(limit: int) -> List[int]:
    """Generate primes up to limit."""
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    p = 2
    while p * p <= limit:
        if is_prime[p]:
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
        p += 1
    return [i for i in range(2, limit + 1) if is_prime[i]]


def next_prime(n: int) -> int:
    """Find next prime after n."""
    if n < 2:
        return 2
    if n == 2:
        return 3
    
    candidate = n + 1 if n % 2 == 0 else n + 2
    
    while True:
        if is_prime_deterministic(candidate):
            return candidate
        candidate += 2


def get_all_carmichael_numbers() -> List[int]:
    """
    Comprehensive list of Carmichael numbers.
    Includes small, medium, and large Carmichael numbers.
    """
    carmichael = [
        # Tiny (3-4 digits)
        561, 1105, 1729, 2465, 2821, 6601, 8911,
        
        # Small (5 digits)
        10585, 15841, 29341, 41041, 46657, 52633, 62745, 63973, 75361,
        
        # Medium (6 digits)
        101101, 115921, 126217, 162401, 172081, 188461, 252601, 278545,
        294409, 314821, 334153, 340561, 399001, 410041, 449065, 488881,
        512461, 530881, 552721, 656601, 658801, 670033, 748657, 825265,
        838201, 852841, 997633,
        
        # Large (7 digits)
        1024651, 1033669, 1050985, 1082809, 1152271, 1193221, 1461241,
        1569457, 1615681, 1773289, 1857241, 1909001, 2100901, 2113921,
        2433601, 2455921, 2508013, 2531845, 2628073, 2704801, 3057601,
        3146221, 3581761, 4335241, 4463641, 4767841, 4903921, 5049001,
        5148001, 5444489, 5481451, 5968873, 6733693, 6868261, 7995169,
        8134561, 8341201, 8355841, 8719921, 9439201, 9582145,
        
        # Very Large (8-9 digits)
        10024561, 10185841, 10267951, 10606681, 11346205, 11972017,
        12945745, 13992265, 15247621, 15829633, 16778881, 18162001,
        19384289, 23382529, 26474581, 27062101, 29111881, 31405501,
        34657141, 41471521, 43331401, 44238481, 45318561, 47006785,
        49699921, 52843201, 55462177, 56052361, 60957361, 63623641,
        67902031, 68154001, 75151441, 79207105, 82929001, 83966401,
        87318001, 88689601, 93614521, 97986421,
        
        # Huge (10+ digits)
        104569501, 118901521, 123551821, 129024481, 149490337,
        168003672409, 564651361, 1024651, 1152271, 
        278545, 10585, 15841, 29341, 41041, 46657, 52633,
    ]
    
    return sorted(set(carmichael))


def generate_small_accuracy_dataset() -> List[Tuple[int, bool, str]]:
    """
    Generate dataset for ACCURACY testing.
    Range: 100 to 10,000,000 (10^2 to 10^7)
    Focus: Balanced primes/composites with ALL Carmichael numbers
    """
    print("\n" + "="*70)
    print("GENERATING SMALL NUMBERS DATASET (ACCURACY TESTING)")
    print("="*70)
    
    dataset = []
    
    # Get all Carmichael numbers in range
    all_carmichael = get_all_carmichael_numbers()
    carmichael_small = [c for c in all_carmichael if 100 <= c <= 10000000]
    
    print(f"Found {len(carmichael_small)} Carmichael numbers in range")
    
    # Add all Carmichael numbers (CRITICAL for testing)
    for c in carmichael_small:
        dataset.append((c, False, 'carmichael'))
    
    # Generate primes across range
    print("Generating primes...")
    ranges = [
        (100, 1000, 30),
        (1000, 10000, 40),
        (10000, 100000, 40),
        (100000, 1000000, 40),
        (1000000, 10000000, 30),
    ]
    
    for start, end, count in ranges:
        print(f"  Range [{start}, {end}): {count} primes")
        primes_found = 0
        n = start
        while primes_found < count and n < end:
            n = next_prime(n)
            if n < end:
                dataset.append((n, True, 'prime'))
                primes_found += 1
    
    # Generate regular composites (excluding Carmichael)
    print("Generating composites...")
    carmichael_set = set(carmichael_small)
    
    for start, end, count in ranges:
        print(f"  Range [{start}, {end}): {count} composites")
        composites_found = 0
        n = start
        while composites_found < count and n < end:
            if not is_prime_deterministic(n) and n not in carmichael_set:
                dataset.append((n, False, 'composite'))
                composites_found += 1
            n += 1
    
    # Add some pseudoprimes (Fermat liars that are NOT Carmichael)
    pseudoprimes_non_carmichael = [341, 645, 1387, 2047, 2701, 3277, 4033, 4369, 4371, 5461]
    for p in pseudoprimes_non_carmichael:
        if p not in carmichael_set and 100 <= p <= 10000000:
            dataset.append((p, False, 'pseudoprime'))
    
    print(f"\nTotal: {len(dataset)} test cases")
    return dataset


def generate_large_asymptotic_dataset() -> List[Tuple[int, bool, str, int]]:
    """
    Generate dataset for ASYMPTOTIC COMPLEXITY analysis.
    Range: 10^3 to 10^18 (spanning 16 orders of magnitude)
    Focus: Evenly distributed across magnitudes
    """
    print("\n" + "="*70)
    print("GENERATING LARGE NUMBERS DATASET (ASYMPTOTIC ANALYSIS)")
    print("="*70)
    
    dataset = []
    
    # Magnitudes to test (powers of 10)
    magnitudes = [
        10**3, 10**4, 10**5, 10**6, 10**7, 10**8, 10**9,
        10**10, 10**11, 10**12, 10**13, 10**14, 10**15,
        10**16, 10**17, 10**18
    ]
    
    # For each magnitude, get primes
    print("Generating primes at different magnitudes...")
    for mag in magnitudes:
        mag_digits = len(str(mag))
        print(f"  10^{mag_digits-1} ({mag_digits} digits): ", end='', flush=True)
        
        # Get 5 primes near this magnitude
        p = next_prime(mag)
        for i in range(5):
            dataset.append((p, True, 'prime', mag_digits))
            p = next_prime(p + 1)
        print(f"5 primes")
    
    # For each magnitude, generate composites
    print("\nGenerating composites at different magnitudes...")
    for mag in magnitudes:
        mag_digits = len(str(mag))
        print(f"  10^{mag_digits-1} ({mag_digits} digits): ", end='', flush=True)
        
        # Generate 5 composites by multiplying primes
        for i in range(5):
            # Create composite = p1 * p2 where both are near sqrt(mag)
            sqrt_mag = int(mag**0.5)
            p1 = next_prime(sqrt_mag + random.randint(0, sqrt_mag // 10))
            p2 = next_prime(p1 + random.randint(100, 10000))
            composite = p1 * p2
            
            if mag <= composite < mag * 10:
                dataset.append((composite, False, 'composite', len(str(composite))))
        print(f"5 composites")
    
    # Add large Carmichael numbers
    print("\nAdding Carmichael numbers...")
    all_carmichael = get_all_carmichael_numbers()
    for c in all_carmichael:
        mag_digits = len(str(c))
        dataset.append((c, False, 'carmichael', mag_digits))
    
    print(f"\nTotal: {len(dataset)} test cases")
    return dataset


def save_small_dataset(filename: str = "test_cases_small.csv"):
    """Save small numbers dataset for accuracy testing."""
    dataset = generate_small_accuracy_dataset()
    
    filepath = Path('../data') / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving to {filepath}...")
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['number', 'is_prime', 'category'])
        writer.writeheader()
        
        for number, is_prime, category in sorted(dataset, key=lambda x: x[0]):
            writer.writerow({
                'number': number,
                'is_prime': is_prime,
                'category': category
            })
    
    # Print summary
    categories = {}
    for _, _, cat in dataset:
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n" + "="*70)
    print("SMALL DATASET SUMMARY")
    print("="*70)
    print(f"Total: {len(dataset)} test cases")
    print("\nBy category:")
    for cat in sorted(categories.keys()):
        print(f"  {cat:15s}: {categories[cat]:4d} cases")
    
    primes = sum(1 for _, is_p, _ in dataset if is_p)
    composites = len(dataset) - primes
    print(f"\nPrimes: {primes}, Composites: {composites}")
    print(f"Range: {min(n for n, _, _ in dataset):,} to {max(n for n, _, _ in dataset):,}")


def save_large_dataset(filename: str = "test_cases_large.csv"):
    """Save large numbers dataset for asymptotic analysis."""
    dataset = generate_large_asymptotic_dataset()
    
    filepath = Path('../data') / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving to {filepath}...")
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['number', 'is_prime', 'category', 'magnitude'])
        writer.writeheader()
        
        for number, is_prime, category, magnitude in sorted(dataset, key=lambda x: x[0]):
            writer.writerow({
                'number': number,
                'is_prime': is_prime,
                'category': category,
                'magnitude': magnitude
            })
    
    # Print summary
    categories = {}
    magnitudes = {}
    for _, _, cat, mag in dataset:
        categories[cat] = categories.get(cat, 0) + 1
        magnitudes[mag] = magnitudes.get(mag, 0) + 1
    
    print("\n" + "="*70)
    print("LARGE DATASET SUMMARY")
    print("="*70)
    print(f"Total: {len(dataset)} test cases")
    
    print("\nBy category:")
    for cat in sorted(categories.keys()):
        print(f"  {cat:15s}: {categories[cat]:4d} cases")
    
    print("\nBy magnitude (digits):")
    for mag in sorted(magnitudes.keys()):
        print(f"  10^{mag-1:2d} - 10^{mag:2d}: {magnitudes[mag]:3d} cases")
    
    numbers = [n for n, _, _, _ in dataset]
    print(f"\nRange: {min(numbers):,} to {max(numbers):,}")
    print(f"Span: {max(numbers) / min(numbers):.2e}")


def main():
    """Generate both datasets."""
    print("="*70)
    print("COMPREHENSIVE DATASET GENERATOR")
    print("="*70)
    
    # Generate small dataset for accuracy
    save_small_dataset("test_cases_small.csv")
    
    print("\n" + "="*70 + "\n")
    
    # Generate large dataset for asymptotic analysis
    save_large_dataset("test_cases_large.csv")
    
    print("\n" + "="*70)
    print("GENERATION COMPLETE!")
    print("="*70)
    print("\nCreated two datasets:")
    print("  1. test_cases_small.csv - For accuracy testing (10^2 to 10^7)")
    print("  2. test_cases_large.csv - For asymptotic analysis (10^3 to 10^18)")


if __name__ == "__main__":
    main()
