/* Primality Testing: Fermat vs Miller-Rabin Comparison
 * Demonstrates the critical difference in handling Carmichael numbers
 */

#include "utils.h"
#include "fermat.h"
#include "miller_rabin.h"
#include <iostream>
#include <iomanip>
#include <vector>

using namespace std;

/**
 * @brief Run and compare Fermat and Miller-Rabin on a single number.
 *
 * Performs warmup runs, times multiple runs of each algorithm, and
 * reports average timing and correctness against an optional ground truth.
 *
 * @param n Number to test.
 * @param k Number of iterations for probabilistic tests.
 * @param is_actually_prime Optional ground truth: 1 = prime, 0 = composite, -1 = unknown.
 */
void test_number(uint64_t n, int k, int is_actually_prime = -1) {
    cout << "\n" << string(80, '=') << "\n";
    cout << "Testing n = " << n << " with k = " << k << " iterations\n";
    cout << string(80, '=') << "\n";

    // Warmup runs to eliminate cache effects
    for (int i = 0; i < 3; i++) {
        fermat_test(n, k);
        miller_rabin_test(n, k);
    }

    // Actual timed runs - run multiple times and take average
    double fermat_total = 0, miller_total = 0;
    bool fermat_is_prime, miller_is_prime;
    const int runs = 10;
    
    for (int i = 0; i < runs; i++) {
        PrimalityResult fr = fermat_test(n, k);
        fermat_total += fr.time_ms;
        fermat_is_prime = fr.is_probably_prime;
        
        PrimalityResult mr = miller_rabin_test(n, k);
        miller_total += mr.time_ms;
        miller_is_prime = mr.is_probably_prime;
    }
    
    PrimalityResult fermat_result = {fermat_is_prime, fermat_total / runs};
    PrimalityResult miller_result = {miller_is_prime, miller_total / runs};

    cout << "\nFermat Test:\n";
    cout << "  Result: " << (fermat_result.is_probably_prime ? "PROBABLY PRIME" : "COMPOSITE") << "\n";
    cout << "  Time: " << fixed << setprecision(3) << fermat_result.time_ms << " ms\n";

    cout << "\nMiller-Rabin Test:\n";
    cout << "  Result: " << (miller_result.is_probably_prime ? "PROBABLY PRIME" : "COMPOSITE") << "\n";
    cout << "  Time: " << fixed << setprecision(3) << miller_result.time_ms << " ms\n";

    if (is_actually_prime != -1) {
        cout << "\nGround Truth: " << (is_actually_prime ? "PRIME" : "COMPOSITE") << "\n";
        
        bool fermat_correct = (fermat_result.is_probably_prime == is_actually_prime);
        bool miller_correct = (miller_result.is_probably_prime == is_actually_prime);

        cout << "\nCorrectness Analysis:\n";
        cout << "  Fermat:        " << (fermat_correct ? "✓ CORRECT" : "✗ INCORRECT");
        if (!fermat_correct) {
            cout << (fermat_result.is_probably_prime ? " (False Positive)" : " (False Negative)");
        }
        cout << "\n  Miller-Rabin:  " << (miller_correct ? "✓ CORRECT" : "✗ INCORRECT");
        if (!miller_correct) {
            cout << (miller_result.is_probably_prime ? " (False Positive)" : " (False Negative)");
        }
        cout << "\n";
    }

    double overhead = ((miller_result.time_ms - fermat_result.time_ms) / fermat_result.time_ms) * 100;
    double speedup = (fermat_result.time_ms / miller_result.time_ms);
    
    cout << "\nPerformance Comparison:\n";
    cout << "  Miller-Rabin overhead: " << fixed << setprecision(1) << overhead << "%\n";
    cout << "  Relative speed: Fermat " << fixed << setprecision(2) << speedup << "x";
    if (speedup > 1) cout << " faster";
    else cout << " slower";
    cout << "\n";
    
    if (miller_result.time_ms < fermat_result.time_ms && is_actually_prime == 1) {
        cout << "\n  ℹ️  Note: Miller-Rabin can be faster for primes because it uses\n";
        cout << "      a smaller exponent d=(n-1)/2^s in the initial computation.\n";
    }
    
    double error_prob_fermat = pow(0.5, k);
    double error_prob_miller = pow(0.25, k);
    cout << "\nError Probability Bounds:\n";
    cout << "  Fermat:        ≤ (1/2)^" << k << " = " << scientific << setprecision(2) << error_prob_fermat << "\n";
    cout << "  Miller-Rabin:  ≤ (1/4)^" << k << " = " << scientific << setprecision(2) << error_prob_miller << "\n";
    cout << fixed;
}

/**
 * @brief Demonstrate Fermat's weakness on Carmichael numbers.
 *
 * Runs both tests over a set of known Carmichael numbers and prints a
 * comparative table showing when Fermat fails and Miller-Rabin succeeds.
 */
void demonstrate_carmichael_weakness() {
    cout << "\n\n" << string(80, '=') << "\n";
    cout << "CRITICAL TEST: CARMICHAEL NUMBERS\n";
    cout << string(80, '=') << "\n";
    cout << "\nCarmichael numbers are composite numbers that fool Fermat's test\n";
    cout << "for ALL bases coprime to n. Miller-Rabin detects them correctly.\n";
    cout << "\n⚠  WARNING: These are composite but Fermat may report PRIME!\n\n";

    vector<pair<uint64_t, string>> carmichael_numbers = {
        {561, "3 × 11 × 17"},
        {1105, "5 × 13 × 17"},
        {1729, "7 × 13 × 19"},
        {2465, "5 × 17 × 29"},
        {2821, "7 × 13 × 31"},
        {6601, "7 × 23 × 41"},
        {8911, "7 × 19 × 67"},
        {10585, "5 × 29 × 73"}
    };

    int k = 10;
    int fermat_correct = 0, miller_correct = 0;

    cout << left << setw(12) << "Number" 
         << setw(22) << "Factorization"
         << setw(22) << "Fermat (k=10)"
         << setw(22) << "Miller-Rabin" << "\n";
    cout << string(78, '-') << "\n";

    for (const auto& [num, factors] : carmichael_numbers) {
        PrimalityResult fermat_result = fermat_test(num, k);
        PrimalityResult miller_result = miller_rabin_test(num, k);

        if (!fermat_result.is_probably_prime) fermat_correct++;
        if (!miller_result.is_probably_prime) miller_correct++;

        cout << left << setw(12) << num
             << setw(22) << factors
             << setw(22) << (fermat_result.is_probably_prime ? "PRIME ✗" : "COMPOSITE ✓")
             << setw(22) << (miller_result.is_probably_prime ? "PRIME ✗" : "COMPOSITE ✓")
             << "\n";
    }

    cout << "\n" << string(78, '=') << "\n";
    cout << "CRITICAL FINDING - Carmichael Number Detection:\n";
    cout << string(78, '=') << "\n";
    cout << "  Fermat:        " << fermat_correct << "/" << carmichael_numbers.size() 
         << " (" << (fermat_correct * 100 / carmichael_numbers.size()) << "%) correctly identified\n";
    cout << "  Miller-Rabin:  " << miller_correct << "/" << carmichael_numbers.size()
         << " (" << (miller_correct * 100 / carmichael_numbers.size()) << "%) correctly identified\n";
    cout << string(78, '=') << "\n";

    if (fermat_correct == 0 && miller_correct == (int)carmichael_numbers.size()) {
        cout << "\n🎯 KEY RESULT:\n";
        cout << "   Fermat FAILS on ALL Carmichael numbers (false positives)!\n";
        cout << "   Miller-Rabin SUCCEEDS on ALL (no false positives)!\n";
        cout << "\n   ⚡ This is why Miller-Rabin is required for cryptography.\n";
    } else if (fermat_correct < (int)carmichael_numbers.size()) {
        cout << "\n⚠  Fermat produced " << (carmichael_numbers.size() - fermat_correct) 
             << " FALSE POSITIVES on Carmichael numbers!\n";
        cout << "   These composites were incorrectly reported as PRIME.\n";
    }
}

/**
 * @brief Demo driver for randomized primality test comparison.
 *
 * If invoked with arguments, runs the specified test; otherwise runs the
 * demonstration suite comparing Fermat and Miller-Rabin.
 */
int main(int argc, char* argv[]) {
    cout << "===================================================================\n";
    cout << "RANDOMIZED ALGORITHMS: PRIMALITY TESTING COMPARISON\n";
    cout << "Fermat vs Miller-Rabin Monte Carlo Algorithms\n";
    cout << "===================================================================\n";

    if (argc >= 3) {
        uint64_t n = stoull(argv[1]);
        int k = stoi(argv[2]);
        int is_prime = (argc >= 4) ? stoi(argv[3]) : -1;
        
        test_number(n, k, is_prime);
        return 0;
    }

    cout << "\nUsage: " << argv[0] << " <number> <iterations> [is_prime]\n";
    cout << "  Example: " << argv[0] << " 561 10 0  (test Carmichael number)\n\n";
    cout << "🔬 Running demonstration mode...\n";

    cout << "\n" << string(80, '=') << "\n";
    cout << "TEST SET 1: KNOWN PRIMES\n";
    cout << string(80, '=') << "\n";
    test_number(17, 10, 1);
    test_number(97, 10, 1);
    test_number(2147483647, 10, 1);  // Mersenne prime 2^31-1

    cout << "\n\n" << string(80, '=') << "\n";
    cout << "TEST SET 2: REGULAR COMPOSITES\n";
    cout << string(80, '=') << "\n";
    test_number(15, 10, 0);
    test_number(1234, 10, 0);

    demonstrate_carmichael_weakness();

    cout << "\n\n" << string(80, '=') << "\n";
    cout << "FINAL CONCLUSION\n";
    cout << string(80, '=') << "\n";
    cout << "\n📊 Miller-Rabin Advantages:\n\n";
    cout << "  ✓ Universal correctness: Handles ALL composites (including Carmichael)\n";
    cout << "  ✓ Tighter error bound: (1/4)^k vs Fermat's (1/2)^k\n";
    cout << "  ✓ Comparable speed: Similar or faster for primes, slightly slower worst-case\n";
    cout << "  ✓ Cryptographically secure: No exceptions or special cases\n";
    cout << "\n⚡ Performance Note:\n";
    cout << "   Miller-Rabin can be FASTER than Fermat for primes because it uses\n";
    cout << "   a reduced exponent d=(n-1)/2^s. The key advantage is CORRECTNESS,\n";
    cout << "   not speed - it detects ALL composites including Carmichael numbers.\n";
    cout << "\n🔐 Cryptographic Usage:\n";
    cout << "    With k=40-50 iterations: Error probability ≤ 2^-80 to 2^-100\n";
    cout << "    (Secure for RSA key generation and digital signatures)\n\n";

    return 0;
}
