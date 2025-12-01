

#include <iostream>
#include <vector>
#include <cstdlib>   // rand, srand
#include <ctime>     // clock
#include <iomanip>   // setprecision
using namespace std;

struct Counters {
    unsigned long long comparisons = 0;
    unsigned long long swaps = 0;
};

// counted swap
inline void cswap(int &a, int &b, Counters &c) {
    c.swaps++;
    int t = a;
    a = b;
    b = t;
}

int hoare_partition(vector<int> &A, int l, int r, Counters &c) {
    int pivot = A[l];
    int i = l - 1;
    int j = r + 1;

    while (true) {
        do {
            i++;
            c.comparisons++;
        } while (A[i] < pivot);

        do {
            j--;
            c.comparisons++;
        } while (A[j] > pivot);

        if (i >= j) return j;

        cswap(A[i], A[j], c);
    }
}

void quicksort(vector<int> &A, int l, int r, Counters &c) {
    if (l >= r) return;

    int p = l + rand() % (r - l + 1);

    cswap(A[l], A[p], c);

    int mid = hoare_partition(A, l, r, c);

    quicksort(A, l, mid, c);
    quicksort(A, mid + 1, r, c);
}

int main() {
    int n;
    cin >> n;

    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];

    srand(time(nullptr));
    Counters c;

    clock_t t0 = clock();
    quicksort(A, 0, n - 1, c);
    clock_t t1 = clock();

    double time_ms = 1000.0 * (t1 - t0) / CLOCKS_PER_SEC;

    cerr << "Time (ms): " << fixed << setprecision(3) << time_ms << "\n";
    cerr << "Comparisons: " << c.comparisons << "\n";
    cerr << "Swaps: " << c.swaps << "\n";

    // print sorted array
    for (int x : A) cout << x << " ";
    cout << "\n";

    return 0;
}
