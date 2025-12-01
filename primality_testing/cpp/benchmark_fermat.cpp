#include "utils.h"
#include "fermat.h"
#include <iostream>
#include <iomanip>
#include <vector>
#include <chrono>
#include <bits/stdc++.h>
using namespace std;

/**
 * @brief Benchmark Fermat test on a single number
 */
void benchmark_single(uint64_t n, int k, int iterations = 100) {
    cout << "\n" << string(70, '=') << "\n";
    cout << "FERMAT TEST BENCHMARK\n";
    cout << "Number: " << n << ", k=" << k << ", iterations=" << iterations << "\n";
    cout << string(70, '=') << "\n";

    vector<double> times;
    bool result = false;

    // Warmup
    for (int i = 0; i < 5; i++) {
        fermat_test(n, k);
    }

    // Actual benchmark
    for (int i = 0; i < iterations; i++) {
        auto start = chrono::high_resolution_clock::now();
        PrimalityResult res = fermat_test(n, k);
        auto end = chrono::high_resolution_clock::now();
        
        double time_ms = chrono::duration<double, milli>(end - start).count();
        times.push_back(time_ms);
        result = res.is_probably_prime;
    }

    // Calculate statistics
    double sum = 0, min_time = times[0], max_time = times[0];
    for (double t : times) {
        sum += t;
        if (t < min_time) min_time = t;
        if (t > max_time) max_time = t;
    }
    double avg_time = sum / times.size();

    // Calculate median
    sort(times.begin(), times.end());
    double median_time = times[times.size() / 2];

    // Calculate standard deviation
    double variance = 0;
    for (double t : times) {
        variance += (t - avg_time) * (t - avg_time);
    }
    double std_dev = sqrt(variance / times.size());

    // Print results
    cout << "\nResult: " << (result ? "PROBABLY PRIME" : "COMPOSITE") << "\n";
    cout << "\nWall-Clock Time Statistics (" << iterations << " runs):\n";
    cout << "  Average:  " << fixed << setprecision(4) << avg_time << " ms\n";
    cout << "  Median:   " << median_time << " ms\n";
    cout << "  Min:      " << min_time << " ms\n";
    cout << "  Max:      " << max_time << " ms\n";
    cout << "  Std Dev:  " << std_dev << " ms\n";
    cout << "  Total:    " << sum << " ms\n";
}

/**
 * @brief Benchmark Fermat across different input sizes
 */
void benchmark_scaling(int k = 10, int iterations = 50) {
    cout << "\n" << string(70, '=') << "\n";
    cout << "FERMAT TEST SCALING BENCHMARK\n";
    cout << "k=" << k << ", iterations per number=" << iterations << "\n";
    cout << string(70, '=') << "\n";

    vector<uint64_t> test_numbers = {
        1009,           // ~10^3
        10007,          // ~10^4
        100003,         // ~10^5
        1000003,        // ~10^6
        10000019,       // ~10^7
        100000007,      // ~10^8
        1000000007,     // ~10^9
        10000000019ULL  // ~10^10
    };

    cout << "\n" << left << setw(15) << "Number" 
         << setw(12) << "Avg (ms)" 
         << setw(12) << "Median (ms)"
         << setw(12) << "Std Dev"
         << setw(10) << "Result" << "\n";
    cout << string(70, '-') << "\n";

    for (uint64_t n : test_numbers) {
        vector<double> times;
        bool result = false;

        // Warmup
        for (int i = 0; i < 3; i++) {
            fermat_test(n, k);
        }

        // Benchmark
        for (int i = 0; i < iterations; i++) {
            auto start = chrono::high_resolution_clock::now();
            PrimalityResult res = fermat_test(n, k);
            auto end = chrono::high_resolution_clock::now();
            
            double time_ms = chrono::duration<double, milli>(end - start).count();
            times.push_back(time_ms);
            result = res.is_probably_prime;
        }

        // Statistics
        double sum = 0;
        for (double t : times) sum += t;
        double avg_time = sum / times.size();

        sort(times.begin(), times.end());
        double median_time = times[times.size() / 2];

        double variance = 0;
        for (double t : times) {
            variance += (t - avg_time) * (t - avg_time);
        }
        double std_dev = sqrt(variance / times.size());

        cout << left << setw(15) << n
             << setw(12) << fixed << setprecision(4) << avg_time
             << setw(12) << median_time
             << setw(12) << std_dev
             << setw(10) << (result ? "PRIME" : "COMPOSITE") << "\n";
    }
}

/**
 * @brief Benchmark Fermat with varying k values
 */
void benchmark_k_variation(uint64_t n = 1000000007, int iterations = 50) {
    cout << "\n" << string(70, '=') << "\n";
    cout << "FERMAT TEST: ITERATIONS (k) BENCHMARK\n";
    cout << "Number: " << n << ", iterations per k=" << iterations << "\n";
    cout << string(70, '=') << "\n";

    vector<int> k_values = {1, 2, 5, 10, 20, 50, 100};

    cout << "\n" << left << setw(8) << "k" 
         << setw(12) << "Avg (ms)" 
         << setw(12) << "Median (ms)"
         << setw(12) << "Time/iter" << "\n";
    cout << string(50, '-') << "\n";

    for (int k : k_values) {
        vector<double> times;

        // Warmup
        for (int i = 0; i < 3; i++) {
            fermat_test(n, k);
        }

        // Benchmark
        for (int i = 0; i < iterations; i++) {
            auto start = chrono::high_resolution_clock::now();
            fermat_test(n, k);
            auto end = chrono::high_resolution_clock::now();
            
            double time_ms = chrono::duration<double, milli>(end - start).count();
            times.push_back(time_ms);
        }

        // Statistics
        double sum = 0;
        for (double t : times) sum += t;
        double avg_time = sum / times.size();

        sort(times.begin(), times.end());
        double median_time = times[times.size() / 2];
        double time_per_iter = avg_time / k;

        cout << left << setw(8) << k
             << setw(12) << fixed << setprecision(4) << avg_time
             << setw(12) << median_time
             << setw(12) << time_per_iter << "\n";
    }
}

/**
 * @brief Benchmark Fermat on Carmichael numbers
 */
void benchmark_carmichael(int k = 10, int iterations = 50) {
    cout << "\n" << string(70, '=') << "\n";
    cout << "FERMAT TEST: CARMICHAEL NUMBERS BENCHMARK\n";
    cout << "k=" << k << ", iterations per number=" << iterations << "\n";
    cout << string(70, '=') << "\n";

    vector<pair<uint64_t, string>> carmichael_numbers = {
        {561, "3 x 11 x 17"},
        {1105, "5 x 13 x 17"},
        {1729, "7 x 13 x 19"},
        {2465, "5 x 17 x 29"},
        {2821, "7 x 13 x 31"},
        {6601, "7 x 23 x 41"},
        {8911, "7 x 19 x 67"},
        {10585, "5 x 29 x 73"}
    };

    cout << "\n" << left << setw(10) << "Number" 
         << setw(18) << "Factorization"
         << setw(12) << "Avg (ms)"
         << setw(10) << "Result" << "\n";
    cout << string(55, '-') << "\n";

    for (const auto& [num, factors] : carmichael_numbers) {
        vector<double> times;
        bool result = false;

        // Warmup
        for (int i = 0; i < 3; i++) {
            fermat_test(num, k);
        }

        // Benchmark
        for (int i = 0; i < iterations; i++) {
            auto start = chrono::high_resolution_clock::now();
            PrimalityResult res = fermat_test(num, k);
            auto end = chrono::high_resolution_clock::now();
            
            double time_ms = chrono::duration<double, milli>(end - start).count();
            times.push_back(time_ms);
            result = res.is_probably_prime;
        }

        // Statistics
        double sum = 0;
        for (double t : times) sum += t;
        double avg_time = sum / times.size();

        cout << left << setw(10) << num
             << setw(18) << factors
             << setw(12) << fixed << setprecision(4) << avg_time
             << setw(10) << (result ? "PRIME*" : "COMPOSITE") << "\n";
    }

    cout << "\n* PRIME = INCORRECT (Carmichael numbers are composite)\n";
}

/**
 * @brief Main entry point
 */
int main(int argc, char* argv[]) {
    cout << "===================================================================\n";
    cout << "FERMAT PRIMALITY TEST - WALL-CLOCK TIME BENCHMARK\n";
    cout << "===================================================================\n";

    if (argc == 2) {
        string command = argv[1];
        
        if (command == "single") {
            benchmark_single(1000000007, 10, 100);
        }
        else if (command == "scaling") {
            benchmark_scaling(10, 50);
        }
        else if (command == "k-variation") {
            benchmark_k_variation(1000000007, 50);
        }
        else if (command == "carmichael") {
            benchmark_carmichael(10, 50);
        }
        else if (command == "all") {
            benchmark_single(1000000007, 10, 100);
            benchmark_scaling(10, 50);
            benchmark_k_variation(1000000007, 50);
            benchmark_carmichael(10, 50);
        }
        else {
            cout << "\nUnknown command: " << command << "\n";
            cout << "Available commands: single, scaling, k-variation, carmichael, all\n";
        }
    }
    else if (argc == 4) {
        // Custom: benchmark_fermat <number> <k> <iterations>
        uint64_t n = stoull(argv[1]);
        int k = stoi(argv[2]);
        int iterations = stoi(argv[3]);
        benchmark_single(n, k, iterations);
    }
    else {
        cout << "\nUsage:\n";
        cout << "  " << argv[0] << " <command>\n";
        cout << "  " << argv[0] << " <number> <k> <iterations>\n\n";
        cout << "Commands:\n";
        cout << "  single        - Benchmark single number with detailed stats\n";
        cout << "  scaling       - Benchmark across different input sizes\n";
        cout << "  k-variation   - Benchmark with different k values\n";
        cout << "  carmichael    - Benchmark on Carmichael numbers\n";
        cout << "  all           - Run all benchmarks\n\n";
        cout << "Examples:\n";
        cout << "  " << argv[0] << " all\n";
        cout << "  " << argv[0] << " scaling\n";
        cout << "  " << argv[0] << " 1000000007 10 100\n\n";
        
        cout << "Running default benchmark (scaling)...\n";
        benchmark_scaling(10, 50);
    }

    cout << "\n===================================================================\n";
    cout << "BENCHMARK COMPLETE\n";
    cout << "===================================================================\n\n";

    return 0;
}
