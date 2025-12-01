#ifndef UTILS_H
#define UTILS_H

#include <iostream>
#include <cstdint>
#include <random>

uint64_t modular_exp(uint64_t base, uint64_t exponent, uint64_t modulus);

uint64_t gcd(uint64_t a, uint64_t b);

uint64_t random_range(uint64_t min, uint64_t max);

bool is_prime_trial_division(uint64_t n);

#endif // UTILS_H
