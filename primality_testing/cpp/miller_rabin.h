#ifndef MILLER_RABIN_H
#define MILLER_RABIN_H

#include "fermat.h"  // Reuse PrimalityResult struct
#include <cstdint>

PrimalityResult miller_rabin_test(uint64_t n, int k);

bool miller_rabin_test_single(uint64_t n, uint64_t d, int s, uint64_t base);

#endif // MILLER_RABIN_H
