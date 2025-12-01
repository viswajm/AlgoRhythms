/**
 * @file miller_rabin.cpp
 * @brief Miller-Rabin primality test implementation
 */

#include "miller_rabin.h"
#include "utils.h"
#include <chrono>

/**
 * @brief Perform a single Miller-Rabin witness test for a given base.
 *
 * Tests whether the provided base is a witness for compositeness using the
 * decomposition n-1 = 2^s * d. Returns true if this base passes the
 * strong probable-prime checks, false if it proves compositeness.
 *
 * @param n The number to test.
 * @param d The odd component of n-1 (n-1 = 2^s * d).
 * @param s The exponent of two in n-1.
 * @param base The base to test.
 * @return true if base indicates n may be prime for this round, false if composite.
 */
bool miller_rabin_test_single(uint64_t n, uint64_t d, int s, uint64_t base) {
    uint64_t x = modular_exp(base, d, n);

    if (x == 1 || x == n - 1) {
        return true;
    }

    for (int r = 0; r < s - 1; r++) {
        x = (__uint128_t)x * x % n;

        if (x == n - 1) return true;
        if (x == 1) return false;
    }

    return false;
}

/**
 * @brief Run the Miller-Rabin primality test k times and measure elapsed time.
 *
 * Chooses k random bases and applies the single-round witness test; returns
 * a PrimalityResult with a boolean (probably prime) and elapsed wall-clock time in ms.
 *
 * @param n Number to test.
 * @param k Number of random bases (iterations).
 * @return PrimalityResult with is_probably_prime and time_ms fields.
 */
PrimalityResult miller_rabin_test(uint64_t n, int k) {
    auto start = std::chrono::high_resolution_clock::now();

    if (n == 2) {
        auto end = std::chrono::high_resolution_clock::now();
        double time_ms = std::chrono::duration<double, std::milli>(end - start).count();
        return {true, time_ms};
    }

    if (n < 2 || n % 2 == 0) {
        auto end = std::chrono::high_resolution_clock::now();
        double time_ms = std::chrono::duration<double, std::milli>(end - start).count();
        return {false, time_ms};
    }

    uint64_t d = n - 1;
    int s = 0;
    while (d % 2 == 0) {
        d /= 2;
        s++;
    }

    for (int i = 0; i < k; i++) {
        uint64_t base = random_range(2, n - 2);

        if (!miller_rabin_test_single(n, d, s, base)) {
            auto end = std::chrono::high_resolution_clock::now();
            double time_ms = std::chrono::duration<double, std::milli>(end - start).count();
            return {false, time_ms};
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    double time_ms = std::chrono::duration<double, std::milli>(end - start).count();
    return {true, time_ms};
}
