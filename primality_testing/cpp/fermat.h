#ifndef FERMAT_H
#define FERMAT_H

#include <cstdint>
#include <chrono>

struct PrimalityResult {
    bool is_probably_prime;  ///< true if number is probably prime, false if definitely composite
    double time_ms;          ///< Execution time in milliseconds
};


PrimalityResult fermat_test(uint64_t n, int k);

bool fermat_test_single(uint64_t n, uint64_t base);

#endif // FERMAT_H
