echo "5 3 1 4 2" | ./rqs
echo -e "5\n3 1 4 2 5" | ./rqs
# Randomized Quick Sort Experiment Driver

This project provides a command-line harness for studying how different Quick Sort pivot policies behave on a variety of input distributions. The core executable (`rqs.cpp`) generates data, runs the selected algorithm variant, and emits CSV-formatted measurements for downstream analysis.

## Quick Start

```powershell
# Compile (PowerShell)


# Run five trials on nearly sorted arrays of length 5000
./rqs --n 5000 --trials 5 --variant det_med3 --input nearly_sorted --nearly_k 20

# Save results to a file
./rqs --n 20000 --trials 20 > results.csv
```

Use `make` if you prefer the provided `Makefile`, or call the compiler directly as shown above. On Windows PowerShell you may use either `./rqs` or `rqs.exe` when launching the program.

## Command-Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `--n <int>` | Number of elements per trial. | `10000` |
| `--trials <int>` | Number of independent runs. | `100` |
| `--variant <string>` | Pivot rule (`random`, `det_first`, `det_last`, `det_med3`). | `random` |
| `--input <string>` | Input distribution (`random`, `sorted`, `reverse`, `nearly_sorted`, `few_distinct`). | `random` |
| `--seed <ull>` | Override the automatically generated base seed. | `chrono::steady_clock` timestamp |
| `--nearly_k <int>` | Number of swaps applied in the `nearly_sorted` generator. | `10` |
| `--domain <int>` | Value range size for the `few_distinct` generator. | `5` |
| `--no-header` | Suppress the CSV header line. | header printed |

Arguments are processed sequentially, so each flag that expects a value must be followed immediately by that value.

## Implementation Overview

### Instrumentation

```cpp
struct Counters {
    unsigned long long comparisons = 0;
    unsigned long long swaps = 0;
    int max_depth = 0;
};
```

- **comparisons** increments each time the partition loop compares an element with the pivot.
- **swaps** increments via `do_swap`, which wraps every element exchange performed by the algorithm.
- **max_depth** records the deepest level of recursion reached, helping diagnose unbalanced partitions.

`ResultRow` (defined near the bottom of the file) packages the outcome of each trial so it can be printed as a single CSV record.

### Pivot Selection Strategies

Pivot choice is driven by the `variant` string:

- `random`: uniform random index in the current subarray via `rand()`.
- `det_first`: leftmost element.
- `det_last`: rightmost element.
- `det_med3`: median of the first, middle, and last values.
- Any unrecognized label falls back to the `random` strategy.

### Partitioning

`quicksort` employs Hoare's partition scheme directly:

1. Seed the pivot in the left slot when necessary.
2. Advance two indices (`i` from the left, `j` from the right) toward each other, counting comparisons.
3. Swap out-of-place elements with `do_swap` until the indices cross.
4. Recurse on the two partitions `[l, q]` and `[q + 1, r]` while updating `max_depth`.

This approach performs fewer swaps than Lomuto's scheme and interacts well with repeated values, though it still benefits from 3-way partitioning when duplicates are common.

### Seeding

Unless the user supplies `--seed`, the program derives a base seed from `std::chrono::steady_clock::now().time_since_epoch().count()`. Each trial uses `seed = base + trial_index`, which keeps runs reproducible while ensuring distinct pseudo-random sequences inside a single execution (`srand(static_cast<unsigned>(seed))`).

## Input Distributions

`run_trial` uses the requested `input_type` to build the working array before sorting:

- `random`: Fisher–Yates shuffle of the sequence `[0, …, n-1]`.
- `sorted`: Ascending order.
- `reverse`: Descending order.
- `nearly_sorted`: Start sorted, then apply `nearly_k` random swaps.
- `few_distinct`: Each entry is `rand() % domain`, creating many duplicates.
- Any other label reverts to the `random` generator.

## Output Format

The program writes CSV rows to standard output. Unless `--no-header` is set, the first line is:

```
algorithm,variant,input_type,n,trial,seed,comparisons,swaps,time_ms,max_depth
```

Each trial then contributes one row, with `time_ms` reported as a fixed-point millisecond duration measured using `std::chrono::steady_clock`.

## Experiment Automation

`run_experiments.sh` automates the benchmark matrix and mirrors the datasets under `results/`:

- **Array sizes**: `1000`, `5000`, `10000`, `50000`.
- **Input types**: `random`, `sorted`, `reverse`, `nearly_sorted`, `few_distinct`.
- **Pivot variants**: `random`, `det_first`, `det_last`, `det_med3`.
- **Trial counts**: 200 for `n ≤ 5000`, 100 for `n ≤ 10000`, otherwise 30.
- **Generator parameters**: `--nearly_k 50` for nearly sorted arrays, `--domain 5` for few-distinct arrays.

For each combination the script writes `results/<variant>_<input>_n<size>.csv`. After sweeping all runs it concatenates the data (skipping duplicate headers) into `results/combined_results.csv` so the Python analysis can consume a single file. Review or modify the arrays at the top of the script to tailor the experiment grid to your needs. `analysis.py` reads any CSVs produced by the driver and generates plots under `plots/`.

## Extending the Codebase

- Add new pivot policies by inserting another branch in the `variant` selection block inside `quicksort`.
- Factor out the partition loop if you want to compare Hoare against Lomuto or 3-way partitioning.
- Record additional metrics by updating `Counters` and the CSV emission logic.
- Swap in C++ `<random>` engines if you require better statistical properties or independent RNG streams.

## Known Limitations

- The implementation reuses the global C RNG for both data generation and pivot selection; determinism depends on consistent platform behavior of `rand()`.
- Deep recursion is possible for extremely unbalanced partitions; tail-recursion elimination or an introspective fallback is a potential enhancement.
- Arrays with many duplicates can still exhibit extra recursive work without a dedicated 3-way partition routine.

This README reflects the current `rqs.cpp` implementation so you can navigate, run, and extend the experiment driver with confidence.

