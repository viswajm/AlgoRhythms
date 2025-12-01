#!/usr/bin/env python3

import csv
import random
from pathlib import Path
from typing import List, Tuple


def miller_rabin_deterministic(n: int, witnesses: List[int]) -> bool:
    """
    Deterministic Miller-Rabin for generating ground truth.
    For n < 3,317,044,064,679,887,385,961,981, testing a=2,3,5,7,11,13,17,19,23,29,31,37 is deterministic.
    """
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop
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
    """Deterministic primality test using Miller-Rabin with known witnesses."""
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
    
    # These witnesses work for all n < 3,317,044,064,679,887,385,961,981
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    return miller_rabin_deterministic(n, witnesses)


def next_prime(n: int) -> int:
    """Find next prime after n."""
    if n < 2:
        return 2
    if n == 2:
        return 3
    
    # Start with next odd number
    candidate = n + 1 if n % 2 == 0 else n + 2
    
    while True:
        if is_prime_deterministic(candidate):
            return candidate
        candidate += 2


def generate_primes_by_magnitude() -> List[int]:
    """
    Generate primes at different magnitudes to test scaling.
    From 10^3 to 10^18 (limit of 64-bit)
    """
    primes = []
    
    # Target magnitudes (powers of 10)
    magnitudes = [
        10**3,      # 1,000
        10**4,      # 10,000
        10**5,      # 100,000
        10**6,      # 1,000,000
        10**7,      # 10,000,000
        10**8,      # 100,000,000
        10**9,      # 1,000,000,000
        10**10,     # 10,000,000,000
        10**11,     # 100,000,000,000
        10**12,     # 1,000,000,000,000
        10**13,     # 10^13
        10**14,     # 10^14
        10**15,     # 10^15
        10**16,     # 10^16
        10**17,     # 10^17
        10**18,     # 10^18 (near 64-bit limit)
    ]
    
    print("Generating primes at different magnitudes...")
    for mag in magnitudes:
        # Get 5 primes near this magnitude
        print(f"  Finding primes near 10^{len(str(mag))-1}...")
        p = next_prime(mag)
        for _ in range(5):
            primes.append(p)
            p = next_prime(p + 1)
    
    return primes


def generate_composites_by_magnitude() -> List[int]:
    """Generate composite numbers at different magnitudes."""
    composites = []
    
    magnitudes = [
        10**3, 10**4, 10**5, 10**6, 10**7, 10**8, 10**9,
        10**10, 10**11, 10**12, 10**13, 10**14, 10**15, 10**16, 10**17, 10**18
    ]
    
    print("Generating composites at different magnitudes...")
    for mag in magnitudes:
        print(f"  Finding composites near 10^{len(str(mag))-1}...")
        # Generate 5 composites near this magnitude
        for _ in range(5):
            # Create composite by multiplying two primes
            p1 = next_prime(int(mag**0.5))
            p2 = next_prime(p1 + random.randint(100, 10000))
            composite = p1 * p2
            
            # Make sure it's in the right range
            if composite >= mag and composite < mag * 10:
                composites.append(composite)
    
    return composites


def generate_large_carmichael() -> List[int]:
    """
    Known large Carmichael numbers for testing.
    These are critical for showing Fermat's weakness.
    """
    # Carmichael numbers spanning wide range
    carmichael = [
        # Small ones
        561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341,
        41041, 46657, 52633, 62745, 63973, 75361,
        
        # Medium (10^5 - 10^6)
        101101, 115921, 126217, 162401, 172081, 188461, 252601, 278545,
        294409, 314821, 334153, 340561, 399001, 410041, 449065, 488881,
        
        # Large (10^6+)
        512461, 530881, 552721, 656601, 658801, 670033, 748657, 825265,
        838201, 852841, 997633,
        
        # Very large (10^7+)
        1024651, 1033669, 1050985, 1082809, 1569457, 1615681, 3057601,
        3146221, 3581761, 5148001, 5444489, 5481451, 5968873, 6733693,
        6868261, 7995169, 8134561, 8341201, 8355841, 8719921,
    ]
    
    return carmichael


def generate_asymptotic_test_suite() -> List[Tuple[int, bool, str, int]]:
    """
    Generate test suite optimized for asymptotic complexity analysis.
    
    Returns:
        List of (number, is_prime, category, magnitude) tuples
    """
    test_suite = []
    
    print("\n" + "="*70)
    print("GENERATING ASYMPTOTIC ANALYSIS TEST SUITE")
    print("="*70)
    
    # Generate primes at various magnitudes
    primes = generate_primes_by_magnitude()
    for p in primes:
        magnitude = len(str(p))
        test_suite.append((p, True, 'prime', magnitude))
    
    # Generate composites at various magnitudes
    composites = generate_composites_by_magnitude()
    for c in composites:
        magnitude = len(str(c))
        test_suite.append((c, False, 'composite', magnitude))
    
    # Add Carmichael numbers
    print("\nAdding Carmichael numbers...")
    carmichael = generate_large_carmichael()
    for c in carmichael:
        magnitude = len(str(c))
        test_suite.append((c, False, 'carmichael', magnitude))
    
    return test_suite


def save_asymptotic_test_suite(filename: str = "test_cases_large.csv") -> None:
    """Save the asymptotic test suite to CSV."""
    
    test_suite = generate_asymptotic_test_suite()
    
    filepath = Path('../data') / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSaving to {filepath}...")
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['number', 'is_prime', 'category', 'magnitude'])
        writer.writeheader()
        
        for number, is_prime, category, magnitude in sorted(test_suite, key=lambda x: x[0]):
            writer.writerow({
                'number': number,
                'is_prime': is_prime,
                'category': category,
                'magnitude': magnitude
            })
    
    print(f"Saved {len(test_suite)} test cases")
    
    # Print summary
    print("\n" + "="*70)
    print("DATASET SUMMARY")
    print("="*70)
    
    categories = {}
    magnitudes = {}
    
    for _, _, cat, mag in test_suite:
        categories[cat] = categories.get(cat, 0) + 1
        magnitudes[mag] = magnitudes.get(mag, 0) + 1
    
    print("\nBy category:")
    for cat in sorted(categories.keys()):
        print(f"  {cat:15s}: {categories[cat]:4d} cases")
    
    print("\nBy magnitude (digits):")
    for mag in sorted(magnitudes.keys()):
        print(f"  10^{mag-1:2d} - 10^{mag:2d}: {magnitudes[mag]:4d} cases")
    
    print("\nThis dataset spans:")
    print(f"  Smallest: 10^{min(magnitudes.keys())-1}")
    print(f"  Largest:  10^{max(magnitudes.keys())-1}")
    print(f"  Range:    {max(magnitudes.keys()) - min(magnitudes.keys())} orders of magnitude")
    print("\nWith this range, you should observe O(log³n) complexity!")


def main():
    """Main execution."""
    print("Large Number Generator for Asymptotic Complexity Analysis")
    print("="*70)
    
    save_asymptotic_test_suite()
    
    print("\n" + "="*70)
    print("DONE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Run experiments with this dataset")
    print("2. Plot time vs log(n) to observe O(log³n) scaling")
    print("3. The slope on log-log plot should be ~3 for modular exponentiation")


if __name__ == "__main__":
    main()
