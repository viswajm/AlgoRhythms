#include <bits/stdc++.h>
using namespace std;
using ull = unsigned long long;

struct Counters {
    ull comparisons = 0;
    ull swaps = 0;
    int max_depth = 0;
};


void do_swap(int &a, int &b, Counters &c) {
    ++c.swaps;
    int tmp = a;
    a = b;
    b = tmp;
}

int det_median_of_three_index(const vector<int> &A, int l, int r) {
    int m = l + (r - l) / 2;
    int a = A[l], b = A[m], c = A[r];
    if ((a <= b && b <= c) || (c <= b && b <= a)) return m;
    if ((b <= a && a <= c) || (c <= a && a <= b)) return l;
    return r;
}

void quicksort(vector<int> &A, int l, int r, Counters &c, int depth, const string &variant) {
    if (l >= r) return;
    c.max_depth = max(c.max_depth, depth);

    int pidx = l;
    if (variant == "random") {
        pidx = l + (rand() % (r - l + 1));
    } else if (variant == "det_first") {
        pidx = l;
    } else if (variant == "det_last") {
        pidx = r;
    } else if (variant == "det_med3") {
        pidx = det_median_of_three_index(A, l, r);
    } else {
        pidx = l + (rand() % (r - l + 1));
    }

    int pivot = A[pidx];
    if (pidx != l) do_swap(A[pidx], A[l], c);
    int i = l - 1;
    int j = r + 1;
    while (true) {
        do {
            ++i;
            ++c.comparisons;
        } while (A[i] < pivot);

        do {
            --j;
            ++c.comparisons;
        } while (A[j] > pivot);

        if (i >= j) break;
        do_swap(A[i], A[j], c);
    }
    int q = j; 

    quicksort(A, l, q, c, depth + 1, variant);
    quicksort(A, q + 1, r, c, depth + 1, variant);
}

struct ResultRow {
    string variant, input_type;
    int n, trial;
    ull seed, comparisons, swaps;
    double time_ms;
    int max_depth;
};

ResultRow run_trial(int n, const string &input_type, const string &variant,
                    int trial_idx, ull seed, int nearly_k, int domain) {

    srand(static_cast<unsigned>(seed));
    vector<int> A(n);

    if (input_type == "random") {
        iota(A.begin(), A.end(), 0);
        for (int i = n - 1; i > 0; --i) {
            int j = rand() % (i + 1);
            int tmp = A[i]; A[i] = A[j]; A[j] = tmp;
        }
    } else if (input_type == "sorted") {
        iota(A.begin(), A.end(), 0);
    } else if (input_type == "reverse") {
        for (int i = 0; i < n; ++i) A[i] = n - i;
    } else if (input_type == "nearly_sorted") {
        iota(A.begin(), A.end(), 0);
        for (int k = 0; k < nearly_k; ++k) {
            int i = rand() % n;
            int j = rand() % n;
            if (i != j) {
                int tmp = A[i]; A[i] = A[j]; A[j] = tmp;
            }
        }
    } else if (input_type == "few_distinct") {
        int dom = max(1, domain);
        for (int i = 0; i < n; ++i) A[i] = rand() % dom;
    } else {
        iota(A.begin(), A.end(), 0);
        for (int i = n - 1; i > 0; --i) {
            int j = rand() % (i + 1);
            int tmp = A[i]; A[i] = A[j]; A[j] = tmp;
        }
    }

    Counters c;
    auto t0 = chrono::steady_clock::now();
    quicksort(A, 0, n - 1, c, 0, variant);
    auto t1 = chrono::steady_clock::now();

    double ms = chrono::duration<double, milli>(t1 - t0).count();
    return {variant, input_type, n, trial_idx, seed, c.comparisons, c.swaps, ms, c.max_depth};
}

void print_csv_header() {
    cout << "algorithm,variant,input_type,n,trial,seed,comparisons,swaps,time_ms,max_depth\n";
}

int main(int argc, char **argv) {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n = 10000, trials = 100, nearly_k = 10, domain = 5;
    string variant = "random", input_type = "random";
    ull seed0 = chrono::steady_clock::now().time_since_epoch().count();
    bool header = true;

    for (int i = 1; i < argc; ++i) {
        string s = argv[i];
        if (s == "--n") n = atoi(argv[++i]);
        else if (s == "--trials") trials = atoi(argv[++i]);
        else if (s == "--variant") variant = argv[++i];
        else if (s == "--input") input_type = argv[++i];
        else if (s == "--seed") seed0 = stoull(argv[++i]);
        else if (s == "--nearly_k") nearly_k = atoi(argv[++i]);
        else if (s == "--domain") domain = atoi(argv[++i]);
        else if (s == "--no-header") header = false;
    }

    if (header) print_csv_header();

    for (int t = 0; t < trials; ++t) {
        ull seed = seed0 + t;
        ResultRow r = run_trial(n, input_type, variant, t, seed, nearly_k, domain);
        cout << "QuickSort," << r.variant << "," << r.input_type << ","
             << r.n << "," << r.trial << "," << r.seed << ","
             << r.comparisons << "," << r.swaps << ","
             << fixed << setprecision(6) << r.time_ms << ","
             << r.max_depth << "\n";
    }
    return 0;
}
