/**
 * @file utils.cpp
 * @brief Utility functions for primality testing
 */

#include "utils.h"
#include <cmath>

static std::random_device rd;
static std::mt19937_64 gen(rd());

/**
 * @brief Compute (base^exponent) mod modulus using binary exponentiation.
 *
 * Efficiently computes modular exponentiation using repeated squaring and
 * 128-bit intermediate to avoid overflow on 64-bit inputs.
 *
 * @param base The base value.
 * @param exponent The exponent.
 * @param modulus The modulus.
 * @return The value (base^exponent) mod modulus.
 */
uint64_t modular_exp(uint64_t base, uint64_t exponent, uint64_t modulus) {
    if (modulus == 1) return 0;

    uint64_t result = 1;
    base = base % modulus;

    while (exponent > 0) {
        if (exponent & 1) {
            result = (__uint128_t)result * base % modulus;
        }
        base = (__uint128_t)base * base % modulus;
        exponent >>= 1;
    }

    return result;
}

/**
 * @brief Compute the greatest common divisor of a and b.
 *
 * Uses the iterative Euclidean algorithm.
 *
 * @param a First integer.
 * @param b Second integer.
 * @return gcd(a, b).
 */
uint64_t gcd(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

/**
 * @brief Return a uniformly distributed random integer in [min, max].
 *
 * @param min Lower bound (inclusive).
 * @param max Upper bound (inclusive).
 * @return Random uint64_t in the interval [min, max].
 */
uint64_t random_range(uint64_t min, uint64_t max) {
    std::uniform_int_distribution<uint64_t> dist(min, max);
    return dist(gen);
}

/**
 * @brief Deterministic primality check using trial division.
 *
 * Suitable for small-to-moderate values of n; checks divisibility by
 * small primes and then tests factors of the form 6k ± 1 up to sqrt(n).
 *
 * @param n Number to test.
 * @return true if n is prime, false otherwise.
 */
bool is_prime_trial_division(uint64_t n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;

    for (uint64_t i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0)
            return false;
    }

    return true;
}
