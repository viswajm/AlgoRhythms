# Primality Testing: Fermat vs Miller-Rabin

A comprehensive implementation and analysis of randomized primality testing algorithms in C++ with Python analysis tools. This project compares the **Fermat Primality Test** and **Miller-Rabin Primality Test**, focusing on accuracy, performance, and handling of edge cases like Carmichael numbers.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
  - [Basic Operations](#basic-operations)
  - [Running Experiments](#running-experiments)
  - [Advanced Analysis](#advanced-analysis)
  - [Generating Plots](#generating-plots)
  - [Testing Specific Numbers](#testing-specific-numbers)
- [Makefile Commands Reference](#makefile-commands-reference)
- [Results Directory Structure](#results-directory-structure)
- [Key Findings](#key-findings)
- [Implementation Details](#implementation-details)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project implements and benchmarks two Monte Carlo algorithms for primality testing:

1. **Fermat Primality Test**: Fast but vulnerable to Carmichael numbers
2. **Miller-Rabin Primality Test**: More robust, cryptographically secure

The implementation includes:
- High-performance C++ implementations with arbitrary precision arithmetic
- Comprehensive Python analysis and visualization tools
- Extensive benchmarking across different input sizes and iteration counts
- Special handling of edge cases (Carmichael numbers, pseudoprimes)
- Publication-quality visualizations

---

## ✨ Features

- **Dual Implementation**: Efficient C++ backends with Python analysis frontends
- **Comprehensive Testing**: Accuracy analysis, performance benchmarking, asymptotic complexity analysis
- **Edge Case Analysis**: Special focus on Carmichael numbers and pseudoprimes
- **Automated Workflows**: One-command execution of complete analysis pipelines
- **Rich Visualizations**: Publication-quality plots with matplotlib
- **Reproducible Results**: All experiments generate CSV data for further analysis

---

## 📁 Project Structure

```
primality_testing/
├── README.md                    # This file
├── Makefile                     # Build and automation commands
├── setup.sh                     # Initial setup script
├── cpp/                         # C++ implementations
│   ├── primality_test          # Main testing binary
│   ├── benchmark_fermat        # Benchmark binary
│   ├── fermat.cpp/h            # Fermat test implementation
│   ├── miller_rabin.cpp/h      # Miller-Rabin implementation
│   └── utils.cpp/h             # Utility functions
├── python/                      # Python analysis tools
│   ├── experiment_runner.py    # Main experiment orchestrator
│   ├── benchmark_fermat.py     # Fermat benchmarking
│   ├── comprehensive_analysis.py  # Full analysis suite
│   ├── asymptotic_benchmark.py    # Complexity analysis
│   ├── plotter.py              # Basic plotting
│   ├── plot_fermat_analysis.py    # Fermat-specific plots
│   ├── plot_fermat_benchmarks.py  # Benchmark visualizations
│   ├── plot_comprehensive_results.py  # Comprehensive plots
│   └── path_utils.py           # Path resolution utilities
├── data/                        # Test datasets
│   ├── test_cases_small.csv    # Small test suite (454 cases)
│   └── test_cases_large.csv    # Large test suite
└── results/                     # All generated results (auto-created)
    ├── *.csv                    # Experiment data
    ├── plots/                   # Basic plots
    ├── fermat_analysis/         # Fermat-specific analysis
    ├── fermat_benchmarks/       # Benchmark results
    └── comprehensive/           # Comprehensive analysis
```

---

## 🔧 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, Fedora, or similar)
- **Compiler**: GCC 7.0+ with C++17 support
- **Python**: Python 3.8+
- **Make**: GNU Make

### Python Dependencies
- matplotlib (for plotting)
- numpy (for numerical analysis)
- Other standard library modules (csv, subprocess, pathlib, etc.)

---

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Clone the repository and navigate to the project directory
cd primality_testing

# Run the setup script (installs dependencies, creates virtual environment)
make setup
```

This will:
- Create a Python virtual environment
- Install required Python packages (matplotlib, numpy)
- Build the C++ binaries
- Set up the project structure

### 2. Build C++ Components

```bash
make build
```

This compiles:
- `cpp/primality_test` - Main testing binary
- `cpp/benchmark_fermat` - Benchmarking binary

### 3. Run Basic Experiments

```bash
# Run all basic experiments (accuracy, Carmichael analysis, performance)
make experiments

# View analysis of results
make analyze

# Generate plots
make plot
```

### 4. View Results

```bash
# Display the results directory structure
make show-results

# Results are saved in:
# - results/*.csv (experiment data)
# - results/plots/ (visualizations)
```

---

## 📖 Detailed Usage

### Basic Operations

#### Run a Demo
```bash
make run
```
Executes the C++ binary with default test cases, demonstrating both algorithms.

#### Test a Specific Number
```bash
make test-number n=561 k=10
```
- `n` = Number to test (e.g., 561 is a Carmichael number)
- `k` = Number of iterations (higher = more accurate)

**Examples:**
```bash
# Test a prime number
make test-number n=1000000007 k=20

# Test a Carmichael number (exposes Fermat weakness)
make test-number n=1729 k=10

# Test a composite number
make test-number n=1000 k=5
```

#### Test Carmichael Numbers
```bash
make test-carmichael
```
Tests several well-known Carmichael numbers to demonstrate algorithm differences.

---

### Running Experiments

#### 1. Basic Experiments Suite
```bash
make experiments
```

**What it does:**
- Tests accuracy vs. number of iterations (k = 1, 2, 3, 5, 10, 20, 50)
- Analyzes performance on Carmichael numbers
- Compares execution time across different input sizes

**Output:**
- `results/accuracy_vs_k.csv` - Accuracy measurements
- `results/carmichael_analysis.csv` - Carmichael number results
- `results/performance_results.csv` - Timing data

**Duration:** ~2-5 minutes

#### 2. Analyze Results
```bash
make analyze
```

**What it does:**
- Generates comprehensive analysis report
- Shows accuracy comparisons
- Highlights Carmichael number detection rates
- Calculates performance overhead

**Output:** Console report with key findings

---

### Advanced Analysis

#### 1. Fermat Benchmarks
```bash
make benchmark
```

**What it does:**
- Runs detailed Fermat primality test benchmarks
- Tests scaling across input sizes (10³ to 10¹⁰)
- Analyzes k-variation (different iteration counts)
- Benchmarks Carmichael number detection

**Output:**
- `results/fermat_benchmarks/fermat_scaling.csv`
- `results/fermat_benchmarks/fermat_k_variation.csv`

**Duration:** ~5-10 minutes

#### 2. Comprehensive Analysis
```bash
make comprehensive
```

**What it does:**
- Accuracy analysis on 454 test cases
- Asymptotic complexity analysis on large numbers
- Category-wise performance breakdown

**Output:**
- `results/comprehensive/asymptotic_analysis.csv`

**Duration:** ~10-15 minutes

#### 3. Asymptotic Complexity Analysis
```bash
make asymptotic
```

**What it does:**
- Tests algorithm scaling with input size
- Verifies O(log³n) complexity empirically
- Generates timing data across magnitudes

**Output:**
- `results/asymptotic/*.csv`

**Duration:** ~5-10 minutes

---

### Generating Plots

#### 1. Basic Plots
```bash
make plot
```

**Generates:**
- `accuracy.png` - Accuracy vs iterations comparison
- `carmichael.png` - Carmichael number detection comparison
- `performance.png` - Performance comparison

**Location:** `results/plots/`

#### 2. Fermat Analysis Plots
```bash
make plot-fermat
```

**Generates:**
1. `fermat_accuracy_vs_k.png` - Fermat accuracy across k values
2. `fermat_false_positive_rates.png` - FP rates by category
3. `fermat_asymptotic_complexity.png` - Time complexity analysis
4. `fermat_carmichael_detection.png` - Carmichael detection rates
5. `fermat_time_distribution.png` - Execution time distributions

**Location:** `results/fermat_analysis/plots/`

**Note:** Requires `make comprehensive` to be run first for plot 3.

#### 3. Miller-Rabin Analysis Plots
```bash
make plot-miller-rabin
```

**Generates:**
1. `miller_rabin_accuracy_vs_k.png` - Miller-Rabin accuracy (should be 100%)
2. `miller_rabin_false_positive_rates.png` - FP rates (should be 0%)
3. `miller_rabin_asymptotic_complexity.png` - Time complexity analysis
4. `miller_rabin_time_distribution.png` - Execution time distributions

**Location:** `results/miller_rabin_analysis/plots/`

**Note:** Requires `make comprehensive` to be run first for plot 3.

#### 4. Fermat Benchmark Plots
```bash
make plot-fermat-benchmarks
```

**Generates:**
1. `fermat_scaling.png` - Performance scaling analysis
2. `fermat_k_variation.png` - Impact of iteration count
3. `fermat_comprehensive.png` - Multi-panel benchmark overview

**Location:** `results/fermat_benchmarks/plots/`

**Prerequisite:** Run `make benchmark-fermat` first.

#### 5. Miller-Rabin Benchmark Plots
```bash
make plot-miller-rabin-benchmarks
```

**Generates:**
1. `miller_rabin_scaling.png` - Performance scaling analysis
2. `miller_rabin_k_variation.png` - Impact of iteration count
3. `miller_rabin_comprehensive.png` - Multi-panel benchmark overview

**Location:** `results/miller_rabin_benchmarks/plots/`

**Prerequisite:** Run `make benchmark-miller-rabin` first.

#### 6. Comprehensive Plots
```bash
make plot-comprehensive
```

**Generates:**
1. `accuracy_vs_k.png` - Both algorithms accuracy comparison
2. `false_positive_rates.png` - FP rates by category for both
3. `asymptotic_complexity.png` - Complexity analysis both algorithms
4. `performance_comparison.png` - Head-to-head performance
5. `carmichael_detection.png` - Carmichael detection comparison

**Location:** `results/comprehensive/plots/`

#### 7. Generate All Plots
```bash
make plot-all
```

**What it does:**
- Runs all plot commands: `plot`, `plot-fermat`, `plot-miller-rabin`, `plot-fermat-benchmarks`, `plot-miller-rabin-benchmarks`, and `plot-comprehensive`
- Generates all 20+ visualization plots at once

**Duration:** ~5-10 minutes (includes running tests)

---

### Testing Specific Numbers

#### Example Test Cases

**Prime Numbers:**
```bash
make test-number n=1009 k=10        # Small prime
make test-number n=1000000007 k=10  # Large prime
make test-number n=10000000019 k=20 # Very large prime
```

**Carmichael Numbers** (Fermat test weakness):
```bash
make test-number n=561 k=10    # Smallest Carmichael number
make test-number n=1105 k=10   # 5 × 13 × 17
make test-number n=1729 k=10   # Hardy-Ramanujan number
make test-number n=2821 k=10   # 7 × 13 × 31
```

**Composite Numbers:**
```bash
make test-number n=1000 k=5    # Small composite
make test-number n=10000 k=10  # Medium composite
```

**Pseudoprimes:**
```bash
make test-number n=341 k=10    # Fermat pseudoprime
make test-number n=2047 k=15   # Fermat pseudoprime
```

---

## 🎮 Makefile Commands Reference

### Setup & Build
| Command | Description | Duration |
|---------|-------------|----------|
| `make setup` | Initial project setup (run once) | 2-3 min |
| `make build` | Build C++ components | 10-20 sec |
| `make clean` | Clean build artifacts | 1 sec |

### Basic Operations
| Command | Description | Output |
|---------|-------------|--------|
| `make run` | Run demonstration | Console |
| `make test-number n=<N> k=<K>` | Test specific number | Console |
| `make test-carmichael` | Test Carmichael numbers | Console |

### Experiments & Analysis
| Command | Description | Duration | Output Files |
|---------|-------------|----------|--------------|
| `make experiments` | Run basic experiments | 2-5 min | 3 CSVs |
| `make benchmark-fermat` | Fermat benchmarks | 5-10 min | 2 CSVs |
| `make benchmark-miller-rabin` | Miller-Rabin benchmarks | 5-10 min | 2 CSVs |
| `make benchmark` | Both benchmarks | 10-20 min | 4 CSVs |
| `make comprehensive` | Comprehensive analysis | 10-15 min | 1 CSV |
| `make asymptotic` | Asymptotic analysis | 5-10 min | Multiple CSVs |
| `make analyze` | Analyze existing results | 1 sec | Console report |

### Plotting
| Command | Description | Plots Generated | Prerequisite |
|---------|-------------|-----------------|--------------|
| `make plot` | Basic plots | 3 | `make experiments` |
| `make plot-fermat` | Fermat analysis | 5 | None (runs tests) |
| `make plot-miller-rabin` | Miller-Rabin analysis | 4 | None (runs tests) |
| `make plot-fermat-benchmarks` | Fermat benchmark plots | 3 | `make benchmark-fermat` |
| `make plot-miller-rabin-benchmarks` | Miller-Rabin benchmark plots | 3 | `make benchmark-miller-rabin` |
| `make plot-comprehensive` | Comprehensive plots | 5 | None (runs tests) |
| `make plot-all` | All plots | 20+ | None (runs all) |

### Workflows
| Command | Description | What It Runs |
|---------|-------------|--------------|
| `make full-run` | Basic workflow | setup → experiments → analyze → plot |
| `make full-analysis` | Complete workflow | setup → benchmark → comprehensive → asymptotic → plot-all |

### Utilities
| Command | Description |
|---------|-------------|
| `make show-results` | Display results directory tree |
| `make help` | Show all available commands |

---

## 📊 Results Directory Structure

After running experiments, your `results/` directory will contain:

```
results/
├── accuracy_vs_k.csv                    # Accuracy vs iterations data
├── carmichael_analysis.csv              # Carmichael number analysis
├── performance_results.csv              # Performance comparison data
│
├── plots/                               # Basic experiment plots
│   ├── accuracy.png
│   ├── carmichael.png
│   └── performance.png
│
├── fermat_analysis/                     # Fermat-specific analysis
│   ├── fermat_summary_statistics.csv
│   └── plots/
│       ├── fermat_accuracy_vs_k.png
│       ├── fermat_false_positive_rates.png
│       ├── fermat_asymptotic_complexity.png
│       ├── fermat_carmichael_detection.png
│       └── fermat_time_distribution.png
│
├── fermat_benchmarks/                   # Benchmark results
│   ├── fermat_scaling.csv
│   ├── fermat_k_variation.csv
│   └── plots/
│       ├── fermat_scaling.png
│       ├── fermat_k_variation.png
│       └── fermat_comprehensive.png
│
├── comprehensive/                       # Comprehensive analysis
│   ├── asymptotic_analysis.csv
│   └── plots/
│       ├── accuracy_vs_k.png
│       ├── false_positive_rates.png
│       ├── asymptotic_complexity.png
│       ├── performance_comparison.png
│       └── carmichael_detection.png
│
└── asymptotic/                          # Asymptotic complexity data
    └── *.csv
```

---

## 🔍 Key Findings

### Accuracy Comparison
- **Fermat Test**: 
  - k=1: ~85-90% accuracy
  - k=10: ~94-95% accuracy
  - k=50: ~98-100% accuracy
  - **Critical Weakness**: 22-30% false positive rate on Carmichael numbers

- **Miller-Rabin Test**:
  - k=2: 100% accuracy (typical)
  - k=10: 100% accuracy
  - **No false positives** on Carmichael numbers

### Performance
- Miller-Rabin is only ~10-30% slower than Fermat
- Both achieve O(log³n) time complexity
- Negligible overhead for vastly superior accuracy

### Recommendation
**For cryptographic applications (RSA, etc.):**
- Use **Miller-Rabin** with k=40-50 iterations
- Provides security guarantees
- Error probability: (1/4)^k

**For quick heuristic checks:**
- Fermat with k=10-20 may suffice
- But beware of Carmichael numbers!

---

## 🛠️ Implementation Details

### Technical Stack

**Language & Standards:**
- **C++17** with STL vectors and data structures
- Modern C++ features (auto, range-based loops, structured bindings)
- Type-safe integer arithmetic with `uint64_t` and `__uint128_t`

**Compiler & Optimization:**
- **GCC 7.0+** (tested with GCC 11.2.0)
- Optimization flags: `-O3 -march=native`
- C++17 standard: `-std=c++17`
- Full warnings enabled: `-Wall -Wextra`

**Implementation Philosophy:**
- All algorithms implemented **from scratch** without external libraries
- No dependency on GMP, Boost, or other math libraries
- Pure STL: Only uses `<iostream>`, `<cstdint>`, `<random>`, `<chrono>`
- Comprehensive benchmarking harness for empirical analysis

**Python Analysis Tools:**
- Python 3.8+ with matplotlib and numpy
- Automated experiment orchestration
- Statistical analysis and visualization
- CSV-based data pipeline for reproducibility

### Core Algorithms

#### Fermat Primality Test
```
Input: n (number to test), k (iterations)
1. If n ≤ 1, return COMPOSITE
2. For i = 1 to k:
   a. Pick random a in [2, n-1]
   b. If gcd(a, n) > 1, return COMPOSITE
   c. If a^(n-1) mod n ≠ 1, return COMPOSITE
3. Return PROBABLY PRIME
```

**Time Complexity:** O(k × log³n)  
**Space Complexity:** O(1)  
**Error Probability:** At most (1/2)^k for non-Carmichael numbers  
**Critical Weakness:** Always fails on Carmichael numbers

#### Miller-Rabin Primality Test
```
Input: n (number to test), k (iterations)
1. Write n-1 = 2^s × d (d odd)
2. For i = 1 to k:
   a. Pick random a in [2, n-2]
   b. x = a^d mod n
   c. If x = 1 or x = n-1, continue
   d. For r = 1 to s-1:
      - x = x² mod n
      - If x = n-1, continue outer loop
      - If x = 1, return COMPOSITE (found nontrivial sqrt)
   e. If reached here, return COMPOSITE
3. Return PROBABLY PRIME
```

**Time Complexity:** O(k × log³n)  
**Space Complexity:** O(1)  
**Error Probability:** At most (1/4)^k for all composites  
**Key Strength:** No exceptions - works on ALL composites including Carmichael numbers

### Key Implementation Details

**Modular Exponentiation:**
- Binary exponentiation algorithm (square-and-multiply)
- Uses `__uint128_t` for intermediate calculations to prevent overflow
- Handles numbers up to 2^64 - 1

**Random Number Generation:**
- Uses `<random>` library with `std::mt19937_64` (Mersenne Twister)
- Cryptographically seeded with `std::random_device`
- Uniform distribution over specified ranges

**Benchmarking Harness:**
- High-resolution timing with `std::chrono::high_resolution_clock`
- Warmup runs to eliminate cache effects
- Multiple iterations with statistical analysis (mean, median, std dev)
- CSV output for reproducible analysis

### Test Dataset

**test_cases_small.csv** (454 cases):
- 182 Prime numbers (including Mersenne primes)
- 181 Composite numbers (various forms)
- 84 Carmichael numbers (critical test cases)
- 71 Pseudoprimes (Fermat pseudoprimes, strong pseudoprimes)

**test_cases_large.csv** (extended dataset):
- Numbers ranging from 10³ to 10¹⁸
- Includes large primes for cryptographic testing
- Additional Carmichael numbers and edge cases

---

## 🐛 Troubleshooting

### Issue: "Virtual environment not found"
**Solution:**
```bash
make setup
```

### Issue: "primality_test: command not found"
**Solution:**
```bash
make build
```

### Issue: Plots showing 0% accuracy
**Solution:**
Ensure C++ binaries are built:
```bash
make build
make plot-all
```

### Issue: "matplotlib not found"
**Solution:**
```bash
source venv/bin/activate
pip install matplotlib numpy
```

### Issue: Permission denied
**Solution:**
```bash
chmod +x cpp/primality_test
chmod +x setup.sh
```

### Issue: Compilation errors
**Solution:**
Ensure GCC 7+ is installed:
```bash
g++ --version
# Should show version 7.0 or higher
```

---

## 📝 Example Complete Workflow

```bash
# 1. Initial setup (first time only)
make setup

# 2. Run basic experiments
make experiments

# 3. View analysis
make analyze

# 4. Generate basic plots
make plot

# 5. Run advanced benchmarks
make benchmark

# 6. Run comprehensive analysis
make comprehensive

# 7. Generate all plots
make plot-all

# 8. View results
make show-results

# Results are in:
# - results/plots/
# - results/fermat_analysis/plots/
# - results/fermat_benchmarks/plots/
# - results/comprehensive/plots/
```

---