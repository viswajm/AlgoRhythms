# Monte Carlo Integration

Implementation and comparison of Monte Carlo and Quasi-Monte Carlo methods for numerical integration.

## Overview

This project implements two approaches for numerical integration:
1. **Simple Monte Carlo (MC)** - Uses pseudo-random sampling
2. **Quasi-Monte Carlo (QMC)** - Uses low-discrepancy Halton sequences

Both methods estimate definite integrals by sampling function values and computing statistical estimates.

## Theory

### Monte Carlo Integration

For computing $\int_a^b f(x) dx$:

1. Sample n random points $x_1, x_2, ..., x_n$ uniformly from [a,b]
2. Estimate: $I \approx (b-a) \cdot \frac{1}{n}\sum_{i=1}^n f(x_i)$
3. Error decreases as $O(1/\sqrt{n})$

### Quasi-Monte Carlo Integration

Uses deterministic low-discrepancy sequences (Halton sequence) instead of random numbers:
- Better space-filling properties
- More uniform coverage of the integration domain
- Faster convergence: $O((\log n)^d/n)$ for d dimensions
- For 1D: typically $O(\log n/n)$ or better

### Halton Sequence

The Halton sequence generates points in [0,1) with better uniformity:
```
H(i, base) = Σ (d_k / base^(k+1))
```
where $i = \sum d_k \cdot base^k$ is the base-b representation of i.

For 1D integration, we use base-2 Halton sequence.

## Files

- `simple_monte_carlo.cpp` - Monte Carlo integration using pseudo-random sampling
- `quasi_mc.cpp` - Quasi-Monte Carlo using Halton sequences  
- `simple_plotter.py` - Visualization script for comparing convergence rates
- `errors.csv` - Output file with MC error data
- `errors_quasi.csv` - Output file with QMC error data

## Implementation Details

### Test Functions

Both implementations test multiple functions:

1. **Linear**: $f(x) = x$ on [0, 1]
   - Exact: 0.5

2. **Polynomial**: $f(x) = x^2$ on [0, 1]
   - Exact: 1/3

3. **Trigonometric**: $f(x) = \sin(x)$ on [0, π]
   - Exact: 2.0

4. **Exponential**: $f(x) = e^x$ on [0, 1]
   - Exact: e - 1 ≈ 1.718281828

5. **Reciprocal**: $f(x) = 1/x$ on [1, 2]
   - Exact: ln(2) ≈ 0.693147181

6. **Gaussian**: $f(x) = e^{-x^2}$ on [0, 1]
   - Exact: (√π/2) · erf(1) ≈ 0.746824133

### Sample Sizes

Tests are run with varying sample sizes to observe convergence:
```
100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000
```

## Usage

### Compilation

```bash
# Compile Monte Carlo
g++ -o simple_monte_carlo simple_monte_carlo.cpp -std=c++17 -O3

# Compile Quasi-Monte Carlo
g++ -o quasi_mc quasi_mc.cpp -std=c++17 -O3
```

### Running the Programs

```bash
# Run Monte Carlo integration
./simple_monte_carlo

# Run Quasi-Monte Carlo integration  
./quasi_mc
```

### Output

Both programs generate:
1. **Console output**: Tables showing estimate, absolute error, and percentage error for each sample size
2. **CSV files**: 
   - `errors.csv` (from simple_monte_carlo)
   - `errors_quasi.csv` (from quasi_mc)

Example output:
```
Function: f(x) = x^2 on [0, 1]
Exact Integral = 0.3333333333
-------------------------------------------------------------
    Samples            Estimate           Abs Error          Error (%)
-------------------------------------------------------------
         100      0.3289512755      0.0043820578        1.314617
        1000      0.3325841267      0.0007492066        0.224762
       10000      0.3331234891      0.0002098442        0.062953
      100000      0.3333119482      0.0000213851        0.006416
-------------------------------------------------------------
```

### Visualization

Use the plotting script to compare convergence:

```bash
python simple_plotter.py
```

This generates plots showing:
- Error vs. number of samples
- Comparison between MC and QMC convergence rates
- Log-log plots to visualize convergence order

## Expected Results

### Monte Carlo
- **Convergence rate**: $O(1/\sqrt{n})$
- Error should halve when sample size increases by 4×
- Works well but slower convergence

### Quasi-Monte Carlo
- **Convergence rate**: $O(\log n / n)$ or better
- Significantly faster convergence than standard MC
- More consistent results (deterministic)
- Better suited for smooth integrands

### Comparison

For smooth functions in low dimensions:
- QMC typically achieves 2-3 orders of magnitude better accuracy
- QMC reaches 10^-6 error with ~100x fewer samples than MC
- MC has larger variance between runs due to randomness

## Error Analysis

The CSV files contain:
- Function name
- Number of samples
- Absolute error: |estimate - exact|
- Relative error: 100 × |estimate - exact| / |exact|

### Interpreting Results

Monitor convergence by plotting log(error) vs log(n):
- **Monte Carlo**: slope ≈ -0.5
- **Quasi-Monte Carlo**: slope < -0.5 (faster convergence)

## Dependencies

### C++ Code
- C++11 or later
- Standard library: `<cmath>`, `<random>`, `<functional>`, `<fstream>`

### Python Scripts
- Python 3.6+
- matplotlib
- pandas (optional, for advanced analysis)

Install dependencies:
```bash
pip install matplotlib pandas
```

## Extensions

Possible improvements:
1. **Multi-dimensional integration**: Extend to 2D, 3D integrals
2. **Stratified sampling**: Divide domain into strata
3. **Importance sampling**: Sample more where integrand varies most
4. **Sobol sequences**: Alternative low-discrepancy sequence
5. **Adaptive sampling**: Increase sampling in regions with high variance

## Performance Notes

- Both implementations use Welford's online algorithm for variance computation
- Single-pass computation minimizes memory usage
- CSV output allows post-processing and comparison
- Seed=42 ensures reproducibility for Monte Carlo

