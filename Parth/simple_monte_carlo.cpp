#include <iostream>
#include <iomanip>
#include <cmath>
#include <random>
#include <functional>
#include <vector>
#include <string>
#include <fstream>   // CSV ADDITION

// ------------------- Result -------------------
struct MCResult {
    double estimate;
    double std_error;
};

// ------------------- Monte Carlo Integration -------------------
MCResult monte_carlo_integration(
    const std::function<double(double)>& func,
    double a, double b,
    int num_samples,
    unsigned int seed = 42
) {
    std::mt19937 rng(seed);
    std::uniform_real_distribution<double> dist(a, b);

    double mean = 0.0;
    double m2 = 0.0;

    for (int i = 1; i <= num_samples; ++i) {
        double x = dist(rng);
        double fx = func(x);

        double delta = fx - mean;
        mean += delta / i;
        double delta2 = fx - mean;
        m2 += delta * delta2;
    }

    double volume = b - a;
    double estimate = volume * mean;

    double std_error = 0.0;
    if (num_samples > 1) {
        double variance = m2 / (num_samples - 1);
        double std_dev = std::sqrt(variance);
        std_error = volume * std_dev / std::sqrt((double)num_samples);
    }

    return { estimate, std_error };
}

// ------------------- Test Case -------------------
struct TestCase {
    std::function<double(double)> func;
    double a;
    double b;
    double exact;
    std::string name;
};

// ------------------- Run MC on selected function -------------------
void run_single_function(
    const TestCase& test,
    const std::vector<int>& sample_sizes
) {
    // CSV ADDITION — open file in append mode
    std::ofstream csv("errors.csv", std::ios::app);

    std::cout << "\nFunction: " << test.name
              << "\nExact Integral = " << std::setprecision(10) << test.exact
              << "\n-------------------------------------------------------------\n";

    std::cout << std::setw(12) << "Samples"
              << std::setw(20) << "Estimate"
              << std::setw(20) << "Abs Error"
              << std::setw(20) << "Error (%)" << "\n";

    std::cout << "-------------------------------------------------------------\n";

    for (int n : sample_sizes) {
        MCResult res = monte_carlo_integration(test.func, test.a, test.b, n, 42);

        double estimate = res.estimate;
        double abs_err = std::abs(estimate - test.exact);

        double pct_err =
            (test.exact != 0.0) ? (abs_err / std::abs(test.exact)) * 100.0 : 0.0;

        std::cout << std::setw(12) << n
                  << std::setw(20) << std::fixed << std::setprecision(10) << estimate
                  << std::setw(20) << std::fixed << std::setprecision(10) << abs_err
                  << std::setw(20) << std::fixed << std::setprecision(6) << pct_err
                  << "\n";

        // ---------------- CSV ADDITION ----------------
        csv << "\"" << test.name << "\","
            << n << ","
            << std::setprecision(12) << abs_err << ","
            << std::setprecision(12) << pct_err
            << "\n";
        // ------------------------------------------------
    }

    csv.close();   // CSV ADDITION

    std::cout << "-------------------------------------------------------------\n\n";
}

// ------------------- Main -------------------
int main() {
    const double PI = std::acos(-1.0);

    std::vector<TestCase> all_tests;

    all_tests.push_back({ [](double x){ return x*x; }, 
        0.0, 1.0, 1.0/3.0, "x^2 on [0,1]" });

    all_tests.push_back({ [](double x){ return std::sin(x); },
        0.0, PI, 2.0, "sin(x) on [0,pi]" });

    all_tests.push_back({ [](double x){ return std::exp(-x*x); },
        0.0, 1.0, 0.5 * std::sqrt(PI) * std::erf(1.0), "exp(-x^2) on [0,1]" });

    all_tests.push_back({ [](double x){ return std::sqrt(x); },
        0.0, 1.0, 2.0/3.0, "sqrt(x) on [0,1]" });

    all_tests.push_back({ [](double x){ return std::log(1+x); },
        0.0, 1.0, 2*std::log(2.0) - 1.0, "ln(1+x) on [0,1]" });

    all_tests.push_back({ [](double x){ return 1.0/(1+x*x); },
        0.0, 1.0, PI/4.0, "1/(1+x^2) on [0,1]" });

    all_tests.push_back({ [](double x){ return std::cos(5*x); },
        0.0, 1.0, std::sin(5.0)/5.0, "cos(5x) on [0,1]" });

    std::cout << "Available functions:\n";
    for (size_t i = 0; i < all_tests.size(); ++i) {
        std::cout << (i+1) << ". " << all_tests[i].name << "\n";
    }

    std::cout << "Choose function index: ";
    int choice;
    std::cin >> choice;

    if (choice < 1 || choice > (int)all_tests.size()) {
        std::cerr << "Invalid choice. Exiting.\n";
        return 1;
    }

    std::vector<int> sample_sizes = {
        100, 500, 1000, 5000, 10000,
        20000, 50000, 100000, 200000, 500000
    };

    run_single_function(all_tests[choice-1], sample_sizes);

    printf("Run benchmarking test for all functions? (y/n): \n");
    char resp;
    scanf(" %c", &resp);
    if(resp == 'y' || resp == 'Y'){
        for (const auto& test : all_tests) {
            run_single_function(test, sample_sizes);
        }
    }

    return 0;
}
