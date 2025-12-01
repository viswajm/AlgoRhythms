# Randomized Quick Sort

Implementation and experimental analysis of Randomized Quick Sort with comprehensive performance benchmarking across different input distributions and pivot selection strategies.

## Overview

This project implements Quick Sort with random pivot selection and compares its performance against deterministic variants. The implementation includes detailed instrumentation for counting comparisons, swaps, and measuring execution time.

## Algorithm Description

Quick Sort is a divide-and-conquer sorting algorithm:

1. **Pivot Selection**: Choose a pivot element (randomly or deterministically)
2. **Partitioning**: Rearrange array so elements < pivot come before elements > pivot
3. **Recursion**: Recursively sort the subarrays on either side of the pivot

### Randomized Quick Sort

The randomized version selects the pivot uniformly at random:
- Expected time complexity: **O(n log n)**
- Worst case: O(n²) but with very low probability
- In-place sorting with O(log n) stack space

### Partitioning Scheme

Uses **Hoare's partition scheme**:
- Two pointers move toward each other
- Swap elements that are on the wrong side
- Generally faster than Lomuto partition (fewer swaps)
- Returns partition index for recursive calls

## Files

- `rqs.cpp` - Main implementation of randomized Quick Sort with Hoare partitioning
- `run_experiments.sh` - Bash script to run comprehensive experiments
- `analysis.py` - Python script to analyze results and generate plots
- `Makefile` - Build configuration
- `requirements.txt` - Python dependencies

## Implementation Details

### Instrumentation

The implementation tracks:
- **Comparisons**: Number of element comparisons during partitioning
- **Swaps**: Number of element exchanges
- **Time**: Wall-clock execution time in milliseconds

```cpp
struct Counters {
    unsigned long long comparisons = 0;
    unsigned long long swaps = 0;
};
```

### Key Functions

1. **`hoare_partition(A, l, r, c)`**
   - Implements Hoare's partitioning scheme
   - Returns partition index
   - Updates comparison and swap counters

2. **`quicksort(A, l, r, c)`**
   - Main recursive sorting function
   - Randomly selects pivot from range [l, r]
   - Swaps pivot to first position
   - Recursively sorts left and right subarrays

3. **`cswap(a, b, c)`**
   - Counted swap that increments swap counter
   - Inline for performance

## Usage

### Compilation

Using Make:
```bash
make
```

Manual compilation:
```bash
g++ -O3 -std=c++17 -march=native rqs.cpp -o rqs
```

### Running Individual Sorts

```bash
# Basic usage (reads from stdin)
echo "5 3 1 4 2" | ./rqs

# Input format:
# First line: n (number of elements)
# Second line: n space-separated integers
```

Example:
```bash
echo -e "5\n3 1 4 2 5" | ./rqs
```

### Running Experiments

The experiment script tests multiple configurations:

```bash
# Run all experiments
bash run_experiments.sh

# Results will be saved in results/ directory
```

### Experimental Parameters

From `run_experiments.sh`:

**Array Sizes (n)**:
- 1,000
- 5,000
- 10,000
- 50,000

**Input Types**:
- `random` - Randomly generated integers
- `sorted` - Already sorted in ascending order
- `reverse` - Sorted in descending order
- `nearly_sorted` - Mostly sorted with k random swaps
- `few_distinct` - Limited number of distinct values

**Variants** (based on script):
- `random` - Random pivot selection (main implementation)
- `det_first` - Deterministic: always choose first element
- `det_last` - Deterministic: always choose last element
- `det_med3` - Deterministic: median-of-three

**Number of Trials**:
- Small arrays (≤5,000): 200 trials
- Medium arrays (≤10,000): 100 trials
- Large arrays (>10,000): 30 trials

## Analysis

### Running Analysis Script

```bash
python analysis.py
```

This generates:
1. **Time vs n plots** - For each input type, comparing variants
2. **Normalized comparison plots** - Comparisons/(n log n) vs n
3. **Regression analysis** - Fitting T(n) = a·n log n + b·n + c

### Output Files

Results are saved in `results/` directory:
- Individual CSV files: `{variant}_{input_type}_n{size}.csv`
- Combined results: `combined_results.csv`

### Plots

Generated in `plots/` directory:
- `time_vs_n_{input_type}.png` - Runtime comparison
- `comp_norm_{variant}.png` - Normalized comparison counts
- `fit_random_random.png` - Regression fit for random/random case

## Expected Results

### Time Complexity

**Randomized Quick Sort** (random pivot):
- **Average case**: O(n log n)
- **Worst case**: O(n²) with probability O(1/n!)
- **Best case**: O(n log n)

### Performance by Input Type

1. **Random Input**: Optimal performance, close to theoretical O(n log n)
2. **Sorted/Reverse**: Good performance with random pivot (unlike deterministic variants)
3. **Nearly Sorted**: Similar to random input
4. **Few Distinct**: Slightly worse due to uneven partitioning

### Comparisons

Expected number of comparisons:
- Average: ~1.39 n ln n ≈ 2n log₂ n
- Observed: Should align closely with theoretical predictions

### Swaps

- Generally fewer swaps than comparisons
- Hoare partition minimizes swaps compared to Lomuto

## Experimental Observations

### Advantages of Randomization

1. **Eliminates worst-case inputs**: No single input triggers O(n²) behavior
2. **Consistent performance**: Similar runtime across all input types
3. **No adversarial inputs**: Unlike deterministic pivot selection

### Comparison with Deterministic Variants

- **First element pivot**: O(n²) on sorted/reverse arrays
- **Last element pivot**: O(n²) on sorted/reverse arrays  
- **Median-of-three**: Better than first/last but still vulnerable
- **Random pivot**: Robust across all input distributions

## Dependencies

### C++ Code
- C++17 or later
- Standard library: `<iostream>`, `<vector>`, `<cstdlib>`, `<ctime>`

### Analysis Scripts
- Python 3.6+
- numpy
- pandas
- matplotlib

Install Python dependencies:
```bash
pip install -r requirements.txt
# or
pip install numpy pandas matplotlib
```

## Performance Tuning

### Compiler Optimizations
The Makefile uses:
- `-O3`: Aggressive optimization
- `-std=c++17`: C++17 standard
- `-march=native`: Optimize for local CPU architecture

### Potential Improvements

1. **Hybrid sorting**: Switch to insertion sort for small subarrays (n < 10)
2. **Three-way partitioning**: Better for arrays with many duplicates
3. **Tail recursion optimization**: Eliminate one recursive call
4. **Parallel Quick Sort**: Use threading for large subarrays

## Limitations

### Current Implementation
- Basic Hoare partitioning (no optimizations)
- No special handling for duplicate elements
- Simple random number generation (not cryptographically secure)

### Known Issues
- Very large arrays may cause stack overflow (deep recursion)
- Performance degrades with many duplicate values

## Extensions

Possible enhancements:
1. **Introspective Sort**: Fall back to heap sort if recursion depth exceeds log n
2. **Three-way partitioning**: Handle duplicates efficiently (Bentley-McIlroy)
3. **Dual-pivot Quick Sort**: Use two pivots (Java's Arrays.sort approach)
4. **Parallel Quick Sort**: Multi-threaded version for large arrays

