#include "fermat.h"
#include "utils.h"

/**
 * @brief Perform a single Fermat check for a given base.
 *
 * Returns true if base^(n-1) ≡ 1 (mod n), which is a necessary condition
 * for n to be prime with respect to this base.
 *
 * @param n The number to test.
 * @param base The base to use for the Fermat check.
 * @return true if the congruence holds, false otherwise.
 */
bool fermat_test_single(uint64_t n, uint64_t base) {
    if (gcd(base, n) > 1) {
        return false;
    }

    uint64_t result = modular_exp(base, n - 1, n);
    return result == 1;
}

/**
 * @brief Run the Fermat primality test k times and measure elapsed time.
 *
 * Tries k random bases and returns a PrimalityResult containing a boolean
 * (probably prime or composite) and the elapsed wall-clock time in ms.
 *
 * @param n Number to test.
 * @param k Number of random bases (iterations).
 * @return PrimalityResult with is_probably_prime and time_ms fields.
 */
PrimalityResult fermat_test(uint64_t n, int k) {
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

    for (int i = 0; i < k; i++) {
        uint64_t base = random_range(2, n - 2);

        if (!fermat_test_single(n, base)) {
            auto end = std::chrono::high_resolution_clock::now();
            double time_ms = std::chrono::duration<double, std::milli>(end - start).count();
            return {false, time_ms};
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    double time_ms = std::chrono::duration<double, std::milli>(end - start).count();
    return {true, time_ms};
}
